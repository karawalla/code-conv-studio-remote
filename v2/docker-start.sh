#!/bin/bash

echo "Building and starting Any-to-Any Conversion Studio v2 with Docker..."

# Build and start the container
docker-compose up --build -d

echo ""
echo "✅ Application started successfully!"
echo "🌐 Access the dashboard at: http://localhost:8080"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"