# Claude Code Authentication Guide

This Flask application now includes automatic Claude Code authentication management to maintain persistent connections without timeouts.

## How It Works

Claude Code doesn't use traditional refresh tokens. Instead, it uses an **API key helper** mechanism:

1. **API Key Helper Script**: A script that Claude Code calls to get fresh API keys
2. **Automatic Refresh**: The helper is called "after 5 minutes or on HTTP 401 response"
3. **Background Daemon**: Our implementation refreshes credentials every 4 minutes (before the 5-minute timeout)

## Setup

### Quick Setup

Run the setup script:
```bash
python setup_claude_auth.py
```

### Manual Setup

1. Set your API key as an environment variable:
   ```bash
   export CLAUDE_API_KEY="your-api-key-here"
   ```

2. Or create a file at `~/.claude/api_key`:
   ```bash
   echo "your-api-key-here" > ~/.claude/api_key
   chmod 600 ~/.claude/api_key
   ```

3. Start your Flask app - authentication will be managed automatically

## Architecture

### Components

1. **ClaudeAuthManager** (`claude_auth.py`):
   - Manages API keys and authentication
   - Creates and maintains the auth helper script
   - Runs a background thread that refreshes auth every 4 minutes
   - Stores API keys securely

2. **EnhancedProcessManager** (`claude_auth.py`):
   - Wraps Claude process execution with authentication
   - Handles auth errors with automatic retry
   - Falls back to standard execution if auth manager fails

3. **Flask Integration** (`app.py`):
   - Initializes auth manager on startup
   - Uses enhanced process manager for all Claude executions
   - Provides API endpoints for auth management

### API Endpoints

- `GET /api/auth/status` - Check current authentication status
- `POST /api/auth/refresh` - Manually trigger authentication refresh
- `POST /api/auth/update-key` - Update the API key

### Authentication Flow

1. **Startup**: 
   - Auth manager initializes with API key from environment/file
   - Creates auth helper script at `~/.claude/auth_helper.sh`
   - Starts background refresh daemon

2. **During Execution**:
   - Claude Code calls the auth helper when needed
   - Helper returns the current API key
   - Background daemon refreshes every 4 minutes

3. **Error Handling**:
   - 401 errors trigger immediate refresh
   - Automatic retry with refreshed credentials
   - Falls back to manual auth if manager fails

## Security Considerations

1. **API Key Storage**:
   - Environment variables (for session)
   - File with 600 permissions (for persistence)
   - Never committed to version control

2. **Auth Helper Script**:
   - Created with 755 permissions (executable by owner)
   - Located in user's home directory
   - Can be customized for enterprise secret management

## Customization

### Using AWS Secrets Manager

Modify the auth helper script in `claude_auth.py`:

```python
helper_content = '''#!/bin/bash
# Fetch from AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id claude-api-key --query SecretString --output text
'''
```

### Using HashiCorp Vault

```python
helper_content = '''#!/bin/bash
# Fetch from Vault
vault kv get -field=api_key secret/claude
'''
```

## Troubleshooting

1. **Authentication Fails**:
   - Check API key is valid
   - Verify environment variable is set
   - Check file permissions on `~/.claude/api_key`

2. **Timeouts Still Occur**:
   - Check refresh daemon is running (see logs)
   - Verify auth helper script exists and is executable
   - Check system time is synchronized

3. **Permission Errors**:
   - Ensure `~/.claude/` directory is writable
   - Check auth helper has execute permissions
   - Verify Flask app has necessary permissions

## Environment Variables

- `CLAUDE_API_KEY` - Your Claude API key
- `CLAUDE_AUTH_REFRESH_INTERVAL` - Seconds between refreshes (default: 240)

## Logs

The auth manager logs important events:
- Authentication initialization
- Refresh operations
- Error conditions
- Retry attempts

Check your Flask app logs for details.