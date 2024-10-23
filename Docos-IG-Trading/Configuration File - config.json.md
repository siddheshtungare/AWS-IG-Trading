# Configuration File: `config.json`

## Overview

The `config.json` file is a critical component of the IG-Trading-1 AWS SAM project. It contains various configuration parameters that guide the behavior of the trading algorithms and API interactions. This file allows for flexible adjustments to the trading strategy and API settings without modifying the core code.

## Configuration Elements and Their Usage

### 1. `prominence`

- **Usage**: 
  - Found in `fibo_strategy.py` within the `strategy` function.
  - Determines the prominence of peaks and troughs in the market data, which is crucial for identifying significant retracement levels.
  - Passed as a parameter to the `get_peaks_and_troughs` function to filter out less significant peaks and troughs.

### 2. `fibo_level_from` and `fibo_level_to`

- **Usage**: 
  - Used in `fibo_strategy.py` within the `strategy` function.
  - Define the range of Fibonacci retracement levels to consider for potential buy/sell signals.
  - These levels are used to evaluate whether the retracement is within a specified zone, indicating a potential trading opportunity.

### 3. `tp_level`

- **Usage**: 
  - Utilized in `fibo_strategy.py` within the `strategy` function.
  - Sets the target price (TP) level for trades, calculated as a multiple of the wave length.
  - Helps determine the potential profit target for a trade.

### 4. `max_drawdown_multiplier`

- **Usage**: 
  - Found in both `fibo_strategy.py` and `ig_buy_sell_api_helper.py`.
  - In `fibo_strategy.py`, it is part of the return value of the `strategy` function, indicating the risk tolerance for a trade.
  - In `ig_buy_sell_api_helper.py`, it is used in the `calculate_position_size` function to determine the maximum allowable drawdown for a position, influencing the position size calculation.

### 5. `MarketId`

- **Usage**: 
  - Utilized in `ig_buy_sell_api_helper.py` within the `IG_buy_sell` class.
  - Specifies the market identifier for which trades are to be executed.
  - Used in API calls to fetch market details and execute trades for the specified market.

### 6. `trade_params`

- **Usage**: 
  - Found in `ig_buy_sell_api_helper.py` within the `IG_buy_sell` class.
  - Contains parameters such as stop-loss (SL) and target price (TP) levels for executing trades.
  - These parameters are used in the `create_position` function to set the conditions for opening a new trade.

## Conclusion

The `config.json` file provides a centralized location for configuring various aspects of the trading strategy and API interactions. By adjusting the values in this file, users can fine-tune the trading algorithm's behavior and risk management parameters without altering the underlying code. This flexibility is essential for adapting to changing market conditions and optimizing trading performance.