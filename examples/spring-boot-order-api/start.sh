#!/bin/bash

echo "🚀 Starting Spring Boot Order Management API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "📦 Starting external services (PostgreSQL, Redis, ActiveMQ)..."
docker-compose up -d postgres redis activemq

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."
docker-compose ps

echo "🏗️  Building and starting the application..."
docker-compose up --build -d order-api

echo "⏳ Waiting for application to start..."
sleep 30

echo "✅ Application started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   API: http://localhost:8080/api"
echo "   Swagger UI: http://localhost:8080/swagger-ui.html"
echo "   Database Admin: http://localhost:8081"
echo "   ActiveMQ Console: http://localhost:8161/console (admin/admin)"
echo ""
echo "📚 Sample API calls:"
echo "   Register: curl -X POST http://localhost:8080/api/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\",\"firstName\":\"Test\",\"lastName\":\"User\"}'"
echo "   Login: curl -X POST http://localhost:8080/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"password123\"}'"
echo "   Get Products: curl http://localhost:8080/api/products"
echo ""
echo "📊 Monitor logs with: docker-compose logs -f order-api"
echo "🛑 Stop with: docker-compose down"
