# IG-Trading-1 AWS SAM Project Documentation

## Project Overview

This project is built using the AWS Serverless Application Model (SAM) and is designed to automate stock trading operations using a state machine. The project includes several AWS Lambda functions that handle different aspects of the trading process, such as logging in, running trading strategies, and processing buy/sell orders.

## Architecture

### AWS Lambda Functions

- **[[IgLoginFunction]]**

  - **Purpose**: Handles the login process to the IG trading platform.
  - **Logic**:
    - Connects to the IG trading platform using provided credentials.
    - Retrieves and stores session tokens for subsequent API calls.

- **[[IgRunStrategyFunction]]**

  - **Purpose**: Executes trading strategies based on market data.
  - **Logic**:
    - **Data Preparation**:
      - Fetches the last 40 rows of market data for analysis.
      - Identifies peaks and troughs in the data using the `get_peaks_and_troughs` function.
    - **Signal Generation**:
      - Evaluates conditions for buy/sell signals based on Fibonacci retracement levels.
      - Confirms retracement patterns and calculates target price (TP) and stop-loss (SL) levels.
      - Generates a buy signal if the retracement forms a trough and meets specific conditions.
      - Generates a sell signal if the retracement forms a peak and meets specific conditions.
    - **Output**:
      - Returns trading signals along with calculated TP and SL levels, and price points for further processing.

- **[[IgProcessBuySellFunction]]**

  - **Purpose**: Processes buy and sell orders based on trading signals.
  - **Logic**:
    - Receives trading signals from the strategy function.
    - Executes buy/sell orders on the IG trading platform.
    - Records transaction details in the `TransactionTable` and `EquityTable` DynamoDB tables.

### Other AWS Services

- **AWS Step Functions**: Orchestrates the execution of the Lambda functions in a defined sequence.
- **DynamoDB**: Stores transaction and equity data.
- **S3**: Provides full access for storing and retrieving data related to the trading process.

### State Machine Workflow

The state machine, as detailed in the [[StateMachineWorkflow]], is a crucial component of this project. It automates the trading process by coordinating the execution of various Lambda functions. The workflow begins with the `Ig-Login` state, which handles authentication with the IG platform. It then proceeds to execute trading strategies and process buy/sell orders based on the signals generated. The state machine includes robust error handling and retry mechanisms to ensure reliability and resilience in trading operations. Each state in the workflow is designed to handle specific tasks, such as checking for errors, processing configuration files, and executing trades, ensuring a seamless and automated trading experience.

## Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.9
- Docker (for local testing)

## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repo/aws-sam-project.git
   cd aws-sam-project
   ```

2. **Build the project**:

   ```bash
   sam build
   ```

3. **Deploy the project**:
   ```bash
   sam deploy --guided
   ```
   Follow the prompts to set up your stack name, region, and other parameters.

## Testing

- **Local Testing**: Use the SAM CLI to invoke functions locally.

  ```bash
  sam local invoke FunctionName --event event.json
  ```

- **Unit Tests**: [Describe how to run unit tests, e.g., using pytest or another framework]

## Usage

- **API Endpoints**: [List and describe any API endpoints]
- **Event Sources**: The state machine is triggered by a scheduled event every hour.

## Monitoring and Logging

- **CloudWatch Logs**: Access logs for each Lambda function to monitor execution and troubleshoot issues.
