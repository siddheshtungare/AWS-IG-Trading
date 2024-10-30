import json
import pandas as pd
import numpy as np
import datetime as dt

def strategy(df_data, params):
    """
    SMA crossing strategy implementation
    Buy when SMA50 crosses above SMA200
    Sell when SMA50 crosses below SMA200
    Args:
        df_data: DataFrame with OHLCV data
        params: Dictionary containing strategy parameters
    Returns:
        signal: 1 for buy, -1 for sell, 0 for no trade
        params: Dictionary with trade parameters
        logs: List of logs generated during the strategy analysis
    """
    logs = []
    
    # Extract strategy parameters
    sma_fast = params.get("sma_fast", 50)
    sma_slow = params.get("sma_slow", 200)
    max_drawdown_multiplier = params.get('max_drawdown_multiplier', 0.02)

    logs.append("\nStarting SMA Crossing strategy analysis...")
    logs.append(f"Parameters: Fast SMA={sma_fast}, Slow SMA={sma_slow}")

    # Calculate SMAs
    df_data['SMA_fast'] = df_data['Close'].rolling(window=sma_fast).mean()
    df_data['SMA_slow'] = df_data['Close'].rolling(window=sma_slow).mean()

    # Calculate previous values for crossing detection
    df_data['SMA_fast_prev'] = df_data['SMA_fast'].shift(1)
    df_data['SMA_slow_prev'] = df_data['SMA_slow'].shift(1)

    # Get current row
    row = df_data.iloc[-1]
    prev_row = df_data.iloc[-2]

    logs.append("\nCurrent market state:")
    logs.append(f"Close: {row['Close']:.2f}")
    logs.append(f"Fast SMA: {row['SMA_fast']:.2f}")
    logs.append(f"Slow SMA: {row['SMA_slow']:.2f}")

    signal = 0
    sl_price = 0
    tp_price = 0

    # Check for crossings
    if (prev_row['SMA_fast'] <= prev_row['SMA_slow']) and (row['SMA_fast'] > row['SMA_slow']):
        # Bullish crossing (SMA50 crosses above SMA200)
        logs.append("\nBullish crossing detected!")
        signal = 1
        
        # Set stop loss below recent low
        lookback_period = 20  # Look back 20 periods for support/resistance
        recent_low = df_data['Low'].tail(lookback_period).min()
        sl_price = recent_low * (1 - 0.01)  # 1% below recent low
        
        # Set take profit based on recent volatility
        atr = df_data['High'].tail(lookback_period).max() - df_data['Low'].tail(lookback_period).min()
        tp_price = row['Close'] + (atr * 1.5)  # 1.5 times the range

    elif (prev_row['SMA_fast'] >= prev_row['SMA_slow']) and (row['SMA_fast'] < row['SMA_slow']):
        # Bearish crossing (SMA50 crosses below SMA200)
        logs.append("\nBearish crossing detected!")
        signal = -1
        
        # Set stop loss above recent high
        lookback_period = 20  # Look back 20 periods for support/resistance
        recent_high = df_data['High'].tail(lookback_period).max()
        sl_price = recent_high * (1 + 0.01)  # 1% above recent high
        
        # Set take profit based on recent volatility
        atr = df_data['High'].tail(lookback_period).max() - df_data['Low'].tail(lookback_period).min()
        tp_price = row['Close'] - (atr * 1.5)  # 1.5 times the range

    trade_params = {
        "tp": round(float(tp_price), 2),
        "sl": round(float(sl_price), 2),
        "max_drawdown_multiplier": max_drawdown_multiplier,
        'indicators': {
            'sma_fast': round(float(row['SMA_fast']), 2),
            'sma_slow': round(float(row['SMA_slow']), 2)
        }
    }

    logs.append("\nStrategy analysis complete")
    logs.append(f"Signal: {signal}")
    logs.append(f"Parameters: {json.dumps(trade_params, indent=2)}")

    return signal, trade_params, logs 