"""
Agents Service
Manages AI agents with specific capabilities for code conversion and project management
"""

import os
import json
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AgentsService:
    """Service for managing AI agents and their capabilities"""
    
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.agents_file = os.path.join(data_folder, 'agents_metadata.json')
        self._ensure_file_exists()
        self._initialize_default_agents()
    
    def _ensure_file_exists(self):
        """Ensure agents metadata file exists"""
        if not os.path.exists(self.agents_file):
            with open(self.agents_file, 'w') as f:
                json.dump({'agents': {}}, f, indent=2)
    
    def _load_agents(self):
        """Load agents from metadata file"""
        try:
            with open(self.agents_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading agents: {e}")
            return {'agents': {}}
    
    def _save_agents(self, data):
        """Save agents to metadata file"""
        try:
            with open(self.agents_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving agents: {e}")
            return False
    
    def _initialize_default_agents(self):
        """Initialize default agents if none exist"""
        data = self._load_agents()
        if not data.get('agents'):
            # Define common capabilities
            common_capabilities = [
                {'id': 'file_create', 'name': 'Create File', 'description': 'Create new files in the project', 'icon': '📄'},
                {'id': 'file_read', 'name': 'Read File', 'description': 'Read and analyze file contents', 'icon': '📖'},
                {'id': 'file_delete', 'name': 'Delete File', 'description': 'Remove files from the project', 'icon': '🗑️'},
                {'id': 'search', 'name': 'Search', 'description': 'Search through codebase and documentation', 'icon': '🔍'},
                {'id': 'send_email', 'name': 'Send Email', 'description': 'Send email notifications', 'icon': '📧'},
                {'id': 'send_notification', 'name': 'Send Notification', 'description': 'Send system notifications', 'icon': '🔔'}
            ]
            
            # Define default agents
            default_agents = [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Code Architect',
                    'role': 'architect',
                    'description': 'Designs system architecture and creates technical plans',
                    'avatar': '🏗️',
                    'status': 'active',
                    'capabilities': common_capabilities + [
                        {'id': 'plan', 'name': 'Plan Architecture', 'description': 'Create detailed system architecture plans', 'icon': '📋'},
                        {'id': 'analyze', 'name': 'Analyze System', 'description': 'Analyze existing system architecture and patterns', 'icon': '🔬'},
                        {'id': 'document_architecture', 'name': 'Document Architecture', 'description': 'Create architecture documentation and diagrams', 'icon': '📐'}
                    ]
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Code Engineer',
                    'role': 'engineer',
                    'description': 'Implements code migrations and transformations',
                    'avatar': '👨‍💻',
                    'status': 'active',
                    'capabilities': common_capabilities + [
                        {'id': 'migrate', 'name': 'Migrate Code', 'description': 'Transform code from one framework to another', 'icon': '🔄'},
                        {'id': 'generate', 'name': 'Generate Code', 'description': 'Generate new code based on specifications', 'icon': '⚡'},
                        {'id': 'validate', 'name': 'Validate Code', 'description': 'Validate code quality and correctness', 'icon': '✅'},
                        {'id': 'refactor', 'name': 'Refactor Code', 'description': 'Improve code structure and quality', 'icon': '🔧'},
                        {'id': 'debug_fix', 'name': 'Debug & Fix', 'description': 'Debug issues and fix code problems', 'icon': '🐛'}
                    ]
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Technical Writer',
                    'role': 'writer',
                    'description': 'Creates documentation and guides',
                    'avatar': '✍️',
                    'status': 'active',
                    'capabilities': common_capabilities + [
                        {'id': 'document_code', 'name': 'Document Code', 'description': 'Create inline code documentation and comments', 'icon': '📝'},
                        {'id': 'write_help', 'name': 'Write Help Docs', 'description': 'Create user help documentation', 'icon': '❓'},
                        {'id': 'create_guides', 'name': 'Create How-To Guides', 'description': 'Write step-by-step tutorials and guides', 'icon': '📚'},
                        {'id': 'api_docs', 'name': 'API Documentation', 'description': 'Generate API reference documentation', 'icon': '📡'}
                    ]
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Project Manager',
                    'role': 'manager',
                    'description': 'Manages projects and coordinates team activities',
                    'avatar': '📊',
                    'status': 'active',
                    'capabilities': common_capabilities + [
                        {'id': 'project_kickoff', 'name': 'Project Kickoff', 'description': 'Initialize new projects with proper structure', 'icon': '🚀'},
                        {'id': 'project_tracking', 'name': 'Track Progress', 'description': 'Monitor project progress and milestones', 'icon': '📈'},
                        {'id': 'jira_create', 'name': 'Create Jira Issues', 'description': 'Create and manage Jira tickets', 'icon': '🎫'},
                        {'id': 'jira_update', 'name': 'Update Jira', 'description': 'Update Jira ticket status and comments', 'icon': '🔄'},
                        {'id': 'resource_planning', 'name': 'Resource Planning', 'description': 'Plan and allocate team resources', 'icon': '👥'},
                        {'id': 'risk_assessment', 'name': 'Risk Assessment', 'description': 'Identify and assess project risks', 'icon': '⚠️'}
                    ]
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Scrum Master',
                    'role': 'scrum_master',
                    'description': 'Facilitates Scrum ceremonies and agile practices',
                    'avatar': '🏃',
                    'status': 'active',
                    'capabilities': common_capabilities + [
                        {'id': 'sprint_planning', 'name': 'Sprint Planning', 'description': 'Plan and organize sprint activities', 'icon': '📅'},
                        {'id': 'daily_standup', 'name': 'Daily Standup', 'description': 'Facilitate daily standup meetings', 'icon': '☀️'},
                        {'id': 'sprint_review', 'name': 'Sprint Review', 'description': 'Conduct sprint review sessions', 'icon': '🔍'},
                        {'id': 'retrospective', 'name': 'Retrospective', 'description': 'Facilitate sprint retrospectives', 'icon': '🔄'},
                        {'id': 'backlog_grooming', 'name': 'Backlog Grooming', 'description': 'Refine and prioritize backlog items', 'icon': '📋'},
                        {'id': 'velocity_tracking', 'name': 'Track Velocity', 'description': 'Monitor team velocity and burndown', 'icon': '📊'}
                    ]
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'DevOps Engineer',
                    'role': 'devops',
                    'description': 'Manages deployment and infrastructure automation',
                    'avatar': '🔧',
                    'status': 'active',
                    'capabilities': common_capabilities + [
                        {'id': 'deploy', 'name': 'Deploy Application', 'description': 'Deploy applications to various environments', 'icon': '🚀'},
                        {'id': 'ci_pipeline', 'name': 'Create CI Pipeline', 'description': 'Set up continuous integration pipelines', 'icon': '🔄'},
                        {'id': 'cd_pipeline', 'name': 'Create CD Pipeline', 'description': 'Set up continuous deployment pipelines', 'icon': '📦'},
                        {'id': 'infrastructure', 'name': 'Manage Infrastructure', 'description': 'Provision and manage cloud infrastructure', 'icon': '☁️'},
                        {'id': 'monitoring', 'name': 'Setup Monitoring', 'description': 'Configure monitoring and alerting', 'icon': '📊'},
                        {'id': 'security_scan', 'name': 'Security Scanning', 'description': 'Run security vulnerability scans', 'icon': '🔒'}
                    ]
                }
            ]
            
            # Save agents
            for agent in default_agents:
                agent['created_at'] = datetime.now().isoformat()
                agent['updated_at'] = datetime.now().isoformat()
                data['agents'][agent['id']] = agent
            
            self._save_agents(data)
    
    def get_all_agents(self):
        """Get all configured agents"""
        data = self._load_agents()
        agents = []
        
        for agent_id, agent in data.get('agents', {}).items():
            agents.append(agent)
        
        return agents
    
    def get_agent(self, agent_id):
        """Get a specific agent by ID"""
        data = self._load_agents()
        return data.get('agents', {}).get(agent_id)
    
    def create_agent(self, agent_data):
        """Create a new agent"""
        if not agent_data.get('name'):
            raise ValueError("Agent name is required")
        
        data = self._load_agents()
        
        agent = {
            'id': str(uuid.uuid4()),
            'name': agent_data['name'],
            'role': agent_data.get('role', 'custom'),
            'description': agent_data.get('description', ''),
            'avatar': agent_data.get('avatar', '🤖'),
            'status': 'active',
            'capabilities': agent_data.get('capabilities', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['agents'][agent['id']] = agent
        
        if self._save_agents(data):
            return agent
        else:
            raise RuntimeError("Failed to save agent")
    
    def update_agent(self, agent_id, updates):
        """Update an existing agent"""
        data = self._load_agents()
        
        if agent_id not in data.get('agents', {}):
            return None
        
        agent = data['agents'][agent_id]
        
        # Update allowed fields
        for field in ['name', 'description', 'avatar', 'status', 'capabilities']:
            if field in updates:
                agent[field] = updates[field]
        
        agent['updated_at'] = datetime.now().isoformat()
        
        if self._save_agents(data):
            return agent
        else:
            raise RuntimeError("Failed to update agent")
    
    def delete_agent(self, agent_id):
        """Delete an agent"""
        data = self._load_agents()
        
        if agent_id in data.get('agents', {}):
            del data['agents'][agent_id]
            return self._save_agents(data)
        
        return False
    
    def get_capabilities_catalog(self):
        """Get catalog of all available capabilities"""
        return {
            'common': [
                {'id': 'file_create', 'name': 'Create File', 'description': 'Create new files in the project', 'icon': '📄'},
                {'id': 'file_read', 'name': 'Read File', 'description': 'Read and analyze file contents', 'icon': '📖'},
                {'id': 'file_delete', 'name': 'Delete File', 'description': 'Remove files from the project', 'icon': '🗑️'},
                {'id': 'search', 'name': 'Search', 'description': 'Search through codebase and documentation', 'icon': '🔍'},
                {'id': 'send_email', 'name': 'Send Email', 'description': 'Send email notifications', 'icon': '📧'},
                {'id': 'send_notification', 'name': 'Send Notification', 'description': 'Send system notifications', 'icon': '🔔'}
            ],
            'architect': [
                {'id': 'plan', 'name': 'Plan Architecture', 'description': 'Create detailed system architecture plans', 'icon': '📋'},
                {'id': 'analyze', 'name': 'Analyze System', 'description': 'Analyze existing system architecture and patterns', 'icon': '🔬'},
                {'id': 'document_architecture', 'name': 'Document Architecture', 'description': 'Create architecture documentation and diagrams', 'icon': '📐'}
            ],
            'engineer': [
                {'id': 'migrate', 'name': 'Migrate Code', 'description': 'Transform code from one framework to another', 'icon': '🔄'},
                {'id': 'generate', 'name': 'Generate Code', 'description': 'Generate new code based on specifications', 'icon': '⚡'},
                {'id': 'validate', 'name': 'Validate Code', 'description': 'Validate code quality and correctness', 'icon': '✅'},
                {'id': 'refactor', 'name': 'Refactor Code', 'description': 'Improve code structure and quality', 'icon': '🔧'}
            ],
            'writer': [
                {'id': 'document_code', 'name': 'Document Code', 'description': 'Create inline code documentation and comments', 'icon': '📝'},
                {'id': 'write_help', 'name': 'Write Help Docs', 'description': 'Create user help documentation', 'icon': '❓'},
                {'id': 'create_guides', 'name': 'Create How-To Guides', 'description': 'Write step-by-step tutorials and guides', 'icon': '📚'},
                {'id': 'api_docs', 'name': 'API Documentation', 'description': 'Generate API reference documentation', 'icon': '📡'}
            ],
            'manager': [
                {'id': 'project_kickoff', 'name': 'Project Kickoff', 'description': 'Initialize new projects with proper structure', 'icon': '🚀'},
                {'id': 'project_tracking', 'name': 'Track Progress', 'description': 'Monitor project progress and milestones', 'icon': '📈'},
                {'id': 'jira_create', 'name': 'Create Jira Issues', 'description': 'Create and manage Jira tickets', 'icon': '🎫'},
                {'id': 'jira_update', 'name': 'Update Jira', 'description': 'Update Jira ticket status and comments', 'icon': '🔄'},
                {'id': 'resource_planning', 'name': 'Resource Planning', 'description': 'Plan and allocate team resources', 'icon': '👥'},
                {'id': 'risk_assessment', 'name': 'Risk Assessment', 'description': 'Identify and assess project risks', 'icon': '⚠️'}
            ],
            'scrum_master': [
                {'id': 'sprint_planning', 'name': 'Sprint Planning', 'description': 'Plan and organize sprint activities', 'icon': '📅'},
                {'id': 'daily_standup', 'name': 'Daily Standup', 'description': 'Facilitate daily standup meetings', 'icon': '☀️'},
                {'id': 'sprint_review', 'name': 'Sprint Review', 'description': 'Conduct sprint review sessions', 'icon': '🔍'},
                {'id': 'retrospective', 'name': 'Retrospective', 'description': 'Facilitate sprint retrospectives', 'icon': '🔄'},
                {'id': 'backlog_grooming', 'name': 'Backlog Grooming', 'description': 'Refine and prioritize backlog items', 'icon': '📋'},
                {'id': 'velocity_tracking', 'name': 'Track Velocity', 'description': 'Monitor team velocity and burndown', 'icon': '📊'}
            ],
            'devops': [
                {'id': 'deploy', 'name': 'Deploy Application', 'description': 'Deploy applications to various environments', 'icon': '🚀'},
                {'id': 'ci_pipeline', 'name': 'Create CI Pipeline', 'description': 'Set up continuous integration pipelines', 'icon': '🔄'},
                {'id': 'cd_pipeline', 'name': 'Create CD Pipeline', 'description': 'Set up continuous deployment pipelines', 'icon': '📦'},
                {'id': 'infrastructure', 'name': 'Manage Infrastructure', 'description': 'Provision and manage cloud infrastructure', 'icon': '☁️'},
                {'id': 'monitoring', 'name': 'Setup Monitoring', 'description': 'Configure monitoring and alerting', 'icon': '📊'},
                {'id': 'security_scan', 'name': 'Security Scanning', 'description': 'Run security vulnerability scans', 'icon': '🔒'}
            ]
        }