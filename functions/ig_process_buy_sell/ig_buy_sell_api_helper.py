import json
import os 
import requests
import datetime as dt
import pandas as pd 
import numpy as np 
import math
import pytz

class IG_buy_sell: 

    request_headers = {'Content-Type': 'application/json','X-IG-API-KEY': os.environ.get("DEMO_API_KEY"), 'Version': '2'}
    account_balance = {}
    config = {}
    market_id = ''
    signal = 0
    trade_params = {}
    market_details = {}
    df_open_positions = None

    edit_position_sl = 0
    edit_position_tp = 0
    edit_position_trail_distance = 0

    # Collect the info and warning messages raised in this class and send them to the output of the step functions
    bapiret_tab = []

    # Util func
    def add_message(self, message_func, message, message_type='I'):

        self.bapiret_tab.append({
                "message_type": message_type,
                "message_source": message_func,
                "message_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                "message": message
            })
        
        return True


# ====================== API LOGIN ==============================================================
    def __init__(self, i_config, i_signal, i_trade_params):

        url = os.environ.get("DEMO_API_URL") + "/session"

        payload = json.dumps({
        "identifier": os.environ.get("DEMO_USERNAME"),
        "password": os.environ.get("DEMO_PASSWORD"),
        "encryptedPassword": None
        })

        self.request_headers['Version'] = '2'
        
        response = requests.request("POST", url, headers=self.request_headers, data=payload)
        if response.status_code != 200: 
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in login API. Error response = {response.text}"
            }
            raise RuntimeError(error_message)

        request_header = dict(response.headers)

        response_body = json.loads(response.text)

        self.account_balance = response_body['accountInfo']
        self.request_headers.update({"CST": request_header['CST'], "X-SECURITY-TOKEN": request_header['X-SECURITY-TOKEN']})

        # Setting global variables
        # global config, market_id, trade_params
        self.config = i_config
        self.market_id = i_config.get("MarketId")
        self.signal = i_signal
        self.trade_params = i_trade_params

        # Initialising the global variables 
        self.get_account_balance(refresh=True)
        # self.get_account_info()
        self.get_market_details()
        self.get_open_positions()

    
    # ======================GET ACCOUNT BALANCE===================================================
    # Get the account balance
    def get_account_balance(self, refresh=True):
    
        if refresh: 
            # Call the account balance API once again and set it to the global parameter
            account_info = self.get_account_info()
            self.account_balance = account_info['accounts'][0]['balance']
        
        return self.account_balance
    
    # ====================== API ACCOUNT INFO ==============================================================
    # API for calling account info 
    def get_account_info(self):
        
        url = os.environ.get("DEMO_API_URL") + "/accounts"

        payload = ""
        
        self.request_headers["Version"] = '1'
        
        response = requests.request("GET", url, headers=self.request_headers, data=payload)
        if response.status_code != 200: 
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in Account info API. Error response = {response.text}"
            }
            raise RuntimeError(error_message)
        
        self.account_info = json.loads(response.text)
        
        return self.account_info

    # ====================== API Market details ==============================================================
    # API for fetching market details
    def get_market_details(self):

        url = os.getenv("DEMO_API_URL") + "/markets/" + self.market_id

        payload = {}

        self.request_headers['Version'] = '2'

        response = requests.request("GET", url, headers=self.request_headers, data=payload)
        if response.status_code != 200: 
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in Markte Details API. Error response = {response.text}"
            }
            raise RuntimeError(error_message)

        market_details_response = json.loads(response.text)
        market_details_instr = market_details_response['instrument']
        market_details_dealingrules = market_details_response['dealingRules']
        market_details_snapshot = market_details_response['snapshot']

        self.market_details =  {
            "currency": market_details_instr['currencies'][0]['code'],
            "marginFactor": market_details_instr['marginFactor'], 
            "marginFactorUnit": market_details_instr['marginFactorUnit'],
            "minNormalStopOrLimitDistance": market_details_dealingrules['minNormalStopOrLimitDistance']['value'],
            "marketStatus": market_details_snapshot['marketStatus'],
            "bid": market_details_snapshot['bid'],
            "offer": market_details_snapshot['offer']
        }

        return True

    # ====================== API Open Positions ==============================================================
    # API for fetching open positions for the symbol in context
    def get_open_positions(self):

        url = os.getenv("DEMO_API_URL") + "/positions"

        payload = {}

        self.request_headers['Version'] = '2'

        response = requests.request("GET", url, headers=self.request_headers, data=payload)
        if response.status_code != 200: 
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in Get Open Positions API. Error response = {response.text}"
            }
            raise RuntimeError(error_message)

        positions_list = json.loads(response.text)['positions']

        positions_for_symbol = [position for position in positions_list if position['market']['epic'] == self.market_id]


        positions_2 = []

        for position in positions_for_symbol: 

            positions_2.append({
                "dealId": position['position']['dealId'],
                "size": position['position']['size'], 
                "direction": position['position']['direction'] ,
                "limitLevel": position['position']['limitLevel'],
                "stopLevel": position['position']['stopLevel'] ,
            })

        if len(positions_2) == 0: 

            df = pd.DataFrame(columns= ['dealId', 'size', 'direction', 'limitLevel', 'stopLevel'])
        
        else: 

            df = pd.DataFrame(positions_2)

        self.df_open_positions = df

        return df
    
    # ====================== API Create position ==============================================================
    def create_position(self):

        url = os.getenv("DEMO_API_URL") + "/positions/otc"

        sl = self.trade_params['sl']
        tp = self.trade_params['tp']

        direction = "BUY" if self.signal == 1 else "SELL"

        current_price = self.market_details['offer'] if direction == "BUY" else self.market_details['bid']

        print(f"Placing a {direction} trade with the following parameters:"
            f"Current price: {current_price}, "
            f"size = {self.calculate_position_size()}, " 
            f"sl = {sl}, "
            f"tp = {tp}")
        
        self.add_message(
            message_func="create_position", 
            message= f"Placing a {direction} trade with the following parameters: Current price: {current_price}, size = {self.calculate_position_size()}, sl = {sl}, tp = {tp}"
            )

        payload = {
            "epic": self.market_id,
            "expiry": "-",
            "direction": direction,
            "size": self.calculate_position_size(),
            "orderType": "MARKET",
            "timeInForce": "FILL_OR_KILL",
            "guaranteedStop": "false",
            "forceOpen": "true",
            "stopLevel": sl,
            "limitLevel": tp,
            "currencyCode": self.market_details['currency']
        }

        self.request_headers['Version'] = '2'

        create_trade_response = requests.request("POST", url, headers=self.request_headers, data=json.dumps(payload))
        if create_trade_response.status_code != 200: 
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in Create Position API. Error response = {create_trade_response.text}"
            }
            raise RuntimeError(error_message)

        deal_ref = json.loads(create_trade_response.text)['dealReference']

        # Need to call the trade confirm API here and get the valiue of the fields `dealStatus` and `reason` 
        url = os.getenv("DEMO_API_URL") + "/confirms/" + deal_ref

        self.request_headers['Version'] = '1'

        confirm_trade_response = requests.request("GET", url, headers=self.request_headers, data=payload)
        if confirm_trade_response.status_code != 200: 
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in Confirm Position API. Error response = {confirm_trade_response.text}"
            }
            raise RuntimeError(error_message)

        confirm_trade = json.loads(confirm_trade_response.text)

        if confirm_trade['dealStatus'] == "REJECTED":
            error_message = {
                "error_function": "create_position",
                "error_message": f"Error in Confirm Position API. Error response = {confirm_trade['reason']}"
            }
            raise RuntimeError(error_message)
        
        self.add_message(
            message_func= "create_position",
            message=f"New position created. Deal id = {confirm_trade['dealId']}",
            message_type="S"
        )
        
        return {"Epic": confirm_trade['epic'], "DealId": confirm_trade["dealId"], 
                "Status": "OPENED", "OpeningPrice": confirm_trade['level'], 
                "Size": confirm_trade['size'], "Direction": confirm_trade['direction'], 
                "SL": confirm_trade['stopLevel'], "TP": confirm_trade['limitLevel']}
    

    # ====================== API Close One Position ==============================================================
    def close_position(self, dealId):

        df_position = self.df_open_positions.loc[self.df_open_positions['dealId'] == 'DIAAAAPHXACPEAW'].copy()
        if df_position.shape[0] == 0: 
            error_message = {
                "error_function": "close_1_position",
                "error_message": f"Invalid Dealid - Dealid {dealId} deosnt exist."
            }
            raise RuntimeError(error_message)
        
        size = df_position['size'][0]
        direction = df_position['direction'][0]

        payload = {
        "dealId": dealId,
        "expiry": "-",
        "direction": "SELL" if direction == 'BUY' else 'BUY',
        "size": int(size),
        "orderType": "MARKET",
        "timeInForce": "FILL_OR_KILL"
        }
        
        url = os.getenv("DEMO_API_URL") + "/positions/otc"
        
        self.request_headers['Version'] = '1'
        self.request_headers["_method"] = 'DELETE'

        close_position_response = requests.request("POST", url, headers=self.request_headers, data=json.dumps(payload))
        self.request_headers.pop("_method", None)
        
        if close_position_response.status_code != 200: 
            error_message = {
                "error_function": "close_position",
                "error_message": f"Error in the Close One Position API. Error message: {close_position_response.text}"
            }
            raise RuntimeError(error_message)
        
        deal_ref = json.loads(close_position_response.text)['dealReference']

        # Need to call the trade confirm API here and get the valiue of the fields `dealStatus` and `reason` 
        url = os.getenv("DEMO_API_URL") + "/confirms/" + deal_ref

        self.request_headers['Version'] = '1'

        confirm_trade_response = requests.request("GET", url, headers=self.request_headers, data=payload)
        
        if confirm_trade_response.status_code != 200: 
            error_message = {
                "error_function": "close_one_position",
                "error_message": f"Error in Confirm Close One Position API. Error message = {confirm_trade_response}"
            }
            raise RuntimeError(error_message)

        confirm_trade = json.loads(confirm_trade_response.text)

        if confirm_trade['dealStatus'] == "REJECTED":
            error_message = {
                "error_function": "close_one_position",
                "error_message": f"Error in Confirm Close One Position API. Error reason = {confirm_trade['reason']}"
            }
            raise RuntimeError(error_message)
        
        self.add_message(
            message_func= "close_one_position", 
            message=f"DealId {dealId} was invalidated. So it was closed",
            message_type="S"
        )
        
        # Update the open positions dataframe
        self.get_open_positions()


        return True 


    # ====================== API Close All Positions ==============================================================
    def close_all_positions(self): 

        # First get the open positions for this market id 
        if self.df_open_positions.shape[0] == 0:
            return True

        url = os.getenv("DEMO_API_URL") + "/positions/otc"

        size = self.df_open_positions['size'].sum()
        position_dirn = self.df_open_positions['direction'].to_list()[0]

        print(f"{self.df_open_positions.shape[0]} open positions found. Total size: {int(size)}; Direction: {position_dirn}")

        payload = {
        "epic": self.market_id,
        "expiry": "-",
        "direction": "SELL" if position_dirn == 'BUY' else 'BUY',
        "size": int(size),
        "orderType": "MARKET",
        "timeInForce": "FILL_OR_KILL"
        }
        
        self.request_headers['Version'] = '1'
        self.request_headers["_method"] = 'DELETE'

        print(f"\n{json.dumps(payload)}\n")

        close_positions_response = requests.request("POST", url, headers=self.request_headers, data=json.dumps(payload))
        self.request_headers.pop("_method", None)
        
        if close_positions_response.status_code != 200: 
            error_message = {
                "error_function": "close_positions",
                "error_message": f"Error in the Close Positions API. Error message: {close_positions_response.text}"
            }
            raise RuntimeError(error_message)

        
        deal_ref = json.loads(close_positions_response.text)['dealReference']

        # Need to call the trade confirm API here and get the valiue of the fields `dealStatus` and `reason` 
        url = os.getenv("DEMO_API_URL") + "/confirms/" + deal_ref

        self.request_headers['Version'] = '1'

        confirm_trade_response = requests.request("GET", url, headers=self.request_headers, data=payload)
        
        if confirm_trade_response.status_code != 200: 
            error_message = {
                "error_function": "close_positions",
                "error_message": f"Error in Confirm Close Position API. Error message = {confirm_trade_response}"
            }
            raise RuntimeError(error_message)

        confirm_trade = json.loads(confirm_trade_response.text)

        if confirm_trade['dealStatus'] == "REJECTED":
            error_message = {
                "error_function": "close_positions",
                "error_message": f"Error in Confirm Close Position API. Error reason = {confirm_trade['reason']}"
            }
            raise RuntimeError(error_message)
        
        self.add_message(
            message_func= "close_all_positions", 
            message=f"All existing open positions closed",
            message_type="S"
        )
        
        # Update the open positions dataframe  - This will be a redundant call, since al positions have been closed
        # It will update the global varialble with an empty DF 
        self.get_open_positions()

        return True
    
    # ====================== Util Func to calculate the position size ==============================================================
    ### Util func for position sizing

    # 1. Step1: the actual SL distance. It has to be the higher of 
    #     * current - StopLevel determined by algo AND 
    #     * minNormalStopOrLimitDistance from the market details API
    # 2. Step2: Calculate the max drawdown value. It will be (the 'balance' field from account details API) * 0.02
    # 3. Step3: Calculation of position size
    #     * Step3.1: position size = max drawdown value (*Step2*) / SL distance (*Step1*)
    #     * Step3.2: margin used = position size (*Step3.1*) * ask price (*or bidprice for short positions*) * marginFactor (*Market details API*) / 100
    #     * Step3.3: If margin used (*Step3.2*) is higher than available funds * 0.80 (*'available' field from account details API*)
    #         * position size = (available funds * 0.80) * 100 / (Ask price * 5)
    def calculate_position_size(self):

        # current_price, sl, tp, min_stop_distance, margin_requirements, curr_balance, available_funds 
        # Derived parameters for formula
        current_price = self.market_details['offer'] if self.signal == 1 else self.market_details['bid']

        if current_price is None:
            error_message = {
                "error_function": "calculate_size",
                "error_message": "Error in Calculating size of the position. Current price == Null"
            }
            raise RuntimeError(error_message)


        sl = self.trade_params['sl']
        tp = self.trade_params['tp']
        max_drawdown_multiplier = self.trade_params['max_drawdown_multiplier']

        min_stop_distance = self.market_details['minNormalStopOrLimitDistance']
        margin_requirements = self.market_details['marginFactor']

        current_balance = self.account_balance['balance']
        available_funds = self.account_balance['available']

        print(f"Function: Calculate Position; Parameters for calculations - part1: sl={sl}, tp={tp}, current_price={current_price}")
        print(f"Function: Calculate Position; Parameters for calculations - part2: current_balance={current_balance}, available_funds={available_funds}")

        # Step1: the actual SL distance
        sl_distance = max(abs(current_price - sl), min_stop_distance)
        print(f"Function: Calculate Position; Step1: Stop level distance: {sl_distance}" )

        # Step2: Calculate the max drawdown value
        max_drawdown = current_balance * max_drawdown_multiplier           # 0.02 - It was 2 % earlier. Parameterised it on 3rd May

        # Step3: Calculation of position size
        # 3.1 position size = max drawdown value (*Step2*) / SL distance (*Step1*)
        position_size = max_drawdown / sl_distance
        print(f"Function: Calculate Position; Position size after step 3.1: {position_size:.1f}")


        # 3.2 margin used = position size (*Step3.1*) * ask price (*or bidprice for short positions*) * marginFactor (*Market details API*) / 100
        margin_used = position_size * current_price * margin_requirements / 100
        print("Function: Calculate Position; Margin used in this position:", margin_used)

        # 3.3
        available_margin = available_funds * 0.8
        if margin_used > available_margin: 
            position_size = available_margin * 100 / (current_price * margin_requirements)
            print(f"Function: Calculate Position; Margin was not enough for the position-size. Opening the position with a revised size = {position_size:.1f}")

        return int(position_size) if position_size > 1 else 1
    
    # ====================== API Edit position (Set Trailing stop) ==============================================================
    def edit_position(self, deal_id):

        url = os.getenv("DEMO_API_URL") + "/positions/otc/" + deal_id


        sl = self.edit_position_sl
        tp = self.edit_position_tp
        trail_stop_dist = self.edit_position_trail_distance

        print(f"Editing the position {deal_id} with the following parameters:"
            # f"Current price: {current_price}, "
            # f"size = {self.calculate_position_size()}," 
            f"sl = {sl},"
            f"tp = {tp}"
            f"trailing_sl = {self.edit_position_trail_distance}"
            )

        payload = {
            "stopLevel": sl,
            "limitLevel": tp,
            "trailingStop": True,
            "trailingStopDistance": trail_stop_dist,
            "trailingStopIncrement": 1
        }

        self.request_headers['Version'] = '2'

        edit_position_response = requests.request("PUT", url, headers=self.request_headers, data=json.dumps(payload))
        if edit_position_response.status_code != 200: 
            error_message = {
                "error_function": "edit_position",
                "error_message": f"Error in Edit Position API. Error response = {edit_position_response.text}"
            }
            raise RuntimeError(error_message)

        deal_ref = json.loads(edit_position_response.text)['dealReference']

        # Need to call the trade confirm API here and get the valiue of the fields `dealStatus` and `reason` 
        url = os.getenv("DEMO_API_URL") + "/confirms/" + deal_ref

        self.request_headers['Version'] = '1'

        confirm_trade_response = requests.request("GET", url, headers=self.request_headers)
        if confirm_trade_response.status_code != 200: 
            error_message = {
                "error_function": "edit_position",
                "error_message": f"Error in Confirm Position API. Error response = {confirm_trade_response.text}"
            }
            raise RuntimeError(error_message)

        confirm_trade = json.loads(confirm_trade_response.text)

        if confirm_trade['dealStatus'] == "REJECTED":
            error_message = {
                "error_function": "edit_position",
                "error_message": f"Error in Confirm Position API. Error response = {confirm_trade['reason']}"
            }
            raise RuntimeError(error_message)

        return True 

    # ====================== Util Func to evaluate Trailing Stop level ==============================================================
    ### Util func to evaluate Trailing Stop level and take appropriate action

    def evaluate_trailing_stop(self, deal_id, df_positions_db):

        # Details from the DB 
        direction = df_positions_db['Direction'][0]
        price_point_1, price_point_2, price_point_3 = df_positions_db['price_points'][0]
        wave_length = abs(price_point_2 - price_point_1)

        if "trailing_stop_rating" in df_positions_db.columns.to_list():
            trailing_stop_rating = df_positions_db['trailing_stop_rating'][0]
        else: 
            # It may be an earlier record. Position created before the trailing_stop change was implemented
            trailing_stop_rating = 0        

        # For old records trailing_stop_rating will be nan. Need to consider it as 0 
        trailing_stop_rating = 0 if math.isnan(trailing_stop_rating)  else trailing_stop_rating

        # If we are at the highest rating, nothing to do further, exit
        if trailing_stop_rating == 2:
            print("Already at trailing_stop_rating level of 2, so nothing to do further")
            return trailing_stop_rating

        current_price =  (self.market_details['offer'] + self.market_details['bid']) / 2

        # Nothing to do if the price hasnt crossed the earlier peak/trough
        if direction == "BUY" and current_price < price_point_2: 
            print(f"Current price = {current_price}, Price point 2 = {price_point_2}, Trailing stop cant be updated")
            return trailing_stop_rating         
        
        if direction == "SELL" and current_price > price_point_2:
            print(f"Current price = {current_price}, Price point 2 = {price_point_2}, Trailing stop cant be updated")
            return trailing_stop_rating

        # Read details from IG 
        df_position_ig = self.df_open_positions.query(
                f"(dealId == '{deal_id}')"
            ).copy()
        
        if df_position_ig.shape[0] != 1: 
            error_message = {
                "error_function": "evaluate_trailing_stop",
                "error_message": f"Error in getting the position details for the active dealid {deal_id}!"
            }
            raise RuntimeError(error_message)

        df_position_ig = df_position_ig.reset_index().copy()

        tp_level = df_position_ig['limitLevel'][0]
        sl_level = df_position_ig['stopLevel'][0]

        # print("We have reached the end of the WIP method: evaluate_trailing_stop")

        # So now what we have is: 
        # 1. Wave is in extension. i.e. the price has crossed the earlier peak/trough.
        extension = (abs(current_price - price_point_1) - wave_length) / wave_length

        if extension > 0.2:          # if the existing trail stop is either 0 or 1 

            # Edit the trailing stop 
            if direction == 'BUY': 
                
                # Allow for a 38% retracement
                self.edit_position_sl = round(current_price - (0.4 * wave_length), 2)
                self.edit_position_tp = tp_level
                self.edit_position_trail_distance = math.ceil(0.4 * wave_length) + 1    # Adding the 1 just to be safe
            
            if direction == 'SELL': 

                # Allow for a 38% retracement
                self.edit_position_sl = round(current_price + (0.4 * wave_length), 2)
                self.edit_position_tp = tp_level
                self.edit_position_trail_distance = math.ceil(0.4 * wave_length) + 1    # Adding the 1 just to be safe

            print(f"Extension has reached beyond 1.2 level. Editing the trailing stop level now. Deal id = {deal_id}, New Trail stop dist = {self.edit_position_trail_distance}")

            # Call the edit position API
            self.edit_position(deal_id)

            self.add_message(
                message_func="evaluate_trailing_stop",
                message=f"The open position {deal_id} has been edited. New trailing stop rating applied of 2",
                message_type="S"
            )

            # Return value as 2, so that we will update the DB in the lambda handler
            return 2

        # This doesnt look right to me - but because of earlier conditions, the below condition works! - 
        if extension <= 0.2  and trailing_stop_rating == 0 :           # Only check for the level between 0 and 1.2 extension if existing trail stop level is 0
                
            self.edit_position_sl = round(price_point_1,2)                  # Raise the SL to the price_point1
            self.edit_position_tp = tp_level
            self.edit_position_trail_distance = math.ceil(abs(current_price - self.edit_position_sl)) + 1    # Adding the 1 just to be safe

            print(f"We have reached extension of less than 1.2. Editing the trailing stop level now. Deal id = {deal_id}, New Trail stop dist = {self.edit_position_trail_distance}")

            # Call the edit position API
            self.edit_position(deal_id)

            self.add_message(
                message_func="evaluate_trailing_stop",
                message=f"The open position {deal_id} has been edited. New trailing stop rating applied of 1",
                message_type="S"
            )

            # Return value as 1, so that we will update the DB in the lambda handler
            return 1
        
        return True
    
