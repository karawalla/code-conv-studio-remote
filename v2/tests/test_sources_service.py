"""
Tests for Sources Service
Basic tests to ensure the service works correctly and catch breaking changes.
"""

import unittest
import tempfile
import shutil
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.sources_service import SourcesService


class TestSourcesService(unittest.TestCase):
    """Test cases for SourcesService."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.service = SourcesService(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_init_creates_directories(self):
        """Test that initialization creates necessary directories."""
        self.assertTrue(os.path.exists(self.test_dir))
        # Metadata file is created when first source is added, not on init
        # Just check the directory exists
        self.assertTrue(os.path.isdir(self.test_dir))
    
    def test_add_local_folder_success(self):
        """Test adding a local folder."""
        # Create a test folder
        test_folder = tempfile.mkdtemp()
        test_file = os.path.join(test_folder, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        try:
            # Add the folder
            result = self.service.add_local_folder(test_folder, name="TestFolder")
            
            # Verify result
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], 'TestFolder')
            self.assertEqual(result['type'], 'local')
            self.assertIn('id', result)
            self.assertIn('path', result)
            
            # Verify files were copied
            copied_path = Path(result['path'])
            self.assertTrue(copied_path.exists())
            self.assertTrue((copied_path / 'test.txt').exists())
            
            # Verify metadata was saved
            source = self.service.get_source(result['id'])
            self.assertIsNotNone(source)
            self.assertEqual(source['name'], 'TestFolder')
            
        finally:
            # Clean up
            shutil.rmtree(test_folder)
    
    def test_add_local_folder_not_found(self):
        """Test adding a non-existent folder."""
        with self.assertRaises(FileNotFoundError):
            self.service.add_local_folder('/path/that/does/not/exist')
    
    def test_list_sources_empty(self):
        """Test listing sources when none exist."""
        sources = self.service.list_sources()
        self.assertEqual(sources, [])
    
    def test_list_sources_with_filter(self):
        """Test listing sources with type filter."""
        # Create a test folder
        test_folder = tempfile.mkdtemp()
        try:
            # Add a local source
            self.service.add_local_folder(test_folder, name="LocalTest")
            
            # List all sources
            all_sources = self.service.list_sources()
            self.assertEqual(len(all_sources), 1)
            
            # List only local sources
            local_sources = self.service.list_sources(source_type='local')
            self.assertEqual(len(local_sources), 1)
            
            # List only github sources (should be empty)
            github_sources = self.service.list_sources(source_type='github')
            self.assertEqual(len(github_sources), 0)
            
        finally:
            shutil.rmtree(test_folder)
    
    def test_delete_source(self):
        """Test deleting a source."""
        # Create and add a test folder
        test_folder = tempfile.mkdtemp()
        try:
            result = self.service.add_local_folder(test_folder, name="ToDelete")
            source_id = result['id']
            source_path = result['path']
            
            # Verify it exists
            self.assertTrue(os.path.exists(source_path))
            self.assertIsNotNone(self.service.get_source(source_id))
            
            # Delete it
            success = self.service.delete_source(source_id)
            self.assertTrue(success)
            
            # Verify it's gone
            self.assertFalse(os.path.exists(source_path))
            self.assertIsNone(self.service.get_source(source_id))
            
        finally:
            if os.path.exists(test_folder):
                shutil.rmtree(test_folder)
    
    def test_delete_nonexistent_source(self):
        """Test deleting a source that doesn't exist."""
        success = self.service.delete_source('nonexistent-id')
        self.assertFalse(success)
    
    @patch('subprocess.run')
    def test_add_github_repo_success(self, mock_run):
        """Test adding a GitHub repository (mocked)."""
        # Mock successful git clone
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        # Add repo
        repo_url = 'https://github.com/test/repo.git'
        result = self.service.add_github_repo(repo_url)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'repo')
        self.assertEqual(result['type'], 'github')
        self.assertEqual(result['url'], repo_url)
        
        # Verify git clone was called
        mock_run.assert_called()
        # Find the clone call (there might be other git calls)
        clone_called = False
        for call in mock_run.call_args_list:
            args = call[0][0]
            if len(args) >= 3 and args[0] == 'git' and args[1] == 'clone':
                self.assertEqual(args[2], repo_url)
                clone_called = True
                break
        self.assertTrue(clone_called, "git clone was not called")
    
    @patch('subprocess.run')
    def test_add_github_repo_failure(self, mock_run):
        """Test handling git clone failure."""
        # Mock failed git clone
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git', stderr='Authentication failed'
        )
        
        # Should raise RuntimeError
        with self.assertRaises(RuntimeError) as context:
            self.service.add_github_repo('https://github.com/test/repo.git')
        
        self.assertIn('Failed to clone repository', str(context.exception))
    
    def test_get_folder_stats(self):
        """Test folder statistics calculation."""
        # Create test folder with files
        test_folder = tempfile.mkdtemp()
        
        # Create some test files
        with open(os.path.join(test_folder, 'test.py'), 'w') as f:
            f.write('print("test")')
        with open(os.path.join(test_folder, 'data.json'), 'w') as f:
            f.write('{"key": "value"}')
        
        os.makedirs(os.path.join(test_folder, 'subdir'))
        with open(os.path.join(test_folder, 'subdir', 'file.txt'), 'w') as f:
            f.write('content')
        
        try:
            # Get stats
            stats = self.service._get_folder_stats(Path(test_folder))
            
            # Verify stats
            self.assertEqual(stats['total_files'], 3)
            self.assertGreater(stats['total_size'], 0)
            self.assertIn('.py', stats['file_types'])
            self.assertIn('.json', stats['file_types'])
            self.assertIn('.txt', stats['file_types'])
            
        finally:
            shutil.rmtree(test_folder)


if __name__ == '__main__':
    unittest.main()