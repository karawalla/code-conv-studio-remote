"""
Any-to-Any Code Conversion Studio v2
A modern web application for converting between different frameworks and languages
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
from services import SourcesService
import base64
import shutil
from pathlib import Path

# Application Configuration
class Config:
    """Application configuration"""
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATA_FOLDER = os.path.join(os.getcwd(), 'data')
    UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    
    # Ensure folders exist
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
sources_service = SourcesService()

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/orchestration')
def orchestration_viewer():
    """Prompt orchestration viewer page"""
    return render_template('orchestration_viewer.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    # Mock data for now
    return jsonify({
        'sources': {
            'total': 5,
            'active': 3,
            'types': ['Java Spring Boot', 'Python Django', 'Node.js Express', 'Ruby on Rails', 'PHP Laravel']
        },
        'targets': {
            'total': 4,
            'active': 2,
            'types': ['Sage IT', 'AWS Lambda', 'Kubernetes', 'Docker Compose']
        },
        'jobs': {
            'total': 15,
            'running': 2,
            'completed': 10,
            'failed': 3,
            'recent': [
                {'id': 1, 'name': 'Spring to Sage Migration', 'status': 'completed', 'progress': 100},
                {'id': 2, 'name': 'Django to Lambda', 'status': 'running', 'progress': 45},
                {'id': 3, 'name': 'Express to K8s', 'status': 'running', 'progress': 72}
            ]
        },
        'conversions': {
            'today': 5,
            'week': 28,
            'month': 156,
            'success_rate': 87.5
        }
    })

@app.route('/api/sources')
def get_sources():
    """Get all configured sources"""
    try:
        sources = sources_service.list_sources()
        # Transform for UI display
        ui_sources = []
        for source in sources:
            ui_source = {
                'id': source['id'],
                'name': source['name'],
                'type': source['type'],
                'description': f"{source['type'].title()} repository",
                'icon': '📦' if source['type'] == 'local' else '🐙',
                'active': source.get('status') == 'active',
                'created_at': source.get('created_at'),
                'updated_at': source.get('updated_at'),
                'info': source.get('info', {})
            }
            if source['type'] == 'github':
                ui_source['url'] = source.get('url')
            ui_sources.append(ui_source)
        return jsonify(ui_sources)
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources', methods=['POST'])
def add_source():
    """Add a new source (GitHub repo or local folder)"""
    try:
        data = request.get_json()
        source_type = data.get('type')
        name = data.get('name')
        
        if source_type == 'github':
            url = data.get('url')
            if not url:
                return jsonify({'error': 'URL is required for GitHub sources'}), 400
            
            result = sources_service.add_github_repo(url, name)
            return jsonify(result), 201
            
        elif source_type == 'local':
            path = data.get('path')
            if not path:
                return jsonify({'error': 'Path is required for local sources'}), 400
            
            result = sources_service.add_local_folder(path, name)
            return jsonify(result), 201
            
        else:
            return jsonify({'error': 'Invalid source type. Must be "github" or "local"'}), 400
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error adding source: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sources/<source_id>')
def get_source(source_id):
    """Get a specific source by ID"""
    try:
        source = sources_service.get_source(source_id)
        if source:
            return jsonify(source)
        else:
            return jsonify({'error': 'Source not found'}), 404
    except Exception as e:
        logger.error(f"Error getting source: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Delete a source"""
    try:
        success = sources_service.delete_source(source_id)
        if success:
            return jsonify({'message': 'Source deleted successfully'})
        else:
            return jsonify({'error': 'Source not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting source: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources/<source_id>/update', methods=['POST'])
def update_source(source_id):
    """Update a source (pull latest for GitHub repos)"""
    try:
        result = sources_service.update_source(source_id)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to update source or source not found'}), 400
    except Exception as e:
        logger.error(f"Error updating source: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources/<source_id>/tree')
def get_source_tree(source_id):
    """Get file tree for a source"""
    try:
        source = sources_service.get_source(source_id)
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        # Get file tree
        from services.sources_service import FileManager
        tree = FileManager.get_file_tree(source['path'])
        
        return jsonify(tree)
    except Exception as e:
        logger.error(f"Error getting source tree: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources/<source_id>/file')
def get_source_file(source_id):
    """Get file content from a source"""
    try:
        source = sources_service.get_source(source_id)
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        # Get file path from query params
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        # Construct full path
        full_path = os.path.join(source['path'], file_path)
        
        # Security check - ensure path is within source directory
        if not os.path.abspath(full_path).startswith(os.path.abspath(source['path'])):
            return jsonify({'error': 'Invalid file path'}), 403
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        if not os.path.isfile(full_path):
            return jsonify({'error': 'Path is not a file'}), 400
        
        # Read file content
        try:
            # Check if it's a binary file
            with open(full_path, 'rb') as f:
                content = f.read(1024)  # Read first 1KB to check
                
            # Try to decode as text
            try:
                content = open(full_path, 'r', encoding='utf-8').read()
                return jsonify({'content': content, 'type': 'text'})
            except UnicodeDecodeError:
                # Binary file - check if it's an image
                import base64
                ext = os.path.splitext(file_path)[1].lower()
                image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.bmp', '.webp']
                
                if ext in image_extensions:
                    with open(full_path, 'rb') as f:
                        content = base64.b64encode(f.read()).decode('utf-8')
                    return jsonify({'content': content, 'type': 'image'})
                else:
                    return jsonify({'content': None, 'type': 'binary'})
                    
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return jsonify({'error': 'Error reading file'}), 500
            
    except Exception as e:
        logger.error(f"Error getting file content: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/targets')
def get_targets():
    """Get configured targets"""
    try:
        # Import targets service with data folder
        from services.targets_service import TargetsService
        targets_service = TargetsService(Config.DATA_FOLDER)
        
        targets = targets_service.get_all_targets()
        return jsonify(targets)
    except Exception as e:
        logger.error(f"Error getting targets: {e}")
        # Fallback to some default targets if service fails
        return jsonify([])

@app.route('/api/targets/defaults')
def get_default_targets():
    """Get default target templates"""
    try:
        from services.targets_service import TargetsService
        targets_service = TargetsService(Config.DATA_FOLDER)
        return jsonify(targets_service.get_default_targets())
    except Exception as e:
        logger.error(f"Error getting default targets: {e}")
        return jsonify([])

@app.route('/api/targets/<target_id>')
def get_target(target_id):
    """Get a specific target by ID"""
    try:
        from services.targets_service import TargetsService
        targets_service = TargetsService(Config.DATA_FOLDER)
        target = targets_service.get_target(target_id)
        if target:
            return jsonify(target)
        else:
            return jsonify({'error': 'Target not found'}), 404
    except Exception as e:
        logger.error(f"Error getting target: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/targets', methods=['POST'])
def create_target():
    """Create a new target"""
    try:
        from services.targets_service import TargetsService
        targets_service = TargetsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = targets_service.create_target(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating target: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/targets/<target_id>', methods=['PUT'])
def update_target(target_id):
    """Update an existing target"""
    try:
        from services.targets_service import TargetsService
        targets_service = TargetsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = targets_service.update_target(target_id, data)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Target not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating target: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/targets/<target_id>', methods=['DELETE'])
def delete_target(target_id):
    """Delete a target"""
    try:
        from services.targets_service import TargetsService
        targets_service = TargetsService(Config.DATA_FOLDER)
        if targets_service.delete_target(target_id):
            return jsonify({'message': 'Target deleted successfully'})
        else:
            return jsonify({'error': 'Target not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting target: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents')
def get_agents():
    """Get all configured agents"""
    try:
        from services.agents_service import AgentsService
        agents_service = AgentsService(Config.DATA_FOLDER)
        agents = agents_service.get_all_agents()
        return jsonify(agents)
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return jsonify([])

@app.route('/api/agents/<agent_id>')
def get_agent(agent_id):
    """Get a specific agent by ID"""
    try:
        from services.agents_service import AgentsService
        agents_service = AgentsService(Config.DATA_FOLDER)
        agent = agents_service.get_agent(agent_id)
        if agent:
            return jsonify(agent)
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """Create a new agent"""
    try:
        from services.agents_service import AgentsService
        agents_service = AgentsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = agents_service.create_agent(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update an existing agent"""
    try:
        from services.agents_service import AgentsService
        agents_service = AgentsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = agents_service.update_agent(agent_id, data)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete an agent"""
    try:
        from services.agents_service import AgentsService
        agents_service = AgentsService(Config.DATA_FOLDER)
        if agents_service.delete_agent(agent_id):
            return jsonify({'message': 'Agent deleted successfully'})
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/capabilities/catalog')
def get_capabilities_catalog():
    """Get catalog of all available capabilities"""
    try:
        from services.agents_service import AgentsService
        agents_service = AgentsService(Config.DATA_FOLDER)
        catalog = agents_service.get_capabilities_catalog()
        return jsonify(catalog)
    except Exception as e:
        logger.error(f"Error getting capabilities catalog: {e}")
        return jsonify({})

@app.route('/api/jobs')
def get_jobs():
    """Get all jobs"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        jobs = jobs_service.get_all_jobs()
        return jsonify(jobs)
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify([])

@app.route('/api/jobs/<job_id>')
def get_job(job_id):
    """Get a specific job by ID"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        job = jobs_service.get_job(job_id)
        if job:
            return jsonify(job)
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new migration job"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = jobs_service.create_job(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """Update an existing job"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = jobs_service.update_job(job_id, data)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        logger.error(f"Error updating job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        if jobs_service.delete_job(job_id):
            return jsonify({'message': 'Job deleted successfully'})
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>', methods=['PUT'])
def update_job_stage(job_id, stage_id):
    """Update a specific stage in a job"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        data = request.get_json()
        result = jobs_service.update_stage(job_id, stage_id, data)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Job or stage not found'}), 404
    except Exception as e:
        logger.error(f"Error updating job stage: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/logs', methods=['POST'])
def add_job_log(job_id):
    """Add a log entry to a job"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        data = request.get_json()
        if jobs_service.add_log(job_id, data):
            return jsonify({'message': 'Log entry added successfully'})
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        logger.error(f"Error adding job log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/artifacts', methods=['POST'])
def add_job_artifact(job_id):
    """Add an artifact to a job"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        data = request.get_json()
        if jobs_service.add_artifact(job_id, data):
            return jsonify({'message': 'Artifact added successfully'})
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        logger.error(f"Error adding job artifact: {e}")
        return jsonify({'error': str(e)}), 500

# Configuration Management APIs
@app.route('/api/jobs/<job_id>/config')
def get_job_config(job_id):
    """Get configuration for a job"""
    try:
        from services.config_service import ConfigurationService
        from services.integration_plugins import create_default_plugins
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        
        # Register default plugins
        for name, plugin in create_default_plugins().items():
            config_service.register_plugin(name, plugin)
        
        config = config_service.get_job_config(job_id)
        if config:
            return jsonify(config)
        else:
            # Return default configuration if none exists
            return jsonify({
                'job_id': job_id,
                'global_config': {
                    'integrations': {},
                    'defaults': {
                        'timeout_minutes': 30,
                        'retry_attempts': 3,
                        'notification_level': 'all'
                    }
                },
                'stage_configs': {}
            })
    except Exception as e:
        logger.error(f"Error getting job config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/config', methods=['PUT'])
def update_job_config(job_id):
    """Update configuration for a job"""
    try:
        from services.config_service import ConfigurationService
        from services.integration_plugins import create_default_plugins
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        
        # Register default plugins
        for name, plugin in create_default_plugins().items():
            config_service.register_plugin(name, plugin)
        
        data = request.get_json()
        
        # Validate configuration
        if 'global_config' in data and 'integrations' in data['global_config']:
            for integration, config in data['global_config']['integrations'].items():
                if integration in config_service.plugins:
                    is_valid, error = config_service.validate_config(integration, config)
                    if not is_valid:
                        return jsonify({'error': f'Invalid {integration} config: {error}'}), 400
        
        if config_service.save_job_config(job_id, data):
            return jsonify({'message': 'Configuration updated successfully'})
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
    except Exception as e:
        logger.error(f"Error updating job config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>/config')
def get_stage_config(job_id, stage_id):
    """Get configuration for a specific stage"""
    try:
        from services.config_service import ConfigurationService
        from services.integration_plugins import create_default_plugins
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        
        # Register default plugins
        for name, plugin in create_default_plugins().items():
            config_service.register_plugin(name, plugin)
        
        config = config_service.get_stage_config(job_id, stage_id)
        if config:
            return jsonify(config)
        else:
            return jsonify({})
    except Exception as e:
        logger.error(f"Error getting stage config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>/config', methods=['PUT'])
def update_stage_config(job_id, stage_id):
    """Update configuration for a specific stage"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        
        data = request.get_json()
        
        # Update stage with credentials and other config
        if jobs_service.update_stage_credentials(job_id, stage_id, data.get('credentials', [])):
            # Also update additional config if needed
            updates = {}
            if 'notify_on_start' in data:
                updates['notify_on_start'] = data['notify_on_start']
            if 'notify_on_complete' in data:
                updates['notify_on_complete'] = data['notify_on_complete']
            if 'create_jira_ticket' in data:
                updates['create_jira_ticket'] = data['create_jira_ticket']
            
            if updates:
                jobs_service.update_stage(job_id, stage_id, updates)
            
            return jsonify({'message': 'Stage configuration updated successfully'})
        else:
            return jsonify({'error': 'Failed to save stage configuration'}), 500
    except Exception as e:
        logger.error(f"Error updating stage config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>/tasks/<int:task_index>/config', methods=['PUT'])
def update_task_config(job_id, stage_id, task_index):
    """Update configuration for a specific task within a stage"""
    try:
        from services.jobs_service import JobsService
        jobs_service = JobsService(Config.DATA_FOLDER)
        
        data = request.get_json()
        
        # Get the job to update the task
        job = jobs_service.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Find the stage
        stage = None
        for s in job['stages']:
            if s['id'] == stage_id:
                stage = s
                break
        
        if not stage:
            return jsonify({'error': 'Stage not found'}), 404
        
        # Check if task exists
        if task_index >= len(stage.get('tasks', [])):
            return jsonify({'error': 'Task not found'}), 404
        
        # Update task configuration
        if 'tasks' not in stage:
            stage['tasks'] = []
        
        task = stage['tasks'][task_index]
        task['config'] = data
        
        # Save the updated job
        if jobs_service.update_job(job_id, {'stages': job['stages']}):
            return jsonify({'message': 'Task configuration updated successfully'})
        else:
            return jsonify({'error': 'Failed to save task configuration'}), 500
            
    except Exception as e:
        logger.error(f"Error updating task config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/templates')
def get_config_templates():
    """Get all configuration templates"""
    try:
        from services.config_service import ConfigurationService
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        template_type = request.args.get('type')
        
        templates = config_service.get_templates(template_type)
        return jsonify(templates)
    except Exception as e:
        logger.error(f"Error getting config templates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/templates/<template_id>')
def get_config_template(template_id):
    """Get a specific configuration template"""
    try:
        from services.config_service import ConfigurationService
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        templates = config_service.get_templates()
        
        template = next((t for t in templates if t.get('id') == template_id), None)
        if template:
            return jsonify(template)
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        logger.error(f"Error getting config template: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/templates', methods=['POST'])
def create_config_template():
    """Create a new configuration template"""
    try:
        from services.config_service import ConfigurationService
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Template name is required'}), 400
        
        template_id = config_service.create_template(data)
        return jsonify({'id': template_id, 'message': 'Template created successfully'}), 201
    except Exception as e:
        logger.error(f"Error creating config template: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    """Validate a configuration"""
    try:
        from services.config_service import ConfigurationService
        from services.integration_plugins import create_default_plugins
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        
        # Register default plugins
        for name, plugin in create_default_plugins().items():
            config_service.register_plugin(name, plugin)
        
        data = request.get_json()
        config_type = data.get('type')
        config = data.get('config')
        
        if not config_type or not config:
            return jsonify({'error': 'Both type and config are required'}), 400
        
        is_valid, error = config_service.validate_config(config_type, config)
        
        return jsonify({
            'valid': is_valid,
            'error': error,
            'type': config_type
        })
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/integrations/test', methods=['POST'])
def test_integration():
    """Test an integration configuration"""
    try:
        from services.config_service import ConfigurationService
        from services.integration_plugins import create_default_plugins
        
        config_service = ConfigurationService(Config.DATA_FOLDER)
        
        # Register default plugins
        plugins = create_default_plugins()
        for name, plugin in plugins.items():
            config_service.register_plugin(name, plugin)
        
        data = request.get_json()
        integration_type = data.get('type')
        config = data.get('config')
        
        if not integration_type or not config:
            return jsonify({'error': 'Both type and config are required'}), 400
        
        if integration_type not in plugins:
            return jsonify({'error': f'Unknown integration type: {integration_type}'}), 400
        
        # First validate the configuration
        is_valid, error = plugins[integration_type].validate_config(config)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error,
                'type': integration_type
            })
        
        # Mock test results for now
        test_results = {
            'jira': {
                'connection': True,
                'project_access': True,
                'create_permission': True,
                'message': 'Successfully connected to Jira'
            },
            'slack': {
                'connection': True,
                'channel_access': True,
                'message': 'Successfully connected to Slack'
            },
            'email': {
                'connection': True,
                'smtp_auth': True,
                'message': 'Successfully connected to email server'
            },
            'teams': {
                'connection': True,
                'webhook_valid': True,
                'message': 'Successfully connected to Teams'
            }
        }
        
        result = test_results.get(integration_type, {
            'connection': False,
            'message': 'Test not implemented'
        })
        
        return jsonify({
            'success': result.get('connection', False),
            'type': integration_type,
            'details': result
        })
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        return jsonify({'error': str(e)}), 500

# Credentials Management APIs
@app.route('/api/credentials')
def get_credentials():
    """Get all credentials"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        credentials = credentials_service.get_all_credentials()
        return jsonify(credentials)
    except Exception as e:
        logger.error(f"Error getting credentials: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials/<credential_id>')
def get_credential(credential_id):
    """Get a specific credential"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        credential = credentials_service.get_credential(credential_id)
        if credential:
            return jsonify(credential)
        else:
            return jsonify({'error': 'Credential not found'}), 404
    except Exception as e:
        logger.error(f"Error getting credential: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials', methods=['POST'])
def create_credential():
    """Create a new credential"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        data = request.get_json()
        credential = credentials_service.create_credential(data)
        return jsonify(credential), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating credential: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials/<credential_id>', methods=['PUT'])
def update_credential(credential_id):
    """Update a credential"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        data = request.get_json()
        if credentials_service.update_credential(credential_id, data):
            return jsonify({'message': 'Credential updated successfully'})
        else:
            return jsonify({'error': 'Credential not found'}), 404
    except Exception as e:
        logger.error(f"Error updating credential: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials/<credential_id>', methods=['DELETE'])
def delete_credential(credential_id):
    """Delete a credential"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        if credentials_service.delete_credential(credential_id):
            return jsonify({'message': 'Credential deleted successfully'})
        else:
            return jsonify({'error': 'Credential not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting credential: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials/<credential_id>/test', methods=['POST'])
def test_credential(credential_id):
    """Test a credential connection"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        result = credentials_service.test_credential(credential_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing credential: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/credentials/types')
def get_credential_types():
    """Get all credential types and their schemas"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        types = credentials_service.get_credential_types()
        return jsonify(types)
    except Exception as e:
        logger.error(f"Error getting credential types: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials/search')
def search_credentials():
    """Search credentials"""
    try:
        from services.credentials_service import CredentialsService
        credentials_service = CredentialsService(Config.DATA_FOLDER)
        query = request.args.get('q', '')
        credentials = credentials_service.search_credentials(query)
        return jsonify(credentials)
    except Exception as e:
        logger.error(f"Error searching credentials: {e}")
        return jsonify({'error': str(e)}), 500

# Orchestration Endpoints
@app.route('/api/orchestration/info')
def get_orchestration_info():
    """Get information about prompt orchestration"""
    try:
        from services.prompt_orchestrator import prompt_orchestrator
        info = prompt_orchestrator.get_orchestration_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting orchestration info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orchestration/validate', methods=['POST'])
def validate_orchestration():
    """Validate orchestration for specific agent/capability/targets"""
    try:
        from services.prompt_orchestrator import prompt_orchestrator
        data = request.get_json()
        
        agent = data.get('agent', '')
        capability = data.get('capability', '')
        targets = data.get('targets', [])
        
        if not agent or not capability:
            return jsonify({'error': 'Agent and capability are required'}), 400
            
        result = prompt_orchestrator.validate_orchestration(agent, capability, targets)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error validating orchestration: {e}")
        return jsonify({'error': str(e)}), 500

# Task Execution Endpoints
@app.route('/api/jobs/<job_id>/stages/<stage_id>/tasks/<int:task_index>/execute', methods=['POST'])
def execute_task(job_id, stage_id, task_index):
    """Execute a specific task within a job stage"""
    try:
        from services.jobs_service import JobsService
        from services.execution_service import execution_service
        
        jobs_service = JobsService(Config.DATA_FOLDER)
        
        # Get job details
        job = jobs_service.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        # Find the stage and task
        stage = next((s for s in job.get('stages', []) if s['id'] == stage_id), None)
        if not stage:
            return jsonify({'error': 'Stage not found'}), 404
            
        if task_index >= len(stage.get('tasks', [])):
            return jsonify({'error': 'Task not found'}), 404
            
        task = stage['tasks'][task_index]
        
        # Get source information for working directory
        source = sources_service.get_source(job.get('source_id'))
        source_path = None
        
        if source:
            # The source path is stored in the 'path' field for both local and GitHub sources
            source_path = source.get('path')
            
        # Create task folder paths
        task_name = task.get('name', 'unknown').lower().replace(' ', '_')
        task_folder = os.path.join(Config.DATA_FOLDER, 'jobs', job_id, stage_id, f"{task_index}_{task_name}")
        task_input_folder = os.path.join(task_folder, 'input')
        task_output_folder = os.path.join(task_folder, 'output')
        
        # Ensure task folders exist
        os.makedirs(task_input_folder, exist_ok=True)
        os.makedirs(task_output_folder, exist_ok=True)
        
        # Copy source code to task input folder if source exists
        if source_path and os.path.exists(source_path):
            # For Code Architect analyze source task, copy the source to input folder
            if 'architect' in task.get('agent', '').lower() and 'analyze' in task.get('name', '').lower():
                logger.info(f"Copying source from {source_path} to {task_input_folder}")
                
                # Clear the input folder first
                for item in os.listdir(task_input_folder):
                    item_path = os.path.join(task_input_folder, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                
                # Copy all contents from source to input folder
                for item in os.listdir(source_path):
                    src_item = os.path.join(source_path, item)
                    dst_item = os.path.join(task_input_folder, item)
                    if os.path.isdir(src_item):
                        shutil.copytree(src_item, dst_item)
                    else:
                        shutil.copy2(src_item, dst_item)
                        
                logger.info(f"Source code copied to task input folder: {task_input_folder}")
        
        # Use task input folder as working directory for analyze tasks
        if 'architect' in task.get('agent', '').lower() and 'analyze' in task.get('name', '').lower():
            working_directory = task_input_folder
        else:
            # For other tasks, use the source path or current directory
            working_directory = source_path if source_path and os.path.exists(source_path) else os.getcwd()
        
        # Prepare execution context
        context = {
            'job_id': job_id,
            'job_name': job.get('name', ''),
            'source_id': job.get('source_id', ''),
            'source_name': job.get('source_name', ''),
            'source_type': job.get('source_type', ''),
            'target_id': job.get('target_id', ''),
            'target_name': job.get('target_name', ''),
            'target_type': job.get('target_type', ''),
            'stage_id': stage_id,
            'stage_name': stage.get('name', ''),
            'task_name': task.get('name', ''),
            'agent': task.get('agent', ''),
            'capability': task.get('name', '').lower().replace(' ', '_'),
            'task_config': task.get('config', {}),
            'working_directory': working_directory,
            'task_folder': task_folder,
            'task_input_folder': task_input_folder,
            'task_output_folder': task_output_folder
        }
        
        # Execute the task
        result = execution_service.execute_task(job_id, stage_id, task_index, task, context)
        
        # Update task status based on execution result
        if result['status'] == 'success':
            task['status'] = 'completed'
        else:
            task['status'] = 'failed'
            
        # Save updated job
        jobs_service.update_job(job_id, job)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/executions/<execution_id>')
def get_execution_details(execution_id):
    """Get details of a specific execution"""
    try:
        from services.execution_service import execution_service
        
        execution = execution_service.get_execution_details(execution_id)
        if execution:
            return jsonify(execution)
        else:
            return jsonify({'error': 'Execution not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting execution details: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/executions')
def get_job_executions(job_id):
    """Get all executions for a specific job"""
    try:
        from services.execution_service import execution_service
        
        executions = execution_service.get_execution_history(job_id)
        return jsonify(executions)
        
    except Exception as e:
        logger.error(f"Error getting job executions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>/tasks/<int:task_index>/output')
def get_task_output(job_id, stage_id, task_index):
    """Get the output for a specific task"""
    try:
        from services.execution_service import execution_service
        
        output = execution_service.get_task_output(job_id, stage_id, task_index)
        if output:
            return jsonify(output)
        else:
            return jsonify({'error': 'No output found for this task'}), 404
            
    except Exception as e:
        logger.error(f"Error getting task output: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>/tasks/<int:task_index>/files')
def get_task_files(job_id, stage_id, task_index):
    """Get the file structure for a task's folders"""
    try:
        from services.jobs_service import JobsService
        import json
        
        jobs_service = JobsService(Config.DATA_FOLDER)
        job = jobs_service.get_job(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        # Find the task
        stage = next((s for s in job.get('stages', []) if s['id'] == stage_id), None)
        if not stage or task_index >= len(stage.get('tasks', [])):
            return jsonify({'error': 'Task not found'}), 404
            
        task = stage['tasks'][task_index]
        task_name = task.get('name', 'unknown').lower().replace(' ', '_')
        
        # Build task folder path
        task_folder = os.path.join(Config.DATA_FOLDER, 'jobs', job_id, stage_id, f"{task_index}_{task_name}")
        
        # Get folder structure
        folder_structure = {
            'task_name': task['name'],
            'task_folder': task_folder,
            'folders': {}
        }
        
        # Check each subfolder
        for subfolder in ['input', 'output', 'data']:
            subfolder_path = os.path.join(task_folder, subfolder)
            if os.path.exists(subfolder_path):
                folder_structure['folders'][subfolder] = _get_folder_tree(subfolder_path, max_depth=3)
            else:
                folder_structure['folders'][subfolder] = {'exists': False}
                
        return jsonify(folder_structure)
        
    except Exception as e:
        logger.error(f"Error getting task files: {e}")
        return jsonify({'error': str(e)}), 500

def _get_folder_tree(path: str, current_depth: int = 0, max_depth: int = 3) -> dict:
    """Get folder tree structure with limited depth"""
    if current_depth >= max_depth:
        return {'type': 'folder', 'truncated': True}
        
    result = {
        'type': 'folder' if os.path.isdir(path) else 'file',
        'name': os.path.basename(path),
        'path': path
    }
    
    if os.path.isdir(path):
        result['children'] = []
        try:
            items = sorted(os.listdir(path))
            for item in items:
                if item.startswith('.'):
                    continue
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    child = _get_folder_tree(item_path, current_depth + 1, max_depth)
                    result['children'].append(child)
                else:
                    # For files, include size
                    try:
                        size = os.path.getsize(item_path)
                        result['children'].append({
                            'type': 'file',
                            'name': item,
                            'path': item_path,
                            'size': size
                        })
                    except:
                        result['children'].append({
                            'type': 'file',
                            'name': item,
                            'path': item_path
                        })
        except PermissionError:
            result['error'] = 'Permission denied'
    else:
        # For files, include size
        try:
            result['size'] = os.path.getsize(path)
        except:
            pass
            
    return result

@app.route('/api/jobs/<job_id>/files/content', methods=['POST'])
def get_file_content(job_id):
    """Get content of a specific file"""
    try:
        data = request.get_json()
        file_path = data.get('path')
        
        if not file_path:
            return jsonify({'error': 'File path required'}), 400
            
        # Security check - ensure file is within job folder
        jobs_folder = os.path.join(Config.DATA_FOLDER, 'jobs', job_id)
        abs_file_path = os.path.abspath(file_path)
        abs_jobs_folder = os.path.abspath(jobs_folder)
        
        if not abs_file_path.startswith(abs_jobs_folder):
            return jsonify({'error': 'Access denied'}), 403
            
        if not os.path.exists(abs_file_path):
            return jsonify({'error': 'File not found'}), 404
            
        # Read file content
        try:
            with open(abs_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Limit content size for UI
            max_size = 1024 * 1024  # 1MB
            if len(content) > max_size:
                content = content[:max_size] + "\n\n... [Content truncated]"
                
            return jsonify({
                'path': file_path,
                'name': os.path.basename(file_path),
                'content': content,
                'size': os.path.getsize(abs_file_path)
            })
        except UnicodeDecodeError:
            return jsonify({
                'path': file_path,
                'name': os.path.basename(file_path),
                'content': '[Binary file]',
                'binary': True,
                'size': os.path.getsize(abs_file_path)
            })
            
    except Exception as e:
        logger.error(f"Error reading file content: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/stages/<stage_id>/tasks/<int:task_index>/logs')
def get_task_logs(job_id, stage_id, task_index):
    """Get execution logs for a specific task"""
    try:
        from services.execution_service import execution_service
        from services.jobs_service import JobsService
        
        jobs_service = JobsService(Config.DATA_FOLDER)
        job = jobs_service.get_job(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        # Find the task
        stage = next((s for s in job.get('stages', []) if s['id'] == stage_id), None)
        if not stage or task_index >= len(stage.get('tasks', [])):
            return jsonify({'error': 'Task not found'}), 404
            
        task = stage['tasks'][task_index]
        
        # Get logs from execution service
        logs = execution_service.get_task_logs(job_id, stage_id, task_index)
        
        # Determine status
        status = task.get('status', 'pending')
        if status == 'pending' and logs:
            status = 'running'
        
        return jsonify({
            'status': status,
            'logs': logs,
            'task_name': task.get('name', ''),
            'agent': task.get('agent', '')
        })
        
    except Exception as e:
        logger.error(f"Error getting task logs: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Any-to-Any Conversion Studio v2 on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)