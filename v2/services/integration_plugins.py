"""
Integration Plugins for Configuration Management
Provides plugins for Jira, Slack, Email and other integrations
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import re
from services.config_service import ConfigurationPlugin

logger = logging.getLogger(__name__)


class JiraConfigPlugin(ConfigurationPlugin):
    """Configuration plugin for Jira integration"""
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Jira configuration"""
        if not config.get('enabled', False):
            return True, None
        
        # Validate required fields
        required_fields = ['url', 'project_key']
        for field in required_fields:
            if not config.get(field):
                return False, f"Jira configuration missing required field: {field}"
        
        # Validate URL format
        try:
            parsed = urlparse(config['url'])
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid Jira URL format"
        except Exception:
            return False, "Invalid Jira URL format"
        
        # Validate project key format (usually uppercase letters and numbers)
        project_key = config.get('project_key', '')
        if not re.match(r'^[A-Z][A-Z0-9]*$', project_key):
            return False, "Invalid Jira project key format (should be uppercase letters and numbers)"
        
        # Validate auth if provided
        if 'auth' in config and not config['auth']:
            return False, "Jira auth token cannot be empty"
        
        return True, None
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to Jira configuration"""
        defaults = {
            'enabled': False,
            'issue_type': 'Task',
            'priority': 'Medium',
            'labels': [],
            'custom_fields': {},
            'transitions': {
                'start': 'In Progress',
                'complete': 'Done',
                'error': 'Blocked'
            },
            'update_interval_percent': 10,  # Update every 10% progress
            'create_subtasks': True,
            'link_issues': True
        }
        
        # Merge defaults with provided config
        merged = defaults.copy()
        merged.update(config)
        
        return merged
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for Jira configuration"""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "url": {"type": "string", "format": "uri"},
                "project_key": {"type": "string", "pattern": "^[A-Z][A-Z0-9]*$"},
                "auth": {"type": "string"},
                "issue_type": {"type": "string"},
                "priority": {"type": "string", "enum": ["Highest", "High", "Medium", "Low", "Lowest"]},
                "labels": {"type": "array", "items": {"type": "string"}},
                "custom_fields": {"type": "object"},
                "transitions": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string"},
                        "complete": {"type": "string"},
                        "error": {"type": "string"}
                    }
                }
            },
            "required": ["url", "project_key"] if config.get('enabled') else []
        }
    
    def get_sensitive_fields(self) -> List[str]:
        """Return list of sensitive fields"""
        return ['auth']
    
    def create_issue(self, config: Dict[str, Any], issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Jira issue (mock implementation)"""
        # In a real implementation, this would use the Jira REST API
        logger.info(f"Creating Jira issue in project {config['project_key']}: {issue_data}")
        return {
            'key': f"{config['project_key']}-{1234}",
            'id': '12345',
            'self': f"{config['url']}/rest/api/2/issue/12345"
        }
    
    def update_issue(self, config: Dict[str, Any], issue_key: str, update_data: Dict[str, Any]) -> bool:
        """Update a Jira issue (mock implementation)"""
        logger.info(f"Updating Jira issue {issue_key}: {update_data}")
        return True
    
    def transition_issue(self, config: Dict[str, Any], issue_key: str, transition: str) -> bool:
        """Transition a Jira issue (mock implementation)"""
        logger.info(f"Transitioning Jira issue {issue_key} to {transition}")
        return True


class SlackConfigPlugin(ConfigurationPlugin):
    """Configuration plugin for Slack integration"""
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Slack configuration"""
        if not config.get('enabled', False):
            return True, None
        
        # Validate webhook URL if provided
        if 'webhook_url' in config:
            webhook_url = config['webhook_url']
            if webhook_url and not webhook_url.startswith('https://hooks.slack.com/'):
                return False, "Invalid Slack webhook URL format"
        
        # Validate channels format
        if 'channels' in config:
            channels = config['channels']
            if not isinstance(channels, dict):
                return False, "Slack channels must be a dictionary"
            
            for channel_name in channels.values():
                if not isinstance(channel_name, str) or not channel_name.startswith('#'):
                    return False, f"Invalid Slack channel format: {channel_name} (should start with #)"
        
        return True, None
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to Slack configuration"""
        defaults = {
            'enabled': False,
            'channels': {
                'notifications': '#general',
                'alerts': '#alerts',
                'progress': '#progress'
            },
            'notify_on_start': True,
            'notify_on_complete': True,
            'notify_on_error': True,
            'progress_updates': False,
            'mention_on_error': '',
            'message_format': 'rich',  # 'simple' or 'rich'
            'include_details': True
        }
        
        merged = defaults.copy()
        merged.update(config)
        
        return merged
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for Slack configuration"""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "webhook_url": {"type": "string"},
                "channels": {
                    "type": "object",
                    "properties": {
                        "notifications": {"type": "string", "pattern": "^#.*"},
                        "alerts": {"type": "string", "pattern": "^#.*"},
                        "progress": {"type": "string", "pattern": "^#.*"}
                    }
                },
                "notify_on_start": {"type": "boolean"},
                "notify_on_complete": {"type": "boolean"},
                "notify_on_error": {"type": "boolean"},
                "mention_on_error": {"type": "string"},
                "message_format": {"type": "string", "enum": ["simple", "rich"]}
            }
        }
    
    def get_sensitive_fields(self) -> List[str]:
        """Return list of sensitive fields"""
        return ['webhook_url']
    
    def send_message(self, config: Dict[str, Any], channel: str, message: str) -> bool:
        """Send a simple message to Slack (mock implementation)"""
        logger.info(f"Sending Slack message to {channel}: {message}")
        return True
    
    def send_rich_message(self, config: Dict[str, Any], channel: str, blocks: List[Dict]) -> bool:
        """Send a rich formatted message to Slack (mock implementation)"""
        logger.info(f"Sending rich Slack message to {channel}")
        return True


