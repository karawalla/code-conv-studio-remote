#!/bin/bash

# Start script for Any-to-Any Conversion Studio v2

echo "Starting Any-to-Any Conversion Studio v2..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Start the Flask application
python app.py