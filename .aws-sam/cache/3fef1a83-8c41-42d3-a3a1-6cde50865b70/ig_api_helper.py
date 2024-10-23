import json
import os 
import requests
import datetime as dt
import pandas as pd 
import numpy as np 
from util_funcs import *

request_headers = {'Content-Type': 'application/json','X-IG-API-KEY': os.environ.get("DEMO_API_KEY"), 'Version': '2'}
account_balance = {}

# ======================GET REQUEST HEADERS===================================================
# To be used during the request calls
def get_request_header():
    
    return request_headers
  
# ======================GET ACCOUNT BALANCE===================================================
# Get the account balance
def get_account_balance(refresh=False):
    
    global account_balance
  
    if refresh: 
        # Call the account balance API once again and set it to the global parameter
        account_info = get_account_info()
        account_balance = account_info['accounts'][0]['balance']
        return account_balance
    
    else: 
    
        return account_balance

# ====================== API LOGIN ==============================================================
# To be for logging in
def login():
    url = os.environ.get("DEMO_API_URL") + "/session"

    payload = json.dumps({
    "identifier": os.environ.get("DEMO_USERNAME"),
    "password": os.environ.get("DEMO_PASSWORD"),
    "encryptedPassword": None
    })
    
    # headers = headers
    global request_headers
    global account_balance

    request_headers['Version'] = '2'
    
    response = requests.request("POST", url, headers=request_headers, data=payload)
    
    request_header = dict(response.headers)

    response_body = json.loads(response.text)

    print(f"IG-Login API called. Response status code was {response.status_code}")

    try: 
        account_balance = response_body['accountInfo']
    except KeyError: 
        print(f"\nKeyError exception raised in the login API")
        print(f"\nThe response-header from the login API is {response.headers}")
        print(f"\nThe response-text from the login API is {response.text}")
    # print(f"\n{response.text}\n")
    
    request_headers.update({"CST": request_header['CST'], "X-SECURITY-TOKEN": request_header['X-SECURITY-TOKEN']})
    
    return request_header, json.loads(response.text)
    
# ====================== API ACCOUNT INFO ==============================================================
# API for calling account info 
def get_account_info():
    
    url = os.environ.get("DEMO_API_URL") + "/accounts"

    payload = ""
    
    request_headers["Version"] = '1'
    
    response = requests.request("GET", url, headers=request_headers, data=payload)
    
    account_info = json.loads(response.text)
    
    return account_info

# ====================== API PRICE DATA ==============================================================
# API for calling Price data
def get_price_data(symbol_market_id, num_points=2): 

    url = os.environ.get("DEMO_API_URL") + "/prices/" + symbol_market_id + "?resolution=HOUR&max=" + str(num_points) + "&pageSize=10000&pageNumber=1"

    payload = ""
    
    request_headers["Version"] = '3'
    
    response = requests.request("GET", url, headers=request_headers, data=payload)
    
    response_dict = json.loads(response.text)
    prices = response_dict['prices']

    df_prices = create_df_from_prices_dict(prices)

    return df_prices 

# # ====================== API PRICE DATA ==============================================================
# # API for calling Price data
# def get_price_data_for_date_range(symbol_market_id, start_date, end_date): 

#     url = os.getenv("DEMO_API_URL") + "/prices/" + symbol_market_id + "?resolution=HOUR&from=" + \
#         start_date.strftime("%Y-%m-%dT%H:%M:%S") + "&to=" + end_date.strftime("%Y-%m-%dT%H:%M:%S") + \
#         "&pageSize=100&pageNumber=1"

#     payload = {}

#     request_headers["Version"] = '3'

#     response = requests.request("GET", url, headers=request_headers, data=payload)

#     response_dict = json.loads(response.text)
#     prices = response_dict['prices']

#     df_prices = create_df_from_prices_dict(prices)

#     return df_prices 

