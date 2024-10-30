import json
import os 
import requests
import datetime as dt
import pandas as pd 
import numpy as np 
from util_funcs import *
import traceback

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
    """
    Handles IG API login and authentication
    Returns:
        tuple: (request_header, response_body, logs)
    """
    logs = []
    try:
        url = os.environ.get("DEMO_API_URL") + "/session"
        
        # Validate environment variables
        required_env_vars = ["DEMO_API_URL", "DEMO_USERNAME", "DEMO_PASSWORD"]
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        payload = json.dumps({
            "identifier": os.environ.get("DEMO_USERNAME"),
            "password": os.environ.get("DEMO_PASSWORD"),
            "encryptedPassword": None
        })
        
        global request_headers
        global account_balance
        request_headers['Version'] = '2'
        
        logs.append("\nAttempting IG API login...")
        response = requests.request("POST", url, headers=request_headers, data=payload)
        
        # Check response status
        if response.status_code == 200:
            logs.append(f"Login successful (Status: {response.status_code})")
            request_header = dict(response.headers)
            response_body = json.loads(response.text)
            
            # Update headers with authentication tokens
            if 'CST' in request_header and 'X-SECURITY-TOKEN' in request_header:
                request_headers.update({
                    "CST": request_header['CST'], 
                    "X-SECURITY-TOKEN": request_header['X-SECURITY-TOKEN']
                })
                logs.append("Authentication tokens updated")
            else:
                raise ValueError("Authentication tokens missing from response")
            
            # Update account balance
            try:
                account_balance = response_body['accountInfo']
                logs.append("Account balance updated")
            except KeyError:
                logs.append("Warning: Could not update account balance - 'accountInfo' not found in response")
                logs.append(f"Response body: {json.dumps(response_body, indent=2)}")
            
            return request_header, response_body, logs
            
        elif response.status_code == 401:
            logs.append(f"Login failed: Authentication error (Status: {response.status_code})")
            logs.append(f"Response: {response.text}")
            raise ValueError("Invalid credentials")
            
        elif response.status_code == 403:
            logs.append(f"Login failed: Access forbidden (Status: {response.status_code})")
            logs.append(f"Response: {response.text}")
            raise ValueError("Access forbidden - check API permissions")
            
        elif response.status_code == 429:
            logs.append(f"Login failed: Too many requests (Status: {response.status_code})")
            logs.append(f"Response: {response.text}")
            raise ValueError("Rate limit exceeded - try again later")
            
        else:
            logs.append(f"Login failed: Unexpected status code {response.status_code}")
            logs.append(f"Response: {response.text}")
            raise ValueError(f"Login failed with status code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logs.append(f"Network error during login: {str(e)}")
        logs.append(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Network error during login: {str(e)}")
        
    except json.JSONDecodeError as e:
        logs.append(f"Invalid JSON response: {str(e)}")
        logs.append(f"Response text: {response.text}")
        logs.append(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Invalid JSON response from API: {str(e)}")
        
    except Exception as e:
        logs.append(f"Unexpected error during login: {str(e)}")
        logs.append(f"Traceback: {traceback.format_exc()}")
        raise

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

