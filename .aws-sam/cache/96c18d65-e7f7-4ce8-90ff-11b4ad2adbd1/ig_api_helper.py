import json
import os 
import requests
import datetime as dt

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
    if response.status_code != 200: 
        error_message = {
            "error_function": "login function",
            "error_message": f"Error in login API. Error response = {response.text}"
        }
        raise RuntimeError(error_message)
    
    request_header = dict(response.headers)
    # print(response.text)
    response_body = json.loads(response.text)
    account_balance = response_body['accountInfo']

    print(account_balance)
    
    request_headers.update({"CST": request_header['CST'], "X-SECURITY-TOKEN": request_header['X-SECURITY-TOKEN']})
    
    return request_header, json.loads(response.text)
    
# ====================== API ACCOUNT INFO ==============================================================
# API for calling account info 
def get_account_info():
    
    url = os.environ.get("DEMO_API_URL") + "/accounts"

    payload = ""
    
    request_headers["Version"] = '1'
    
    response = requests.request("GET", url, headers=request_headers, data=payload)
    if response.status_code != 200: 
        error_message = {
            "error_function": "create_position",
            "error_message": f"Error in Get Account Info API. Error response = {response.text}"
        }
        raise RuntimeError(error_message)
    
    account_info = json.loads(response.text)
    
    return account_info