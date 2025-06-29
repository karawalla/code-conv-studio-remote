"""
Jobs Service for managing code migration jobs with enterprise workflow
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class JobsService:
    """Service for managing code migration jobs with enterprise workflow"""
    
    def __init__(self, data_folder: str):
        """Initialize the jobs service"""
        self.data_folder = data_folder
        self.jobs_file = os.path.join(data_folder, 'jobs_metadata.json')
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Ensure jobs metadata file exists"""
        if not os.path.exists(self.jobs_file):
            self._save_jobs({})
            
    def _load_jobs(self) -> Dict:
        """Load jobs from file"""
        try:
            with open(self.jobs_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading jobs: {e}")
            return {}
            
    def _save_jobs(self, data: Dict):
        """Save jobs to file"""
        try:
            with open(self.jobs_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving jobs: {e}")
            
    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs"""
        data = self._load_jobs()
        jobs = list(data.get('jobs', {}).values())
        # Sort by created_at descending
        jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return jobs
        
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get a specific job by ID"""
        data = self._load_jobs()
        return data.get('jobs', {}).get(job_id)
        
    def create_job(self, job_data: Dict) -> Dict:
        """Create a new migration job with enterprise workflow"""
        # Validate required fields
        required_fields = ['name', 'source_id', 'target_id']
        for field in required_fields:
            if field not in job_data:
                raise ValueError(f"Missing required field: {field}")
                
        # Create job
        job_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Define enterprise workflow stages
        stages = self._create_workflow_stages()
        
        job = {
            'id': job_id,
            'name': job_data['name'],
            'description': job_data.get('description', ''),
            'source_id': job_data['source_id'],
            'source_name': job_data.get('source_name', ''),
            'target_id': job_data['target_id'],
            'target_name': job_data.get('target_name', ''),
            'status': 'pending',
            'progress': 0,
            'stages': stages,
            'current_stage': 0,
            'total_stages': len(stages),
            'config': job_data.get('config', {}),
            'metadata': {
                'jira_epic': None,
                'jira_tickets': [],
                'slack_channel': job_data.get('slack_channel'),
                'email_recipients': job_data.get('email_recipients', []),
                'sprint_info': {
                    'current_sprint': None,
                    'sprint_goal': None,
                    'velocity': 0
                }
            },
            'artifacts': [],
            'logs': [],
            'created_at': now,
            'updated_at': now,
            'created_by': job_data.get('created_by', 'system'),
            'estimated_completion': None,
            'actual_completion': None
        }
        
        # Save job
        data = self._load_jobs()
        if 'jobs' not in data:
            data['jobs'] = {}
        data['jobs'][job_id] = job
        self._save_jobs(data)
        
        return job
        
    def _create_workflow_stages(self) -> List[Dict]:
        """Create enterprise workflow stages"""
        return [
            {
                'id': 'project_setup',
                'name': 'Project Setup',
                'description': 'Initialize project with Jira epic, tickets, and team notifications',
                'status': 'pending',
                'progress': 0,
                'agents': ['Project Manager', 'Scrum Master'],
                'capabilities': ['jira_create', 'send_email', 'send_notification'],
                'tasks': [
                    {'name': 'Create Jira Epic', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Create Initial Tickets', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Send Kickoff Email', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Send Slack Notification', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Setup Sprint Structure', 'status': 'pending', 'agent': 'Scrum Master'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'code_analysis',
                'name': 'Code Analysis & Planning',
                'description': 'Analyze source code and create migration plan',
                'status': 'pending',
                'progress': 0,
                'agents': ['Code Architect'],
                'capabilities': ['analyze', 'plan', 'document_architecture'],
                'tasks': [
                    {'name': 'Analyze Source Structure', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Identify Dependencies', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Create Migration Plan', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Document Architecture', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Update Jira with Findings', 'status': 'pending', 'agent': 'Code Architect'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'sprint_planning',
                'name': 'Sprint Planning',
                'description': 'Plan migration work across sprints',
                'status': 'pending',
                'progress': 0,
                'agents': ['Scrum Master', 'Project Manager'],
                'capabilities': ['sprint_planning', 'backlog_grooming', 'jira_update'],
                'tasks': [
                    {'name': 'Create Sprint Backlog', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Estimate Story Points', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Assign Sprint Goals', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Update Jira Board', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Schedule Sprint Ceremonies', 'status': 'pending', 'agent': 'Scrum Master'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'code_migration',
                'name': 'Code Migration',
                'description': 'Migrate code from source to target framework',
                'status': 'pending',
                'progress': 0,
                'agents': ['Code Engineer'],
                'capabilities': ['migrate', 'generate', 'refactor', 'file_create'],
                'tasks': [
                    {'name': 'Setup Target Environment', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Migrate Core Components', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Transform Business Logic', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Update Dependencies', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Daily Standup Updates', 'status': 'pending', 'agent': 'Scrum Master'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'validation_fix',
                'name': 'Validation & Fix',
                'description': 'Validate migrated code and fix issues',
                'status': 'pending',
                'progress': 0,
                'agents': ['Code Engineer', 'Technical Writer'],
                'capabilities': ['validate', 'debug_fix', 'document_code'],
                'tasks': [
                    {'name': 'Run Validation Tests', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Debug & Fix Issues', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Code Quality Review', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Update Documentation', 'status': 'pending', 'agent': 'Technical Writer'},
                    {'name': 'Update Jira Tickets', 'status': 'pending', 'agent': 'Code Engineer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'deployment_prep',
                'name': 'Deployment Preparation',
                'description': 'Prepare for deployment with CI/CD setup',
                'status': 'pending',
                'progress': 0,
                'agents': ['DevOps Engineer'],
                'capabilities': ['ci_pipeline', 'cd_pipeline', 'infrastructure', 'security_scan'],
                'tasks': [
                    {'name': 'Setup CI/CD Pipeline', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Configure Infrastructure', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Run Security Scans', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Setup Monitoring', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Create Deployment Guide', 'status': 'pending', 'agent': 'Technical Writer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'sprint_review',
                'name': 'Sprint Review & Retrospective',
                'description': 'Review progress and conduct retrospective',
                'status': 'pending',
                'progress': 0,
                'agents': ['Scrum Master', 'Project Manager'],
                'capabilities': ['sprint_review', 'retrospective', 'velocity_tracking'],
                'tasks': [
                    {'name': 'Conduct Sprint Review', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Demo Migrated Features', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Gather Feedback', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Run Retrospective', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Update Velocity Metrics', 'status': 'pending', 'agent': 'Scrum Master'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            },
            {
                'id': 'project_closure',
                'name': 'Project Closure',
                'description': 'Generate final reports and close project',
                'status': 'pending',
                'progress': 0,
                'agents': ['Scrum Master', 'Project Manager', 'Technical Writer'],
                'capabilities': ['create_guides', 'project_tracking', 'send_email'],
                'tasks': [
                    {'name': 'Generate Status Report', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Create Migration Guide', 'status': 'pending', 'agent': 'Technical Writer'},
                    {'name': 'Close Jira Epic', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Send Completion Email', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Archive Project Artifacts', 'status': 'pending', 'agent': 'Project Manager'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            }
        ]
        
    def update_job(self, job_id: str, updates: Dict) -> Optional[Dict]:
        """Update a job"""
        data = self._load_jobs()
        if job_id not in data.get('jobs', {}):
            return None
            
        job = data['jobs'][job_id]
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'status', 'progress', 'current_stage',
                         'metadata', 'config', 'estimated_completion', 'actual_completion']
        
        for field in allowed_fields:
            if field in updates:
                job[field] = updates[field]
                
        job['updated_at'] = datetime.now().isoformat()
        
        # Save
        self._save_jobs(data)
        return job
        
    def update_stage(self, job_id: str, stage_id: str, updates: Dict) -> Optional[Dict]:
        """Update a specific stage in a job"""
        data = self._load_jobs()
        if job_id not in data.get('jobs', {}):
            return None
            
        job = data['jobs'][job_id]
        
        # Find stage
        stage_index = None
        for i, stage in enumerate(job['stages']):
            if stage['id'] == stage_id:
                stage_index = i
                break
                
        if stage_index is None:
            return None
            
        # Update stage
        stage = job['stages'][stage_index]
        for key, value in updates.items():
            if key in stage:
                stage[key] = value
                
        # Update job progress based on stages
        completed_stages = sum(1 for s in job['stages'] if s['status'] == 'completed')
        job['progress'] = int((completed_stages / len(job['stages'])) * 100)
        
        # Update current stage if needed
        if stage['status'] == 'completed' and stage_index + 1 < len(job['stages']):
            job['current_stage'] = stage_index + 1
            
        job['updated_at'] = datetime.now().isoformat()
        
        # Save
        self._save_jobs(data)
        return job
        
    def add_log(self, job_id: str, log_entry: Dict) -> bool:
        """Add a log entry to a job"""
        data = self._load_jobs()
        if job_id not in data.get('jobs', {}):
            return False
            
        job = data['jobs'][job_id]
        
        log = {
            'timestamp': datetime.now().isoformat(),
            'level': log_entry.get('level', 'info'),
            'agent': log_entry.get('agent', 'system'),
            'message': log_entry.get('message', ''),
            'stage': log_entry.get('stage')
        }
        
        job['logs'].append(log)
        job['updated_at'] = datetime.now().isoformat()
        
        # Save
        self._save_jobs(data)
        return True
        
    def add_artifact(self, job_id: str, artifact: Dict) -> bool:
        """Add an artifact to a job"""
        data = self._load_jobs()
        if job_id not in data.get('jobs', {}):
            return False
            
        job = data['jobs'][job_id]
        
        artifact_data = {
            'id': str(uuid.uuid4()),
            'name': artifact.get('name', ''),
            'type': artifact.get('type', ''),
            'path': artifact.get('path', ''),
            'stage': artifact.get('stage', ''),
            'created_at': datetime.now().isoformat(),
            'created_by': artifact.get('created_by', 'system')
        }
        
        job['artifacts'].append(artifact_data)
        job['updated_at'] = datetime.now().isoformat()
        
        # Save
        self._save_jobs(data)
        return True
        
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        data = self._load_jobs()
        if job_id in data.get('jobs', {}):
            del data['jobs'][job_id]
            self._save_jobs(data)
            return True
        return False
        
    def update_stage_credentials(self, job_id: str, stage_id: str, credentials: List[Dict]) -> bool:
        """Update credentials for a specific stage"""
        data = self._load_jobs()
        if job_id not in data.get('jobs', {}):
            return False
            
        job = data['jobs'][job_id]
        
        # Find stage
        stage = None
        for s in job['stages']:
            if s['id'] == stage_id:
                stage = s
                break
                
        if stage is None:
            return False
            
        # Update stage credentials
        stage['credentials'] = credentials
        job['updated_at'] = datetime.now().isoformat()
        
        # Save
        self._save_jobs(data)
        return True