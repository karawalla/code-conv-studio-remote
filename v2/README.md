# Any-to-Any Conversion Studio v2

A modern web application for converting code between different frameworks and platforms.

## Features

- **Dashboard**: Overview of conversion statistics, active jobs, and recent activity
- **Sources Management**: Configure source frameworks (Java Spring Boot, Python Django, Node.js Express, etc.)
- **Targets Management**: Configure target platforms (Sage IT, AWS Lambda, Kubernetes, etc.)
- **Jobs Management**: Create, monitor, and manage conversion jobs
- **Clean UI**: Modern, responsive interface inspired by professional dashboard designs

## Project Structure

```
v2/
├── app.py                 # Main Flask application
├── templates/            
│   └── dashboard.html    # Main dashboard template
├── static/
│   ├── css/
│   │   └── dashboard.css # Dashboard styles
│   └── js/
│       └── dashboard.js  # Dashboard JavaScript
├── models/               # Data models (future)
├── controllers/          # Route controllers (future)
├── services/             # Business logic services (future)
└── utils/                # Utility functions (future)
```

## Getting Started

### Using Docker (Recommended)

1. Navigate to the v2 directory:
   ```bash
   cd v2
   ```

2. Start the application with Docker:
   ```bash
   ./docker-start.sh
   ```

3. Open your browser to http://localhost:5000

4. To stop the application:
   ```bash
   ./docker-stop.sh
   ```

### Manual Installation

1. Navigate to the v2 directory:
   ```bash
   cd v2
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-cors
   ```

3. Run the application:
   ```bash
   ./start.sh
   ```
   Or directly:
   ```bash
   python app.py
   ```

4. Open your browser to http://localhost:5000

## Dashboard Overview

### Home Page
- Statistics cards showing total conversions, active jobs, success rate, and configured sources
- Conversion overview chart
- Recent jobs activity
- Quick actions for common tasks

### Sources Page
- View all configured source frameworks
- Add new sources
- Enable/disable sources
- View supported frameworks and file patterns

### Targets Page
- View all configured target platforms
- Add new targets
- Enable/disable targets
- View features and requirements

### Jobs Page
- Create new conversion jobs
- Monitor running jobs
- View job history
- Filter and search jobs

### Settings Page
- Configure application settings
- Set notification preferences
- Manage system configuration

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/health` - Health check
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/sources` - List configured sources
- `GET /api/targets` - List configured targets
- `GET /api/jobs` - List conversion jobs

## Next Steps

1. **Backend Integration**: Connect to the existing Claude-based conversion engine
2. **Database**: Add persistent storage for jobs, sources, and targets
3. **Job Processing**: Implement actual conversion job processing
4. **File Upload**: Add file upload functionality for source code
5. **Real-time Updates**: WebSocket support for live job progress
6. **Authentication**: Add user authentication and authorization
7. **Logging**: Comprehensive logging and monitoring

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with modern design principles
- **Icons**: SVG icons for scalability
- **Font**: Inter for clean typography