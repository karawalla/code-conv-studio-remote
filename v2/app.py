"""
Any-to-Any Code Conversion Studio v2
A modern web application for converting between different frameworks and languages
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Application Configuration
class Config:
    """Application configuration"""
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATA_FOLDER = os.path.join(os.getcwd(), 'v2', 'data')
    UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    
    # Ensure folders exist
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    # Mock data for now
    return jsonify({
        'sources': {
            'total': 5,
            'active': 3,
            'types': ['Java Spring Boot', 'Python Django', 'Node.js Express', 'Ruby on Rails', 'PHP Laravel']
        },
        'targets': {
            'total': 4,
            'active': 2,
            'types': ['Sage IT', 'AWS Lambda', 'Kubernetes', 'Docker Compose']
        },
        'jobs': {
            'total': 15,
            'running': 2,
            'completed': 10,
            'failed': 3,
            'recent': [
                {'id': 1, 'name': 'Spring to Sage Migration', 'status': 'completed', 'progress': 100},
                {'id': 2, 'name': 'Django to Lambda', 'status': 'running', 'progress': 45},
                {'id': 3, 'name': 'Express to K8s', 'status': 'running', 'progress': 72}
            ]
        },
        'conversions': {
            'today': 5,
            'week': 28,
            'month': 156,
            'success_rate': 87.5
        }
    })

@app.route('/api/sources')
def get_sources():
    """Get configured sources"""
    # Mock data
    sources = [
        {
            'id': 'java-spring',
            'name': 'Java Spring Boot',
            'description': 'Spring Boot 2.x/3.x applications',
            'icon': '☕',
            'active': True,
            'frameworks': ['Spring Boot 2.x', 'Spring Boot 3.x', 'Spring Cloud'],
            'file_patterns': ['*.java', 'pom.xml', 'build.gradle']
        },
        {
            'id': 'python-django',
            'name': 'Python Django',
            'description': 'Django 3.x/4.x applications',
            'icon': '🐍',
            'active': True,
            'frameworks': ['Django 3.x', 'Django 4.x', 'Django REST Framework'],
            'file_patterns': ['*.py', 'requirements.txt', 'manage.py']
        },
        {
            'id': 'nodejs-express',
            'name': 'Node.js Express',
            'description': 'Express.js applications',
            'icon': '🟢',
            'active': True,
            'frameworks': ['Express 4.x', 'Express 5.x', 'NestJS'],
            'file_patterns': ['*.js', '*.ts', 'package.json']
        }
    ]
    return jsonify(sources)

@app.route('/api/targets')
def get_targets():
    """Get configured targets"""
    # Mock data
    targets = [
        {
            'id': 'sage-it',
            'name': 'Sage IT',
            'description': 'Sage IT Framework with JMS and microservices',
            'icon': '🎯',
            'active': True,
            'features': ['JMS Integration', 'Microservices', 'Event Driven'],
            'requirements': ['Java 11+', 'ActiveMQ', 'Spring Boot']
        },
        {
            'id': 'aws-lambda',
            'name': 'AWS Lambda',
            'description': 'Serverless functions on AWS',
            'icon': '☁️',
            'active': True,
            'features': ['Serverless', 'Auto-scaling', 'Pay per use'],
            'requirements': ['AWS Account', 'Node.js/Python/Java']
        },
        {
            'id': 'kubernetes',
            'name': 'Kubernetes',
            'description': 'Container orchestration platform',
            'icon': '☸️',
            'active': False,
            'features': ['Container Orchestration', 'Auto-scaling', 'Service Mesh'],
            'requirements': ['Docker', 'Kubernetes Cluster']
        }
    ]
    return jsonify(targets)

@app.route('/api/jobs')
def get_jobs():
    """Get jobs list"""
    # Mock data
    jobs = [
        {
            'id': 1,
            'name': 'Spring Boot to Sage IT - Order Service',
            'source': 'java-spring',
            'target': 'sage-it',
            'status': 'completed',
            'progress': 100,
            'created': '2025-06-27T10:00:00',
            'completed': '2025-06-27T10:15:00',
            'stages': 4,
            'current_stage': 4
        },
        {
            'id': 2,
            'name': 'Django API to AWS Lambda',
            'source': 'python-django',
            'target': 'aws-lambda',
            'status': 'running',
            'progress': 45,
            'created': '2025-06-27T11:00:00',
            'stages': 5,
            'current_stage': 2
        },
        {
            'id': 3,
            'name': 'Express Microservice to K8s',
            'source': 'nodejs-express',
            'target': 'kubernetes',
            'status': 'failed',
            'progress': 30,
            'created': '2025-06-27T09:00:00',
            'error': 'Missing Dockerfile configuration',
            'stages': 6,
            'current_stage': 2
        }
    ]
    return jsonify(jobs)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Any-to-Any Conversion Studio v2 on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)