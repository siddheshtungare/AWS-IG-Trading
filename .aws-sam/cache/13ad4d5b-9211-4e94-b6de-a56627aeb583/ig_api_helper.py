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
        
        logs.append("Attempting IG API login...")
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
def get_price_data(epic_id, num_points=50):
    logs = []
    logs.append("API: Fetching price data from IG API...")
    
    try:
        # Construct the prices URL
        prices_url = f"{os.environ['DEMO_API_URL']}/prices/{epic_id}"
        
        # Add query parameters
        params = {
            'resolution': 'HOUR',
            'max': num_points,
            'pageSize': num_points
        }
        
        # Update the API version in the headers
        request_headers['Version'] = '3'
        
        # Make the request
        response = requests.get(
            prices_url,
            params=params,
            headers=request_headers
        )
        
        # Log the response status
        logs.append(f"API: Price data API response status: {response.status_code}")
        
        if response.status_code == 404:
            error_msg = "Epic not found - the requested market ID does not exist or is not accessible"
            logs.append(f"API: {error_msg}")
            logs.append(f"API: Market ID attempted: {epic_id}")
            # Return empty DataFrame for 404 errors
            empty_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'DateTime'])
            return empty_df, logs
            
        elif response.status_code != 200:
            try:
                error_response = response.json()
                error_msg = error_response.get('errorCode', 'Unknown error')
            except:
                error_msg = response.text if response.text else 'No error details available'
                
            logs.append(f"API: Error response: {error_msg}")
            raise Exception(f"Failed to fetch prices. Status code: {response.status_code}, Error: {error_msg}")
            
        response_dict = response.json()
        
        # Check if 'prices' exists in response
        if 'prices' not in response_dict:
            error_msg = f"Unexpected API response format. Available keys: {list(response_dict.keys())}"
            if 'errorCode' in response_dict:
                error_msg += f"\nError code: {response_dict['errorCode']}"
            logs.append(f"API: {error_msg}")
            raise KeyError(error_msg)
            
        prices = response_dict['prices']
        
        # Convert to DataFrame
        df = pd.DataFrame(prices)
        
        logs.append(f"Successfully fetched {len(df)} price records")
        return df, logs
        
    except Exception as e:
        logs.append(f"API: Error in get_price_data: {str(e)}")
        # Return empty DataFrame with expected columns
        empty_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'DateTime'])
        return empty_df, logs
