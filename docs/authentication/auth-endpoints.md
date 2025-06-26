# Authentication API Endpoints

The Code Conversion Studio provides several API endpoints for managing Claude authentication.

## Available Endpoints

### 1. Check Authentication Status
```
GET /api/auth/status
```

Returns the current authentication status and information about the last refresh.

**Response:**
```json
{
  "authenticated": true,
  "last_refresh": "2025-06-23T10:30:00Z",
  "refresh_interval": 240,
  "auth_type": "oauth|api_key",
  "session_active": true
}
```

### 2. Refresh Authentication
```
POST /api/auth/refresh
```

Manually triggers an authentication refresh. This is useful for debugging or when you suspect authentication issues.

**Response:**
```json
{
  "success": true,
  "message": "Authentication refreshed successfully",
  "timestamp": "2025-06-23T10:35:00Z"
}
```

### 3. Update API Key
```
POST /api/auth/update-key
Content-Type: application/json

{
  "api_key": "your-new-api-key-here"
}
```

Updates the Claude API key and refreshes authentication.

**Response:**
```json
{
  "success": true,
  "message": "API key updated successfully",
  "auth_test": true
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": true,
  "message": "Description of the error",
  "code": "ERROR_CODE"
}
```

Common error codes:
- `AUTH_FAILED` - Authentication test failed
- `INVALID_KEY` - Provided API key is invalid
- `REFRESH_ERROR` - Failed to refresh authentication
- `NO_AUTH` - No authentication configured

## Usage Examples

### Check Status with cURL
```bash
curl http://localhost/api/auth/status
```

### Refresh Authentication
```bash
curl -X POST http://localhost/api/auth/refresh
```

### Update API Key
```bash
curl -X POST http://localhost/api/auth/update-key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-ant-api03-..."}'
```

## Integration with Flask App

These endpoints are automatically available when the Flask application is running with the authentication manager enabled. The authentication manager runs a background daemon that automatically refreshes authentication every 4 minutes to prevent timeouts.