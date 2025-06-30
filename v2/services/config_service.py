"""
Configuration Service
Manages pluggable configurations for job stages with support for integrations
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


class ConfigurationPlugin(ABC):
    """Base class for all configuration plugins"""
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate the configuration. Returns (is_valid, error_message)"""
        pass
    
    @abstractmethod
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to the configuration"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for this plugin's configuration"""
        pass
    
    def encrypt_sensitive_data(self, config: Dict[str, Any], key: bytes) -> Dict[str, Any]:
        """Encrypt sensitive fields in the configuration"""
        f = Fernet(key)
        encrypted_config = config.copy()
        
        for field in self.get_sensitive_fields():
            if field in encrypted_config:
                value = json.dumps(encrypted_config[field])
                encrypted_config[field] = f.encrypt(value.encode()).decode()
        
        return encrypted_config
    
    def decrypt_sensitive_data(self, config: Dict[str, Any], key: bytes) -> Dict[str, Any]:
        """Decrypt sensitive fields in the configuration"""
        f = Fernet(key)
        decrypted_config = config.copy()
        
        for field in self.get_sensitive_fields():
            if field in decrypted_config:
                try:
                    encrypted_value = decrypted_config[field].encode()
                    decrypted_value = f.decrypt(encrypted_value).decode()
                    decrypted_config[field] = json.loads(decrypted_value)
                except Exception as e:
                    logger.error(f"Failed to decrypt field {field}: {e}")
        
        return decrypted_config
    
    def get_sensitive_fields(self) -> List[str]:
        """Return list of fields that contain sensitive data"""
        return []


