# IgRunStrategyFunction Logic

## Purpose

The `IgRunStrategyFunction` is designed to execute trading strategies based on market data. It analyzes the data to identify trading opportunities and generates signals for buying or selling stocks.

## Logic

### Data Preparation

1. **Fetch Market Data**:

   - The function retrieves the last 40 rows of market data for analysis. This data is crucial for identifying patterns and making informed trading decisions.

2. **Identify Peaks and Troughs**:
   - Utilizes the `get_peaks_and_troughs` function to detect significant peaks and troughs in the market data. These points are essential for determining potential retracement levels.

### Signal Generation

1. **Evaluate Buy Conditions**:
   - **Retracement Confirmation**: Confirms that the retracement forms a trough by checking the sequence of peaks and troughs.
   - **Retracement Level Check**: Ensures the retracement is within specified Fibonacci levels, controlled through the [[Configuration File - config.json|configuration file]], adjusted by a configurable zone thickness.
   - **Price Level Validation**: Validates that the current price is between the stop-loss (SL) and the previous peak to avoid API failures.

2. **Evaluate Sell Conditions**:
   - **Retracement Confirmation**: Confirms that the retracement forms a peak by checking the sequence of peaks and troughs.
   - **Retracement Level Check**: Ensures the retracement is within specified Fibonacci levels, adjusted by a configurable zone thickness.
   - **Price Level Validation**: Validates that the current price is between the stop-loss (SL) and the previous trough to avoid API failures.

### Output

- The function outputs trading signals, which include:
  - **Signal**: Indicates whether to buy (1) or sell (-1).
  - **Target Price (TP)**: The calculated target price level.
  - **Stop-Loss (SL)**: The calculated stop-loss level.
  - **Price Points**: Key price points used in the analysis.

This logic ensures that trading decisions are based on robust technical analysis, leveraging Fibonacci retracement levels to identify optimal entry and exit points in the market.
