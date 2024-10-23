import json
import requests
import pandas as pd 
import datetime as dt
import pytz
from random import randint
import boto3 
import botocore
from botocore.exceptions import ClientError

from scipy.signal import find_peaks
import numpy as np 
from io import StringIO


from util_funcs import *
from fibo_strategy import strategy

from ig_api_helper import *

import os
import time

# # Sample event structure
# {
#     "request_headers": {},
#     "account_balance": {},
#     "config": {
#         "name": "ASX",
#         "MarketId": "IX.D.ASX.IFT.IP"
#     },
#     "testing_params": {
#         "history-date-last": {
#             "year": 2024,"month": 1,"day": 27,"hour": 8,"min": 0,"sec": 0
#         },
#         "sy-datum": {
#             "year": 2024, "month": 1, "day": 28, "hour": 8, "min": 0, "sec": 0
#         }
#     }
# }
def lambda_handler(event, context):

    # Table to record errors. This will be propagated throughout the workflow 
    gv_bapiret_tab = []
    gv_errors_exist = False
    gv_market_closed = False


    signal = 0
    params = {}
    
    # Get event params
    config = event['config']
    symbol_name = config['name']
    symbol_market_id = config['MarketId']
    prominence = config.get("prominence", 2)

    # Added some functionality for testing 
    testing_params = event.get("testing_params", {})
    if len(testing_params) > 0:
        testing_enabled = True

        history_cutoff_param = testing_params.get("history-date-last")
        if history_cutoff_param is not None:
            history_cutoff = list(history_cutoff_param.values())
            history_cutoff_date = dt.datetime(history_cutoff[0], history_cutoff[1], history_cutoff[2], 
                                            history_cutoff[3], history_cutoff[4], history_cutoff[5]  )
        else: history_cutoff_date = ""
        
        current_datetime_param = testing_params.get("sy-datum")
        if current_datetime_param is not None:
            current_datetime_list = list(current_datetime_param.values())
            current_datetime = dt.datetime(current_datetime_list[0], current_datetime_list[1], current_datetime_list[2], 
                                            current_datetime_list[3], current_datetime_list[4], current_datetime_list[5]  )
        else: current_datetime = ""
        
    else: 
        testing_enabled = False
        history_cutoff_date = ""
        current_datetime = ""


    print(f"*=*=*=*=*=*=*=*=*=*=*=*=*=\nRunning the strategy for the symbol {symbol_name}\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")

    # STEP1: Get the Historical prices CSV file from S3 
    s3_client = boto3.client('s3')
    bucket =  'aws-sam-cli-managed-default-samclisourcebucket-3pncdm36uy1a'
    key = f'IG-Trading-1/Resources/PriceData/Hourly/{symbol_name}.csv'

    try: 
        response = s3_client.get_object(Bucket=bucket, Key=key)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            df_prices_hist = pd.read_csv(response.get("Body"), parse_dates=True, index_col=0)

            if testing_enabled: 
                if history_cutoff_date != "":
                    df_prices_hist = df_prices_hist.loc[df_prices_hist.index <= history_cutoff_date]

            print("\nHistorical data fetched from S3\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
            print(f"Total historical records found: {df_prices_hist.shape[0]}\nIndex value of last record: {df_prices_hist.index[-1]}")
    except ClientError as err: 
        error_message = {
            "error_function": "FetchDataFromS3",
            "error_message": f"Error in reading Historical Price data from S3"
        }
        gv_errors_exist = True
        gv_bapiret_tab.append({
            "message_type": 'E',
            "message_source": "IgRunStrategyFunction",
            "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
            "message": error_message,
        })

    if not gv_errors_exist:
    
        # STEP 2: Call the IG Prices endpoint and get the last 2 records
        login()

        df_prices_new = get_price_data(symbol_market_id, num_points=2)
        print("\nPrice data fetched from IG API\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
        print(df_prices_new)

        # All these scenarios are handled by a different periodic lambda function 
        # # There are multiple scenarios possible: 
        # # 1. new data last row < current timestamp by less than 1 hour.
        # #       This will be the case in most scenarios. 
        # #       This will mean that the last bar is the current "In progress" candle. Dont use it
        # # 2. New data last row < current timestamp by more than 1 hour but less than 2 hours
        # #       This will be the scenario for the end of the trading session - e.g. the first time we go into the weekend
        # #       This will mean that the last bar is the latest completed candle. We will need to use it for the strategy
        # # 3. New data last row < current timestamp by more than 2 hours
        # #       This will be the scenario if the script runs on a weekend
        # #       Exit trading for this scenario

        now_datetime =  dt.datetime.now(pytz.timezone('Australia/Sydney'))
        local_datetime = now_datetime.replace(tzinfo=None)
        difference =  local_datetime - df_prices_new.index[-1]

        if difference < pd.Timedelta(hours=1):
            # Condition 1
            df_prices_new = df_prices_new.iloc[:-1, :].copy()
            print(f"\nCondition 1 satisfied, Difference = {difference}. The last bar is the current 'In progress' candle. Dont use it\n")
        elif (difference > pd.Timedelta(hours=2)):        
            # Condition 3
            error_message = {
                "error_function": "MarketClosed",
                "error_message": f"Market closed for Symbol {symbol_name}. Nothing to do further"
            }
            gv_errors_exist = False
            gv_market_closed = True
            gv_bapiret_tab.append({
                "message_type": 'I',
                "message_source": "IgRunStrategyFunction",
                "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                "message": error_message,
            })

        # STEP 3: Merge both the data
        df_prices = pd.concat([df_prices_hist, df_prices_new], axis="rows")
        df = df_prices.reset_index()
        df_deduplicated = df.drop_duplicates(subset='Date', keep='last')
        df_prices = df_deduplicated.set_index('Date')
        df_prices = df_prices.sort_index()

        print("\nPrice data merged from historical and new dataframes\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
        print(f"Total historical records found: {df_prices.shape[0]}\n{df_prices.tail(3)}")

        # Update the file to S3 in case we forget later on. Actually there may be run time errors in the strategy
        csv_buffer = StringIO()
        df_prices.to_csv(csv_buffer)
        s3_resource = boto3.resource('s3')
        s3_resource.Object(bucket, key).put(Body=csv_buffer.getvalue())

        if not gv_market_closed: 

            # STEP 4: Call the Strategy function and get the signal 
            signal, params = strategy(df_prices, event)

            if signal == 1: 
                print(f"Fibo Strategy outcome: Buy Signal generated")
                gv_bapiret_tab.append({
                    "message_type": 'S',
                    "message_source": "IgRunStrategyFunction",
                    "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                    "message": "Fibo Strategy outcome: Buy Signal generated",
                })
            elif signal == -1: 
                print("Fibo Strategy outcome: Sell Signal generated")
                gv_bapiret_tab.append({
                    "message_type": 'S',
                    "message_source": "IgRunStrategyFunction",
                    "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                    "message": "Fibo Strategy outcome: Sell Signal generated",
                })
            else: 
                print("Fibo Strategy outcome: No signal generated")
                gv_bapiret_tab.append({
                    "message_type": 'I',
                    "message_source": "IgRunStrategyFunction",
                    "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                    "message": "Fibo Strategy outcome: No signal generated",
                })


    return {
        'symbol': symbol_name,
        'config': config,
        'signal': signal,
        'trade_params': params,
        'market_closed': gv_market_closed,
        'errors_exist': gv_errors_exist,
        'messages': gv_bapiret_tab
    }


