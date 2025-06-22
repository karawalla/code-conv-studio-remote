#!/usr/bin/env python3
"""
Setup script for Claude Code authentication
Helps configure API keys and test authentication
"""

import os
import sys
from pathlib import Path
from claude_auth import ClaudeAuthManager, create_claude_auth_manager


def main():
    print("Claude Code Authentication Setup")
    print("================================\n")
    
    # Check for existing API key
    existing_key = os.environ.get('CLAUDE_API_KEY')
    api_key_file = Path.home() / '.claude' / 'api_key'
    
    if existing_key:
        print(f"✓ Found API key in environment variable")
        use_existing = input("Use existing API key? (y/n): ").lower() == 'y'
        if use_existing:
            api_key = existing_key
        else:
            api_key = input("Enter your Claude API key: ").strip()
    elif api_key_file.exists():
        print(f"✓ Found API key in {api_key_file}")
        use_existing = input("Use existing API key? (y/n): ").lower() == 'y'
        if use_existing:
            api_key = api_key_file.read_text().strip()
        else:
            api_key = input("Enter your Claude API key: ").strip()
    else:
        print("No existing API key found.")
        api_key = input("Enter your Claude API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        sys.exit(1)
    
    print("\nSetting up authentication...")
    
    try:
        # Create auth manager
        auth_manager = ClaudeAuthManager(api_key)
        
        # Save API key persistently
        auth_manager.update_api_key(api_key)
        
        # Test authentication
        print("\nTesting authentication...")
        if auth_manager.test_authentication():
            print("✅ Authentication successful!")
            
            # Set environment variable for current session
            os.environ['CLAUDE_API_KEY'] = api_key
            
            print("\nAuthentication is configured and working.")
            print("\nTo make this permanent, add to your shell profile:")
            print(f"export CLAUDE_API_KEY='{api_key}'")
            
            # Start refresh daemon
            auth_manager.start_refresh_daemon()
            print("\n✅ Authentication refresh daemon started")
            print("   - Refreshes every 4 minutes (before 5-minute timeout)")
            print("   - Runs in background to maintain persistent connection")
            
        else:
            print("❌ Authentication failed. Please check your API key.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error setting up authentication: {e}")
        sys.exit(1)
    
    print("\n✅ Setup complete! Your Flask app will now maintain persistent Claude authentication.")
    print("\nAPI endpoints available:")
    print("  - GET  /api/auth/status      - Check authentication status")
    print("  - POST /api/auth/refresh     - Manually refresh authentication")
    print("  - POST /api/auth/update-key  - Update API key")


if __name__ == "__main__":
    main()