"""
Code Conversion Studio - Professional Flask Application
A modern web application for code conversion with real-time file monitoring
and professional UI components.
"""

from flask import Flask, render_template, request, Response, jsonify, send_file
from werkzeug.utils import secure_filename
import subprocess
import json
import threading
import queue
import logging
from datetime import datetime
import os
import time
import shutil
from pathlib import Path
import mimetypes
import zipfile
import tempfile
from typing import List, Dict, Any, Optional

from flask_cors import CORS
from claude_auth import ClaudeAuthManager, EnhancedProcessManager, create_claude_auth_manager

# Application Configuration
class Config:
    """Application configuration"""
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
    INPUT_FOLDER = os.path.join(os.getcwd(), 'input')
    DATA_FOLDER = os.path.join(os.getcwd(), 'data')
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    HOST = '0.0.0.0'
    PORT = 80
    DEBUG = False
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.java', '.xml', '.properties', '.yml', '.yaml', '.json', '.txt', '.md', '.gradle', '.pom'}

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_SIZE

# Set up logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Global state management
class AppState:
    """Centralized application state management"""
    def __init__(self):
        self.message_queue = queue.Queue()
        self.file_update_queue = queue.Queue()
        self.file_monitor_thread = None
        self.file_monitor_running = False
        self.selected_input_folder = Config.INPUT_FOLDER
        self.processing = False
        self.auth_manager = None
        self.enhanced_process_manager = None

app_state = AppState()

# Initialize Claude authentication
try:
    app_state.auth_manager = create_claude_auth_manager()
    app_state.enhanced_process_manager = EnhancedProcessManager(app_state.auth_manager)
    logger.info("Claude authentication manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Claude authentication: {e}")
    logger.warning("Running without authentication manager - manual API key may be required")

