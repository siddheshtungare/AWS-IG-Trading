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

- **Output**:
  - The function outputs the session tokens, which are used by other functions to interact with the IG trading platform securely and efficiently.