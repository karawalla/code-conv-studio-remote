"""
Sources Service
Handles repository cloning and local folder management for the conversion studio.
"""

import os
import shutil
import subprocess
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SourcesService:
    """Service for managing source code repositories and folders."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the sources service.
        
        Args:
            data_dir: Base directory for storing sources. Defaults to v2/data/sources
        """
        if data_dir is None:
            # Get the base directory relative to this file
            base_dir = Path(__file__).parent.parent
            data_dir = os.path.join(base_dir, 'data', 'sources')
        
        self.data_dir = Path(data_dir)
        self.metadata_file = self.data_dir / 'sources_metadata.json'
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load sources metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {'sources': {}}
        return {'sources': {}}
    
    def _save_metadata(self):
        """Save sources metadata to JSON file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise
    
    def add_github_repo(self, repo_url: str, name: Optional[str] = None) -> Dict:
        """
        Clone a GitHub repository to local storage.
        
        Args:
            repo_url: GitHub repository URL (supports both HTTPS and SSH)
            name: Optional custom name for the source
            
        Returns:
            Dict containing source information
            
        Raises:
            ValueError: If repo URL is invalid
            RuntimeError: If cloning fails
        """
        # Validate URL
        if not repo_url:
            raise ValueError("Repository URL cannot be empty")
        
        # Extract repo name if not provided
        if name is None:
            # Extract from URL: https://github.com/user/repo.git -> repo
            name = repo_url.rstrip('/').split('/')[-1]
            if name.endswith('.git'):
                name = name[:-4]
        
        # Generate unique ID
        source_id = str(uuid.uuid4())
        source_path = self.data_dir / source_id
        
        try:
            # Clone the repository
            logger.info(f"Cloning repository {repo_url} to {source_path}")
            result = subprocess.run(
                ['git', 'clone', repo_url, str(source_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get repository info
            repo_info = self._get_git_info(source_path)
            
            # Create metadata entry
            source_data = {
                'id': source_id,
                'name': name,
                'type': 'github',
                'url': repo_url,
                'path': str(source_path),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'info': repo_info
            }
            
            # Save to metadata
            self.metadata['sources'][source_id] = source_data
            self._save_metadata()
            
            logger.info(f"Successfully cloned repository: {name}")
            return source_data
            
        except subprocess.CalledProcessError as e:
            # Clean up on failure
            if source_path.exists():
                shutil.rmtree(source_path)
            
            error_msg = f"Failed to clone repository: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            # Clean up on failure
            if source_path.exists():
                shutil.rmtree(source_path)
            raise
    
    def add_local_folder(self, folder_path: str, name: Optional[str] = None) -> Dict:
        """
        Copy a local folder to sources storage.
        
        Args:
            folder_path: Path to local folder
            name: Optional custom name for the source
            
        Returns:
            Dict containing source information
            
        Raises:
            ValueError: If folder path is invalid
            FileNotFoundError: If folder doesn't exist
        """
        folder_path = Path(folder_path)
        
        # Validate folder
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
        
        # Use folder name if name not provided
        if name is None:
            name = folder_path.name
        
        # Generate unique ID
        source_id = str(uuid.uuid4())
        source_path = self.data_dir / source_id
        
        try:
            # Copy folder
            logger.info(f"Copying folder {folder_path} to {source_path}")
            shutil.copytree(folder_path, source_path)
            
            # Check if it's a git repository
            is_git_repo = (source_path / '.git').exists()
            folder_info = {}
            
            if is_git_repo:
                folder_info = self._get_git_info(source_path)
            
            # Get folder statistics
            folder_info.update(self._get_folder_stats(source_path))
            
            # Create metadata entry
            source_data = {
                'id': source_id,
                'name': name,
                'type': 'local',
                'original_path': str(folder_path),
                'path': str(source_path),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'is_git_repo': is_git_repo,
                'info': folder_info
            }
            
            # Save to metadata
            self.metadata['sources'][source_id] = source_data
            self._save_metadata()
            
            logger.info(f"Successfully copied folder: {name}")
            return source_data
            
        except Exception as e:
            # Clean up on failure
            if source_path.exists():
                shutil.rmtree(source_path)
            raise
    
    def get_source(self, source_id: str) -> Optional[Dict]:
        """Get source information by ID."""
        return self.metadata['sources'].get(source_id)
    
    def list_sources(self, source_type: Optional[str] = None) -> List[Dict]:
        """
        List all sources, optionally filtered by type.
        
        Args:
            source_type: Filter by 'github' or 'local'. None returns all.
            
        Returns:
            List of source dictionaries
        """
        sources = list(self.metadata['sources'].values())
        
        if source_type:
            sources = [s for s in sources if s['type'] == source_type]
        
        # Sort by created date (newest first)
        sources.sort(key=lambda x: x['created_at'], reverse=True)
        
        return sources
    
    def delete_source(self, source_id: str) -> bool:
        """
        Delete a source and its files.
        
        Args:
            source_id: Source ID to delete
            
        Returns:
            True if deleted successfully
        """
        source = self.get_source(source_id)
        if not source:
            logger.warning(f"Source not found: {source_id}")
            return False
        
        try:
            # Remove files
            source_path = Path(source['path'])
            if source_path.exists():
                shutil.rmtree(source_path)
            
            # Remove from metadata
            del self.metadata['sources'][source_id]
            self._save_metadata()
            
            logger.info(f"Deleted source: {source['name']} ({source_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting source: {e}")
            return False
    
    def update_source(self, source_id: str) -> Optional[Dict]:
        """
        Update a source (pull latest for git repos).
        
        Args:
            source_id: Source ID to update
            
        Returns:
            Updated source data or None if failed
        """
        source = self.get_source(source_id)
        if not source:
            return None
        
        if source['type'] != 'github':
            logger.warning(f"Cannot update non-GitHub source: {source_id}")
            return source
        
        try:
            source_path = Path(source['path'])
            
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull'],
                cwd=source_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Update metadata
            source['updated_at'] = datetime.now().isoformat()
            source['info'] = self._get_git_info(source_path)
            
            self.metadata['sources'][source_id] = source
            self._save_metadata()
            
            logger.info(f"Updated source: {source['name']}")
            return source
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update source: {e.stderr}")
            return None
    
    def _get_git_info(self, repo_path: Path) -> Dict:
        """Get information about a git repository."""
        info = {}
        
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            info['branch'] = result.stdout.strip()
            
            # Get last commit
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%an|%ae|%s|%ai'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 5:
                    info['last_commit'] = {
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'message': parts[3],
                        'date': parts[4]
                    }
            
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info['remote_url'] = result.stdout.strip()
                
        except Exception as e:
            logger.warning(f"Error getting git info: {e}")
        
        return info
    
    def _get_folder_stats(self, folder_path: Path) -> Dict:
        """Get statistics about a folder."""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {}
        }
        
        try:
            for root, dirs, files in os.walk(folder_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = Path(root) / file
                    stats['total_files'] += 1
                    stats['total_size'] += file_path.stat().st_size
                    
                    # Count file extensions
                    ext = file_path.suffix.lower()
                    if ext:
                        stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
        
        except Exception as e:
            logger.warning(f"Error getting folder stats: {e}")
        
        return stats


class FileManager:
    """Utility class for file operations."""
    
    @staticmethod
    def get_file_tree(directory: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Get file tree structure for a directory.
        
        Args:
            directory: Directory path to scan
            max_depth: Maximum depth to traverse
            
        Returns:
            List of file/folder dictionaries
        """
        def _get_tree(path: Path, current_depth: int = 0) -> List[Dict[str, Any]]:
            if current_depth >= max_depth:
                return []
            
            tree = []
            try:
                for item in sorted(path.iterdir()):
                    # Skip hidden files and common ignore patterns
                    if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', '.git']:
                        continue
                    
                    if item.is_dir():
                        children = _get_tree(item, current_depth + 1)
                        tree.append({
                            'name': item.name,
                            'type': 'folder',
                            'children': children
                        })
                    else:
                        try:
                            stat = item.stat()
                            tree.append({
                                'name': item.name,
                                'type': 'file',
                                'size': stat.st_size
                            })
                        except:
                            # Skip files we can't stat
                            pass
            except PermissionError:
                # Skip directories we can't read
                pass
            
            return tree
        
        return _get_tree(Path(directory))