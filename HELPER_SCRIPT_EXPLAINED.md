# Auth Helper Script Explained

The auth helper script is a simple bash script that Claude Code executes whenever it needs your API key. Here's the complete script with detailed explanations:

## The Complete Script

```bash
#!/bin/bash
# Claude Code Authentication Helper
# This script is called by Claude Code to get fresh API keys

# You can implement custom logic here to fetch keys from:
# - Environment variables
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
# - Any other secret management system

# For now, return the API key from environment or file
if [ -n "$CLAUDE_API_KEY" ]; then
    echo "$CLAUDE_API_KEY"
elif [ -f "$HOME/.claude/api_key" ]; then
    cat "$HOME/.claude/api_key"
else
    # Fallback - you can implement custom key retrieval here
    echo "{self.api_key or ''}"
fi
```

## Line-by-Line Breakdown

### 1. Shebang Line
```bash
#!/bin/bash
```
- Tells the system to use bash to execute this script
- Required for any executable shell script

### 2. Comments
```bash
# Claude Code Authentication Helper
# This script is called by Claude Code to get fresh API keys
```
- Documentation explaining the script's purpose
- Claude Code will execute this script internally

### 3. First Check: Environment Variable
```bash
if [ -n "$CLAUDE_API_KEY" ]; then
    echo "$CLAUDE_API_KEY"
```

Breaking this down:
- `if [ -n "$CLAUDE_API_KEY" ]; then` - Check if environment variable exists
  - `[ ... ]` - Test command in bash
  - `-n` - Tests if string is NOT empty
  - `$CLAUDE_API_KEY` - The environment variable
- `echo "$CLAUDE_API_KEY"` - Print the API key to stdout
- Claude Code captures this output and uses it as the API key

### 4. Second Check: File
```bash
elif [ -f "$HOME/.claude/api_key" ]; then
    cat "$HOME/.claude/api_key"
```

Breaking this down:
- `elif` - "else if" - only runs if first condition was false
- `[ -f "$HOME/.claude/api_key" ]` - Check if file exists
  - `-f` - Tests if path is a regular file
  - `$HOME` - User's home directory (e.g., /home/ubuntu)
  - Full path: `/home/ubuntu/.claude/api_key`
- `cat "$HOME/.claude/api_key"` - Output file contents to stdout

### 5. Fallback
```bash
else
    # Fallback - you can implement custom key retrieval here
    echo "{self.api_key or ''}"
fi
```

- `else` - If neither environment var nor file exists
- `echo "{self.api_key or ''}"` - This is actually Python template syntax
  - When the script is created, Python replaces `{self.api_key or ''}` with the actual API key
  - If no API key is set, it becomes an empty string

### 6. End
```bash
fi
```
- Closes the if statement in bash

## How Claude Code Uses This Script

When Claude needs authentication, it internally does something like:

```bash
# Claude's internal process (simplified):
API_KEY=$(~/.claude/auth_helper.sh)
curl -H "x-api-key: $API_KEY" https://api.anthropic.com/...
```

## Real-World Examples

### Example 1: Basic Usage
If you set `CLAUDE_API_KEY=sk-ant-abc123`, the script outputs:
```
sk-ant-abc123
```

### Example 2: File-Based
If you have a file `~/.claude/api_key` containing `sk-ant-xyz789`, the script outputs:
```
sk-ant-xyz789
```

### Example 3: AWS Secrets Manager
You could modify the script to:
```bash
#!/bin/bash
# Fetch from AWS Secrets Manager
aws secretsmanager get-secret-value \
    --secret-id claude-api-key \
    --query SecretString \
    --output text
```

### Example 4: HashiCorp Vault
```bash
#!/bin/bash
# Fetch from Vault
export VAULT_ADDR="https://vault.company.com"
vault kv get -field=api_key secret/claude
```

### Example 5: Multiple Environments
```bash
#!/bin/bash
# Use different keys for different environments
if [ "$ENVIRONMENT" = "production" ]; then
    echo "$CLAUDE_API_KEY_PROD"
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo "$CLAUDE_API_KEY_STAGING"
else
    echo "$CLAUDE_API_KEY_DEV"
fi
```

## Security Considerations

1. **Permissions**: The script is created with 755 (rwxr-xr-x)
   - Owner can read, write, execute
   - Others can read and execute
   - This is required for Claude to execute it

2. **API Key File**: Should be 600 (rw-------)
   - Only owner can read/write
   - More secure than the script itself

3. **No Hardcoding**: The fallback uses Python templating
   - Avoids hardcoding keys in version control
   - Can be dynamically generated

## Why This Design?

1. **Flexibility**: Can fetch keys from anywhere
2. **Security**: Keys aren't in command arguments (visible in `ps`)
3. **Standards**: Follows Unix philosophy of "output to stdout"
4. **Simplicity**: Just needs to output the key, nothing else

## Testing the Script

You can test it manually:
```bash
# Make it executable
chmod +x ~/.claude/auth_helper.sh

# Test it
~/.claude/auth_helper.sh
# Should output your API key

# Test with environment
CLAUDE_API_KEY="test-key" ~/.claude/auth_helper.sh
# Should output: test-key
```

## Common Issues

1. **Script outputs nothing**: No API key found in env or file
2. **Permission denied**: Script needs execute permission
3. **Command not found**: Path is wrong or script doesn't exist
4. **Extra output**: Script should ONLY output the API key, nothing else