import json
import os 

import datetime as dt
import pandas as pd 
import numpy as np 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def create_df_from_prices_dict(prices):

    df_prices = pd.DataFrame(columns=[ 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    for price_data in prices:
        
        Date = dt.datetime.strptime(price_data['snapshotTime'], '%Y/%m/%d %H:%M:%S')
        # print(Date)
        try: 
            open_price = np.mean([price_data['openPrice']['bid'], price_data['openPrice']['ask']])
            high_price = np.mean([price_data['highPrice']['bid'], price_data['highPrice']['ask']])
            low_price = np.mean([price_data['lowPrice']['bid'], price_data['lowPrice']['ask']])
            close_price = np.mean([price_data['closePrice']['bid'], price_data['closePrice']['ask']])

            volume = price_data['lastTradedVolume']

            df_prices.loc[len(df_prices)] = [Date, open_price, high_price, low_price, close_price, volume]
        except TypeError:
            # print(f"TypeError occured on {df_prices.iloc[-1, 0]}")
            pass

    df_prices = df_prices.set_index("Date")

    return df_prices 
