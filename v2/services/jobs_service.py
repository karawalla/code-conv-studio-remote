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
        self.jobs_storage_path = os.path.join(data_folder, 'jobs')
        self._ensure_file_exists()
        
        # Ensure jobs storage directory exists
        os.makedirs(self.jobs_storage_path, exist_ok=True)
        
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
        """Create a new migration or modernization job with enterprise workflow"""
        # Validate required fields based on job type
        job_type = job_data.get('job_type', 'migration')
        required_fields = ['name', 'source_id']
        
        if job_type == 'migration':
            required_fields.append('target_id')
        elif job_type == 'modernization':
            if 'modernization_options' not in job_data or not job_data['modernization_options']:
                raise ValueError("Modernization jobs require at least one modernization option")
        
        for field in required_fields:
            if field not in job_data:
                raise ValueError(f"Missing required field: {field}")
                
        # Create job
        job_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Use provided stages or create default workflow stages based on job type
        project_management_enabled = job_data.get('project_management_enabled', True)
        
        if job_type == 'modernization':
            stages = job_data.get('stages', self._create_modernization_stages(
                job_data.get('modernization_options', []),
                project_management_enabled
            ))
        else:
            stages = job_data.get('stages', self._create_workflow_stages(project_management_enabled))
        
        job = {
            'id': job_id,
            'name': job_data['name'],
            'description': job_data.get('description', ''),
            'job_type': job_type,
            'source_id': job_data['source_id'],
            'source_name': job_data.get('source_name', ''),
            'target_id': job_data.get('target_id'),
            'target_name': job_data.get('target_name', ''),
            'modernization_options': job_data.get('modernization_options', []),
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
        
        # Create job folder structure
        self._create_job_folder_structure(job_id, stages)
        
        return job
        
    def _create_workflow_stages(self, include_project_management: bool = True) -> List[Dict]:
        """Create enterprise workflow stages"""
        stages = []
        
        if include_project_management:
            stages.append({
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
            })
            
        # Always include code analysis
        stages.append({
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
                {'name': 'Update Jira with Findings', 'status': 'pending', 'agent': 'Code Architect'} if include_project_management else {'name': 'Document Findings', 'status': 'pending', 'agent': 'Code Architect'}
            ],
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
            
        if include_project_management:
            stages.append({
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
            })
            
        # Core migration stage - always include
        migration_tasks = [
            {'name': 'Setup Target Environment', 'status': 'pending', 'agent': 'Code Engineer'},
            {'name': 'Migrate Core Components', 'status': 'pending', 'agent': 'Code Engineer'},
            {'name': 'Transform Business Logic', 'status': 'pending', 'agent': 'Code Engineer'},
            {'name': 'Update Dependencies', 'status': 'pending', 'agent': 'Code Engineer'}
        ]
        if include_project_management:
            migration_tasks.append({'name': 'Daily Standup Updates', 'status': 'pending', 'agent': 'Scrum Master'})
            
        stages.append({
            'id': 'code_migration',
            'name': 'Code Migration',
            'description': 'Migrate code from source to target framework',
            'status': 'pending',
            'progress': 0,
            'agents': ['Code Engineer'] + (['Scrum Master'] if include_project_management else []),
            'capabilities': ['migrate', 'generate', 'refactor', 'file_create'],
            'tasks': migration_tasks,
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
            
        validation_tasks = [
            {'name': 'Run Validation Tests', 'status': 'pending', 'agent': 'Code Engineer'},
            {'name': 'Debug & Fix Issues', 'status': 'pending', 'agent': 'Code Engineer'},
            {'name': 'Code Quality Review', 'status': 'pending', 'agent': 'Code Engineer'},
            {'name': 'Update Documentation', 'status': 'pending', 'agent': 'Technical Writer'}
        ]
        if include_project_management:
            validation_tasks.append({'name': 'Update Jira Tickets', 'status': 'pending', 'agent': 'Code Engineer'})
            
        stages.append({
            'id': 'validation_fix',
            'name': 'Validation & Fix',
            'description': 'Validate migrated code and fix issues',
            'status': 'pending',
            'progress': 0,
            'agents': ['Code Engineer', 'Technical Writer'],
            'capabilities': ['validate', 'debug_fix', 'document_code'],
            'tasks': validation_tasks,
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
        
        stages.append({
            'id': 'deployment_prep',
            'name': 'Deployment Preparation',
            'description': 'Prepare for deployment with CI/CD setup',
            'status': 'pending',
            'progress': 0,
            'agents': ['DevOps Engineer', 'Technical Writer'],
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
        })
        
        if include_project_management:
            stages.append({
                'id': 'sprint_review',
                'name': 'Sprint Review & Retrospective',
                'description': 'Review progress and conduct retrospective',
                'status': 'pending',
                'progress': 0,
                'agents': ['Scrum Master', 'Project Manager', 'Code Engineer'],
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
            })
        
        # Final stage
        final_tasks = [
            {'name': 'Generate Status Report', 'status': 'pending', 'agent': 'Technical Writer'},
            {'name': 'Create Migration Guide', 'status': 'pending', 'agent': 'Technical Writer'}
        ]
        if include_project_management:
            final_tasks.extend([
                {'name': 'Close Jira Epic', 'status': 'pending', 'agent': 'Project Manager'},
                {'name': 'Send Completion Email', 'status': 'pending', 'agent': 'Project Manager'},
                {'name': 'Archive Project Artifacts', 'status': 'pending', 'agent': 'Project Manager'}
            ])
        else:
            final_tasks.append({'name': 'Send Completion Notification', 'status': 'pending', 'agent': 'Technical Writer'})
            
        stages.append({
            'id': 'project_closure',
            'name': 'Project Closure' if include_project_management else 'Project Completion',
            'description': 'Generate final reports and close project' if include_project_management else 'Generate final deliverables',
            'status': 'pending',
            'progress': 0,
            'agents': ['Technical Writer'] + (['Scrum Master', 'Project Manager'] if include_project_management else []),
            'capabilities': ['create_guides', 'project_tracking', 'send_email'] if include_project_management else ['create_guides'],
            'tasks': final_tasks,
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
        
        return stages
        
    def update_job(self, job_id: str, updates: Dict) -> Optional[Dict]:
        """Update a job"""
        data = self._load_jobs()
        if job_id not in data.get('jobs', {}):
            return None
            
        job = data['jobs'][job_id]
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'status', 'progress', 'current_stage',
                         'metadata', 'config', 'estimated_completion', 'actual_completion',
                         'stages', 'source_name', 'target_name']
        
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
    
    def _create_modernization_stages(self, modernization_options: List[str], include_project_management: bool = True) -> List[Dict]:
        """Create modernization workflow stages based on selected options"""
        stages = []
        
        # Project setup if enabled
        if include_project_management:
            stages.append({
                'id': 'project_setup',
                'name': 'Project Setup',
                'description': 'Initialize modernization project with Jira epic and team notifications',
                'status': 'pending',
                'progress': 0,
                'agents': ['Project Manager', 'Scrum Master'],
                'capabilities': ['jira_create', 'send_email', 'send_notification'],
                'tasks': [
                    {'name': 'Create Jira Epic for Modernization', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Create Modernization Tickets', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Send Kickoff Email', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Send Slack Notification', 'status': 'pending', 'agent': 'Project Manager'},
                    {'name': 'Setup Sprint Structure', 'status': 'pending', 'agent': 'Scrum Master'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
        
        # Always start with analysis
        stages.append({
            'id': 'code_analysis',
            'name': 'Code Analysis & Assessment',
            'description': 'Analyze current codebase and identify modernization opportunities',
            'status': 'pending',
            'progress': 0,
            'agents': ['Code Architect'],
            'capabilities': ['analyze', 'plan', 'document_architecture'],
            'tasks': [
                {'name': 'Analyze Current Architecture', 'status': 'pending', 'agent': 'Code Architect'},
                {'name': 'Identify Technical Debt', 'status': 'pending', 'agent': 'Code Architect'},
                {'name': 'Create Modernization Plan', 'status': 'pending', 'agent': 'Code Architect'},
                {'name': 'Document Current State', 'status': 'pending', 'agent': 'Code Architect'},
                {'name': 'Update Jira with Assessment', 'status': 'pending', 'agent': 'Code Architect'} if include_project_management else {'name': 'Document Assessment', 'status': 'pending', 'agent': 'Code Architect'}
            ],
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
        
        # Add stages based on selected options
        if 'cicd' in modernization_options:
            stages.append({
                'id': 'cicd_setup',
                'name': 'CI/CD Pipeline Setup',
                'description': 'Implement continuous integration and deployment pipelines',
                'status': 'pending',
                'progress': 0,
                'agents': ['DevOps Engineer'],
                'capabilities': ['ci_pipeline', 'cd_pipeline', 'infrastructure'],
                'tasks': [
                    {'name': 'Setup Build Pipeline', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Configure Automated Tests', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Setup Deployment Pipeline', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Configure Environments', 'status': 'pending', 'agent': 'DevOps Engineer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
            
        if 'cloud' in modernization_options:
            stages.append({
                'id': 'cloud_migration',
                'name': 'Cloud Migration',
                'description': 'Migrate application to cloud platform',
                'status': 'pending',
                'progress': 0,
                'agents': ['DevOps Engineer', 'Code Engineer'],
                'capabilities': ['infrastructure', 'deploy', 'migrate'],
                'tasks': [
                    {'name': 'Design Cloud Architecture', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Setup Cloud Infrastructure', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Migrate Data', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Deploy Application', 'status': 'pending', 'agent': 'DevOps Engineer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
            
        if 'containers' in modernization_options:
            stages.append({
                'id': 'containerization',
                'name': 'Containerization',
                'description': 'Containerize application with Docker/Kubernetes',
                'status': 'pending',
                'progress': 0,
                'agents': ['DevOps Engineer'],
                'capabilities': ['infrastructure', 'deploy'],
                'tasks': [
                    {'name': 'Create Dockerfiles', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Setup Container Registry', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Configure Kubernetes', 'status': 'pending', 'agent': 'DevOps Engineer'},
                    {'name': 'Deploy to K8s Cluster', 'status': 'pending', 'agent': 'DevOps Engineer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
            
        if 'microservices' in modernization_options:
            stages.append({
                'id': 'microservices',
                'name': 'Microservices Architecture',
                'description': 'Break monolith into microservices',
                'status': 'pending',
                'progress': 0,
                'agents': ['Code Architect', 'Code Engineer'],
                'capabilities': ['analyze', 'refactor', 'migrate'],
                'tasks': [
                    {'name': 'Identify Service Boundaries', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Extract Services', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Implement Service Communication', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Setup Service Discovery', 'status': 'pending', 'agent': 'DevOps Engineer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
            
        if 'api' in modernization_options:
            stages.append({
                'id': 'api_enablement',
                'name': 'API Enablement',
                'description': 'Create RESTful/GraphQL API layer',
                'status': 'pending',
                'progress': 0,
                'agents': ['Code Engineer'],
                'capabilities': ['generate', 'refactor', 'document_code'],
                'tasks': [
                    {'name': 'Design API Schema', 'status': 'pending', 'agent': 'Code Architect'},
                    {'name': 'Implement API Endpoints', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Add Authentication', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Generate API Documentation', 'status': 'pending', 'agent': 'Technical Writer'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
            
        # Add sprint planning if PM is enabled
        if include_project_management:
            stages.append({
                'id': 'sprint_planning',
                'name': 'Sprint Planning',
                'description': 'Plan modernization work across sprints',
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
            })
        
        # Always end with testing and documentation
        stages.append({
            'id': 'testing_validation',
            'name': 'Testing & Validation',
            'description': 'Validate modernization changes',
            'status': 'pending',
            'progress': 0,
            'agents': ['Code Engineer'],
            'capabilities': ['validate', 'debug_fix'],
            'tasks': [
                {'name': 'Run Automated Tests', 'status': 'pending', 'agent': 'Code Engineer'},
                {'name': 'Performance Testing', 'status': 'pending', 'agent': 'Code Engineer'},
                {'name': 'Security Scanning', 'status': 'pending', 'agent': 'Code Engineer'},
                {'name': 'Fix Issues', 'status': 'pending', 'agent': 'Code Engineer'}
            ],
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
        
        # Sprint review if PM enabled
        if include_project_management:
            stages.append({
                'id': 'sprint_review',
                'name': 'Sprint Review & Retrospective',
                'description': 'Review modernization progress and conduct retrospective',
                'status': 'pending',
                'progress': 0,
                'agents': ['Scrum Master', 'Project Manager', 'Code Engineer'],
                'capabilities': ['sprint_review', 'retrospective', 'velocity_tracking'],
                'tasks': [
                    {'name': 'Conduct Sprint Review', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Demo Modernized Features', 'status': 'pending', 'agent': 'Code Engineer'},
                    {'name': 'Gather Feedback', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Run Retrospective', 'status': 'pending', 'agent': 'Scrum Master'},
                    {'name': 'Update Velocity Metrics', 'status': 'pending', 'agent': 'Scrum Master'}
                ],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            })
        
        # Final documentation
        final_tasks = [
            {'name': 'Update Documentation', 'status': 'pending', 'agent': 'Technical Writer'},
            {'name': 'Create User Guides', 'status': 'pending', 'agent': 'Technical Writer'}
        ]
        if include_project_management:
            final_tasks.extend([
                {'name': 'Prepare Handover Report', 'status': 'pending', 'agent': 'Project Manager'},
                {'name': 'Close Jira Epic', 'status': 'pending', 'agent': 'Project Manager'},
                {'name': 'Send Completion Email', 'status': 'pending', 'agent': 'Project Manager'}
            ])
        else:
            final_tasks.append({'name': 'Send Completion Notification', 'status': 'pending', 'agent': 'Technical Writer'})
            
        stages.append({
            'id': 'documentation',
            'name': 'Documentation & Handover' if include_project_management else 'Documentation & Completion',
            'description': 'Document changes and prepare for handover' if include_project_management else 'Document modernization changes',
            'status': 'pending',
            'progress': 0,
            'agents': ['Technical Writer'] + (['Project Manager'] if include_project_management else []),
            'capabilities': ['document_code', 'create_guides', 'send_email'] if include_project_management else ['document_code', 'create_guides'],
            'tasks': final_tasks,
            'artifacts': [],
            'started_at': None,
            'completed_at': None
        })
        
        return stages    
    def _create_job_folder_structure(self, job_id: str, stages: List[Dict]):
        """Create folder structure for a job with task subdirectories"""
        try:
            # Create main job folder
            job_path = os.path.join(self.jobs_storage_path, job_id)
            os.makedirs(job_path, exist_ok=True)
            
            # Create folders for each stage and task
            for stage in stages:
                stage_id = stage['id']
                tasks = stage.get('tasks', [])
                
                for task_index, task in enumerate(tasks):
                    # Clean task name for folder
                    task_name = task.get('name', 'unknown').lower().replace(' ', '_')
                    task_folder = os.path.join(job_path, stage_id, f"{task_index}_{task_name}")
                    
                    # Create input, output, and data folders for each task
                    os.makedirs(os.path.join(task_folder, 'input'), exist_ok=True)
                    os.makedirs(os.path.join(task_folder, 'output'), exist_ok=True)
                    os.makedirs(os.path.join(task_folder, 'data'), exist_ok=True)
                    
                    logger.info(f"Created task folder structure: {task_folder}")
            
            logger.info(f"Created job folder structure for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error creating job folder structure: {e}")
            # Don't fail the job creation if folder creation fails
            pass