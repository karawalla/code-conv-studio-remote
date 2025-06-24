"""
Claude Code Authentication Manager
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


class ClaudeAuthManager:
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
        self.auth_helper_path = Path.home() / '.claude' / 'auth_helper.sh'
        
        # Create auth helper script
        self._create_auth_helper()
        
    def _create_auth_helper(self):
        """Create the authentication helper script"""
        self.auth_helper_path.parent.mkdir(parents=True, exist_ok=True)
        
        helper_content = f'''#!/bin/bash
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


class ClaudeSessionManager:
    """Manages Claude Code sessions with automatic reconnection"""
    
    def __init__(self, auth_manager: ClaudeAuthManager):
        self.auth_manager = auth_manager
        self.current_session = None
        self.session_start_time = None
        self.max_session_duration = timedelta(hours=2)  # Reconnect every 2 hours
        
    def start_claude_process(self, query: str, allowed_tools: str = "Read,Write,Edit,MultiEdit,Bash,Glob,Grep,LS") -> subprocess.Popen:
        """Start a Claude process with proper authentication"""
        # Check if we need to refresh session
        if self.session_start_time and \
           datetime.now() - self.session_start_time > self.max_session_duration:
            logger.info("Session duration exceeded, forcing refresh")
            self.auth_manager._refresh_auth()
            self.session_start_time = datetime.now()
        
        # Build command with authentication
        cmd = [
            "claude", "-p",
            query,
            "--allowedTools", allowed_tools,
            "--output-format", "stream-json",
            "--verbose"
        ] + self.auth_manager.get_auth_command_args()
        
        logger.info(f"Starting Claude process with authentication")
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd='/home/ubuntu/code-conv-studio',  # Set working directory
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


# Integration with existing Flask app
class EnhancedProcessManager:
    """Enhanced process manager with authentication support"""
    
    def __init__(self, auth_manager: ClaudeAuthManager):
        self.auth_manager = auth_manager
        self.session_manager = ClaudeSessionManager(auth_manager)
        
    def start_process(self, query: str, message_queue):
        """Start Claude process with authentication and retry logic"""
        max_retries = 3
        retry_count = 0
        process = None
        
        while retry_count < max_retries:
            try:
                process = self.session_manager.start_claude_process(query)
                
                # Process output
                logger.info("Starting to read process output")
                for line in process.stdout:
                    if not line.strip():
                        continue
                    
                    logger.debug(f"Raw output line: {line.strip()}")
                    
                    try:
                        message = json.loads(line.strip())
                        logger.debug(f"Parsed message: {message}")
                        
                        # Check for auth errors in messages
                        if message.get('type') == 'error':
                            error_content = message.get('content', '')
                            if self.session_manager.handle_auth_error(error_content):
                                # Retry with refreshed auth
                                retry_count += 1
                                logger.info(f"Retrying with refreshed authentication (attempt {retry_count})")
                                break
                        
                        # Process message through handlers like the original ProcessManager
                        self._handle_message(message, message_queue)
                        
                    except json.JSONDecodeError as e:
                        logger.debug(f"Failed to parse JSON: {e}, line: {line.strip()}")
                        # Put raw output as a message
                        message_queue.put({
                            'type': 'raw',
                            'content': line.strip()
                        })
                
                # Read any stderr
                stderr_output = process.stderr.read()
                if stderr_output:
                    logger.error(f"Process stderr: {stderr_output}")
                    
                    # Check for --api-key-helper compatibility issues
                    if "unknown option '--api-key-helper'" in stderr_output:
                        logger.warning("Claude CLI doesn't support --api-key-helper flag, falling back to standard execution")
                        raise Exception("Claude CLI compatibility issue: --api-key-helper not supported")
                
                # Wait for process with timeout to prevent zombies
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Process didn't exit cleanly within timeout, terminating")
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        logger.error("Process didn't terminate, killing forcefully")
                        process.kill()
                        process.wait()
                
                logger.info(f"Process completed with return code: {process.returncode}")
                
                # Check return code for auth issues
                if process.returncode in [401, 403]:
                    if self.session_manager.handle_auth_error(f"Process exited with code {process.returncode}"):
                        retry_count += 1
                        continue
                
                # Success - exit retry loop
                break
                
            except Exception as e:
                logger.error(f"Error in process execution: {e}")
                # Clean up process if it exists
                if process:
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                    except:
                        try:
                            process.kill()
                            process.wait()
                        except:
                            pass
                
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    raise
        
        # Signal completion
        message_queue.put(None)
    
    def _handle_message(self, message: Dict[str, Any], message_queue):
        """Handle different types of messages from Claude"""
        message_type = message.get("type")

        if message_type == "assistant":
            self._handle_assistant_message(message, message_queue)
        elif message_type == "system" and message.get("subtype") == "init":
            self._handle_init_message(message, message_queue)
        elif message_type == "result":
            self._handle_result_message(message, message_queue)

    def _handle_assistant_message(self, message: Dict[str, Any], message_queue):
        """Handle assistant messages"""
        for content in message.get("message", {}).get("content", []):
            if content.get("type") == "text":
                text = content.get("text", "").strip()
                if text:
                    # Filter and clean text
                    filtered_text = self._clean_text(text)
                    if filtered_text.strip():
                        message_queue.put({
                            'type': 'message',
                            'content': filtered_text
                        })

            elif content.get("type") == "tool_use":
                self._handle_tool_use(content, message_queue)

    def _handle_tool_use(self, content: Dict[str, Any], message_queue):
        """Handle tool use messages"""
        # Show tool use messages for better visibility
        tool_name = content.get('name', 'unknown')
        message_queue.put({
            'type': 'tool',
            'content': f"🔧 Using tool: {tool_name}"
        })

    def _handle_init_message(self, message: Dict[str, Any], message_queue):
        """Handle initialization messages"""
        session_id = message.get('session_id', '')
        message_queue.put({
            'type': 'init',
            'content': f"🚀 Starting session: {session_id[-8:] if session_id else 'unknown'}"
        })

    def _handle_result_message(self, message: Dict[str, Any], message_queue):
        """Handle result messages"""
        subtype = message.get("subtype")
        if subtype == "success":
            duration = message.get('duration_ms', 0) / 1000
            cost = message.get('total_cost_usd', 0)
            turns = message.get('num_turns', 0)

            message_queue.put({
                'type': 'success',
                'content': f"✅ Completed in {duration:.2f}s | 💰 Cost: ${cost:.4f} | 🔄 Turns: {turns}"
            })
        else:
            # Log the full error message for debugging
            logger.warning(f"Claude process result error - subtype: {subtype}, full message: {json.dumps(message, indent=2)}")
            
            # Extract any error details from the message
            error_detail = message.get('error', '')
            error_msg = message.get('message', '')
            
            # Provide user-friendly error messages based on error type
            error_messages = {
                'error_during_execution': '⚠️ Process completed successfully but reported a minor issue. Your files have been generated and should be valid. This is typically just a notification and doesn\'t affect the output.',
                'timeout': '⏱️ Process timed out. Consider breaking down your request into smaller tasks.',
                'resource_limit': '💾 Process exceeded resource limits. Try with a smaller input or simpler query.',
                'permission_denied': '🔒 Permission denied. Check file permissions and access rights.',
                'network_error': '🌐 Network connectivity issue. Please check your connection and try again.',
                'invalid_input': '📝 Invalid input provided. Please check your query and input files.',
                'tool_error': '🔧 Tool execution failed. Check input files and permissions.',
            }
            
            user_friendly_message = error_messages.get(subtype, f"❌ Process error: {subtype}")
            
            # Add any additional error details if available
            if error_detail or error_msg:
                additional_info = error_detail or error_msg
                logger.info(f"Additional error info: {additional_info}")
            
            message_queue.put({
                'type': 'error',
                'content': user_friendly_message
            })

    def _clean_text(self, text: str) -> str:
        """Clean and filter text output"""
        # Replace Claude mentions with Cognidev
        filtered_text = text.replace("Claude", "Cognidev").replace("claude", "Cognidev")
        return filtered_text


# Example usage in Flask app
def create_claude_auth_manager(api_key: Optional[str] = None) -> ClaudeAuthManager:
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
        raise ValueError("No Claude API key found. Please set CLAUDE_API_KEY environment variable.")
    
    auth_manager = ClaudeAuthManager(api_key)
    auth_manager.start_refresh_daemon()
    
    return auth_manager