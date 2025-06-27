# Sources Service Documentation

The Sources Service manages source code repositories and folders for the Any-to-Any Conversion Studio.

## Overview

The service provides functionality to:
- Clone GitHub repositories (public and private with proper authentication)
- Copy local folders into the system
- List and manage sources
- Update sources (pull latest changes for git repos)
- Delete sources

All sources are stored in the `data/sources` directory with unique IDs and metadata tracked in `sources_metadata.json`.

## API Endpoints

### List Sources
```
GET /api/sources
```
Returns all configured sources.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "My Project",
    "type": "github",
    "description": "GitHub repository",
    "icon": "🐙",
    "active": true,
    "created_at": "2025-06-27T...",
    "url": "https://github.com/user/repo"
  }
]
```

### Add Source
```
POST /api/sources
```

**For GitHub Repository:**
```json
{
  "type": "github",
  "url": "https://github.com/user/repo.git",
  "name": "Optional Custom Name"
}
```

**For Local Folder:**
```json
{
  "type": "local",
  "path": "/path/to/folder",
  "name": "Optional Custom Name"
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "name": "repo",
  "type": "github",
  "url": "https://github.com/user/repo.git",
  "path": "/app/data/sources/uuid",
  "created_at": "2025-06-27T...",
  "status": "active"
}
```

### Get Source
```
GET /api/sources/<source_id>
```
Returns details about a specific source.

### Delete Source
```
DELETE /api/sources/<source_id>
```
Removes a source and its files.

### Update Source
```
POST /api/sources/<source_id>/update
```
Updates a source (pulls latest changes for GitHub repos).

## Service Usage

### Python Example
```python
from services import SourcesService

# Initialize service
service = SourcesService()

# Add a GitHub repository
source = service.add_github_repo('https://github.com/user/repo.git')

# Add a local folder
source = service.add_local_folder('/path/to/project', name='My Project')

# List all sources
sources = service.list_sources()

# Delete a source
service.delete_source(source_id)
```

## Data Storage

Sources are stored in:
```
data/
└── sources/
    ├── sources_metadata.json    # Metadata for all sources
    ├── uuid1/                   # First source
    │   └── ... (source files)
    └── uuid2/                   # Second source
        └── ... (source files)
```

## Metadata Structure

Each source in `sources_metadata.json` contains:
- `id`: Unique identifier
- `name`: Display name
- `type`: "github" or "local"
- `path`: Local storage path
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `status`: "active" or other status
- `info`: Additional information (git info, file stats, etc.)

For GitHub sources:
- `url`: Repository URL

For Local sources:
- `original_path`: Original folder path
- `is_git_repo`: Whether it's a git repository

## Error Handling

The service handles common errors:
- `ValueError`: Invalid input (empty URLs, etc.)
- `FileNotFoundError`: Local folder doesn't exist
- `RuntimeError`: Git clone failures
- Automatic cleanup on failures

## Testing

Run tests with:
```bash
cd v2
python -m pytest tests/test_sources_service.py -v
```

Or with unittest:
```bash
python tests/test_sources_service.py
```

## Security Considerations

- Only public GitHub repos are supported without authentication
- For private repos, ensure proper git credentials are configured
- Local folder paths are validated to prevent directory traversal
- All sources are copied/cloned to isolated directories with unique IDs