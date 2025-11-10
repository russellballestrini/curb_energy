# Getting Curb API Credentials

This guide explains how to obtain the necessary credentials to use the Curb Energy API.

## Required Credentials

You need **two sets** of credentials:

### 1. User Credentials (Your Curb Account)

These are your regular Curb account credentials:

```bash
export CURB_USERNAME="your_email@example.com"
export CURB_PASSWORD="your_curb_password"
```

**Where to get them:**
- You already have these! They're your Curb login credentials
- If you don't have a Curb account, create one at https://app.energycurb.com

### 2. OAuth2 Application Credentials (From Curb Developer Program)

These identify your application to the Curb API:

```bash
export CURB_CLIENT_TOKEN="your_oauth_client_id"
export CURB_CLIENT_SECRET="your_oauth_client_secret"
```

**Where to get them:**
- These must be obtained from Curb by registering your application

## How to Get OAuth2 Application Credentials

### Method 1: Contact Curb Support

**Recommended for most users**

1. **Contact Curb Support:**
   - Website: http://energycurb.com/support/
   - Email: Look for support email on their website
   - Phone: Check their website for contact information

2. **Request OAuth2 Credentials:**

   Here's a template email:

   ```
   Subject: Request for OAuth2 API Credentials

   Hello Curb Support Team,

   I am a Curb customer and would like to develop an application to access
   my energy data through the Curb API. I need OAuth2 client credentials
   (client_token and client_secret) to authenticate my application.

   Use Case: [Describe your use case, e.g.:]
   - Personal energy monitoring dashboard
   - Home automation integration
   - Energy usage analytics
   - Custom mobile app

   My Curb account email: your_email@example.com

   Please provide:
   - OAuth2 Client Token (client_id)
   - OAuth2 Client Secret

   Thank you!
   ```

3. **Wait for Response:**
   - Curb will review your request
   - They'll provide your credentials
   - Save them securely!

### Method 2: Curb Developer Portal

**If available**

1. Visit the Curb API documentation: http://docs.energycurb.com/

2. Look for:
   - Developer Portal
   - API Access
   - Register Application
   - Get API Key

3. Follow the registration process

4. Save your credentials

### Method 3: Check Your Curb Account

**May not be available, but worth checking**

1. Log in to https://app.energycurb.com

2. Navigate to:
   - Settings
   - Account Settings
   - Developer Settings
   - API Access
   - Integrations

3. Look for options to:
   - Generate API credentials
   - Register an application
   - Create API token

## Understanding OAuth2 Flow

### Why Two Sets of Credentials?

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                         │
│  Identified by: client_token + client_secret               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     CURB API SERVER                         │
│  Authenticates: Is this a valid registered app?            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    USER AUTHORIZATION                       │
│  User provides: username + password                        │
│  API checks: Does this user exist? Is password correct?    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     ACCESS TOKEN                            │
│  API returns: Temporary access token                       │
│  Token allows: Access to user's energy data               │
└─────────────────────────────────────────────────────────────┘
```

### Security Benefits

1. **Application Tracking:**
   - Curb knows which apps are accessing their API
   - Can revoke credentials for misbehaving apps
   - Can track usage and enforce rate limits

2. **User Security:**
   - Your app never stores user passwords long-term
   - Uses temporary access tokens instead
   - Tokens can be refreshed or revoked

3. **Separation of Concerns:**
   - Application credentials identify the app
   - User credentials identify the user
   - Neither can work without the other

## Setting Up Your Environment

Once you have all four credentials, set them up:

### Option 1: Environment Variables (Temporary)

```bash
# User credentials
export CURB_USERNAME="your_email@example.com"
export CURB_PASSWORD="your_password"

# Application credentials (from Curb)
export CURB_CLIENT_TOKEN="your_client_token_here"
export CURB_CLIENT_SECRET="your_client_secret_here"

# Test it works
make server
```

### Option 2: .env File (Persistent)

```bash
# Copy the example file
cp .env.example .env

# Edit the file
nano .env
```

Add your credentials:
```bash
CURB_USERNAME=your_email@example.com
CURB_PASSWORD=your_password
CURB_CLIENT_TOKEN=your_client_token_here
CURB_CLIENT_SECRET=your_client_secret_here
```

**Load environment variables:**
```bash
# Load from .env file
export $(cat .env | xargs)

