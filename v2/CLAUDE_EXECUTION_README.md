# Claude Execution Setup for Code Conversion Studio V2

## Overview
The v2 implementation now includes real Claude CLI execution instead of mock execution. This allows actual code transformation tasks to be performed using Claude's capabilities.

## Key Components

### 1. Claude Authentication Manager V2 (`claude_auth_v2.py`)
- Manages API key authentication with automatic refresh
- Creates auth helper scripts for secure key management
- Supports multiple authentication methods (environment variables, files, OAuth)
- Includes session management with automatic reconnection

### 2. Execution Service (`execution_service.py`)
- Executes prompt-based tasks using Claude CLI
- Processes prompt templates with variable substitution
- Handles sequential execution of multiple prompts per task
- Captures and processes Claude output in real-time

### 3. Prompt Structure
Prompts are organized by agent and capability:
```
/v2/prompts/
├── code_architect/
│   └── plan/
│       ├── 01_analyze_project_structure.md
│       ├── 02_create_migration_plan.md
│       └── 03_design_target_architecture.md
├── code_engineer/
│   └── migrate/
│       ├── 01_setup_target_project.md
│       └── 02_migrate_data_models.md
└── targets/
    ├── python/
    ├── rust/
    └── ... (15 target frameworks)
```

## How It Works

1. **Task Execution Flow**:
   - User clicks execute button on a task
   - Frontend calls `/api/jobs/{job_id}/stages/{stage_id}/tasks/{task_index}/execute`
   - Backend loads relevant prompt files based on agent/capability
   - Each prompt is processed with variable substitution
   - Claude CLI is invoked with the prompt file
   - Output is captured and processed in real-time
   - Results are returned to the frontend

2. **Claude CLI Integration**:
   - Uses `-f` flag to pass prompt files (instead of `-p` for inline prompts)
   - Supports all standard Claude tools (Read, Write, Edit, Bash, etc.)
   - Handles authentication via API key helper scripts
   - Processes streaming JSON output

3. **Variable Substitution**:
   - Template variables in prompts use `{{variable_name}}` format
   - Common variables: source_name, target_name, job_name, etc.
   - Task-specific configuration is also available

## Setup Requirements

1. **Claude CLI Installation**:
   - Ensure Claude CLI is installed and available in PATH
   - Run `claude --version` to verify installation

2. **Authentication**:
   - Set `CLAUDE_API_KEY` environment variable, OR
   - Create `~/.claude/api_key` file with your API key, OR
   - Use Claude OAuth authentication (`~/.claude/.credentials.json`)

3. **Testing**:
   ```bash
   cd /Users/rajasekharkarawalla/dev/2025/synapse/code-conv-studio-remote/v2
   python test_claude_execution.py
   ```

## Troubleshooting

### Common Issues:

1. **"Claude session manager not initialized"**
   - Check Claude CLI installation
   - Verify API key is set correctly
   - Check logs for authentication errors

2. **"No prompts found for agent/capability"**
   - Ensure prompt files exist in the correct directory structure
   - Check agent and capability names match directory names (lowercase, underscores)

3. **"Claude execution failed"**
   - Check Claude CLI stderr output in logs
   - Verify working directory permissions
   - Ensure sufficient API credits

### Debug Mode:
Enable debug logging to see detailed execution information:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Streaming Output**: Show real-time Claude output in the UI
2. **Execution History**: Persistent storage of execution results
3. **Parallel Execution**: Run multiple prompts concurrently
4. **Custom Tools**: Add project-specific Claude tools
5. **Progress Tracking**: Show progress for long-running tasks

## Security Considerations

1. API keys are never stored in code or logs
2. Auth helper scripts have restricted permissions (0755)
3. Temporary prompt files are cleaned up after execution
4. All file operations are scoped to project directories