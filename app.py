"""
Code Conversion Studio - Professional Flask Application
A modern web application for code conversion with real-time file monitoring
and professional UI components.
"""

from flask import Flask, render_template, request, Response, jsonify
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
from typing import List, Dict, Any, Optional

from flask_cors import CORS

# Application Configuration
class Config:
    """Application configuration"""
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
    INPUT_FOLDER = os.path.join(os.getcwd(), 'input')
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    HOST = '0.0.0.0'
    PORT = 80
    DEBUG = True

# Initialize Flask app
app = Flask(__name__)
CORS(app)

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

app_state = AppState()

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
        """Browse directories for folder selection"""
        try:
            if directory_path is None:
                directory_path = os.getcwd()

            # Security check - prevent browsing outside reasonable bounds
            directory_path = os.path.abspath(directory_path)

            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return {
                    'success': False,
                    'message': 'Directory does not exist or is not accessible',
                    'path': directory_path
                }

            items = []
            try:
                # Add parent directory option (except for root)
                parent_dir = os.path.dirname(directory_path)
                if parent_dir != directory_path:  # Not at root
                    items.append({
                        'name': '..',
                        'type': 'parent',
                        'path': parent_dir,
                        'display_name': '← Parent Directory'
                    })

                # List directories only
                for item in sorted(os.listdir(directory_path)):
                    if item.startswith('.'):
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
        """Monitor file changes in the output directory"""
        last_tree = {}

        while app_state.file_monitor_running:
            try:
                current_tree = FileManager.get_file_tree(Config.OUTPUT_FOLDER)
                current_tree_str = json.dumps(current_tree, sort_keys=True)

                if current_tree_str != last_tree.get('str', ''):
                    app_state.file_update_queue.put({
                        'type': 'file_tree_update',
                        'data': current_tree
                    })
                    last_tree['str'] = current_tree_str

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
        try:
            for line in process.stdout:
                if not line.strip():
                    continue

                try:
                    message = json.loads(line.strip())
                    ProcessManager._handle_message(message)

                except json.JSONDecodeError:
                    # Skip non-JSON output
                    pass

        except Exception as e:
            logger.error(f"Error processing output: {e}")
            app_state.message_queue.put({
                'type': 'error',
                'content': f"Processing error: {str(e)}"
            })
        finally:
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
        # Filter out ALL tool use messages to reduce noise
        return

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
            # Provide user-friendly error messages based on error type
            error_messages = {
                'error_during_execution': '⚠️ Process completed but encountered an issue during finalization. Generated files should still be valid.',
                'timeout': '⏱️ Process timed out. Consider breaking down your request into smaller tasks.',
                'resource_limit': '💾 Process exceeded resource limits. Try with a smaller input or simpler query.',
                'permission_denied': '🔒 Permission denied. Check file permissions and access rights.',
                'network_error': '🌐 Network connectivity issue. Please check your connection and try again.',
                'invalid_input': '📝 Invalid input provided. Please check your query and input files.',
                'tool_error': '🔧 Tool execution failed. Check input files and permissions.',
            }
            
            user_friendly_message = error_messages.get(subtype, f"❌ Process error: {subtype}")
            
            app_state.message_queue.put({
                'type': 'error',
                'content': user_friendly_message
            })

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and filter text output"""
        # Filter out any mentions of Claude
        filtered_text = text.replace("Claude", "").replace("claude", "")
        filtered_text = filtered_text.replace("I'll", "Processing:").replace("I'm", "Currently")
        filtered_text = filtered_text.replace("Let me", "Starting to")
        return filtered_text

    @staticmethod
    def start_process(query: str):
        """Start the Claude process"""
        def run_process():
            cmd = [
                "claude", "-p",
                query,
                "--allowedTools", "Read,Write,Bash",
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
        logger.info("Application shutdown complete")

