"""
Claude Code Authentication Manager V2
Handles API key management and automatic refresh for persistent connections
"""

import os
import json
import time
import threading
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ClaudeAuthManagerV2:
    """Manages Claude Code authentication with automatic refresh"""
    
    def __init__(self, api_key: Optional[str] = None, refresh_interval: int = 240):
        """
        Initialize authentication manager
        
        Args:
            api_key: Claude API key (if None, will try to get from environment)
            refresh_interval: Seconds between refreshes (default 4 minutes, before 5-minute timeout)
        """
        self.api_key = api_key or os.environ.get('CLAUDE_API_KEY')
        self.refresh_interval = refresh_interval
        self.last_refresh = None
        self.refresh_thread = None
        self.running = False
        self.auth_helper_path = Path.home() / '.claude' / 'auth_helper_v2.sh'
        
        # Create auth helper script
        self._create_auth_helper()
        
    def _create_auth_helper(self):
        """Create the authentication helper script"""
        self.auth_helper_path.parent.mkdir(parents=True, exist_ok=True)
        
        helper_content = f'''#!/bin/bash
# Claude Code Authentication Helper V2
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
'''
        
        with open(self.auth_helper_path, 'w') as f:
            f.write(helper_content)
        
        # Make executable
        os.chmod(self.auth_helper_path, 0o755)
        logger.info(f"Created auth helper at {self.auth_helper_path}")
    
    def start_refresh_daemon(self):
        """Start the background thread that refreshes authentication"""
        if self.refresh_thread and self.refresh_thread.is_alive():
            logger.warning("Refresh daemon already running")
            return
        
        self.running = True
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
        logger.info("Started Claude authentication refresh daemon")
    
    def stop_refresh_daemon(self):
        """Stop the refresh daemon"""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=5)
        logger.info("Stopped Claude authentication refresh daemon")
    
    def _refresh_loop(self):
        """Background loop that refreshes authentication"""
        while self.running:
            try:
                self._refresh_auth()
                time.sleep(self.refresh_interval)
            except Exception as e:
                logger.error(f"Error in refresh loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retry on error
    
    def _refresh_auth(self):
        """Refresh the authentication by updating the helper script or environment"""
        try:
            # Update timestamp
            self.last_refresh = datetime.now()
            
            # If using environment variable, ensure it's still set
            if self.api_key:
                os.environ['CLAUDE_API_KEY'] = self.api_key
            
            # Touch the auth helper to update its timestamp
            self.auth_helper_path.touch()
            
            logger.debug(f"Refreshed authentication at {self.last_refresh}")
            
        except Exception as e:
            logger.error(f"Failed to refresh authentication: {e}")
            raise
    
    def get_auth_command_args(self) -> list:
        """Get command line arguments for Claude Code with authentication"""
        args = []
        
        # Only use auth helper if we're not using OAuth
        if self.api_key != "claude-oauth":
            # Use the auth helper script
            args.extend(['--api-key-helper', str(self.auth_helper_path)])
        
        return args
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        try:
            # Test with a simple Claude command that requires authentication
            cmd = ['claude', '-p', 'test', '--output-format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            # Check if we got a valid response (not an auth error)
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    # If we get a proper response structure, auth is working
                    return response.get('type') == 'result'
                except json.JSONDecodeError:
                    return False
            return False
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
    
    def update_api_key(self, new_api_key: str):
        """Update the API key and refresh authentication"""
        self.api_key = new_api_key
        os.environ['CLAUDE_API_KEY'] = new_api_key
        
        # Save to file for persistence
        api_key_file = Path.home() / '.claude' / 'api_key'
        api_key_file.parent.mkdir(parents=True, exist_ok=True)
        with open(api_key_file, 'w') as f:
            f.write(new_api_key)
        os.chmod(api_key_file, 0o600)  # Secure the file
        
        # Recreate helper script with new key
        self._create_auth_helper()
        self._refresh_auth()
        
        logger.info("Updated API key and refreshed authentication")


class ClaudeSessionManagerV2:
    """Manages Claude Code sessions with automatic reconnection"""
    
    def __init__(self, auth_manager: ClaudeAuthManagerV2):
        self.auth_manager = auth_manager
        self.current_session = None
        self.session_start_time = None
        self.max_session_duration = timedelta(hours=2)  # Reconnect every 2 hours
        
    def start_claude_process(self, prompt_file: str, working_dir: str, 
                           allowed_tools: str = "Read,Write,Edit,MultiEdit,Bash,Glob,Grep,LS") -> subprocess.Popen:
        """Start a Claude process with proper authentication"""
        # Check if we need to refresh session
        if self.session_start_time and \
           datetime.now() - self.session_start_time > self.max_session_duration:
            logger.info("Session duration exceeded, forcing refresh")
            self.auth_manager._refresh_auth()
            self.session_start_time = datetime.now()
        
        # Build command with authentication
        # Use -f flag to pass prompt file instead of -p for inline prompt
        cmd = [
            "claude", "-f",
            prompt_file,
            "--allowedTools", allowed_tools,
            "--output-format", "stream-json",
            "--verbose"
        ] + self.auth_manager.get_auth_command_args()
        
        logger.info(f"Starting Claude process with prompt file: {prompt_file}")
        logger.info(f"Working directory: {working_dir}")
        logger.debug(f"Full command: {' '.join(cmd)}")
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=working_dir,  # Set working directory
            env=os.environ.copy()  # Pass environment with API key
        )
        
        self.current_session = process
        if not self.session_start_time:
            self.session_start_time = datetime.now()
        
        return process
    
    def handle_auth_error(self, error_message: str) -> bool:
        """Handle authentication errors and attempt to recover"""
        auth_error_indicators = [
            '401', 'unauthorized', 'authentication', 'auth failed',
            'invalid api key', 'expired', 'forbidden'
        ]
        
        error_lower = error_message.lower()
        is_auth_error = any(indicator in error_lower for indicator in auth_error_indicators)
        
        if is_auth_error:
            logger.warning(f"Detected authentication error: {error_message}")
            
            # Force refresh
            self.auth_manager._refresh_auth()
            
            # Test authentication
            if self.auth_manager.test_authentication():
                logger.info("Authentication refresh successful")
                return True
            else:
                logger.error("Authentication refresh failed")
                return False
        
        return False


# Factory function
def create_claude_auth_manager_v2(api_key: Optional[str] = None) -> ClaudeAuthManagerV2:
    """Factory function to create and configure auth manager"""
    # Try to get API key from various sources
    if not api_key:
        # Try environment variable
        api_key = os.environ.get('CLAUDE_API_KEY')
        
        # Try file
        if not api_key:
            api_key_file = Path.home() / '.claude' / 'api_key'
            if api_key_file.exists():
                api_key = api_key_file.read_text().strip()
        
        # Try AWS Secrets Manager (example)
        if not api_key:
            try:
                import boto3
                client = boto3.client('secretsmanager')
                response = client.get_secret_value(SecretId='claude-api-key')
                api_key = response['SecretString']
            except:
                pass
    
    # If still no key, check if we're using OAuth (Claude CLI authentication)
    if not api_key:
        credentials_file = Path.home() / '.claude' / '.credentials.json'
        if credentials_file.exists():
            # We have OAuth credentials, use a placeholder
            api_key = "claude-oauth"
    
    if not api_key:
        logger.warning("No Claude API key found. Will attempt to use Claude CLI without explicit authentication.")
        # Don't raise error - let Claude CLI handle auth
    
    auth_manager = ClaudeAuthManagerV2(api_key)
    auth_manager.start_refresh_daemon()
    
    return auth_manager