class EmailConfigPlugin(ConfigurationPlugin):
    """Configuration plugin for Email integration"""
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Email configuration"""
        if not config.get('enabled', False):
            return True, None
        
        # Validate SMTP configuration
        smtp_config = config.get('smtp_config', {})
        required_smtp = ['host', 'port']
        for field in required_smtp:
            if field not in smtp_config:
                return False, f"Email SMTP configuration missing: {field}"
        
        # Validate email addresses
        from_address = config.get('from_address', '')
        if not self._is_valid_email(from_address):
            return False, f"Invalid from email address: {from_address}"
        
        # Validate recipient groups
        recipients = config.get('recipients', {})
        if not isinstance(recipients, dict):
            return False, "Email recipients must be a dictionary of groups"
        
        for group, addresses in recipients.items():
            if not isinstance(addresses, list):
                return False, f"Recipient group {group} must be a list"
            
            for email in addresses:
                if not self._is_valid_email(email):
                    return False, f"Invalid email address in group {group}: {email}"
        
        return True, None
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to Email configuration"""
        defaults = {
            'enabled': False,
            'from_address': 'noreply@example.com',
            'from_name': 'Migration System',
            'smtp_config': {
                'host': 'localhost',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
                'timeout': 30
            },
            'recipients': {
                'stakeholders': [],
                'team': [],
                'admins': []
            },
            'templates': {
                'project_kickoff': 'project_kickoff.html',
                'stage_complete': 'stage_complete.html',
                'job_complete': 'job_complete.html',
                'error_alert': 'error_alert.html'
            },
            'send_attachments': True,
            'max_attachment_size_mb': 10
        }
        
        merged = defaults.copy()
        # Deep merge for nested dictionaries
        for key in ['smtp_config', 'recipients', 'templates']:
            if key in config:
                merged[key] = defaults.get(key, {}).copy()
                merged[key].update(config[key])
        
        # Update other fields
        for key, value in config.items():
            if key not in ['smtp_config', 'recipients', 'templates']:
                merged[key] = value
        
        return merged
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for Email configuration"""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "from_address": {"type": "string", "format": "email"},
                "from_name": {"type": "string"},
                "smtp_config": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                        "use_tls": {"type": "boolean"},
                        "use_ssl": {"type": "boolean"},
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    },
                    "required": ["host", "port"]
                },
                "recipients": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string", "format": "email"}
                    }
                },
                "templates": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            }
        }
    
    def get_sensitive_fields(self) -> List[str]:
        """Return list of sensitive fields"""
        return ['smtp_config']  # The entire SMTP config contains sensitive data
    
    def send_email(self, config: Dict[str, Any], to_addresses: List[str], 
                   subject: str, body: str, template: Optional[str] = None) -> bool:
        """Send an email (mock implementation)"""
        logger.info(f"Sending email to {to_addresses} with subject: {subject}")
        return True
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class TeamsConfigPlugin(ConfigurationPlugin):
    """Configuration plugin for Microsoft Teams integration"""
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Teams configuration"""
        if not config.get('enabled', False):
            return True, None
        
        # Validate webhook URL
        webhook_url = config.get('webhook_url', '')
        if not webhook_url:
            return False, "Teams webhook URL is required when enabled"
        
        if not webhook_url.startswith('https://'):
            return False, "Teams webhook URL must use HTTPS"
        
        return True, None
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to Teams configuration"""
        defaults = {
            'enabled': False,
            'webhook_url': '',
            'notify_on_start': True,
            'notify_on_complete': True,
            'notify_on_error': True,
            'card_color': {
                'info': '0078D4',
                'success': '00CC00',
                'warning': 'FFB900',
                'error': 'CC0000'
            },
            'include_actions': True,
            'mention_on_error': ''
        }
        
        merged = defaults.copy()
        merged.update(config)
        
        return merged
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for Teams configuration"""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "webhook_url": {"type": "string", "format": "uri"},
                "notify_on_start": {"type": "boolean"},
                "notify_on_complete": {"type": "boolean"},
                "notify_on_error": {"type": "boolean"},
                "mention_on_error": {"type": "string"}
            }
        }
    
    def get_sensitive_fields(self) -> List[str]:
        """Return list of sensitive fields"""
        return ['webhook_url']


# Factory function to create all default plugins
def create_default_plugins() -> Dict[str, ConfigurationPlugin]:
    """Create and return all default integration plugins"""
    return {
        'jira': JiraConfigPlugin(),
        'slack': SlackConfigPlugin(),
        'email': EmailConfigPlugin(),
        'teams': TeamsConfigPlugin()
    }