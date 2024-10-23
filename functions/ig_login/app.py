import json
import requests
import pandas as pd 
import datetime as dt
import pytz
from random import randint
import boto3 


from ig_api_helper import *

import os
import time

# Sample event structure
# {
#   "sleep": 0,
#   "key2": "value2",
#   "key3": "value3"
# }
def lambda_handler(event, context):
    
    # Get event params
    sleep_time = event.get("sleep", 0)

    # Get the config file from S3 
    s3 = boto3.resource('s3')
    bucket =  'aws-sam-cli-managed-default-samclisourcebucket-3pncdm36uy1a'
    key = 'IG-Trading-1/Resources/config.json'

    obj = s3.Object(bucket, key)
    data = obj.get()['Body'].read().decode('utf-8')
    config_data = json.loads(data)
    
    time.sleep(sleep_time)

    # Table to record errors. This will be propagated throughout the workflow 
    gv_bapiret_tab = []
    gv_errors_exist = False

    config_list = [] 

    try: 

    # Step 2: Call the Login function
        login()

        # Forming the final output - which will be in the form of a json array 
        for item in config_data: 
            config = {
                'request_headers': get_request_header(),
                # 'request_headers': {},
                'account_balance': get_account_balance(),
                'account_balance': {},
                'config': item
            } 
            config_list.append(config)

    except RuntimeError as error: 

        error_string = str(error)
        error_string = error_string.replace("\'", "\"")
        print(error_string)

        gv_bapiret_tab.append({
            "error_type": 'E',
            "error_source": "IgLoginFunction",
            "error_at": dt.datetime.now(tz= pytz.timezone('Australia/Sydney')).strftime(format='%Y-%m-%dT%H:%M:%S.%f'),
            "error_message": json.loads(error_string),
        })

        gv_errors_exist = True

    return {
        'IGLoginStep': {
            'config_items': config_list,
            'errors_exist': gv_errors_exist,
            'messages': gv_bapiret_tab
        }

    }
