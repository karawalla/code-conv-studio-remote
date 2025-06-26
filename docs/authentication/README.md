# Claude Authentication Setup Documentation

This folder contains documentation and example files for setting up Claude authentication in the Code Conversion Studio application.

## Contents

1. **authentication-overview.md** - Complete documentation about the authentication architecture
2. **claude_auth.py** - Authentication manager module (sanitized version)
3. **setup_claude_auth.py** - Setup script for configuring authentication
4. **settings.local.json.example** - Example Claude settings file for permissions
5. **auth-endpoints.md** - API endpoints documentation for authentication

## Quick Start

1. Run the setup script:
   ```bash
   python3 setup_claude_auth.py
   ```

2. Configure your API key:
   - Set environment variable: `export CLAUDE_API_KEY="your-api-key"`
   - Or save to file: `~/.claude/api_key`

3. The application will automatically:
   - Create authentication helper scripts
   - Start background refresh daemon
   - Maintain persistent Claude connections

## Authentication Methods

The system supports multiple authentication methods:
- Environment variables
- File-based API keys
- OAuth (Claude CLI built-in)
- Custom secret managers (AWS, Azure, HashiCorp Vault)

## Security Notes

- API keys are never stored in the repository
- All sensitive files have restricted permissions (600)
- Authentication tokens are automatically refreshed every 4 minutes
- OAuth tokens are managed by Claude CLI

For detailed documentation, see `authentication-overview.md`.