# File System Operations
class FileManager:
    """Handles file system operations and monitoring"""

    @staticmethod
    def get_file_tree(directory: str, base_directory: str = None) -> List[Dict[str, Any]]:
        """Get file tree structure for a directory"""
        if not os.path.exists(directory):
            return []

        # Use the directory itself as base if not provided
        if base_directory is None:
            base_directory = directory

        tree = []
        try:
            for item in sorted(os.listdir(directory)):
                if item.startswith('.'):
                    continue

                item_path = os.path.join(directory, item)
                # Calculate relative path from the base directory
                relative_path = os.path.relpath(item_path, base_directory)

                if os.path.isdir(item_path):
                    tree.append({
                        'name': item,
                        'type': 'folder',
                        'path': relative_path,
                        'children': FileManager.get_file_tree(item_path, base_directory)
                    })
                else:
                    # Get file size and modification time
                    stat = os.stat(item_path)
                    tree.append({
                        'name': item,
                        'type': 'file',
                        'path': relative_path,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {directory}: {e}")
        except Exception as e:
            logger.error(f"Error reading directory {directory}: {e}")

        return tree

    @staticmethod
    def read_file_content(file_path: str, folder_type: str = 'input') -> Dict[str, Any]:
        """Read file content with proper encoding detection"""
        if folder_type == 'input':
            base_folder = app_state.selected_input_folder
        else:  # output
            base_folder = Config.OUTPUT_FOLDER

        full_path = os.path.join(base_folder, file_path)

        # Security check - ensure path is within the specified folder
        if not os.path.abspath(full_path).startswith(os.path.abspath(base_folder)):
            raise ValueError(f'Access denied - path outside {folder_type} folder')

        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise FileNotFoundError('File not found')

        # Get file info
        stat = os.stat(full_path)
        file_info = {
            'path': file_path,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'name': os.path.basename(file_path)
        }

        # Try to read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            file_info['content'] = content
            file_info['encoding'] = 'utf-8'
        except UnicodeDecodeError:
            # Try binary read for non-text files
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                file_info['content'] = content.decode('utf-8', errors='replace')
                file_info['encoding'] = 'binary'
            except Exception:
                file_info['content'] = '[Binary file - cannot display]'
                file_info['encoding'] = 'binary'

        return file_info

    @staticmethod
    def cleanup_output_folder() -> Dict[str, Any]:
        """Clean up the output folder by removing all files and directories"""
        try:
            if not os.path.exists(Config.OUTPUT_FOLDER):
                os.makedirs(Config.OUTPUT_FOLDER)
                return {'success': True, 'message': 'Output folder created and ready'}

            # Count items before cleanup
            items_removed = 0
            total_size = 0

            for root, dirs, files in os.walk(Config.OUTPUT_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        items_removed += 1
                        total_size += file_size
                    except Exception as e:
                        logger.warning(f"Could not remove file {file_path}: {e}")

                # Remove empty directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Only remove if empty
                            os.rmdir(dir_path)
                            items_removed += 1
                    except Exception as e:
                        logger.warning(f"Could not remove directory {dir_path}: {e}")

            # Remove any remaining empty subdirectories
            for root, dirs, files in os.walk(Config.OUTPUT_FOLDER, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except Exception:
                        pass  # Ignore errors for non-empty directories

            return {
                'success': True,
                'message': f'Output folder cleaned successfully',
                'items_removed': items_removed,
                'size_freed': total_size
            }

        except Exception as e:
            logger.error(f"Error cleaning output folder: {e}")
            return {
                'success': False,
                'message': f'Error cleaning output folder: {str(e)}'
            }

    @staticmethod
    def get_input_info() -> Dict[str, Any]:
        """Get information about the input folder and its contents"""
        try:
            input_folder = app_state.selected_input_folder
            if not os.path.exists(input_folder):
                return {
                    'exists': False,
                    'message': 'Input folder does not exist',
                    'path': input_folder
                }

            # Get input folder statistics
            total_files = 0
            total_size = 0
            file_types = {}

            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_files += 1
                        total_size += file_size

                        # Track file extensions
                        _, ext = os.path.splitext(file)
                        ext = ext.lower()
                        if ext:
                            file_types[ext] = file_types.get(ext, 0) + 1
                        else:
                            file_types['no_extension'] = file_types.get('no_extension', 0) + 1

                    except Exception as e:
                        logger.warning(f"Could not access file {file_path}: {e}")

            return {
                'exists': True,
                'path': input_folder,
                'total_files': total_files,
                'total_size': total_size,
                'file_types': file_types,
                'tree': FileManager.get_file_tree(input_folder)
            }

        except Exception as e:
            logger.error(f"Error getting input info: {e}")
            return {
                'exists': False,
                'message': f'Error accessing input folder: {str(e)}',
                'path': app_state.selected_input_folder
            }

    @staticmethod
    def browse_directory(directory_path: str = None) -> Dict[str, Any]:
        """Browse directories for folder selection - restricted to data folder"""
        try:
            # Default to data folder
            if directory_path is None:
                directory_path = Config.DATA_FOLDER

            # Security check - ensure we're within the data folder
            directory_path = os.path.abspath(directory_path)
            data_folder_abs = os.path.abspath(Config.DATA_FOLDER)
            
            # Restrict browsing to data folder only
            if not directory_path.startswith(data_folder_abs):
                directory_path = data_folder_abs

            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return {
                    'success': False,
                    'message': 'Directory does not exist or is not accessible',
                    'path': directory_path
                }

            items = []
            try:
                # Add parent directory option (except when at data folder root)
                parent_dir = os.path.dirname(directory_path)
                if parent_dir != directory_path and directory_path != data_folder_abs:
                    # Only show parent if it's still within data folder
                    if parent_dir.startswith(data_folder_abs):
                        items.append({
                            'name': '..',
                            'type': 'parent',
                            'path': parent_dir,
                            'display_name': '← Parent Directory'
                        })

                # List directories only
                # Skip system files when browsing data folder root
                skip_items = {'rules', 'issues'} if directory_path == data_folder_abs else set()
                
                for item in sorted(os.listdir(directory_path)):
                    if item.startswith('.') or item in skip_items:
                        continue

                    item_path = os.path.join(directory_path, item)
                    if os.path.isdir(item_path):
                        # Get folder info
                        try:
                            stat = os.stat(item_path)
                            items.append({
                                'name': item,
                                'type': 'folder',
                                'path': item_path,
                                'display_name': item,
                                'modified': stat.st_mtime
                            })
                        except PermissionError:
                            # Skip folders we can't access
                            continue

            except PermissionError:
                return {
                    'success': False,
                    'message': 'Permission denied accessing directory',
                    'path': directory_path
                }

            return {
                'success': True,
                'path': directory_path,
                'items': items,
                'current_selection': app_state.selected_input_folder
            }

        except Exception as e:
            logger.error(f"Error browsing directory {directory_path}: {e}")
            return {
                'success': False,
                'message': f'Error browsing directory: {str(e)}',
                'path': directory_path
            }

    @staticmethod
    def set_input_folder(folder_path: str) -> Dict[str, Any]:
        """Set the selected input folder by clearing current input and copying selected folder contents"""
        try:
            folder_path = os.path.abspath(folder_path)

            if not os.path.exists(folder_path):
                return {
                    'success': False,
                    'message': 'Folder does not exist'
                }

            if not os.path.isdir(folder_path):
                return {
                    'success': False,
                    'message': 'Path is not a directory'
                }

            # Step 1: Clear current input folder
            logger.info(f"Clearing current input folder: {Config.INPUT_FOLDER}")
            if os.path.exists(Config.INPUT_FOLDER):
                # Remove all contents of input folder
                for item in os.listdir(Config.INPUT_FOLDER):
                    item_path = os.path.join(Config.INPUT_FOLDER, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except Exception as e:
                        logger.warning(f"Could not remove {item_path}: {e}")
            else:
                # Create input folder if it doesn't exist
                os.makedirs(Config.INPUT_FOLDER)

            # Step 2: Copy selected folder contents to input folder
            logger.info(f"Copying contents from {folder_path} to {Config.INPUT_FOLDER}")
            files_copied = 0
            total_size = 0
            
            for item in os.listdir(folder_path):
                source_path = os.path.join(folder_path, item)
                dest_path = os.path.join(Config.INPUT_FOLDER, item)
                
                try:
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, dest_path)
                        files_copied += 1
                        total_size += os.path.getsize(source_path)
                    elif os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                        # Count files in copied directory
                        for root, dirs, files in os.walk(dest_path):
                            files_copied += len(files)
                            for file in files:
                                total_size += os.path.getsize(os.path.join(root, file))
                except Exception as e:
                    logger.error(f"Error copying {source_path} to {dest_path}: {e}")
                    return {
                        'success': False,
                        'message': f'Error copying files: {str(e)}'
                    }

            # Update the selected input folder to point to the service's input folder
            app_state.selected_input_folder = Config.INPUT_FOLDER
            logger.info(f"Input folder updated with {files_copied} files ({total_size} bytes) from: {folder_path}")

            return {
                'success': True,
                'message': f'Input folder updated successfully - copied {files_copied} files',
                'path': Config.INPUT_FOLDER,
                'source_path': folder_path,
                'files_copied': files_copied,
                'total_size': total_size
            }

        except Exception as e:
            logger.error(f"Error setting input folder: {e}")
            return {
                'success': False,
                'message': f'Error setting input folder: {str(e)}'
            }

# File Monitoring
class FileMonitor:
    """Handles real-time file system monitoring"""

    @staticmethod
    def monitor_files():
        """Monitor file changes in both input and output directories"""
        last_trees = {'input': {}, 'output': {}}

        while app_state.file_monitor_running:
            try:
                # Monitor output folder
                output_tree = FileManager.get_file_tree(Config.OUTPUT_FOLDER)
                output_tree_str = json.dumps(output_tree, sort_keys=True)

                if output_tree_str != last_trees['output'].get('str', ''):
                    app_state.file_update_queue.put({
                        'type': 'file_tree_update',
                        'folder_type': 'output',
                        'data': output_tree
                    })
                    last_trees['output']['str'] = output_tree_str

                # Monitor input folder
                input_tree = FileManager.get_file_tree(app_state.selected_input_folder)
                input_tree_str = json.dumps(input_tree, sort_keys=True)

                if input_tree_str != last_trees['input'].get('str', ''):
                    app_state.file_update_queue.put({
                        'type': 'file_tree_update',
                        'folder_type': 'input',
                        'data': input_tree
                    })
                    last_trees['input']['str'] = input_tree_str

            except Exception as e:
                logger.error(f"Error monitoring files: {e}")

            time.sleep(1)  # Check every second

    @staticmethod
    def start_monitoring():
        """Start file monitoring in a separate thread"""
        if app_state.file_monitor_thread and app_state.file_monitor_thread.is_alive():
            return

        app_state.file_monitor_running = True
        app_state.file_monitor_thread = threading.Thread(target=FileMonitor.monitor_files)
        app_state.file_monitor_thread.daemon = True
        app_state.file_monitor_thread.start()
        logger.info("File monitoring started")

    @staticmethod
    def stop_monitoring():
        """Stop file monitoring"""
        app_state.file_monitor_running = False
        logger.info("File monitoring stopped")

# Process Management
class ProcessManager:
    """Handles Claude process execution and output processing"""

    @staticmethod
    def process_claude_output(process, query: str):
        """Process output from the subprocess and send to queue"""
        stderr_output = []
        try:
            for line in process.stdout:
                if not line.strip():
                    continue

                try:
                    message = json.loads(line.strip())
                    ProcessManager._handle_message(message)

                except json.JSONDecodeError:
                    # Show raw output that isn't JSON
                    if line.strip():
                        app_state.message_queue.put({
                            'type': 'raw',
                            'content': line.strip()
                        })

        except Exception as e:
            logger.error(f"Error processing output: {e}")
            app_state.message_queue.put({
                'type': 'error',
                'content': f"Processing error: {str(e)}"
            })
        finally:
            # Capture any stderr output
            try:
                # Read stderr in non-blocking mode
                import select
                while True:
                    ready = select.select([process.stderr], [], [], 0.1)[0]
                    if ready:
                        line = process.stderr.readline()
                        if line:
                            stderr_output.append(line.strip())
                        else:
                            break
                    else:
                        break
            except:
                pass
            
            # Ensure process is properly cleaned up
            try:
                # Give process a chance to exit gracefully
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Claude process didn't exit within timeout, terminating")
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    logger.error("Claude process didn't terminate, killing forcefully")
                    process.kill()
                    process.wait()
            
            # Log any stderr output if present
            if stderr_output:
                logger.warning(f"Claude process stderr output: {' '.join(stderr_output)}")
            
            # Reset context.md file after migration completion
            context_file_path = os.path.join(os.path.dirname(__file__), 'prompts', 'context.md')
            try:
                with open(context_file_path, 'w') as f:
                    f.write('')  # Clear the file
                logger.info(f"Successfully reset context.md file at {context_file_path}")
            except Exception as e:
                logger.error(f"Failed to reset context.md file: {str(e)}")
            
            # Signal completion
            app_state.message_queue.put(None)

    @staticmethod
    def _handle_message(message: Dict[str, Any]):
        """Handle different types of messages from Claude"""
        message_type = message.get("type")

        if message_type == "assistant":
            ProcessManager._handle_assistant_message(message)
        elif message_type == "system" and message.get("subtype") == "init":
            ProcessManager._handle_init_message(message)
        elif message_type == "result":
            ProcessManager._handle_result_message(message)

    @staticmethod
    def _handle_assistant_message(message: Dict[str, Any]):
        """Handle assistant messages"""
        for content in message.get("message", {}).get("content", []):
            if content.get("type") == "text":
                text = content.get("text", "").strip()
                if text:
                    # Filter and clean text
                    filtered_text = ProcessManager._clean_text(text)
                    if filtered_text.strip():
                        app_state.message_queue.put({
                            'type': 'message',
                            'content': filtered_text
                        })

            elif content.get("type") == "tool_use":
                ProcessManager._handle_tool_use(content)

    @staticmethod
    def _handle_tool_use(content: Dict[str, Any]):
        """Handle tool use messages"""
        # Show tool use messages for better visibility
        tool_name = content.get('name', 'unknown')
        app_state.message_queue.put({
            'type': 'tool',
            'content': f"🔧 Using tool: {tool_name}"
        })

    @staticmethod
    def _handle_init_message(message: Dict[str, Any]):
        """Handle initialization messages"""
        session_id = message.get('session_id', '')
        app_state.message_queue.put({
            'type': 'init',
            'content': f"🚀 Starting session: {session_id[-8:] if session_id else 'unknown'}"
        })

    @staticmethod
    def _handle_result_message(message: Dict[str, Any]):
        """Handle result messages"""
        subtype = message.get("subtype")
        if subtype == "success":
            duration = message.get('duration_ms', 0) / 1000
            cost = message.get('total_cost_usd', 0)
            turns = message.get('num_turns', 0)

            app_state.message_queue.put({
                'type': 'success',
                'content': f"✅ Completed in {duration:.2f}s | 💰 Cost: ${cost:.4f} | 🔄 Turns: {turns}"
            })
        else:
            # Log the full error message for debugging
            logger.warning(f"Claude process result error - subtype: {subtype}, full message: {json.dumps(message, indent=2)}")
            
            # Extract any error details from the message
            error_detail = message.get('error', '')
            error_msg = message.get('message', '')
            
            # Provide user-friendly error messages based on error type
            error_messages = {
                'error_during_execution': '⚠️ Process completed successfully but reported a minor issue. Your files have been generated and should be valid. This is typically just a notification and doesn\'t affect the output.',
                'timeout': '⏱️ Process timed out. Consider breaking down your request into smaller tasks.',
                'resource_limit': '💾 Process exceeded resource limits. Try with a smaller input or simpler query.',
                'permission_denied': '🔒 Permission denied. Check file permissions and access rights.',
                'network_error': '🌐 Network connectivity issue. Please check your connection and try again.',
                'invalid_input': '📝 Invalid input provided. Please check your query and input files.',
                'tool_error': '🔧 Tool execution failed. Check input files and permissions.',
            }
            
            user_friendly_message = error_messages.get(subtype, f"❌ Process error: {subtype}")
            
            # Add any additional error details if available
            if error_detail or error_msg:
                additional_info = error_detail or error_msg
                logger.info(f"Additional error info: {additional_info}")
            
            app_state.message_queue.put({
                'type': 'error',
                'content': user_friendly_message
            })

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and filter text output"""
        # Replace Claude mentions with Cognidev
        filtered_text = text.replace("Claude", "Cognidev").replace("claude", "Cognidev")
        return filtered_text

    @staticmethod
    def start_process(query: str):
        """Start the Claude process"""
        def run_process():
            # Use enhanced process manager if available
            if app_state.enhanced_process_manager:
                try:
                    logger.info(f"Starting process with authentication manager for query: {query}")
                    app_state.enhanced_process_manager.start_process(query, app_state.message_queue)
                    return
                except Exception as e:
                    logger.error(f"Enhanced process manager failed: {e}")
                    logger.info("Falling back to standard process execution")
            
            # Fallback to original implementation
            cmd = [
                "claude", "-p",
                query,
                "--allowedTools", "Read,Write,Edit,MultiEdit,Bash,Glob,Grep,LS",
                "--output-format", "stream-json",
                "--verbose"
            ]

            logger.info(f"Starting process with query: {query}")

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                ProcessManager.process_claude_output(process, query)
                process.wait()

                if process.returncode != 0:
                    stderr = process.stderr.read()
                    logger.error(f"Claude process failed with return code {process.returncode}: {stderr}")
                    
                    # Check for authentication errors
                    if process.returncode == 401 or '401' in stderr or 'unauthorized' in stderr.lower():
                        error_msg = "🔐 Authentication failed. Please check your API key configuration."
                        
                        # Try to provide helpful guidance
                        app_state.message_queue.put({
                            'type': 'error',
                            'content': error_msg + "\n\nTo fix: Set CLAUDE_API_KEY environment variable or create ~/.claude/api_key file"
                        })
                        return
                    
                    # Provide user-friendly error messages based on return code
                    if process.returncode == 1:
                        error_msg = "🚫 Process failed due to invalid arguments or configuration."
                    elif process.returncode == 2:
                        error_msg = "📁 Process failed due to file access issues. Check input folder permissions."
                    elif process.returncode == 126:
                        error_msg = "🔒 Permission denied. Cannot execute Claude command."
                    elif process.returncode == 127:
                        error_msg = "❓ Claude command not found. Please ensure Claude CLI is installed."
                    elif process.returncode == 130:
                        error_msg = "⏹️ Process was interrupted by user."
                    elif process.returncode == 137:
                        error_msg = "💾 Process was killed due to memory limits."
                    else:
                        error_msg = f"❌ Process failed (exit code {process.returncode}). Check logs for details."
                    
                    app_state.message_queue.put({
                        'type': 'error',
                        'content': error_msg
                    })
            except FileNotFoundError:
                logger.error("Claude CLI not found")
                app_state.message_queue.put({
                    'type': 'error',
                    'content': "❓ Claude CLI not found. Please ensure Claude is installed and available in PATH."
                })
            except PermissionError:
                logger.error("Permission denied starting Claude process")
                app_state.message_queue.put({
                    'type': 'error',
                    'content': "🔒 Permission denied. Cannot execute Claude command."
                })
            except Exception as e:
                logger.error(f"Unexpected error starting process: {e}")
                app_state.message_queue.put({
                    'type': 'error',
                    'content': f"💥 Unexpected error occurred: {str(e)}"
                })

        thread = threading.Thread(target=run_process)
        thread.daemon = True
        thread.start()

# Route Handlers
@app.route('/')
def index():
    """Main application page"""
    # Start file monitoring when the app loads
    FileMonitor.start_monitoring()
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    """Get current file tree from selected input folder"""
    try:
        folder_type = request.args.get('type', 'input')
        if folder_type == 'input':
            folder_path = app_state.selected_input_folder
        else:  # output
            folder_path = Config.OUTPUT_FOLDER

        tree = FileManager.get_file_tree(folder_path, folder_path)
        return jsonify({
            'files': tree,
            'folder_type': folder_type,
            'folder_path': folder_path
        })
    except Exception as e:
        logger.error(f"Error getting files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<path:file_path>')
def get_file_content(file_path):
    """Get content of a specific file"""
    try:
        folder_type = request.args.get('type', 'input')
        file_info = FileManager.read_file_content(file_path, folder_type)
        return jsonify(file_info)
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_output():
    """Clean up the output folder"""
    try:
        result = FileManager.cleanup_output_folder()
        if result['success']:
            logger.info(f"Output folder cleaned: {result['items_removed']} items removed")
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_item():
    """Delete a specific file or folder from the output directory"""
    try:
        data = request.get_json()
        item_path = data.get('path')
        item_type = data.get('type', 'file')
        
        if not item_path:
            return jsonify({'success': False, 'error': 'Path is required'}), 400
        
        # Ensure the path is within the output folder
        full_path = os.path.join(Config.OUTPUT_FOLDER, item_path)
        full_path = os.path.abspath(full_path)
        output_folder_abs = os.path.abspath(Config.OUTPUT_FOLDER)
        
        if not full_path.startswith(output_folder_abs):
            return jsonify({'success': False, 'error': 'Invalid path'}), 400
        
        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'Path not found'}), 404
        
        # Delete the item
        if item_type == 'folder' and os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
            logger.info(f"Deleted folder: {item_path}")
        elif os.path.isfile(full_path):
            os.remove(full_path)
            logger.info(f"Deleted file: {item_path}")
        else:
            return jsonify({'success': False, 'error': 'Invalid item type'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {item_type}: {item_path}',
            'path': item_path,
            'type': item_type
        })
        
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/input')
def get_input_info():
    """Get information about the input folder"""
    try:
        input_info = FileManager.get_input_info()
        return jsonify(input_info)
    except Exception as e:
        logger.error(f"Error getting input info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/browse')
def browse_directories():
    """Browse directories for folder selection"""
    try:
        directory_path = request.args.get('path')
        result = FileManager.browse_directory(directory_path)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error browsing directories: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/input/select', methods=['POST'])
def select_input_folder():
    """Set the selected input folder"""
    try:
        data = request.get_json()
        folder_path = data.get('path')

        if not folder_path:
            return jsonify({'error': 'Folder path is required'}), 400

        result = FileManager.set_input_folder(folder_path)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error selecting input folder: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/stream')
def stream_file_updates():
    """Stream file tree updates"""
    def generate():
        while True:
            try:
                update = app_state.file_update_queue.get(timeout=30)
                yield f"data: {json.dumps(update)}\n\n"
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/process', methods=['POST'])
def process():
    """Start a new conversion process"""
    try:
        data = request.json
        query = data.get('query', '') if data else ''

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Clear the message queue
        while not app_state.message_queue.empty():
            try:
                app_state.message_queue.get_nowait()
            except queue.Empty:
                break

        # Start the process
        ProcessManager.start_process(query)

        return jsonify({'status': 'started'})

    except Exception as e:
        logger.error(f"Error starting process: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stream')
def stream():
    """Stream processing messages"""
    def generate():
        while True:
            try:
                message = app_state.message_queue.get(timeout=60)  # 60 second timeout
                if message is None:
                    # Process completed
                    yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                    break
                yield f"data: {json.dumps(message)}\n\n"
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/rules')
def get_rules():
    """Get migration rules"""
    try:
        rules_path = os.path.join(os.getcwd(), 'data', 'rules')
        if os.path.exists(rules_path):
            with open(rules_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'success': True})
        else:
            return jsonify({'error': 'Rules file not found', 'success': False}), 404
    except Exception as e:
        logger.error(f"Error reading rules: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/issues')
def get_issues():
    """Get migration issues"""
    try:
        issues_path = os.path.join(os.getcwd(), 'data', 'issues')
        if os.path.exists(issues_path):
            with open(issues_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'success': True})
        else:
            return jsonify({'error': 'Issues file not found', 'success': False}), 404
    except Exception as e:
        logger.error(f"Error reading issues: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/prompts/<prompt_type>')
def get_prompt(prompt_type):
    """Get prompt content for specific type"""
    try:
        # Map prompt types to files
        file_map = {
            'analyze': 'notes.md',
            'plan': 'plan.md',
            'migrate': 'ship.md',
            'validate': 'validate.md'
        }
        
        if prompt_type not in file_map:
            return jsonify({'error': 'Invalid prompt type', 'success': False}), 400
        
        file_name = file_map[prompt_type]
        app_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(app_dir, 'prompts', file_name)
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'success': True})
        else:
            return jsonify({'error': f'Prompt file not found: {file_name}', 'success': False}), 404
    except Exception as e:
        logger.error(f"Error reading prompt {prompt_type}: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/prompts/<prompt_type>', methods=['POST'])
def save_prompt(prompt_type):
    """Save prompt with backup to prompts-backup folder"""
    try:
        # Map prompt types to files
        file_map = {
            'analyze': 'notes.md',
            'plan': 'plan.md',
            'migrate': 'ship.md',
            'validate': 'validate.md'
        }
        
        if prompt_type not in file_map:
            return jsonify({'error': 'Invalid prompt type', 'success': False}), 400
        
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'No content provided', 'success': False}), 400
        
        file_name = file_map[prompt_type]
        app_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(app_dir, 'prompts', file_name)
        prompts_dir = os.path.dirname(prompt_path)
        backup_dir = os.path.join(app_dir, 'prompts-backup')
        
        # Ensure directories exist
        os.makedirs(prompts_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup with timestamp if file exists
        timestamp = None
        if os.path.exists(prompt_path):
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            backup_filename = f"{os.path.splitext(file_name)[0]}.{timestamp}{os.path.splitext(file_name)[1]}"
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(prompt_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Save new content
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully saved prompt {prompt_type} to: {prompt_path}")
        
        return jsonify({
            'success': True,
            'message': f'{file_name} saved successfully',
            'backup': f"{os.path.splitext(file_name)[0]}.{timestamp}{os.path.splitext(file_name)[1]}" if timestamp else None
        })
        
    except Exception as e:
        logger.error(f"Error saving prompt {prompt_type}: {e}")
        logger.error(f"Stack trace: ", exc_info=True)
        return jsonify({'error': str(e), 'success': False}), 500

# Keep old routes for backward compatibility
@app.route('/api/core-prompt')
def get_core_prompt():
    """Get core prompt (ship.md) content - backward compatibility"""
    return get_prompt('migrate')

@app.route('/api/core-prompt', methods=['POST'])
def save_core_prompt():
    """Save core prompt (ship.md) with backup - backward compatibility"""
    return save_prompt('migrate')

@app.route('/api/context')
def get_context():
    """Get additional context (context.md) content"""
    try:
        context_path = os.path.join(os.getcwd(), 'prompts', 'context.md')
        if os.path.exists(context_path):
            with open(context_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'success': True})
        else:
            # Return empty content if file doesn't exist
            return jsonify({'content': '', 'success': True})
    except Exception as e:
        logger.error(f"Error reading context: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/context', methods=['POST'])
def save_context():
    """Save additional context (context.md)"""
    try:
        data = request.json
        content = data.get('content', '')
        
        prompts_dir = os.path.join(os.getcwd(), 'prompts')
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir)
            
        context_path = os.path.join(prompts_dir, 'context.md')
        
        # Save content (can be empty to clear context)
        with open(context_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'message': 'Additional context saved successfully',
            'path': 'prompts/context.md'
        })
        
    except Exception as e:
        logger.error(f"Error saving context: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/fix')
def get_fix_issues():
    """Get existing fix issues from fix.md"""
    try:
        fix_path = os.path.join(os.getcwd(), 'prompts', 'fix.md')
        
        if not os.path.exists(fix_path):
            return jsonify({'success': True, 'issues': []})
        
        with open(fix_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse issues from the markdown content
        issues = []
        lines = content.split('\n')
        current_issue = []
        in_issue = False
        
        for line in lines:
            if line.startswith('## Issue'):
                if current_issue:
                    issues.append({
                        'id': len(issues) + 1,
                        'text': '\n'.join(current_issue).strip()
                    })
                    current_issue = []
                in_issue = True
            elif line.startswith('---') or line.startswith('*Generated'):
                if current_issue:
                    issues.append({
                        'id': len(issues) + 1,
                        'text': '\n'.join(current_issue).strip()
                    })
                break
            elif in_issue and line.strip():
                current_issue.append(line)
        
        return jsonify({'success': True, 'issues': issues})
        
    except Exception as e:
        logger.error(f"Error reading fix issues: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/fix', methods=['POST'])
def save_fix():
    """Save fix issues to fix.md"""
    try:
        data = request.json
        issues = data.get('issues', [])
        
        if not issues:
            return jsonify({'error': 'No issues provided', 'success': False}), 400
        
        prompts_dir = os.path.join(os.getcwd(), 'prompts')
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir)
            
        fix_path = os.path.join(prompts_dir, 'fix.md')
        
        # Delete existing fix.md if it exists
        if os.path.exists(fix_path):
            os.remove(fix_path)
            logger.info(f"Removed existing fix.md")
        
        # Create new fix.md with the issues
        content = "# Fix Issues\n\n"
        content += "The following issues need to be addressed during migration:\n\n"
        
        for i, issue in enumerate(issues, 1):
            content += f"## Issue {i}\n\n"
            content += f"{issue}\n\n"
        
        content += "---\n\n"
        content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # Save the new fix.md
        with open(fix_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved {len(issues)} fix issues to {fix_path}")
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(issues)} issues to fix.md',
            'file_path': 'prompts/fix.md',
            'issues_count': len(issues)
        })
        
    except Exception as e:
        logger.error(f"Error saving fix issues: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/auth/status')
def get_auth_status():
    """Get current authentication status"""
    try:
        is_authenticated = False
        claude_version = None
        auth_method = "Unknown"
        
        # Check Claude version and assume if CLI works, auth is handled internally
        try:
            version_result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=5)
            if version_result.returncode == 0:
                claude_version = version_result.stdout.strip()
                # If Claude CLI is working, authentication is handled by Claude Code
                is_authenticated = True
                auth_method = "Claude CLI (Built-in)"
        except Exception as e:
            logger.error(f"Claude CLI test failed: {e}")
            pass
        
        auth_info = {
            'authenticated': is_authenticated,
            'claude_version': claude_version,
            'auth_method': auth_method,
            'manager_active': bool(app_state.auth_manager),
        }
        
        # Add manager info if available
        if app_state.auth_manager:
            auth_info.update({
                'last_refresh': app_state.auth_manager.last_refresh.isoformat() if app_state.auth_manager.last_refresh else None,
                'refresh_interval': app_state.auth_manager.refresh_interval,
            })
        
        return jsonify(auth_info)
        
    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/refresh', methods=['POST'])
def refresh_auth():
    """Manually trigger authentication refresh"""
    try:
        if not app_state.auth_manager:
            return jsonify({
                'success': False,
                'error': 'Authentication manager not initialized'
            }), 400
        
        app_state.auth_manager._refresh_auth()
        
        return jsonify({
            'success': True,
            'message': 'Authentication refreshed successfully',
            'last_refresh': app_state.auth_manager.last_refresh.isoformat()
        })
    except Exception as e:
        logger.error(f"Error refreshing auth: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/auth/update-key', methods=['POST'])
def update_api_key():
    """Update the Claude API key"""
    try:
        data = request.json
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400
        
        if not app_state.auth_manager:
            # Create new auth manager with the provided key
            app_state.auth_manager = ClaudeAuthManager(api_key)
            app_state.auth_manager.start_refresh_daemon()
            app_state.enhanced_process_manager = EnhancedProcessManager(app_state.auth_manager)
        else:
            # Update existing manager
            app_state.auth_manager.update_api_key(api_key)
        
        # Test the new key
        is_valid = app_state.auth_manager.test_authentication()
        
        return jsonify({
            'success': is_valid,
            'message': 'API key updated successfully' if is_valid else 'Invalid API key',
            'authenticated': is_valid
        })
    except Exception as e:
        logger.error(f"Error updating API key: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

# Upload Routes
@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file upload"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        project_name = request.form.get('projectName')
        
        # If no project name provided, use the first file's directory name or a default
        if not project_name and files:
            first_file = files[0]
            if '/' in first_file.filename:
                # Extract the root folder name from the path
                project_name = first_file.filename.split('/')[0]
            else:
                project_name = f'upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        # Create project folder directly in data folder
        project_path = os.path.join(Config.DATA_FOLDER, secure_filename(project_name))
            
        os.makedirs(project_path, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file and file.filename:
                # Security check - validate file extension
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in Config.ALLOWED_EXTENSIONS and file_ext != '':
                    logger.warning(f"Skipping file with disallowed extension: {file.filename}")
                    continue
                
                # Preserve directory structure
                filename = secure_filename(file.filename)
                if '/' in file.filename:  # If file was uploaded with path
                    # Create subdirectories
                    file_parts = file.filename.split('/')
                    subdir = os.path.join(project_path, *[secure_filename(part) for part in file_parts[:-1]])
                    os.makedirs(subdir, exist_ok=True)
                    filepath = os.path.join(subdir, secure_filename(file_parts[-1]))
                else:
                    filepath = os.path.join(project_path, filename)
                
                file.save(filepath)
                uploaded_files.append(filename)
                logger.info(f"Uploaded file: {filepath}")
        
        # Copy uploaded files to input folder if requested
        if request.form.get('copyToInput') == 'true':
            shutil.copytree(project_path, Config.INPUT_FOLDER, dirs_exist_ok=True)
            logger.info(f"Copied uploaded files to input folder")
        
        return jsonify({
            'success': True,
            'fileCount': len(uploaded_files),
            'projectPath': project_path,
            'files': uploaded_files
        })
        
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/zip', methods=['POST'])
def upload_zip():
    """Handle ZIP file upload and extraction"""
    try:
        if 'zipfile' not in request.files:
            return jsonify({'error': 'No ZIP file provided'}), 400
        
        zip_file = request.files['zipfile']
        if not zip_file.filename.endswith('.zip'):
            return jsonify({'error': 'File must be a ZIP archive'}), 400
        
        # Use ZIP filename (without extension) as project name if not provided
        project_name = request.form.get('projectName')
        if not project_name:
            project_name = os.path.splitext(zip_file.filename)[0]
        
        # Create project folder directly in data folder
        project_path = os.path.join(Config.DATA_FOLDER, secure_filename(project_name))
            
        os.makedirs(project_path, exist_ok=True)
        
        # Save and extract ZIP file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_file.save(tmp_file.name)
            
            # Extract with security checks
            extracted_files = []
            with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                # Check for malicious paths
                for member in zip_ref.namelist():
                    # Security check - prevent directory traversal
                    if os.path.isabs(member) or '..' in member:
                        logger.warning(f"Skipping potentially malicious path: {member}")
                        continue
                    
                    # Check file extension
                    file_ext = os.path.splitext(member)[1].lower()
                    if file_ext not in Config.ALLOWED_EXTENSIONS and file_ext != '' and not member.endswith('/'):
                        logger.warning(f"Skipping file with disallowed extension: {member}")
                        continue
                    
                    # Extract file
                    zip_ref.extract(member, project_path)
                    extracted_files.append(member)
                    logger.info(f"Extracted: {member}")
            
            # Remove temporary file
            os.unlink(tmp_file.name)
        
        # Copy to input folder if requested
        if request.form.get('copyToInput') == 'true':
            shutil.copytree(project_path, Config.INPUT_FOLDER, dirs_exist_ok=True)
            logger.info(f"Copied extracted files to input folder")
        
        return jsonify({
            'success': True,
            'fileCount': len(extracted_files),
            'projectPath': project_path,
            'files': extracted_files
        })
        
    except zipfile.BadZipFile:
        logger.error("Invalid ZIP file")
        return jsonify({'error': 'Invalid ZIP file'}), 400
    except Exception as e:
        logger.error(f"Error processing ZIP file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects')
def list_projects():
    """List available projects in data folder"""
    try:
        projects = []
        # Skip system files like 'rules' and 'issues'
        skip_items = {'rules', 'issues', 'uploads'}
        
        if os.path.exists(Config.DATA_FOLDER):
            for item in os.listdir(Config.DATA_FOLDER):
                if item in skip_items:
                    continue
                item_path = os.path.join(Config.DATA_FOLDER, item)
                if os.path.isdir(item_path):
                    # Get project info
                    file_count = sum(1 for root, dirs, files in os.walk(item_path) for f in files)
                    mod_time = os.path.getmtime(item_path)
                    
                    projects.append({
                        'name': item,
                        'path': item_path,
                        'fileCount': file_count,
                        'modified': datetime.fromtimestamp(mod_time).isoformat()
                    })
        
        # Sort by modified time (newest first)
        projects.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_name>')
def get_project_files(project_name):
    """Get file tree for a specific project"""
    try:
        project_path = os.path.join(Config.DATA_FOLDER, secure_filename(project_name))
        
        if not os.path.exists(project_path):
            return jsonify({'error': 'Project not found'}), 404
        
        file_tree = FileManager.get_file_tree(project_path)
        
        return jsonify({
            'success': True,
            'projectName': project_name,
            'files': file_tree
        })
        
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_name>', methods=['DELETE'])
def delete_project(project_name):
    """Delete a project folder"""
    try:
        import shutil
        
        # First try to find the project with the exact name
        project_path = os.path.join(Config.DATA_FOLDER, project_name)
        
        # If not found, try with secure_filename
        if not os.path.exists(project_path):
            safe_project_name = secure_filename(project_name)
            project_path = os.path.join(Config.DATA_FOLDER, safe_project_name)
        
        # Check if project exists
        if not os.path.exists(project_path):
            logger.error(f"Project not found: {project_name}")
            return jsonify({'error': f'Project "{project_name}" not found'}), 404
        
        # Don't allow deletion of system folders
        base_name = os.path.basename(project_path)
        if base_name in ['rules', 'issues', 'uploads']:
            return jsonify({'error': 'Cannot delete system folders'}), 403
        
        # Delete the project folder
        shutil.rmtree(project_path)
        logger.info(f"Deleted project: {project_name} at path: {project_path}")
        
        return jsonify({
            'success': True,
            'message': f'Project {project_name} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting project {project_name}: {e}")
        return jsonify({'error': f'Failed to delete project: {str(e)}'}), 500

# Application Entry Point
if __name__ == '__main__':
    try:
        logger.info(f"Starting Code Conversion Studio on {Config.HOST}:{Config.PORT}")
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        FileMonitor.stop_monitoring()
        
        # Stop authentication refresh daemon
        if app_state.auth_manager:
            app_state.auth_manager.stop_refresh_daemon()
            logger.info("Stopped authentication refresh daemon")
        
        logger.info("Application shutdown complete")

