import pandas as pd
from scipy.signal import find_peaks
import numpy as np 
import datetime as dt 
    

def strategy(df_data, params): 

    prominence = params.get("prominence", 2)
    fibo_level_from = params.get("fibo_level_from",0.3)
    fibo_level_to = params.get("fibo_level_to", 0.5)
    tp_level = params.get("tp_level", 1.5)          # Setting the TP level to very high because we are using trailing stops
    max_drawdown_multiplier = params.get('max_drawdown_multiplier', 0.02)

    zone_thickness = 0.025


    # Only need the last 40 rows
    df_data = df_data.iloc[-40: , : ].copy()
    df_peaks_troughs = get_peaks_and_troughs(df_data, prominence)
    df = pd.concat([df_data, df_peaks_troughs ], axis='columns')

    # Current row
    row = df.iloc[-1, :]

    # Details of the last peak/trough 
    entry_peak_or_trough = df_peaks_troughs['Peak_or_trough'][-1]
    entry_wave_length = df_peaks_troughs['Difference'][-1]
    entry_price_point = df_peaks_troughs['Price_point'][-1]
    # date_last_p_or_t = df_peaks_troughs.index[-1].strftime('%Y-%m-%d %H:%M:%S')

    # Details of the second-last peak/trough 
    peak_or_trough = df_peaks_troughs['Peak_or_trough'][-2]
    wave_length = df_peaks_troughs['Difference'][-2]
    price_point = df_peaks_troughs['Price_point'][-2]
    # date_second_last_p_or_t = df_peaks_troughs.index[-2].strftime('%Y-%m-%d %H:%M:%S')


    # Details of the 3rd last peak/trough 
    prev_peak_or_trough = df_peaks_troughs['Peak_or_trough'][-3]
    prev_wave_length = df_peaks_troughs['Difference'][-3]
    prev_price_point = df_peaks_troughs['Price_point'][-3]
    # date_third_last_p_or_t = df_peaks_troughs.index[-3].strftime('%Y-%m-%d %H:%M:%S')

    # ____________________________________________________
    # Now for the final Buy/Sell signals
    # ____________________________________________________

    signal = 0
    tp_price = 0
    sl_price = 0

    # Evaluate Buy conditions 
    # 1. The retracement as a Trough needs to be confirmed 
    if entry_peak_or_trough == 'T' and peak_or_trough == 'P' and prev_peak_or_trough == 'T': 

    # 2. The last retracement needs to be within the 0.48 to 0.52 area of the prev retracement - Replaced by config - zone_thickness
        # retracement_value = abs(price_point - row['Low']) 
        retracement_percent = entry_wave_length / wave_length
        if retracement_percent > (fibo_level_from - zone_thickness ) and retracement_percent < (fibo_level_to + zone_thickness): # 

            tp_price = price_point + (tp_level * wave_length) 
            # sl_price = prev_price_point * 0.995
            sl_price = prev_price_point - (wave_length * 0.2)       # Allow for 1.2 Extension before confirming the stop 


    # 3. Close needs to be between the SL and the TP levels - OTHERWISE THE CREATE POSITION API WILL FAIL
            # if row['Close'] > sl_price and row['Close'] < tp_price: 
            # Variation - Close needs to be between the SL and the previous peak
            if row['Close'] > sl_price and row['Close'] < price_point: 

                df_data.at[df_data.index[-1], 'Signal'] = 1
                signal = 1

            else: 
                print(f"Long aborted on {df_data.index[-1]} because of condition #3")
        
    # Evaluate Sell conditions 
    # 1. The retracement as a Peak needs to be confirmed 
    if entry_peak_or_trough == 'P' and peak_or_trough == 'T' and prev_peak_or_trough == 'P': 

    # 2. The last retracement needs to be within the 0.48 to 0.52 area of the prev retracement - Replaced by config - zone_thickness
        # retracement_value = abs(price_point - row['Low']) 
        retracement_percent = entry_wave_length / wave_length
        if retracement_percent > (fibo_level_from - zone_thickness ) and retracement_percent < (fibo_level_to + zone_thickness): # 

            tp_price = price_point - (tp_level * wave_length) 
            # sl_price = prev_price_point * 1.005
            sl_price = prev_price_point + (wave_length * 0.2)       # Allow for 1.2 Extension before confirming the stop 


    # 3. Close needs to be between the SL and the TP levels - OTHERWISE THE CREATE POSITION API WILL FAIL
            # if row['Close'] < sl_price and row['Close'] > tp_price: 
            # Variation - Close needs to be between the SL and the previous peak
            if row['Close'] < sl_price and row['Close'] > price_point: 
            
                df_data.at[df_data.index[-1], 'Signal'] = -1
                signal = -1

            else: 
                print(f"Short aborted on {df_data.index[-1]} because of condition #6")


    return signal,  { "tp": round(float(tp_price), 2), "sl": round(float(sl_price),2), "max_drawdown_multiplier": max_drawdown_multiplier,
                      'price_points': [ round(float(entry_price_point),2), round(float(price_point),2 ), round(float(prev_price_point),2 ) ]
                    }
                    # For debugging
                    # [
                    #     {'datetime': date_last_p_or_t, 'price_point': entry_price_point}, 
                    #     {'datetime': date_second_last_p_or_t, 'price_point': price_point}, 
                    #     {'datetime': date_third_last_p_or_t, 'price_point': prev_price_point}
                    # ]}
                

