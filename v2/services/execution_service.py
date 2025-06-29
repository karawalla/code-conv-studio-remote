"""
Execution Service for running agent tasks using prompt templates
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import tempfile

class ExecutionService:
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / 'prompts'
        self.executions = {}
        self.execution_logs = []
        
    def execute_task(self, job_id: str, stage_id: str, task_index: int, task: Dict[str, Any], job_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task using prompt templates
        
        Args:
            job_id: The job ID
            stage_id: The stage ID
            task_index: Index of the task in the stage
            task: Task details including agent and capability
            job_context: Context including job details, source, target, etc.
            
        Returns:
            Execution result dictionary
        """
        execution_id = f"{job_id}_{stage_id}_{task_index}_{datetime.now().timestamp()}"
        
        # Extract task details
        agent_name = task.get('agent', '').lower().replace(' ', '_')
        capability = task.get('name', '').lower().replace(' ', '_')
        
        # Find prompt files for this agent/capability
        prompt_dir = self.prompts_dir / agent_name / capability
        
        if not prompt_dir.exists():
            return {
                'execution_id': execution_id,
                'status': 'error',
                'error': f'No prompts found for {agent_name}/{capability}',
                'timestamp': datetime.now().isoformat()
            }
        
        # Get all markdown files in the directory, sorted by name
        prompt_files = sorted(prompt_dir.glob('*.md'))
        
        if not prompt_files:
            return {
                'execution_id': execution_id,
                'status': 'error', 
                'error': f'No prompt files found in {prompt_dir}',
                'timestamp': datetime.now().isoformat()
            }
        
        # Execute each prompt file in sequence
        results = []
        overall_status = 'success'
        
        for prompt_file in prompt_files:
            result = self._execute_prompt(prompt_file, job_context, task)
            results.append(result)
            
            if result['status'] == 'error':
                overall_status = 'error'
                break  # Stop on first error
                
        execution_result = {
            'execution_id': execution_id,
            'job_id': job_id,
            'stage_id': stage_id,
            'task_index': task_index,
            'agent': agent_name,
            'capability': capability,
            'status': overall_status,
            'prompt_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store execution history
        self.executions[execution_id] = execution_result
        self.execution_logs.append(execution_result)
        
        return execution_result
    
    def _execute_prompt(self, prompt_file: Path, context: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single prompt file using Claude
        
        Args:
            prompt_file: Path to the prompt markdown file
            context: Job context for variable substitution
            task: Task details
            
        Returns:
            Execution result for this prompt
        """
        try:
            # Read prompt content
            with open(prompt_file, 'r') as f:
                prompt_content = f.read()
            
            # Replace template variables
            prompt_content = self._substitute_variables(prompt_content, context)
            
            # Prepare the command to execute with Claude
            result = self._execute_with_claude(prompt_content, context)
            
            return {
                'prompt_file': str(prompt_file.name),
                'status': 'success' if result.get('success') else 'error',
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'prompt_file': str(prompt_file.name),
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _substitute_variables(self, content: str, context: Dict[str, Any]) -> str:
        """
        Replace template variables in prompt content
        
        Variables are in format {{variable_name}}
        """
        # Find all variables in the content
        variables = re.findall(r'\{\{(\w+)\}\}', content)
        
        for var in variables:
            value = context.get(var, f'[{var}]')
            content = content.replace(f'{{{{{var}}}}}', str(value))
        
        return content
    
    def _execute_with_claude(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the prompt using Claude via command line
        
        This is where we'll integrate with claude-cli or API
        """
        # For now, we'll create a mock implementation
        # In production, this would call claude-cli or use Claude API
        
        try:
            # Create a temporary file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Mock response for demonstration
            # In real implementation, this would be:
            # cmd = ['claude', 'run', prompt_file]
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            mock_output = f"""
# Execution Result

## Task: {context.get('task_name', 'Unknown')}
## Status: Success

### Analysis
Successfully analyzed the prompt and would execute the following:
- Agent: {context.get('agent', 'Unknown')}
- Capability: {context.get('capability', 'Unknown')}
- Source: {context.get('source_name', 'Unknown')}
- Target: {context.get('target_name', 'Unknown')}

### Next Steps
1. Implement actual Claude CLI integration
2. Process the response
3. Update job status

### Mock Output
This is a mock execution. In production, this would:
1. Call claude-cli with the prompt
2. Process the response
3. Execute any code changes
4. Return structured results
"""
            
            # Clean up
            os.unlink(prompt_file)
            
            return {
                'success': True,
                'output': mock_output
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_execution_history(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get execution history, optionally filtered by job_id"""
        if job_id:
            return [e for e in self.execution_logs if e.get('job_id') == job_id]
        return self.execution_logs
    
    def get_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific execution"""
        return self.executions.get(execution_id)

# Global instance
execution_service = ExecutionService()