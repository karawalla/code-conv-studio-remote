"""
Credentials Service
Manages all authentication credentials in a centralized way
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class CredentialsService:
    """Service for managing authentication credentials"""
    
    CREDENTIAL_TYPES = {
        # Issue Tracking & Project Management
        'jira': {
            'name': 'Jira',
            'icon': '🎫',
            'category': 'project_management',
            'fields': [
                {'key': 'url', 'label': 'Jira URL', 'type': 'url', 'placeholder': 'https://company.atlassian.net'},
                {'key': 'project_key', 'label': 'Project Key', 'type': 'text', 'placeholder': 'MIGRATE'},
                {'key': 'email', 'label': 'Email', 'type': 'email', 'placeholder': 'user@company.com'},
                {'key': 'api_token', 'label': 'API Token', 'type': 'password', 'placeholder': 'Your Jira API token'}
            ]
        },
        'jira_local': {
            'name': 'Jira Server',
            'icon': '🏢',
            'category': 'project_management',
            'fields': [
                {'key': 'url', 'label': 'Jira Server URL', 'type': 'url', 'placeholder': 'https://jira.company.local'},
                {'key': 'project_key', 'label': 'Project Key', 'type': 'text', 'placeholder': 'PROJ'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'jira_user'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Your Jira password'}
            ]
        },
        
        # Version Control
        'github': {
            'name': 'GitHub',
            'icon': '🐙',
            'category': 'version_control',
            'fields': [
                {'key': 'token', 'label': 'Personal Access Token', 'type': 'password', 'placeholder': 'ghp_xxxxxxxxxxxx'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'github-username'}
            ]
        },
        'gitlab': {
            'name': 'GitLab',
            'icon': '🦊',
            'category': 'version_control',
            'fields': [
                {'key': 'url', 'label': 'GitLab URL', 'type': 'url', 'placeholder': 'https://gitlab.com or self-hosted'},
                {'key': 'token', 'label': 'Personal Access Token', 'type': 'password', 'placeholder': 'glpat-xxxxxxxxxxxx'}
            ]
        },
        'bitbucket': {
            'name': 'Bitbucket',
            'icon': '🪣',
            'category': 'version_control',
            'fields': [
                {'key': 'workspace', 'label': 'Workspace', 'type': 'text', 'placeholder': 'your-workspace'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'bitbucket-username'},
                {'key': 'app_password', 'label': 'App Password', 'type': 'password', 'placeholder': 'Your app password'}
            ]
        },
        
        # Communication
        'slack': {
            'name': 'Slack',
            'icon': '💬',
            'category': 'communication',
            'fields': [
                {'key': 'webhook_url', 'label': 'Webhook URL', 'type': 'password', 'placeholder': 'https://hooks.slack.com/...'},
                {'key': 'default_channel', 'label': 'Default Channel', 'type': 'text', 'placeholder': '#general'}
            ]
        },
        'teams': {
            'name': 'Microsoft Teams',
            'icon': '👥',
            'category': 'communication',
            'fields': [
                {'key': 'webhook_url', 'label': 'Webhook URL', 'type': 'password', 'placeholder': 'https://outlook.office.com/webhook/...'}
            ]
        },
        'email': {
            'name': 'Email/SMTP',
            'icon': '📧',
            'category': 'communication',
            'fields': [
                {'key': 'smtp_host', 'label': 'SMTP Host', 'type': 'text', 'placeholder': 'smtp.gmail.com'},
                {'key': 'smtp_port', 'label': 'SMTP Port', 'type': 'number', 'placeholder': '587'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'user@company.com'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'SMTP password'},
                {'key': 'from_address', 'label': 'From Address', 'type': 'email', 'placeholder': 'noreply@company.com'}
            ]
        },
        
        # Databases
        'postgresql': {
            'name': 'PostgreSQL',
            'icon': '🐘',
            'category': 'database',
            'fields': [
                {'key': 'host', 'label': 'Host', 'type': 'text', 'placeholder': 'localhost'},
                {'key': 'port', 'label': 'Port', 'type': 'number', 'placeholder': '5432'},
                {'key': 'database', 'label': 'Database Name', 'type': 'text', 'placeholder': 'mydb'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'postgres'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Database password'},
                {'key': 'ssl_mode', 'label': 'SSL Mode', 'type': 'text', 'placeholder': 'require'}
            ]
        },
        'mysql': {
            'name': 'MySQL',
            'icon': '🐬',
            'category': 'database',
            'fields': [
                {'key': 'host', 'label': 'Host', 'type': 'text', 'placeholder': 'localhost'},
                {'key': 'port', 'label': 'Port', 'type': 'number', 'placeholder': '3306'},
                {'key': 'database', 'label': 'Database Name', 'type': 'text', 'placeholder': 'mydb'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'root'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Database password'}
            ]
        },
        'mongodb': {
            'name': 'MongoDB',
            'icon': '🍃',
            'category': 'database',
            'fields': [
                {'key': 'connection_string', 'label': 'Connection String', 'type': 'password', 'placeholder': 'mongodb://localhost:27017'},
                {'key': 'database', 'label': 'Database Name', 'type': 'text', 'placeholder': 'mydb'}
            ]
        },
        'redis': {
            'name': 'Redis',
            'icon': '🔴',
            'category': 'database',
            'fields': [
                {'key': 'host', 'label': 'Host', 'type': 'text', 'placeholder': 'localhost'},
                {'key': 'port', 'label': 'Port', 'type': 'number', 'placeholder': '6379'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Redis password (optional)'},
                {'key': 'database', 'label': 'Database Number', 'type': 'number', 'placeholder': '0'}
            ]
        },
        'oracle': {
            'name': 'Oracle Database',
            'icon': '🔶',
            'category': 'database',
            'fields': [
                {'key': 'host', 'label': 'Host', 'type': 'text', 'placeholder': 'localhost'},
                {'key': 'port', 'label': 'Port', 'type': 'number', 'placeholder': '1521'},
                {'key': 'service_name', 'label': 'Service Name', 'type': 'text', 'placeholder': 'ORCL'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'system'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Database password'}
            ]
        },
        'sqlserver': {
            'name': 'SQL Server',
            'icon': '🟦',
            'category': 'database',
            'fields': [
                {'key': 'server', 'label': 'Server', 'type': 'text', 'placeholder': 'localhost\\SQLEXPRESS'},
                {'key': 'database', 'label': 'Database', 'type': 'text', 'placeholder': 'mydb'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'sa'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Database password'},
                {'key': 'encrypt', 'label': 'Encrypt Connection', 'type': 'text', 'placeholder': 'true/false'}
            ]
        },
        
        # Cloud Services - AWS
        'aws': {
            'name': 'AWS',
            'icon': '☁️',
            'category': 'cloud',
            'fields': [
                {'key': 'access_key_id', 'label': 'Access Key ID', 'type': 'text', 'placeholder': 'AKIAIOSFODNN7EXAMPLE'},
                {'key': 'secret_access_key', 'label': 'Secret Access Key', 'type': 'password', 'placeholder': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'},
                {'key': 'region', 'label': 'Region', 'type': 'text', 'placeholder': 'us-east-1'},
                {'key': 'session_token', 'label': 'Session Token (Optional)', 'type': 'password', 'placeholder': 'Temporary session token'}
            ]
        },
        's3': {
            'name': 'AWS S3',
            'icon': '🪣',
            'category': 'cloud',
            'fields': [
                {'key': 'bucket_name', 'label': 'Bucket Name', 'type': 'text', 'placeholder': 'my-bucket'},
                {'key': 'access_key_id', 'label': 'Access Key ID', 'type': 'text', 'placeholder': 'AKIAIOSFODNN7EXAMPLE'},
                {'key': 'secret_access_key', 'label': 'Secret Access Key', 'type': 'password', 'placeholder': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'},
                {'key': 'region', 'label': 'Region', 'type': 'text', 'placeholder': 'us-east-1'}
            ]
        },
        
        # Cloud Services - Azure
        'azure': {
            'name': 'Azure',
            'icon': '☁️',
            'category': 'cloud',
            'fields': [
                {'key': 'tenant_id', 'label': 'Tenant ID', 'type': 'text', 'placeholder': 'your-tenant-id'},
                {'key': 'client_id', 'label': 'Client ID', 'type': 'text', 'placeholder': 'your-client-id'},
                {'key': 'client_secret', 'label': 'Client Secret', 'type': 'password', 'placeholder': 'your-client-secret'},
                {'key': 'subscription_id', 'label': 'Subscription ID', 'type': 'text', 'placeholder': 'your-subscription-id'}
            ]
        },
        'azure_storage': {
            'name': 'Azure Storage',
            'icon': '📦',
            'category': 'cloud',
            'fields': [
                {'key': 'account_name', 'label': 'Storage Account Name', 'type': 'text', 'placeholder': 'mystorageaccount'},
                {'key': 'account_key', 'label': 'Account Key', 'type': 'password', 'placeholder': 'your-account-key'},
                {'key': 'container_name', 'label': 'Container Name', 'type': 'text', 'placeholder': 'mycontainer'}
            ]
        },
        
        # Cloud Services - Google Cloud
        'gcp': {
            'name': 'Google Cloud',
            'icon': '☁️',
            'category': 'cloud',
            'fields': [
                {'key': 'project_id', 'label': 'Project ID', 'type': 'text', 'placeholder': 'my-project-123'},
                {'key': 'service_account_json', 'label': 'Service Account JSON', 'type': 'password', 'placeholder': 'Paste entire JSON key'}
            ]
        },
        'gcs': {
            'name': 'Google Cloud Storage',
            'icon': '🪣',
            'category': 'cloud',
            'fields': [
                {'key': 'bucket_name', 'label': 'Bucket Name', 'type': 'text', 'placeholder': 'my-bucket'},
                {'key': 'project_id', 'label': 'Project ID', 'type': 'text', 'placeholder': 'my-project-123'},
                {'key': 'service_account_json', 'label': 'Service Account JSON', 'type': 'password', 'placeholder': 'Paste entire JSON key'}
            ]
        },
        
        # APIs
        'rest_api': {
            'name': 'REST API',
            'icon': '🔌',
            'category': 'api',
            'fields': [
                {'key': 'base_url', 'label': 'Base URL', 'type': 'url', 'placeholder': 'https://api.example.com/v1'},
                {'key': 'auth_type', 'label': 'Auth Type', 'type': 'text', 'placeholder': 'bearer/basic/api_key'},
                {'key': 'auth_header', 'label': 'Auth Header Name', 'type': 'text', 'placeholder': 'Authorization or X-API-Key'},
                {'key': 'auth_value', 'label': 'Auth Value', 'type': 'password', 'placeholder': 'Bearer token or API key'},
                {'key': 'additional_headers', 'label': 'Additional Headers (JSON)', 'type': 'text', 'placeholder': '{"Content-Type": "application/json"}'}
            ]
        },
        'graphql': {
            'name': 'GraphQL API',
            'icon': '🔸',
            'category': 'api',
            'fields': [
                {'key': 'endpoint', 'label': 'GraphQL Endpoint', 'type': 'url', 'placeholder': 'https://api.example.com/graphql'},
                {'key': 'auth_header', 'label': 'Auth Header Name', 'type': 'text', 'placeholder': 'Authorization'},
                {'key': 'auth_token', 'label': 'Auth Token', 'type': 'password', 'placeholder': 'Bearer token'}
            ]
        },
        'oauth2': {
            'name': 'OAuth 2.0',
            'icon': '🔐',
            'category': 'api',
            'fields': [
                {'key': 'client_id', 'label': 'Client ID', 'type': 'text', 'placeholder': 'your-client-id'},
                {'key': 'client_secret', 'label': 'Client Secret', 'type': 'password', 'placeholder': 'your-client-secret'},
                {'key': 'token_url', 'label': 'Token URL', 'type': 'url', 'placeholder': 'https://oauth.example.com/token'},
                {'key': 'auth_url', 'label': 'Authorization URL', 'type': 'url', 'placeholder': 'https://oauth.example.com/authorize'},
                {'key': 'redirect_uri', 'label': 'Redirect URI', 'type': 'url', 'placeholder': 'https://your-app.com/callback'},
                {'key': 'scope', 'label': 'Scopes', 'type': 'text', 'placeholder': 'read write'}
            ]
        },
        
        # Other Services
        'docker': {
            'name': 'Docker Registry',
            'icon': '🐳',
            'category': 'other',
            'fields': [
                {'key': 'registry_url', 'label': 'Registry URL', 'type': 'url', 'placeholder': 'https://registry.hub.docker.com'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'docker-username'},
                {'key': 'password', 'label': 'Password', 'type': 'password', 'placeholder': 'Docker password'}
            ]
        },
        'kubernetes': {
            'name': 'Kubernetes',
            'icon': '☸️',
            'category': 'other',
            'fields': [
                {'key': 'cluster_url', 'label': 'Cluster URL', 'type': 'url', 'placeholder': 'https://k8s.example.com'},
                {'key': 'token', 'label': 'Service Account Token', 'type': 'password', 'placeholder': 'Bearer token'},
                {'key': 'namespace', 'label': 'Default Namespace', 'type': 'text', 'placeholder': 'default'},
                {'key': 'ca_certificate', 'label': 'CA Certificate (Optional)', 'type': 'password', 'placeholder': 'PEM-encoded certificate'}
            ]
        },
        'jenkins': {
            'name': 'Jenkins',
            'icon': '🔨',
            'category': 'other',
            'fields': [
                {'key': 'url', 'label': 'Jenkins URL', 'type': 'url', 'placeholder': 'https://jenkins.example.com'},
                {'key': 'username', 'label': 'Username', 'type': 'text', 'placeholder': 'jenkins-user'},
                {'key': 'api_token', 'label': 'API Token', 'type': 'password', 'placeholder': 'Jenkins API token'}
            ]
        },
        
        # Custom Authentication
        'custom': {
            'name': 'Custom',
            'icon': '🔧',
            'category': 'custom',
            'fields': [
                {'key': 'name', 'label': 'Service Name', 'type': 'text', 'placeholder': 'My Custom Service'},
                {'key': 'endpoint', 'label': 'Endpoint/URL', 'type': 'url', 'placeholder': 'https://api.custom.com'},
                {'key': 'auth_method', 'label': 'Auth Method', 'type': 'text', 'placeholder': 'Basic/Bearer/API Key/Custom'},
                {'key': 'credentials', 'label': 'Credentials (JSON)', 'type': 'password', 'placeholder': '{"key": "value", "token": "xxx"}'},
                {'key': 'notes', 'label': 'Notes', 'type': 'text', 'placeholder': 'Additional configuration notes'}
            ]
        }
    }
    
    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        self.credentials_file = os.path.join(data_folder, 'credentials.json')
        self._init_encryption_key()
        self._ensure_file_exists()
    
    def _init_encryption_key(self):
        """Initialize or load encryption key"""
        key_file = os.path.join(self.data_folder, '.credentials_key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
        self.cipher = Fernet(self.encryption_key)
    
    def _ensure_file_exists(self):
        """Ensure credentials file exists"""
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'w') as f:
                json.dump({'credentials': {}}, f, indent=2)
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load all credentials from file"""
        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return {'credentials': {}}
    
    def _save_credentials(self, data: Dict[str, Any]) -> bool:
        """Save credentials to file"""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return False
    
    def _encrypt_field(self, value: str) -> str:
        """Encrypt a sensitive field"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt_field(self, value: str) -> str:
        """Decrypt a sensitive field"""
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if decryption fails
    
    def get_all_credentials(self) -> List[Dict[str, Any]]:
        """Get all credentials (without sensitive data)"""
        data = self._load_credentials()
        credentials = []
        
        for cred_id, cred in data.get('credentials', {}).items():
            # Create safe version without sensitive fields
            safe_cred = {
                'id': cred_id,
                'name': cred['name'],
                'type': cred['type'],
                'icon': self.CREDENTIAL_TYPES.get(cred['type'], {}).get('icon', '🔑'),
                'created_at': cred.get('created_at'),
                'updated_at': cred.get('updated_at'),
                'last_tested': cred.get('last_tested'),
                'status': cred.get('status', 'unchecked')
            }
            credentials.append(safe_cred)
        
        return credentials
    
    def get_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific credential with decrypted data"""
        data = self._load_credentials()
        cred = data.get('credentials', {}).get(credential_id)
        
        if not cred:
            return None
        
        # Decrypt sensitive fields
        cred_type = cred['type']
        if cred_type in self.CREDENTIAL_TYPES:
            for field in self.CREDENTIAL_TYPES[cred_type]['fields']:
                if field['type'] == 'password' and field['key'] in cred['data']:
                    cred['data'][field['key']] = self._decrypt_field(cred['data'][field['key']])
        
        return cred
    
    def create_credential(self, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new credential"""
        if not credential_data.get('name'):
            raise ValueError("Credential name is required")
        
        if not credential_data.get('type'):
            raise ValueError("Credential type is required")
        
        if credential_data['type'] not in self.CREDENTIAL_TYPES:
            raise ValueError(f"Unknown credential type: {credential_data['type']}")
        
        data = self._load_credentials()
        
        # Generate ID
        cred_id = str(uuid.uuid4())
        
        # Encrypt sensitive fields
        cred_type = credential_data['type']
        encrypted_data = credential_data.get('data', {}).copy()
        
        for field in self.CREDENTIAL_TYPES[cred_type]['fields']:
            if field['type'] == 'password' and field['key'] in encrypted_data:
                encrypted_data[field['key']] = self._encrypt_field(encrypted_data[field['key']])
        
        # Create credential
        credential = {
            'id': cred_id,
            'name': credential_data['name'],
            'type': cred_type,
            'data': encrypted_data,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'unchecked'
        }
        
        data['credentials'][cred_id] = credential
        
        if self._save_credentials(data):
            # Return safe version
            return {
                'id': cred_id,
                'name': credential['name'],
                'type': credential['type'],
                'icon': self.CREDENTIAL_TYPES[cred_type]['icon'],
                'created_at': credential['created_at']
            }
        else:
            raise RuntimeError("Failed to save credential")
    
    def update_credential(self, credential_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing credential"""
        data = self._load_credentials()
        
        if credential_id not in data.get('credentials', {}):
            return False
        
        credential = data['credentials'][credential_id]
        
        # Update name if provided
        if 'name' in updates:
            credential['name'] = updates['name']
        
        # Update data if provided
        if 'data' in updates:
            cred_type = credential['type']
            encrypted_data = updates['data'].copy()
            
            # Encrypt sensitive fields
            for field in self.CREDENTIAL_TYPES[cred_type]['fields']:
                if field['type'] == 'password' and field['key'] in encrypted_data:
                    encrypted_data[field['key']] = self._encrypt_field(encrypted_data[field['key']])
            
            credential['data'] = encrypted_data
        
        credential['updated_at'] = datetime.now().isoformat()
        
        return self._save_credentials(data)
    
    def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential"""
        data = self._load_credentials()
        
        if credential_id in data.get('credentials', {}):
            del data['credentials'][credential_id]
            return self._save_credentials(data)
        
        return False
    
    def test_credential(self, credential_id: str) -> Dict[str, Any]:
        """Test a credential connection"""
        credential = self.get_credential(credential_id)
        if not credential:
            return {'success': False, 'message': 'Credential not found'}
        
        # Update last tested timestamp
        data = self._load_credentials()
        if credential_id in data['credentials']:
            data['credentials'][credential_id]['last_tested'] = datetime.now().isoformat()
            self._save_credentials(data)
        
        # Mock test results for now
        # In a real implementation, this would actually test the connection
        return {
            'success': True,
            'message': f"Successfully connected to {credential['type']}",
            'details': {
                'response_time': '120ms',
                'status': 'active'
            }
        }
    
    def search_credentials(self, query: str) -> List[Dict[str, Any]]:
        """Search credentials by name or type"""
        all_creds = self.get_all_credentials()
        query_lower = query.lower()
        
        return [
            cred for cred in all_creds
            if query_lower in cred['name'].lower() or query_lower in cred['type'].lower()
        ]
    
    def get_credential_types(self) -> Dict[str, Any]:
        """Get all available credential types with their schemas"""
        return self.CREDENTIAL_TYPES