#!/usr/bin/env python3
"""
Test script for Claude execution in v2
"""
import os
import sys
import logging

# Add the v2 directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.claude_auth_v2 import create_claude_auth_manager_v2, ClaudeSessionManagerV2
from services.execution_service import ExecutionService

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_claude_auth():
    """Test Claude authentication"""
    try:
        logger.info("Testing Claude authentication...")
        auth_manager = create_claude_auth_manager_v2()
        
        # Test authentication
        if auth_manager.test_authentication():
            logger.info("✅ Claude authentication successful!")
            return True
        else:
            logger.error("❌ Claude authentication failed!")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing authentication: {e}")
        return False

def test_simple_execution():
    """Test simple Claude execution"""
    try:
        logger.info("Testing simple Claude execution...")
        
        # Create a simple test context
        test_context = {
            'job_id': 'test_job_1',
            'job_name': 'Test Job',
            'source_name': 'Test Source',
            'source_type': 'github',
            'target_name': 'Python',
            'target_type': 'python',
            'working_directory': os.getcwd()
        }
        
        # Create a simple test task
        test_task = {
            'name': 'Test Task',
            'agent': 'Code Architect',
            'configuration': {
                'test_param': 'test_value'
            }
        }
        
        # Initialize execution service
        exec_service = ExecutionService()
        
        # Test with a simple prompt
        from pathlib import Path
        import tempfile
        
        # Create a temporary prompt file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Test Prompt
This is a test prompt to verify Claude execution is working.

Please respond with:
1. Confirmation that you received this prompt
2. The current working directory
3. A simple greeting

Source: {{source_name}}
Target: {{target_name}}
""")
            temp_prompt = f.name
        
        try:
            # Execute the prompt
            result = exec_service._execute_prompt(Path(temp_prompt), test_context, test_task)
            
            if result['status'] == 'success':
                logger.info("✅ Claude execution successful!")
                logger.info(f"Output:\n{result['output']}")
                return True
            else:
                logger.error(f"❌ Claude execution failed: {result.get('error', 'Unknown error')}")
                return False
        finally:
            # Clean up
            os.unlink(temp_prompt)
            
    except Exception as e:
        logger.error(f"❌ Error testing execution: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Claude execution tests for v2...")
    
    # Test 1: Authentication
    auth_ok = test_claude_auth()
    
    # Test 2: Simple execution
    exec_ok = test_simple_execution()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("Test Summary:")
    logger.info(f"Authentication: {'✅ PASSED' if auth_ok else '❌ FAILED'}")
    logger.info(f"Execution: {'✅ PASSED' if exec_ok else '❌ FAILED'}")
    logger.info("="*50)
    
    return auth_ok and exec_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)