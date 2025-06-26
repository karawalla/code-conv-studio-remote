# Code Conversion Studio Authentication Documentation

## Overview

The Code Conversion Studio uses Claude OAuth authentication with automatic token refresh to maintain continuous operation without manual intervention.

## Authentication Architecture

### Components

1. **Claude OAuth Authentication**
   - Uses Claude CLI built-in OAuth flow
   - Tokens stored in `/home/ubuntu/.claude/.credentials.json`
   - Access token and refresh token automatically managed

2. **Authentication Manager** (`claude_auth.py`)
   - `ClaudeAuthManager`: Main authentication coordinator
   - `ClaudeSessionManager`: Handles Claude process lifecycle
   - `EnhancedProcessManager`: Manages process execution with auth retry logic

3. **Auth Helper Script** (`/home/ubuntu/.claude/auth_helper.sh`)
   - Called by Claude CLI when authentication is needed
   - Provides API key from environment or file
   - Fallback mechanism for different auth sources

4. **Background Refresh Daemon**
   - Runs as background thread in Flask application
   - Refreshes authentication every **4 minutes** (240 seconds)
   - Prevents token expiration (Claude tokens expire after 5 minutes)

## Service Configuration

### Systemd Service
- **Service Name**: `code-conv-studio.service`
- **Location**: `/etc/systemd/system/code-conv-studio.service`
- **User**: `ubuntu`
- **Working Directory**: `/home/ubuntu/code-conv-studio`
- **Auto-restart**: Enabled with 10-second delay
- **Boot startup**: Enabled

### Service Features
- **Persistent**: Survives SSH disconnections
- **Auto-restart**: Automatically restarts on failure
- **Logging**: All output goes to systemd journal
- **Environment**: Includes PATH and PYTHONPATH setup

## Authentication Flow

### 1. Service Startup
```
systemd starts code-conv-studio.service
    ↓
Flask app starts (app.py)
    ↓
ClaudeAuthManager initializes
    ↓
Background refresh daemon starts
    ↓
Auth helper script created/updated
```

### 2. User Request Processing
```
User clicks migrate button
    ↓
Flask calls ProcessManager.start_process()
    ↓
EnhancedProcessManager attempts Claude with --api-key-helper
    ↓
If compatibility issue: Falls back to standard Claude CLI
    ↓
Claude process starts with OAuth authentication
```

### 3. Background Maintenance
```
Every 4 minutes:
    ↓
Refresh daemon wakes up
    ↓
Updates auth timestamps
    ↓
Ensures environment variables set
    ↓
Touches auth helper script
    ↓
Goes back to sleep
```

## Current Status (as of 2025-06-23)

### Authentication Method
- **Type**: Claude OAuth (built-in)
- **Status**: Active and working
- **Last Refresh**: Auto-refreshing every 4 minutes
- **Fallback**: Graceful fallback to standard Claude CLI for compatibility

### Known Issues & Solutions

1. **Claude CLI Compatibility**
   - **Issue**: `--api-key-helper` flag not supported in current Claude CLI version
   - **Solution**: Automatic fallback to standard Claude CLI execution
   - **Status**: Fixed with error detection and fallback mechanism

2. **Process Management**
   - **Issue**: Enhanced process manager can fail silently
   - **Solution**: Exception handling triggers fallback to standard process execution
   - **Status**: Working with proper error handling

## API Endpoints

- **GET** `/api/auth/status` - Check authentication status
- **POST** `/api/auth/refresh` - Manual authentication refresh
- **POST** `/api/auth/update-key` - Update API key

## File Locations

- **Service File**: `/etc/systemd/system/code-conv-studio.service`
- **Auth Helper**: `/home/ubuntu/.claude/auth_helper.sh`
- **Credentials**: `/home/ubuntu/.claude/.credentials.json`
- **Auth Manager**: `/home/ubuntu/code-conv-studio/claude_auth.py`
- **Main Application**: `/home/ubuntu/code-conv-studio/app.py`

## Troubleshooting

### Check Service Status
```bash
systemctl status code-conv-studio
```

### View Service Logs
```bash
journalctl -u code-conv-studio -f
```

### Check Authentication Status
```bash
curl http://localhost/api/auth/status
```

### Manual Service Control
```bash
# Start service
systemctl start code-conv-studio

# Stop service
systemctl stop code-conv-studio

# Restart service
systemctl restart code-conv-studio

# Enable auto-start
systemctl enable code-conv-studio
```

## Security Notes

- API keys stored in environment variables and secure files
- OAuth tokens automatically managed by Claude CLI
- Auth helper script has restricted permissions (executable by owner only)
- All authentication logs go to systemd journal for audit trail