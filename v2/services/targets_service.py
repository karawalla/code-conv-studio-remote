"""
Targets Service
Manages target configurations for code conversion including prompts
"""

import os
import json
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TargetsService:
    """Service for managing conversion targets"""
    
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.targets_file = os.path.join(data_folder, 'targets_metadata.json')
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure targets metadata file exists"""
        if not os.path.exists(self.targets_file):
            with open(self.targets_file, 'w') as f:
                json.dump({'targets': {}}, f, indent=2)
    
    def _load_targets(self):
        """Load targets from metadata file"""
        try:
            with open(self.targets_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading targets: {e}")
            return {'targets': {}}
    
    def _save_targets(self, data):
        """Save targets to metadata file"""
        try:
            with open(self.targets_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving targets: {e}")
            return False
    
    def get_all_targets(self):
        """Get all configured targets"""
        data = self._load_targets()
        targets = []
        
        for target_id, target in data.get('targets', {}).items():
            targets.append({
                'id': target_id,
                'name': target.get('name', 'Unnamed Target'),
                'description': target.get('description', ''),
                'active': target.get('active', True),
                'created_at': target.get('created_at', ''),
                'updated_at': target.get('updated_at', ''),
                'prompts': target.get('prompts', self._get_default_prompts()),
                'knowledge_store': target.get('knowledge_store', [])
            })
        
        return sorted(targets, key=lambda x: x['created_at'], reverse=True)
    
    def get_target(self, target_id):
        """Get a specific target by ID"""
        data = self._load_targets()
        target = data.get('targets', {}).get(target_id)
        
        if not target:
            return None
        
        return {
            'id': target_id,
            'name': target.get('name', 'Unnamed Target'),
            'framework': target.get('framework', ''),
            'description': target.get('description', ''),
            'active': target.get('active', True),
            'created_at': target.get('created_at', ''),
            'updated_at': target.get('updated_at', ''),
            'prompts': target.get('prompts', self._get_default_prompts()),
            'knowledge_store': target.get('knowledge_store', [])
        }
    
    def _get_default_prompts(self):
        """Get default prompts for a new target"""
        return {
            'analyze': 'Analyze the source code architecture, patterns, and dependencies to understand the current implementation.',
            'plan': 'Create a detailed migration plan to convert from the source framework to {framework}, including steps, timeline, and potential challenges.',
            'migrate': 'Convert the following code from the source framework to {framework}, maintaining functionality while following {framework} best practices.',
            'validate': 'Validate the migrated code for correctness, performance, and adherence to {framework} conventions. Identify any issues or improvements.',
            'fix': 'Fix the identified issues in the migrated code and ensure it follows {framework} best practices and patterns.',
            'discuss': 'Discuss the migration approach, trade-offs, and alternative solutions for converting to {framework}.'
        }
    
    def create_target(self, name, description='', prompts=None):
        """Create a new target configuration"""
        try:
            data = self._load_targets()
            target_id = str(uuid.uuid4())
            
            # Use provided prompts or defaults
            if prompts is None:
                prompts = self._get_default_prompts()
            
            # Replace {framework} placeholder in prompts with target name
            for key, prompt in prompts.items():
                prompts[key] = prompt.replace('{framework}', name)
            
            target = {
                'id': target_id,
                'name': name,
                'description': description,
                'active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'prompts': prompts,
                'knowledge_store': []
            }
            
            data['targets'][target_id] = target
            
            if self._save_targets(data):
                logger.info(f"Created target: {name} ({target_id})")
                return target
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating target: {e}")
            return None
    
    def update_target(self, target_id, updates):
        """Update an existing target"""
        try:
            data = self._load_targets()
            
            if target_id not in data['targets']:
                return None
            
            target = data['targets'][target_id]
            
            # Update allowed fields
            allowed_fields = ['name', 'description', 'active', 'prompts', 'knowledge_store']
            for field in allowed_fields:
                if field in updates:
                    if field == 'prompts':
                        # Merge prompt updates
                        target['prompts'].update(updates['prompts'])
                    else:
                        target[field] = updates[field]
            
            target['updated_at'] = datetime.now().isoformat()
            
            if self._save_targets(data):
                logger.info(f"Updated target: {target_id}")
                return self.get_target(target_id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error updating target: {e}")
            return None
    
    def delete_target(self, target_id):
        """Delete a target"""
        try:
            data = self._load_targets()
            
            if target_id not in data['targets']:
                return False
            
            del data['targets'][target_id]
            
            if self._save_targets(data):
                logger.info(f"Deleted target: {target_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error deleting target: {e}")
            return False
    
    def get_default_targets(self):
        """Get list of default target templates"""
        return [
            {
                'name': 'Python',
                'description': 'Python frameworks and libraries including Django, FastAPI, Flask',
                'icon': '🐍'
            },
            {
                'name': 'Java',
                'description': 'Java frameworks including Spring Boot, Spring MVC, Jakarta EE',
                'icon': '☕'
            },
            {
                'name': 'JavaScript',
                'description': 'JavaScript/TypeScript frameworks including React, Vue, Angular, Node.js',
                'icon': '🟨'
            },
            {
                'name': 'C#/.NET',
                'description': '.NET frameworks including ASP.NET Core, Blazor, WPF',
                'icon': '🔷'
            },
            {
                'name': 'Ruby',
                'description': 'Ruby frameworks including Ruby on Rails, Sinatra',
                'icon': '💎'
            },
            {
                'name': 'PHP',
                'description': 'PHP frameworks including Laravel, Symfony, CodeIgniter',
                'icon': '🐘'
            },
            {
                'name': 'Go',
                'description': 'Go frameworks including Gin, Echo, Fiber',
                'icon': '🐹'
            },
            {
                'name': 'Rust',
                'description': 'Rust frameworks including Actix, Rocket, Axum',
                'icon': '🦀'
            }
        ]