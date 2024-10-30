import json
import os 
import datetime as dt
import pandas as pd 
import numpy as np 
import boto3
from botocore.exceptions import ClientError
import pytz
import traceback
from io import StringIO

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_historical_data(symbol_name, bucket):
    """
    Retrieves historical price data from S3
    """
    logs = []
    try:
        s3_client = boto3.client('s3')
        key = f'IG-Trading-1/Resources/PriceData/Hourly/{symbol_name}.csv'
        
        response = s3_client.get_object(Bucket=bucket, Key=key)
        df_prices_hist = pd.read_csv(response.get("Body"), parse_dates=True, index_col=0)
        
        logs.append("\nHistorical data fetched successfully")
        logs.append(f"Records found: {len(df_prices_hist)}")
        return df_prices_hist, logs
        
    except ClientError as e:
        logs.append(f"S3 error: {str(e)}")
        logs.append(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to fetch historical data: {str(e)}")

def check_market_status(df_prices_new):
    """
    Checks if market is open and handles incomplete candles
    """
    logs = []
    now_datetime = dt.datetime.now(pytz.timezone('Australia/Sydney'))
    local_datetime = now_datetime.replace(tzinfo=None)
    difference = local_datetime - df_prices_new.index[-1]
    logs.append(f"\nTime difference from last candle: {difference}")

    market_closed = False
    error_message = None
    
    if difference < pd.Timedelta(hours=1):
        # Last candle still forming
        df_prices_new = df_prices_new.iloc[:-1, :].copy()
        logs.append(f"\nCondition 1: Last candle still forming (difference = {difference})")
        logs.append("Removed incomplete candle. Using this data:")
        logs.append(str(df_prices_new))
    elif difference > pd.Timedelta(hours=2):
        # Market closed
        logs.append(f"\nCondition 2: Market appears closed (difference = {difference})")
        market_closed = True
        error_message = "Market closed. Nothing to do further"
    
    return df_prices_new, market_closed, error_message, logs

def merge_price_data(df_prices_hist, df_prices_new):
    """
    Merges historical and new price data
    """
    logs = []
    logs.append("\nMerging historical and new data...")
    
    # Concatenate the dataframes
    df_prices = pd.concat([df_prices_hist, df_prices_new], axis="rows")
    logs.append(f"Total rows after concat: {len(df_prices)}")
    
    # Reset index to handle duplicates
    df = df_prices.reset_index()
    df_deduplicated = df.drop_duplicates(subset='Date', keep='last')
    logs.append(f"Rows after deduplication: {len(df_deduplicated)}")
    
    # Set the date back as index and ensure chronological order
    df_prices = df_deduplicated.set_index('Date')
    df_prices = df_prices.sort_index()

    logs.append("\nFinal merged dataset:")
    logs.append(f"Total records: {df_prices.shape[0]}")
    logs.append("Last 3 records:")
    logs.append(str(df_prices.tail(3)))
    
    return df_prices, logs

def update_s3_data(df_prices, bucket, symbol_name):
    """
    Updates the historical data in S3
    """
    logs = []
    try:
        logs.append("\nUpdating historical data in S3...")
        csv_buffer = StringIO()
        df_prices.to_csv(csv_buffer)
        
        s3_resource = boto3.resource('s3')
        key = f'IG-Trading-1/Resources/PriceData/Hourly/{symbol_name}.csv'
        s3_resource.Object(bucket, key).put(Body=csv_buffer.getvalue())
        logs.append("S3 update complete")
        return logs
        
    except Exception as e:
        logs.append(f"S3 update error: {str(e)}")
        logs.append(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to update S3 data: {str(e)}")

def prepare_strategy_data(df_prices, num_records=500):
    """
    Prepares the last N records for strategy analysis
    """
    logs = []
    logs.append(f"\nPreparing data for strategy...")
    logs.append(f"Total available records: {len(df_prices)}")
    
    df_strategy = df_prices.iloc[-num_records:].copy()
    logs.append(f"Using last {num_records} records")
    logs.append(f"Date range: {df_strategy.index[0]} to {df_strategy.index[-1]}")
    
    return df_strategy, logs

def create_df_from_prices_dict(prices):
    """
    Converts raw price data from IG API into a pandas DataFrame
    """
    logs = []
    logs.append("\nCreating DataFrame from IG API price data...")
    df_prices = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    for price_data in prices:
        # Convert snapshot time to datetime
        Date = dt.datetime.strptime(price_data['snapshotTime'], '%Y/%m/%d %H:%M:%S')
        
        try: 
            # Calculate mid prices from bid/ask
            open_price = np.mean([price_data['openPrice']['bid'], price_data['openPrice']['ask']])
            high_price = np.mean([price_data['highPrice']['bid'], price_data['highPrice']['ask']])
            low_price = np.mean([price_data['lowPrice']['bid'], price_data['lowPrice']['ask']])
            close_price = np.mean([price_data['closePrice']['bid'], price_data['closePrice']['ask']])
            volume = price_data['lastTradedVolume']

            # Add row to DataFrame
            df_prices.loc[len(df_prices)] = [Date, open_price, high_price, low_price, close_price, volume]
        except TypeError:
            logs.append(f"Warning: TypeError occurred while processing data for {Date}")
            pass

    # Set Date as index
    df_prices = df_prices.set_index("Date")
    
    logs.append(f"Created DataFrame with {len(df_prices)} rows")
    logs.append("Sample of data:")
    logs.append(str(df_prices.tail(2)))
    
    return df_prices, logs
