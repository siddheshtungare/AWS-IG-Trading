import json
import requests
import pandas as pd 
import datetime as dt
import pytz
import boto3 
import botocore
from botocore.exceptions import ClientError
from io import StringIO
import traceback

from scipy.signal import find_peaks
import numpy as np 
from io import StringIO


from util_funcs import *

from ig_api_helper import *

import os
import time

from strategy_loader import load_strategy

# # Sample event structure
# {
#     "request_headers": {},
#     "account_balance": {},
#     "config": {
#         "name": "ASX",
#         "MarketId": "IX.D.ASX.IFT.IP"
#     }
# }
def lambda_handler(event, context):
    """
    Main Lambda handler for running trading strategies
    Args:
        event: Lambda event containing configuration
        context: Lambda context
    Returns:
        dict: Result containing signal, parameters, and status messages
    """
    try:
        # Validate input event
        if not event or 'config' not in event:
            raise ValueError("Invalid event structure: 'config' is required")
        
        config = event['config']
        required_fields = ['name', 'MarketId']
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Missing required fields in config: {', '.join(missing_fields)}")

        # Initialize variables
        gv_bapiret_tab = []
        gv_errors_exist = False
        gv_market_closed = False
        signal = 0
        params = {}
        
        # Get configuration
        symbol_name = config['name']
        symbol_market_id = config['MarketId']
        strategy_name = config.get('strategy', 'fibo')
        bucket = 'aws-sam-cli-managed-default-samclisourcebucket-3pncdm36uy1a'

        print(f"\n{'='*50}")
        print(f"Starting strategy execution for {symbol_name}")
        print(f"Strategy: {strategy_name}")
        print(f"{'='*50}\n")

        try:
            # Load strategy
            strategy_func, strategy_params = load_strategy(strategy_name)
            # Merge strategy params with any overrides from event
            strategy_params.update(config.get('strategy_params', {}))
        except Exception as e:
            print(f"Strategy loading error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Failed to load strategy: {str(e)}")

        # Get historical and current data
        df_prices_hist = get_historical_data(symbol_name, bucket)
        
        login()
        df_prices_new = get_price_data(symbol_market_id, num_points=2)
        
        # Check market status
        df_prices_new, market_closed, error_message = check_market_status(df_prices_new)
        if market_closed:
            gv_market_closed = True
            gv_bapiret_tab.append({
                "message_type": 'I',
                "message_source": "IgRunStrategyFunction",
                "message_at": dt.datetime.now(tz=pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                "message": error_message,
            })
        
        # Merge and update data
        df_prices = merge_price_data(df_prices_hist, df_prices_new)
        update_s3_data(df_prices, bucket, symbol_name)

        if not gv_market_closed:
            # Prepare data for strategy
            df_strategy = prepare_strategy_data(df_prices, num_records=500)
            
            # Apply strategy
            strategy_input = {**event, **strategy_params}
            signal, params = strategy_func(df_strategy, strategy_input)

            # Log strategy outcome
            if signal == 1:
                message = "Buy Signal generated"
                message_type = 'S'
            elif signal == -1:
                message = "Sell Signal generated"
                message_type = 'S'
            else:
                message = "No signal generated"
                message_type = 'I'

            print(f"\nStrategy Result: {message}")
            if signal != 0:
                print(f"Entry Parameters: {json.dumps(params, indent=2)}")

            gv_bapiret_tab.append({
                "message_type": message_type,
                "message_source": "IgRunStrategyFunction",
                "message_at": dt.datetime.now(tz=pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                "message": f"{strategy_name} Strategy outcome: {message}",
            })

        return {
            'symbol': symbol_name,
            'strategy': strategy_name,
            'config': config,
            'signal': signal,
            'trade_params': params,
            'market_closed': gv_market_closed,
            'errors_exist': gv_errors_exist,
            'messages': gv_bapiret_tab
        }

    except Exception as e:
        print(f"Critical error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'messages': [{
                "message_type": 'E',
                "message_source": "IgRunStrategyFunction",
                "message_at": dt.datetime.now(tz=pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
                "message": f"Critical error: {str(e)}"
            }]
        }


