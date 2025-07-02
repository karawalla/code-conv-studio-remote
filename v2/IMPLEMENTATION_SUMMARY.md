# Analyze Source Integration Implementation Summary

## Overview
This implementation integrates Claude Code execution with the execute button for the first step in migration/modernization workflows - the "Analyze Source" task performed by the Code Architect agent.

## Changes Made

### 1. Job Folder Structure Creation
**File**: `v2/services/jobs_service.py`
- Added `jobs_storage_path` to store job folders under `data/jobs/`
- Created `_create_job_folder_structure()` method that creates the following structure for each task:
  ```
  data/jobs/{job_id}/{stage_id}/{task_index}_{task_name}/
    ├── input/     # Source code copied here for analysis
    ├── output/    # Claude Code execution outputs
    └── data/      # Additional task data
  ```
- This structure is created automatically when a job is created

### 2. Source Code Copying to Task Input
**File**: `v2/app.py`
- Modified `execute_task()` endpoint to:
  - Create task folder paths
  - Copy source code from `data/sources/{source_id}/` to task's `input/` folder
  - This happens specifically for Code Architect "analyze" tasks
  - Uses the task input folder as the working directory for Claude Code

### 3. Fixed Working Directory Issues
**File**: `v2/app.py`
- Fixed incorrect working directory logic for GitHub sources
- Now correctly uses the `path` field from source metadata
- Ensures Claude Code runs in the correct directory with access to source files

### 4. Updated Output Storage
**File**: `v2/services/execution_service.py`
- Modified `_save_execution_outputs()` to use the new task output folder structure
- Maintains backward compatibility with old output structure
- Outputs are now saved directly to the task's `output/` folder

### 5. Created Analyze Prompt
**File**: `v2/prompts/code_architect/analyze_source_structure/01_analyze_source_structure.md`
- Created comprehensive prompt for source code analysis
- Covers architecture, dependencies, code quality, technical debt, etc.
- Uses template variables for job context

### 6. Test Script
**File**: `v2/test_analyze_source_integration.py`
- Created test script to verify the full workflow:
  1. Create a GitHub source (clones repo)
  2. Create a modernization job
  3. Execute the analyze source task
  4. Verify folder structure and outputs

## How It Works

1. **Source Creation**: When a GitHub repo or local folder is added as a source, it's copied/cloned to `data/sources/{source_id}/`

2. **Job Creation**: When a job is created, the folder structure is created for all tasks with `input/`, `output/`, and `data/` subdirectories

3. **Task Execution**: When the execute button is clicked for an analyze task:
   - Source code is copied from `data/sources/{source_id}/` to the task's `input/` folder
   - Claude Code is executed with the `input/` folder as the working directory
   - Outputs are saved to the task's `output/` folder
   - The working directory ensures Claude has access to all source files for analysis

4. **Results**: The execution outputs include:
   - Individual prompt outputs
   - Combined output markdown file
   - Execution summary JSON
   - Any errors encountered

## Benefits

1. **Isolation**: Each task execution has its own isolated copy of the source code
2. **Traceability**: Clear folder structure shows inputs and outputs for each task
3. **Reusability**: Task outputs can be used as inputs for subsequent tasks
4. **Debugging**: Easy to inspect what Claude Code saw and produced

## Next Steps

To extend this to other tasks:
1. Add similar logic for other Code Architect tasks (plan, document, etc.)
2. Implement task chaining where outputs from one task become inputs to another
3. Add support for Code Engineer tasks that modify code
4. Implement proper error handling and retry mechanisms