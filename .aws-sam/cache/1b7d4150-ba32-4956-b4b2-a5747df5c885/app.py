import json
import requests
import pandas as pd 
import datetime as dt
import pytz
from random import randint
import boto3 
import botocore
from scipy.signal import find_peaks
import numpy as np 
from io import StringIO
import uuid 
from decimal import Decimal


from ig_buy_sell_api_helper import IG_buy_sell


# # Sample event structure
# {
#     "symbol": "FTSE",
#     "config": {
#         "name": "FTSE",
#         "MarketId": "IX.D.FTSE.IFA.IP",
#         "prominence": 2
#     },
#     "signal": 1,
#     "trade_params": {
#         "tp": 7608.900000000001,
#         "sl": 7516.23,
#         "max_drawdown_multiplier": 0.02,
#         "price_points": [
#             7574.6,
#             7590.6,
#             7554
#         ]
#     }
# }
def lambda_handler(event, context):
    
    # Get event params
    symbol_name = event['symbol']
    config = event['config']
    signal = event['signal']
    trade_params = event['trade_params']

    symbol_market_id = config['MarketId']

    sl = trade_params['sl']
    tp = trade_params['tp']

    # ========================================================================================================================
    #                         Function Variables
    # ========================================================================================================================


    # Propagate the global variables from the prev steps through this step
    gv_errors_exist = event["errors_exist"]
    gv_bapiret_tab = event["messages"]



    print(f"*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=\nRunning the order-execution logic for the symbol {symbol_name}\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
    
    try: 
        # STEP 1: Login and init the IG_helper class
        ig = IG_buy_sell(config, signal, trade_params)

        # ========================================================================================================================
        #                   CODE FOR BUY OR SELL - YEAH!!
        # ========================================================================================================================
        if signal != 0: 

            # If there are no open positions, just create a new position
            if ig.df_open_positions.shape[0] == 0: 

                position_details = ig.create_position()  | {"price_points": trade_params['price_points'], "trailing_stop_rating": 0}
                print(f"Going to create new item in DB for position id {position_details['DealId']}")
                create_db(position_details)

            else:       # Handle existing long and short positions here

                SAME_DIRECTION = "BUY" if signal == 1 else "SELL"
                OPPOSITE_DIRECTION = "SELL" if signal == 1 else "BUY"

                # Verify that all the positions are in the same direction. If they arent, thats an error 
                if ig.df_open_positions['direction'].unique().size > 1:
                    print("Simultaneous long and short positions exist for this instrument. Please investigate.")

                # If there are existing positions in the opposite direction, close all of them
                if ig.df_open_positions['direction'].unique()[0] == OPPOSITE_DIRECTION: 
                    ig.close_all_positions()

                # Now that all the positions in the opposite  dirn are closed, create a new position as per the signal 
                    position_details = ig.create_position()  | {"price_points": trade_params['price_points'], "trailing_stop_rating": 0}
                    print(f"Going to create new item in DB for position id {position_details['DealId']}")
                    create_db(position_details)
                
                
                # If there are existing positions in the same direction: 
                    # 1. Check if any of those positions are same as the new position we are trying to create 
                    # 2. If they are different, create a new position
                else:
                    df_positions_db = read_db() 
                    
                    df_positions_db = df_positions_db.query(
                        f"(Epic == '{symbol_market_id}') and "
                        "(Status == 'OPENED') and "
                        f"(Direction == '{SAME_DIRECTION}')"
                    ).copy()

                    if df_positions_db.shape[0] > 0: 

                    # 1. Check if any of those positions are same as the new position we are trying to create 
                        duplicate_position = False
                        for position in df_positions_db.itertuples():
                            if position.price_points == trade_params['price_points']: 
                                duplicate_position = True

                        if not duplicate_position:
                    # 2. If they are different, create a new position
                            position_details = ig.create_position()  | {"price_points": trade_params['price_points'], "trailing_stop_rating": 0}
                            print(f"Going to create new item in DB for position id {position_details['DealId']}")
                            create_db(position_details)
                        else: 
                            print("Duplicate position, nothing to do here")
                    
                    else: 
                    # If there are no entries found in DB. 
                    # Again, this shouldnt happen - cos ideally all our positions will be in the DB
                        position_details = ig.create_position()  | {"price_points": trade_params['price_points'], "trailing_stop_rating": 0}
                        print(f"Going to create new item in DB for position id {position_details['DealId']}")
                        create_db(position_details)
                    

        # ========================================================================================================================
        #                   CODE FOR NO SIGNAL
        # ========================================================================================================================
        if signal == 0: 

            # This part is to revise the SL values of the existing positions 

            # Only do the further processing if there are any open positions
            # STEPS:
            # 1. Get all the open positions from IG APIs. 
            # 2. Get all the values from DB for this DealId. Lookup the price points for these positions from the DB
            # 3. IF its an open long position
            #   3.1. If the current price is above price_point[1] but below 1.2 extension level
            #           SET the stop distance to price_point_1 and trailing_stop_distance 
            #   3.2. Calculate the extension level: 
            #        extension level = (current_price - price_point[1]) / (price_point[1] - price_point[2]) * 100
            #   3.3. Calculate the extension band (1=10%-20%, 2=20%-30%, 3=30%-40%, ...): formula = extension level DIV 10
            #   3.4. IF extension band <= prev_highest_ext_band (fetched from DB records), do nothing
            #   3.5. IF 

            # Only when they are open positions
            if ig.df_open_positions.shape[0] > 0: 

                # Pre-reqs - Pre-validations - to check the solution quality
                if ig.df_open_positions['direction'].unique().size > 1:

                    gv_bapiret_tab.append({
                        "message_type": 'E',
                        "message_source": "IgProcessBuySellFunction",
                        "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                        "message": "Simultaneous long and short positions exist for this instrument. Please investigate."
                    })
                    gv_errors_exist = True
                
                if not gv_errors_exist: 

                    # Read the DB. find the record from the db for each position
                    df_positions_db = read_db() 

                    # for position in ig.df_open_positions: 
                    for _, position in ig.df_open_positions.iterrows():

                        print(f"Evaluating the trailing stop conditions for position {position['dealId']}")
                    
                        df_positions_db = df_positions_db.query(
                            f"(DealId == '{position['dealId']}')"
                        ).copy()

                        if df_positions_db.shape[0] == 0: 

                            print(f"DB Read issue: Open position on IG, but couldnt find the record in DB for the dealId = {position['dealId']}")

                        elif df_positions_db.shape[0] > 1: 

                            print(f"DB Read issue: Multiple DB entries found for the dealId = {position['dealId']}")

                        else: 

                            df_positions_db = df_positions_db.reset_index(drop=True).copy()

                            primary_key = df_positions_db['Id'][0]

                            if "trailing_stop_rating" in df_positions_db.columns.to_list():
                                trailing_stop_rating = df_positions_db['trailing_stop_rating'][0]
                            else: 
                                # It may be an earlier record. Position created before the trailing_stop change was implemented
                                trailing_stop_rating = 0                

                            updated_trailing_stop_level = ig.evaluate_trailing_stop(position['dealId'], df_positions_db)

                            if trailing_stop_rating != updated_trailing_stop_level:

                                update_db(position['dealId'], primary_key, 'trailing_stop_rating', updated_trailing_stop_level)


        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Last part 
        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        gv_bapiret_tab = gv_bapiret_tab + ig.bapiret_tab
                        

    except RuntimeError as error: 

        error_string = str(error)
        error_string = error_string.replace("\'", "\"")
        print(error_string)

        gv_bapiret_tab.append({
            "message_type": 'E',
            "message_source": "IgProcessBuySellFunction",
            "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
            "message": json.loads(error_string)
        })

        gv_errors_exist = True


    return {
        'symbol': symbol_name,
        'config': config,
        'signal': signal,
        'trade_params': trade_params,
        'errors_exist': gv_errors_exist,
        'messages': gv_bapiret_tab
    }


def create_db(position_details): 

    # Create a DynamoDB service client
    dynamodb = boto3.resource('dynamodb', 
                            region_name='us-east-1')

    # Specify your DynamoDB table name
    table_name = 'IG-Trading-1-TransactionTable-1UQVEKJ9H4KTV'  

    # Get the table resource
    table = dynamodb.Table(table_name)

    # Define the new item to insert
    new_item = {
        'Id': str(uuid.uuid1()),
        'Source': "IgProcessBuySellFunction",
        'Timestamp': dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S'),
        'Updated_on': dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S')
    } | position_details

    new_entry = json.loads(json.dumps(new_item), parse_float=Decimal)
    
    print(f"Adding new item to DB\n{new_entry}")
    # Insert the new item
    response = table.put_item(Item=new_entry)

    # print(f"Adding new item to DB. Position id: ")
    print(f"Response after adding the new item for deal id {position_details['DealId']} to DB: {response}")

    return True

def read_db(): 

    # Create a DynamoDB service client
    dynamodb = boto3.resource('dynamodb', 
                            region_name='us-east-1')

    # Specify your DynamoDB table name
    table_name = 'IG-Trading-1-TransactionTable-1UQVEKJ9H4KTV'  

    # Get the table resource
    table = dynamodb.Table(table_name)

    # Scan the table
    try:
        response = table.scan()
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("DB read successful")
    except botocore.exceptions.ClientError as error:
        print(error)
        return False

    df_data = pd.DataFrame(response['Items'])
    df_data['Timestamp'] = pd.to_datetime(df_data['Timestamp'], format="%Y-%m-%dT%H:%M:%S")

    def convert_decimal_to_float(item):
        if isinstance(item, Decimal):
            return float(item)
        # Since the price_points is going to be a list containing decimal values 
        if isinstance(item, list):
            # Use list comprehension to convert Decimal to float within the list
            return [float(x) if isinstance(x, Decimal) else x for x in item]
        return item

    # Convert decimal.Decimal to float for each column
    for column in df_data.columns:
        df_data[column] = df_data[column].map(convert_decimal_to_float)

    return df_data

def update_db(dealId, primary_key, param_name, param_val):

    # Create a DynamoDB service client
    dynamodb = boto3.resource('dynamodb', 
                            region_name='us-east-1')

    # Specify your DynamoDB table name
    table_name = 'IG-Trading-1-TransactionTable-1UQVEKJ9H4KTV'  

    # Get the table resource
    table = dynamodb.Table(table_name)

    # Update the trailing_stop_rating field for the specified record
    response = table.update_item(
        Key={
            'Id': primary_key  # The primary key column name and its value
        },
        UpdateExpression= f'SET {param_name} = :val, Updated_on = :uo',
        ExpressionAttributeValues={
            ':val': param_val,
            ':uo':  dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S')
    },
        ReturnValues="UPDATED_NEW"  # Specifies that you want to get back the new value of the updated attribute
    )

    return True