def fix_consequtive_peaks_troughs(df, col_name):

    df_ori = df[["Date", col_name]].copy()
    df_fin = pd.DataFrame(columns=df_ori.columns, index=None)
    df_temp = pd.DataFrame(columns=df_ori.columns, index=None)

    # Add a dummy nan to the end 
    df_ori.loc[len(df_ori)] = [dt.datetime.now(), pd.NA]

    for row in df_ori.iterrows():
        date = row[1]["Date"]
        value = row[1][col_name]

        if pd.isna(value): 

            if df_temp.shape[0] > 0:
                # At every nan value, get the max/min of the records in df_temp and append it to df_fin. 
                # After that clear the df_temp 
                if col_name == 'Peak': 
                    idx = df_temp[col_name].idxmax()
                elif col_name == 'Trough':
                    idx = df_temp[col_name].idxmin()

                idx_date = df_temp.iloc[idx]['Date']
                idx_value = df_temp.iloc[idx][col_name]
                df_fin.loc[len(df_fin)] = [idx_date, idx_value]

                df_temp = pd.DataFrame(columns=df_ori.columns, index=None)
            
            # Also append the nan to the final dataframe 
            value = pd.NA
            df_fin.loc[len(df_fin)] = [date, value]

        else: 
            df_temp.loc[len(df_temp)] = [date, value]

    df_fin = df_fin.iloc[:-1]
    df_fin = df_fin.set_index("Date")

    return df_fin 

def get_peaks_and_troughs(df_data, prominence): 

    peak_indices, peaks_properties = find_peaks(df_data["High"], distance=5, prominence= prominence)      
    trough_indices, troughs_properties = find_peaks(-df_data["Low"], distance= 5, prominence= prominence)

    # Create a column for marking peaks and troughs on the plot
    df_data['Peak'] = df_data.iloc[peak_indices]["High"]
    df_data['Trough'] = df_data.iloc[trough_indices]["Low"]

    df = df_data[['Peak', "Trough"]].copy()
    df.dropna(how="all", inplace=True)
    df.reset_index(inplace=True)

    df_peak_fin = fix_consequtive_peaks_troughs(df.copy(), "Peak")
    df_trough_fin = fix_consequtive_peaks_troughs(df.copy(), "Trough")

    # print("\nPeaks found\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
    # print(f"Total peaks found: {df_peak_fin.shape[0]}\n{df_peak_fin.tail(3)}")

    # print("\nTroughs found\n*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
    # print(f"Total troughs found: {df_trough_fin.shape[0]}\n{df_trough_fin.tail(3)}")


    df_peak_trough = pd.concat([df_peak_fin, df_trough_fin], axis= "columns").dropna(how="all")
    df_peak_trough['Price_point'] = df_peak_trough.apply( lambda row: row['Peak'] if pd.isna(row['Trough']) else row['Trough'], axis="columns")
    df_peak_trough['Peak_or_trough'] = df_peak_trough.apply( lambda row: "P" if pd.isna(row['Trough']) else "T", axis="columns")
    df_peak_trough['Difference'] = abs(df_peak_trough['Price_point'].diff())

    return df_peak_trough 