class ConfigurationService:
    """Service for managing job and stage configurations"""
    
    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        self.configs_folder = os.path.join(data_folder, 'configurations')
        self.templates_folder = os.path.join(data_folder, 'config_templates')
        self.history_folder = os.path.join(data_folder, 'config_history')
        
        # Ensure directories exist
        for folder in [self.configs_folder, self.templates_folder, self.history_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # Initialize encryption key (in production, this should come from secure storage)
        self._init_encryption_key()
        
        # Plugin registry
        self.plugins: Dict[str, ConfigurationPlugin] = {}
        
        # Load default templates
        self._init_default_templates()
    
    def _init_encryption_key(self):
        """Initialize or load encryption key"""
        key_file = os.path.join(self.data_folder, '.config_key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
    
    def _init_default_templates(self):
        """Initialize default configuration templates"""
        default_templates = {
            'stage_project_setup': {
                'id': 'stage_project_setup',
                'name': 'Project Setup Configuration',
                'type': 'stage',
                'version': '1.0',
                'config': {
                    'timeout_minutes': 30,
                    'retry_on_failure': True,
                    'integrations': {
                        'jira': {
                            'enabled': True,
                            'create_epic': True,
                            'epic_name_template': '{job_name} - Migration Epic',
                            'story_points': 8,
                            'labels': ['migration', 'automated'],
                            'custom_fields': {}
                        },
                        'slack': {
                            'enabled': True,
                            'notify_on_start': True,
                            'notify_on_complete': True,
                            'message_template': 'project_kickoff'
                        },
                        'email': {
                            'enabled': True,
                            'send_kickoff_email': True,
                            'template': 'project_kickoff',
                            'recipient_groups': ['stakeholders', 'team']
                        }
                    },
                    'artifacts': {
                        'project_charter': True,
                        'wiki_page': True,
                        'team_roster': True
                    }
                }
            },
            'stage_code_migration': {
                'id': 'stage_code_migration',
                'name': 'Code Migration Configuration',
                'type': 'stage',
                'version': '1.0',
                'config': {
                    'timeout_minutes': 240,
                    'parallel_files': 5,
                    'batch_size': 10,
                    'integrations': {
                        'jira': {
                            'enabled': True,
                            'update_on_progress': True,
                            'progress_interval': 10,  # Update every 10%
                            'transition_on_start': 'In Progress',
                            'transition_on_complete': 'Code Review'
                        },
                        'slack': {
                            'enabled': True,
                            'progress_updates': True,
                            'error_notifications': True,
                            'channel_override': '#migration-progress'
                        }
                    },
                    'validation': {
                        'syntax_check': True,
                        'dependency_check': True,
                        'test_generation': True
                    }
                }
            },
            'global_integration_defaults': {
                'id': 'global_integration_defaults',
                'name': 'Default Integration Settings',
                'type': 'global',
                'version': '1.0',
                'config': {
                    'jira': {
                        'url': 'https://company.atlassian.net',
                        'project_key': 'MIGRATE',
                        'issue_type': 'Task',
                        'priority': 'Medium'
                    },
                    'slack': {
                        'default_channel': '#migrations',
                        'error_channel': '#migration-alerts',
                        'mention_on_error': '@migration-team'
                    },
                    'email': {
                        'from_address': 'migrations@company.com',
                        'smtp_host': 'smtp.company.com',
                        'smtp_port': 587,
                        'use_tls': True
                    }
                }
            }
        }
        
        # Save default templates if they don't exist
        for template_id, template in default_templates.items():
            template_file = os.path.join(self.templates_folder, f"{template_id}.json")
            if not os.path.exists(template_file):
                with open(template_file, 'w') as f:
                    json.dump(template, f, indent=2)
    
    def register_plugin(self, name: str, plugin: ConfigurationPlugin):
        """Register a configuration plugin"""
        self.plugins[name] = plugin
        logger.info(f"Registered configuration plugin: {name}")
    
    def get_job_config(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the configuration for a job"""
        config_file = os.path.join(self.configs_folder, f"job_{job_id}.json")
        if not os.path.exists(config_file):
            return None
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Decrypt sensitive data for all registered plugins
            if 'integrations' in config.get('global_config', {}):
                for integration, plugin in self.plugins.items():
                    if integration in config['global_config']['integrations']:
                        config['global_config']['integrations'][integration] = \
                            plugin.decrypt_sensitive_data(
                                config['global_config']['integrations'][integration],
                                self.encryption_key
                            )
            
            return config
        except Exception as e:
            logger.error(f"Error loading job config: {e}")
            return None
    
    def save_job_config(self, job_id: str, config: Dict[str, Any]) -> bool:
        """Save job configuration"""
        try:
            # Create a copy for encryption
            config_to_save = json.loads(json.dumps(config))
            
            # Encrypt sensitive data for all registered plugins
            if 'integrations' in config_to_save.get('global_config', {}):
                for integration, plugin in self.plugins.items():
                    if integration in config_to_save['global_config']['integrations']:
                        config_to_save['global_config']['integrations'][integration] = \
                            plugin.encrypt_sensitive_data(
                                config_to_save['global_config']['integrations'][integration],
                                self.encryption_key
                            )
            
            # Save to file
            config_file = os.path.join(self.configs_folder, f"job_{job_id}.json")
            with open(config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            
            # Save to history
            self._save_config_history(job_id, config_to_save, 'update')
            
            return True
        except Exception as e:
            logger.error(f"Error saving job config: {e}")
            return False
    
    def get_stage_config(self, job_id: str, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific stage"""
        job_config = self.get_job_config(job_id)
        if not job_config:
            return None
        
        return job_config.get('stage_configs', {}).get(stage_id)
    
    def update_stage_config(self, job_id: str, stage_id: str, stage_config: Dict[str, Any]) -> bool:
        """Update configuration for a specific stage"""
        job_config = self.get_job_config(job_id) or {
            'job_id': job_id,
            'global_config': {},
            'stage_configs': {}
        }
        
        job_config['stage_configs'][stage_id] = stage_config
        return self.save_job_config(job_id, job_config)
    
    def apply_template(self, template_id: str, overrides: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Apply a configuration template with optional overrides"""
        template_file = os.path.join(self.templates_folder, f"{template_id}.json")
        if not os.path.exists(template_file):
            return None
        
        try:
            with open(template_file, 'r') as f:
                template = json.load(f)
            
            config = template.get('config', {}).copy()
            
            # Apply overrides
            if overrides:
                self._deep_merge(config, overrides)
            
            return config
        except Exception as e:
            logger.error(f"Error applying template: {e}")
            return None
    
    def validate_config(self, config_type: str, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate a configuration using registered plugins"""
        if config_type in self.plugins:
            return self.plugins[config_type].validate_config(config)
        
        # Basic validation if no plugin
        if not config:
            return False, "Configuration cannot be empty"
        
        return True, None
    
    def get_templates(self, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all available templates, optionally filtered by type"""
        templates = []
        
        for filename in os.listdir(self.templates_folder):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.templates_folder, filename), 'r') as f:
                        template = json.load(f)
                    
                    if template_type is None or template.get('type') == template_type:
                        templates.append(template)
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {e}")
        
        return templates
    
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new configuration template"""
        template_id = template_data.get('id') or str(uuid.uuid4())
        template_data['id'] = template_id
        template_data['created_at'] = datetime.now().isoformat()
        
        template_file = os.path.join(self.templates_folder, f"{template_id}.json")
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        return template_id
    
    def _save_config_history(self, job_id: str, config: Dict[str, Any], action: str):
        """Save configuration change to history"""
        history_entry = {
            'job_id': job_id,
            'action': action,
            'config_snapshot': config,
            'timestamp': datetime.now().isoformat()
        }
        
        history_file = os.path.join(
            self.history_folder,
            f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(history_file, 'w') as f:
            json.dump(history_entry, f, indent=2)
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]):
        """Deep merge two dictionaries"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value