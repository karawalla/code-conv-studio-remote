"""
Execution Service for running agent tasks using prompt templates
"""
import os
import json
import re
import time
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import tempfile
import logging

from .claude_auth_v2 import create_claude_auth_manager_v2, ClaudeSessionManagerV2
from .prompt_orchestrator import prompt_orchestrator

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / 'prompts'
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.executions = {}
        self.execution_logs = []
        self.task_logs = {}  # Store logs by task key
        
        # Initialize Claude authentication
        try:
            self.auth_manager = create_claude_auth_manager_v2()
            self.session_manager = ClaudeSessionManagerV2(self.auth_manager)
            logger.info("Claude authentication manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude authentication: {e}")
            self.auth_manager = None
            self.session_manager = None
        
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
        target_name = job_context.get('target_name', '').lower()
        
        # Get orchestrated prompt sequence
        prompt_sequence = prompt_orchestrator.get_prompt_sequence(
            agent=agent_name,
            capability=capability,
            target=target_name
        )
        
        if not prompt_sequence:
            # Fallback to old behavior if no orchestration defined
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
            
            # Convert to orchestrated format for consistency
            prompt_sequence = [
                {
                    'type': 'agent',
                    'path': pf,
                    'file': pf.name,
                    'purpose': 'Agent task',
                    'agent': agent_name,
                    'capability': capability
                }
                for pf in prompt_files
            ]
        
        # Clear previous logs for this task
        task_key = f"{job_id}_{stage_id}_{task_index}"
        self.task_logs[task_key] = []
        
        # Add initial log
        self.add_task_log(job_id, stage_id, task_index, 'info', f'Starting execution of {task.get("name", "task")}')
        self.add_task_log(job_id, stage_id, task_index, 'info', f'Agent: {agent_name}, Capability: {capability}')
        
        # Execute each prompt in the orchestrated sequence
        results = []
        overall_status = 'success'
        
        logger.info(f"Executing orchestrated sequence of {len(prompt_sequence)} prompts for {agent_name}/{capability} -> {target_name}")
        self.add_task_log(job_id, stage_id, task_index, 'info', f'Found {len(prompt_sequence)} prompts to execute')
        
        for i, prompt_info in enumerate(prompt_sequence):
            # Log prompt execution
            self.add_task_log(job_id, stage_id, task_index, 'info', 
                             f'Executing prompt {i+1}/{len(prompt_sequence)}: {prompt_info.get("file", "prompt")}')
            
            # Add prompt metadata to context
            enhanced_context = {
                **job_context,
                'prompt_type': prompt_info['type'],
                'prompt_purpose': prompt_info['purpose']
            }
            
            if prompt_info['type'] == 'target':
                enhanced_context['target_prompt'] = prompt_info['file']
            else:
                enhanced_context['agent_prompt'] = prompt_info['file']
            
            result = self._execute_prompt(prompt_info['path'], enhanced_context, task, prompt_info, 
                                        job_id, stage_id, task_index)
            results.append(result)
            
            if result['status'] == 'error':
                overall_status = 'error'
                self.add_task_log(job_id, stage_id, task_index, 'error', 
                                 f'Prompt execution failed: {result.get("error", "Unknown error")}')
                break  # Stop on first error
            else:
                self.add_task_log(job_id, stage_id, task_index, 'info', 
                                 f'Prompt {i+1} completed successfully')
                
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
        
        # Save outputs to file system
        output_paths = self._save_execution_outputs(job_id, stage_id, task_index, task, results, job_context)
        execution_result['output_paths'] = output_paths
        
        # Store execution history
        self.executions[execution_id] = execution_result
        self.execution_logs.append(execution_result)
        
        # Final log
        if overall_status == 'success':
            self.add_task_log(job_id, stage_id, task_index, 'info', 
                             f'Task completed successfully! Executed {len(results)} prompts.')
        else:
            self.add_task_log(job_id, stage_id, task_index, 'error', 
                             f'Task failed. Check errors above.')
        
        return execution_result
    
    def _execute_prompt(self, prompt_file: Path, context: Dict[str, Any], task: Dict[str, Any], 
                       prompt_info: Optional[Dict[str, Any]] = None, job_id: str = None, 
                       stage_id: str = None, task_index: int = None) -> Dict[str, Any]:
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
            
            # Add context about the task and orchestration
            orchestration_context = ""
            if prompt_info:
                orchestration_context = f"""
# Prompt Orchestration Context
Prompt Type: {prompt_info.get('type', 'Unknown')}
Purpose: {prompt_info.get('purpose', 'Unknown')}
{'Target Framework: ' + prompt_info.get('target', '') if prompt_info.get('type') == 'target' else ''}
{'Agent: ' + prompt_info.get('agent', '') + ' | Capability: ' + prompt_info.get('capability', '') if prompt_info.get('type') == 'agent' else ''}

## Important Instructions:
{'''- This is a TARGET-SPECIFIC prompt. Follow the patterns and best practices for the target framework.
- Reference the source code and migration plan from previous steps.
- Ensure all code follows idiomatic patterns for the target framework.''' if prompt_info.get('type') == 'target' else '''- This is an AGENT-SPECIFIC prompt. Focus on the agent's role and responsibilities.
- If this capability involves target-specific work, subsequent prompts will handle target details.
- Prepare outputs that can be used by target-specific prompts.'''}
"""
            
            full_prompt = f"""# Task Execution Context
Current Task: {task.get('name', 'Unknown')}
Agent: {task.get('agent', 'Unknown')}
Source: {context.get('source_name', 'Unknown')} ({context.get('source_type', 'Unknown')})
Target: {context.get('target_name', 'Unknown')} ({context.get('target_type', 'Unknown')})
Working Directory: {context.get('working_directory', os.getcwd())}
{orchestration_context}
# Task Configuration
{json.dumps(task.get('configuration', {}), indent=2)}

# Original Prompt
{prompt_content}
"""
            
            # Prepare the command to execute with Claude
            result = self._execute_with_claude(full_prompt, context, job_id, stage_id, task_index)
            
            return {
                'prompt_file': str(prompt_file.name),
                'status': 'success' if result.get('success') else 'error',
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing prompt {prompt_file}: {e}")
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
    
    def _execute_with_claude(self, prompt: str, context: Dict[str, Any], job_id: str = None, 
                           stage_id: str = None, task_index: int = None) -> Dict[str, Any]:
        """
        Execute the prompt using Claude via command line
        """
        if not self.session_manager:
            return {
                'success': False,
                'error': 'Claude session manager not initialized. Please check Claude CLI installation.'
            }
        
        try:
            # Create a temporary file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Set working directory - use job's working directory if available
            working_dir = context.get('working_directory', os.getcwd())
            
            if job_id and stage_id is not None and task_index is not None:
                self.add_task_log(job_id, stage_id, task_index, 'info', f'Working directory: {working_dir}')
                self.add_task_log(job_id, stage_id, task_index, 'info', 'Starting Claude execution...')
            
            # Create message queue for output
            message_queue = queue.Queue()
            output_lines = []
            
            # Function to process Claude output
            def process_output(process):
                try:
                    for line in process.stdout:
                        if not line.strip():
                            continue
                        
                        try:
                            message = json.loads(line.strip())
                            
                            # Extract text content from assistant messages
                            if message.get("type") == "assistant":
                                for content in message.get("message", {}).get("content", []):
                                    if content.get("type") == "text":
                                        text = content.get("text", "").strip()
                                        if text:
                                            output_lines.append(text)
                                            message_queue.put({'type': 'message', 'content': text})
                                            if job_id and stage_id is not None and task_index is not None:
                                                # Log first 200 chars of assistant messages
                                                preview = text[:200] + "..." if len(text) > 200 else text
                                                self.add_task_log(job_id, stage_id, task_index, 'info', f'Claude: {preview}')
                            
                            # Handle tool use
                            elif message.get("type") == "tool_use":
                                tool_name = message.get('name', 'unknown')
                                message_queue.put({'type': 'tool', 'content': f'Using tool: {tool_name}'})
                                if job_id and stage_id is not None and task_index is not None:
                                    self.add_task_log(job_id, stage_id, task_index, 'debug', f'Tool use: {tool_name}')
                            
                            # Handle results
                            elif message.get("type") == "result":
                                subtype = message.get("subtype")
                                if subtype == "success":
                                    duration = message.get('duration_ms', 0) / 1000
                                    cost = message.get('total_cost_usd', 0)
                                    message_queue.put({
                                        'type': 'success',
                                        'content': f'Completed in {duration:.2f}s | Cost: ${cost:.4f}'
                                    })
                                else:
                                    error_msg = message.get('message', 'Unknown error')
                                    message_queue.put({'type': 'error', 'content': error_msg})
                                    
                        except json.JSONDecodeError:
                            # If not JSON, treat as raw output
                            if line.strip():
                                output_lines.append(line.strip())
                                
                except Exception as e:
                    logger.error(f"Error processing Claude output: {e}")
                    message_queue.put({'type': 'error', 'content': str(e)})
                finally:
                    message_queue.put(None)  # Signal completion
            
            # Start Claude process
            process = self.session_manager.start_claude_process(
                prompt_file=prompt_file,
                working_dir=working_dir,
                allowed_tools="Read,Write,Edit,MultiEdit,Bash,Glob,Grep,LS"
            )
            
            # Process output in a separate thread
            output_thread = threading.Thread(target=process_output, args=(process,))
            output_thread.start()
            
            # Collect output with timeout
            timeout = 300  # 5 minutes timeout
            start_time = time.time()
            
            while True:
                if time.time() - start_time > timeout:
                    logger.warning("Claude execution timed out")
                    process.terminate()
                    break
                
                try:
                    msg = message_queue.get(timeout=1)
                    if msg is None:
                        break  # Process completed
                    # Log messages for debugging
                    logger.debug(f"Claude message: {msg}")
                except queue.Empty:
                    continue
            
            # Wait for output thread to complete
            output_thread.join(timeout=5)
            
            # Get process return code
            return_code = process.poll()
            
            # Read any stderr
            stderr_output = process.stderr.read() if process.stderr else ""
            
            # Clean up
            try:
                os.unlink(prompt_file)
            except:
                pass
            
            # Determine success
            success = return_code == 0 and len(output_lines) > 0
            
            if not success and stderr_output:
                logger.error(f"Claude stderr: {stderr_output}")
                return {
                    'success': False,
                    'error': f'Claude execution failed: {stderr_output}'
                }
            
            return {
                'success': success,
                'output': '\n'.join(output_lines)
            }
            
        except Exception as e:
            logger.error(f"Error executing Claude: {e}")
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
    
    def _save_execution_outputs(self, job_id: str, stage_id: str, task_index: int, 
                               task: Dict[str, Any], results: List[Dict[str, Any]], job_context: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """
        Save execution outputs to the file system
        
        Uses task output folder if provided in context, otherwise falls back to old structure
        """
        # Use task output folder if provided in context
        if job_context and 'task_output_folder' in job_context:
            output_dir = Path(job_context['task_output_folder'])
        else:
            # Fallback to old structure: data/jobs/{job_id}/outputs/{stage_id}/{task_index}_{task_name}/
            task_name = task.get('name', 'unknown').lower().replace(' ', '_')
            output_dir = self.data_dir / 'jobs' / job_id / 'outputs' / stage_id / f"{task_index}_{task_name}"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_paths = {
            'directory': str(output_dir),
            'files': []
        }
        
        # Save execution summary
        summary_path = output_dir / 'execution_summary.json'
        summary_data = {
            'job_id': job_id,
            'stage_id': stage_id,
            'task_index': task_index,
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'total_prompts': len(results),
            'successful_prompts': len([r for r in results if r['status'] == 'success']),
            'failed_prompts': len([r for r in results if r['status'] == 'error'])
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        output_paths['files'].append(str(summary_path))
        
        # Save individual prompt outputs
        for i, result in enumerate(results):
            prompt_filename = result.get('prompt_file', f'prompt_{i}.md')
            base_name = prompt_filename.replace('.md', '')
            
            # Save the output
            if result['status'] == 'success' and result.get('output'):
                output_file = output_dir / f"{base_name}_output.md"
                with open(output_file, 'w') as f:
                    f.write(f"# Output for {prompt_filename}\n\n")
                    f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n\n")
                    f.write("---\n\n")
                    f.write(result['output'])
                output_paths['files'].append(str(output_file))
            
            # Save any errors
            if result['status'] == 'error' and result.get('error'):
                error_file = output_dir / f"{base_name}_error.txt"
                with open(error_file, 'w') as f:
                    f.write(f"Error for {prompt_filename}\n")
                    f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n\n")
                    f.write(result['error'])
                output_paths['files'].append(str(error_file))
        
        # Create a combined output file
        combined_output = output_dir / 'combined_output.md'
        with open(combined_output, 'w') as f:
            f.write(f"# Combined Output for {task.get('name', 'Task')}\n\n")
            f.write(f"Agent: {task.get('agent', 'Unknown')}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            
            for i, result in enumerate(results):
                f.write(f"## Prompt {i+1}: {result.get('prompt_file', 'Unknown')}\n\n")
                if result['status'] == 'success':
                    f.write(result.get('output', 'No output'))
                else:
                    f.write(f"**Error**: {result.get('error', 'Unknown error')}")
                f.write("\n\n---\n\n")
        
        output_paths['files'].append(str(combined_output))
        
        logger.info(f"Saved {len(output_paths['files'])} output files to {output_dir}")
        return output_paths
    
    def get_task_output(self, job_id: str, stage_id: str, task_index: int) -> Optional[Dict[str, Any]]:
        """
        Get the output for a specific task
        """
        # Find the most recent execution for this task
        for execution in reversed(self.execution_logs):
            if (execution['job_id'] == job_id and 
                execution['stage_id'] == stage_id and 
                execution['task_index'] == task_index):
                
                output_paths = execution.get('output_paths', {})
                if output_paths and 'directory' in output_paths:
                    # Read the combined output
                    combined_path = Path(output_paths['directory']) / 'combined_output.md'
                    if combined_path.exists():
                        with open(combined_path, 'r') as f:
                            content = f.read()
                        
                        return {
                            'execution_id': execution['execution_id'],
                            'timestamp': execution['timestamp'],
                            'status': execution['status'],
                            'content': content,
                            'output_paths': output_paths
                        }
        
        return None
    
    def get_task_logs(self, job_id: str, stage_id: str, task_index: int) -> List[Dict[str, Any]]:
        """
        Get logs for a specific task
        """
        task_key = f"{job_id}_{stage_id}_{task_index}"
        return self.task_logs.get(task_key, [])
    
    def add_task_log(self, job_id: str, stage_id: str, task_index: int, level: str, message: str):
        """
        Add a log entry for a task
        """
        task_key = f"{job_id}_{stage_id}_{task_index}"
        
        if task_key not in self.task_logs:
            self.task_logs[task_key] = []
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        
        self.task_logs[task_key].append(log_entry)
        
        # Keep only last 1000 logs per task
        if len(self.task_logs[task_key]) > 1000:
            self.task_logs[task_key] = self.task_logs[task_key][-1000:]

# Global instance
execution_service = ExecutionService()