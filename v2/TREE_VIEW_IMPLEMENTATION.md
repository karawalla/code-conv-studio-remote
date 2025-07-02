# Tree View Implementation for Task Files

## Overview
This implementation adds a file browser tree view to the task output modal, allowing users to explore the input, output, and data folders for each task execution.

## Features

### 1. **Controlled Tree View**
- The tree view only expands one level at a time to prevent horizontal overflow
- Folders show item count and can be toggled open/closed
- Files display with appropriate icons and file sizes
- Empty folders are shown with "(empty)" indicator

### 2. **Breadcrumb Navigation**
- Shows the current path at the top of the modal
- Updates dynamically when viewing different files
- Displays task name or file path depending on context

### 3. **Split View Interface**
- Left panel: File browser tree (250px width, collapsible)
- Right panel: Content viewer (expands to fill remaining space)
- Toggle button to hide/show the file browser

### 4. **File Content Viewing**
- Click any file in the tree to view its contents
- Supports text files with syntax preservation
- Binary files show a placeholder with file info
- Large files are truncated at 1MB with a notice

## API Endpoints Added

### `GET /api/jobs/{job_id}/stages/{stage_id}/tasks/{task_index}/files`
Returns the folder structure for a task:
```json
{
  "task_name": "Analyze Source Structure",
  "task_folder": "/path/to/task/folder",
  "folders": {
    "input": { "type": "folder", "children": [...] },
    "output": { "type": "folder", "children": [...] },
    "data": { "type": "folder", "children": [...] }
  }
}
```

### `POST /api/jobs/{job_id}/files/content`
Loads content of a specific file:
```json
Request: { "path": "/path/to/file" }
Response: {
  "path": "/path/to/file",
  "name": "filename.txt",
  "content": "file contents...",
  "size": 1234,
  "binary": false
}
```

## UI Components

### File Tree Structure
```
📁 input/
   └─ src/
      ├─ 📄 index.js (2.3 KB)
      └─ 📄 app.css (1.1 KB)
📁 output/
   ├─ 📋 execution_summary.json (456 B)
   └─ 📝 combined_output.md (12.4 KB)
📁 data/ (empty)
```

### Visual Design
- Consistent with existing glass-morphism UI style
- Subtle hover effects on folders and files
- File type icons based on extension
- Responsive layout that works at different screen sizes

## Usage

1. Click "View Output" button on any task
2. Modal opens showing both file tree and task output
3. Browse folders by clicking the arrow icons
4. Click any file to view its contents
5. Use toggle button to hide/show file browser
6. Breadcrumb shows current location

## Security

- File access is restricted to job folders only
- Path traversal attacks are prevented
- Binary files are not executed, only displayed as info

## Testing

Two test scripts are provided:
1. `test_analyze_source_integration.py` - Tests the full workflow
2. `test_tree_view.py` - Tests specifically the tree view functionality

## Benefits

1. **Better Visibility**: Users can see all inputs and outputs for each task
2. **Easy Navigation**: Tree structure makes it easy to find specific files
3. **Context Awareness**: Breadcrumb shows where you are in the folder structure
4. **Space Efficient**: Collapsible panels prevent UI clutter
5. **Consistent UX**: Maintains the existing UI design language