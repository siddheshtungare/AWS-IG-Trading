### IgLoginFunction

- **Purpose**:

  - The `IgLoginFunction` is responsible for managing the login process to the IG trading platform. It ensures that the application can authenticate and maintain a session with the trading platform.

- **Logic**:

  1. **Connect to IG Trading Platform**:

     - The function initiates a connection to the IG trading platform using the credentials provided. This step is crucial for accessing the platform's services and data.

  2. **Retrieve Session Tokens**:

     - Upon successful authentication, the function retrieves session tokens. These tokens are necessary for making subsequent API calls to the IG platform, as they validate the session and permissions.

  3. **Store Session Tokens**:

     - The retrieved session tokens are stored securely for use in future interactions with the IG platform. This storage ensures that the application can maintain a session without needing to re-authenticate frequently.

  4. **Error Handling**:

     - The function includes error handling to manage any issues that arise during the login process. If an error occurs, it captures the error details, including the function name and error message, and raises a `RuntimeError` with this information.

  5. **Configuration Management**:

     - The function retrieves [[Configuration File - config.json|configuration data]] from an S3 bucket. This configuration data is stored in a file named `config.json`. The file is accessed using the AWS SDK for Python (Boto3), which reads the file from the specified S3 bucket and key.
     - The configuration data is then parsed from JSON format into a Python dictionary. This data is used to form the final output, which includes request headers and account balance information for each configuration item.
     - Each configuration item is processed to include the request headers and account balance, which are retrieved using helper functions. This processed configuration data is appended to a list that forms part of the function's output.

  6. **Account Balance Retrieval**:
     - The function can retrieve the account balance from the IG platform. This is done by calling the `get_account_balance` function, which can refresh the balance by making an API call if needed.

- **Output**:
  - The function outputs a JSON object containing configuration items, error messages (if any), and a flag indicating whether errors exist. This output is used by other functions to interact with the IG trading platform securely and efficiently.
