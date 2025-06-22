# Claude Code Authentication: End-to-End Flow Explained

## Overview

Claude Code doesn't use OAuth-style refresh tokens. Instead, it uses an **API Key Helper** mechanism - a script that Claude calls whenever it needs authentication credentials.

## The Complete Authentication Flow

### 1. Initial Setup Phase

```
User starts Flask app
    ↓
Flask app initializes ClaudeAuthManager
    ↓
ClaudeAuthManager creates auth helper script (~/.claude/auth_helper.sh)
    ↓
Background refresh daemon starts (runs every 4 minutes)
```

**What happens:**
- When your Flask app starts, it creates a `ClaudeAuthManager` instance
- This manager creates a shell script at `~/.claude/auth_helper.sh`
- The script is what Claude Code will call to get your API key
- A background thread starts that "touches" this script every 4 minutes

### 2. The Auth Helper Script

The auth helper script looks like this:
```bash
#!/bin/bash
# This script is called by Claude Code whenever it needs the API key

if [ -n "$CLAUDE_API_KEY" ]; then
    echo "$CLAUDE_API_KEY"
elif [ -f "$HOME/.claude/api_key" ]; then
    cat "$HOME/.claude/api_key"
else
    echo "your-stored-api-key"
fi
```

**Key points:**
- Claude Code calls this script internally when it needs authentication
- The script simply returns your API key to stdout
- Claude uses this key for API requests

### 3. When User Makes a Request

```
User submits query in Flask app
    ↓
Flask calls ProcessManager.start_process()
    ↓
EnhancedProcessManager builds Claude command with auth flags
    ↓
Command includes: --api-key-helper ~/.claude/auth_helper.sh
    ↓
Claude process starts
```

**The actual command looks like:**
```bash
claude -p "your query" \
  --allowedTools Read,Write,Bash \
  --output-format stream-json \
  --verbose \
  --api-key-helper /home/user/.claude/auth_helper.sh
```

### 4. During Claude Execution

```
Claude runs and needs to make API call
    ↓
Claude checks: "Do I need fresh credentials?"
    ↓
If YES (5 minutes passed or got 401 error):
    Claude executes: ~/.claude/auth_helper.sh
    ↓
Helper script returns API key
    ↓
Claude uses key for API request
```

**Important timing:**
- Claude calls the helper after 5 minutes OR on authentication failure
- Our daemon refreshes every 4 minutes (before the 5-minute mark)
- This prevents timeouts during long operations

### 5. The Background Refresh Daemon

```python
def _refresh_loop(self):
    while self.running:
        # Every 4 minutes:
        1. Update environment variable (if used)
        2. Touch the auth helper script (updates timestamp)
        3. Log the refresh
        
        time.sleep(240)  # 4 minutes
```

**Why this works:**
- By "touching" the script, we update its modification time
- This signals to Claude that credentials are fresh
- Even though the API key doesn't change, the system thinks it's "refreshed"

### 6. Error Recovery Flow

```
Claude gets 401 Unauthorized error
    ↓
EnhancedProcessManager detects auth error
    ↓
Forces immediate refresh:
    - Updates environment variable
    - Touches auth helper script
    - Tests authentication
    ↓
Retries the Claude command (up to 3 times)
```

### 7. API Key Storage Hierarchy

```
1. Environment Variable (CLAUDE_API_KEY)
   ↓ (if not found)
2. File (~/.claude/api_key)
   ↓ (if not found)
3. Hardcoded in auth helper script
   ↓ (if not found)
4. Error: No API key available
```

## Visual Flow Diagram

```
┌─────────────────┐
│   Flask App     │
│    Starts       │
└────────┬────────┘
         │
         v
┌─────────────────┐     Creates      ┌─────────────────┐
│ ClaudeAuthMgr   │ ───────────────> │ Auth Helper     │
│                 │                   │ Script          │
└────────┬────────┘                   └─────────────────┘
         │                                    ^
         │ Starts                            │ Calls
         v                                   │
┌─────────────────┐                   ┌──────┴──────────┐
│ Refresh Daemon  │                   │  Claude Code    │
│ (every 4 min)   │                   │   Process       │
└─────────────────┘                   └─────────────────┘
```

## Why This Design?

1. **No Token Expiry**: API keys don't expire like JWT tokens
2. **Claude's Design**: Claude expects a helper script, not direct key injection
3. **Flexibility**: Helper script can fetch keys from any source (Vault, AWS, etc.)
4. **Reliability**: Background refresh prevents mid-operation timeouts

## Common Scenarios

### Scenario 1: Quick Task (< 5 minutes)
- User submits query
- Claude starts with helper script
- Task completes before 5 minutes
- No refresh needed

### Scenario 2: Long Task (> 5 minutes)
- User submits complex query
- After 5 minutes, Claude calls helper script
- Helper returns same API key (but fresh timestamp)
- Task continues without interruption

### Scenario 3: Network Error
- Claude gets 401 error mid-task
- Helper script is called immediately
- Fresh credentials provided
- Task retries automatically

## Security Notes

1. **API Key Never in Command Line**: Uses helper script instead
2. **File Permissions**: Script is 755, API key file is 600
3. **Memory Only**: Can run entirely from environment variables
4. **Audit Trail**: All refreshes are logged

## Customization Points

You can modify the auth helper to:
- Fetch from AWS Secrets Manager
- Rotate keys on each call
- Use temporary credentials
- Integrate with enterprise SSO

The key is: whatever your helper script outputs is what Claude uses as the API key.