# Or use a tool like direnv
# https://direnv.net/
```

### Option 3: Configuration File (For Scripts)

```python
# config.py
import os

CURB_CONFIG = {
    'username': os.getenv('CURB_USERNAME'),
    'password': os.getenv('CURB_PASSWORD'),
    'client_token': os.getenv('CURB_CLIENT_TOKEN'),
    'client_secret': os.getenv('CURB_CLIENT_SECRET'),
}
```

## Troubleshooting

### "I contacted Curb but haven't heard back"

**What to do:**
- Follow up after 3-5 business days
- Try different contact methods (email, phone, web form)
- Check your spam folder
- Be patient - this might take time

### "Curb says they don't provide API credentials"

**Possible reasons:**
- API might be for internal use only
- They might have discontinued public API access
- You might need a specific account type

**Alternatives:**
- Ask about partner/developer programs
- Check if there's a beta program you can join
- Look for official integrations (Home Assistant, etc.)

### "I can't find developer documentation"

**The original Curb API docs:**
- http://docs.energycurb.com/
- http://docs.energycurb.com/authentication.html
- https://github.com/curb (Curb's GitHub organization)

**Note:** Documentation may have moved or changed. Contact Curb for current information.

### "Can I use someone else's credentials?"

**❌ No - This is not recommended:**
- Violates terms of service
- Security risk
- Could get your account banned
- Each app should have its own credentials

### "Can I reverse-engineer credentials from the app?"

**❌ Not recommended:**
- Violates terms of service
- Extracted credentials might be invalidated
- Could break when app updates
- Legal concerns

## Testing Without Credentials

If you're unable to get credentials but want to test the library:

### 1. Use Mock Data

```python
# tests/test_with_mocks.py
from unittest.mock import Mock, AsyncMock
from curb_energy.client import RestApiClient

# Create mock client
mock_client = AsyncMock(spec=RestApiClient)
mock_client.profiles = AsyncMock(return_value=[...])

# Test your code with mocks
```

### 2. Use Test Fixtures

```bash
# Run unit and integration tests (use mocked API)
make test

# These tests don't require real credentials
make test-unit
make test-integration
```

### 3. Contribute to Testing

Help improve the library without needing credentials:
- Write better test coverage
- Improve documentation
- Add features
- Fix bugs

## Security Best Practices

### ✅ Do:

- Store credentials in environment variables
- Use `.env` files (and add `.env` to `.gitignore`)
- Keep credentials secret
- Rotate credentials periodically
- Use different credentials for dev/prod
- Revoke credentials you're not using

### ❌ Don't:

- Commit credentials to Git
- Share credentials publicly
- Hardcode credentials in source code
- Use production credentials for testing
- Share credentials between applications
- Post credentials in screenshots or logs

## Example Usage

Once you have all credentials:

```bash
# 1. Set environment variables
export CURB_USERNAME="user@example.com"
export CURB_PASSWORD="mypassword"
export CURB_CLIENT_TOKEN="abc123"
export CURB_CLIENT_SECRET="secret456"

# 2. Start the server
make server

# 3. Access the dashboard
open http://localhost:8000

# 4. Use the API
curl http://localhost:8000/profiles
```

## Getting Help

If you're stuck getting credentials:

1. **Check Curb's official channels:**
   - Website: http://energycurb.com/
   - Support: http://energycurb.com/support/
   - Documentation: http://docs.energycurb.com/

2. **Check community resources:**
   - Home Assistant Curb integration (may have setup guides)
   - Forums and community discussions
   - Stack Overflow

3. **Alternative integrations:**
   - If direct API access isn't available, check for official integrations
   - Home Assistant, IFTTT, or other platforms might have Curb support

## Summary

**To use this library, you need:**

1. ✅ Curb account (username + password) - **You can get this yourself**
2. ⏳ OAuth2 credentials (client_token + client_secret) - **Must request from Curb**

**Next steps:**

1. Contact Curb support to request OAuth2 credentials
2. While waiting, explore the codebase and tests
3. Once you have credentials, follow the setup guide
4. Start building your energy monitoring application!

## Resources

- **Curb Website:** http://energycurb.com/
- **API Docs:** http://docs.energycurb.com/
- **Support:** http://energycurb.com/support/
- **This Library:** https://github.com/russellballestrini/curb_energy

## Questions?

If you have questions about getting credentials, please:
- Open an issue on GitHub
- Check existing issues for similar questions
- Contact Curb support directly for credential requests
