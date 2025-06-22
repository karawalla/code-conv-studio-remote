# Spring Boot Order Management API

A comprehensive, production-ready Spring Boot REST API for order management with authentication, caching, message queuing, and database integration.

## 🚀 Features

### Core Features
- **RESTful API** - Complete CRUD operations for orders, products, and users
- **JWT Authentication** - Secure token-based authentication and authorization
- **Role-based Access Control** - User and Admin roles with different permissions
- **Database Integration** - PostgreSQL with JPA/Hibernate
- **Caching** - Redis-based caching for improved performance
- **Message Queuing** - ActiveMQ for asynchronous order processing
- **API Documentation** - Swagger/OpenAPI 3.0 documentation
- **Monitoring** - Spring Boot Actuator for health checks and metrics

### Architecture
- **Layered Architecture** - Controller → Service → Repository pattern
- **DTO Pattern** - Separate request/response objects
- **Exception Handling** - Global exception handler with proper error responses
- **Validation** - Bean validation with custom error messages
- **Transaction Management** - Declarative transaction management
- **Testing** - Unit and integration tests with high coverage

## 🛠️ Technology Stack

- **Java 17** - Latest LTS version
- **Spring Boot 3.2.1** - Latest stable version
- **Spring Security** - Authentication and authorization
- **Spring Data JPA** - Database access layer
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **ActiveMQ** - Message broker
- **JWT** - Token-based authentication
- **Maven** - Build tool
- **Docker** - Containerization
- **JUnit 5** - Testing framework
- **Testcontainers** - Integration testing

## 📋 Prerequisites

- Java 17 or higher
- Maven 3.6 or higher
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)
- ActiveMQ (if running locally)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd spring-boot-order-api
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Wait for services to be healthy**
   ```bash
   docker-compose ps
   ```

4. **Access the application**
   - API: http://localhost:8080/api
   - Swagger UI: http://localhost:8080/swagger-ui.html
   - Database Admin: http://localhost:8081 (Adminer)
   - ActiveMQ Console: http://localhost:8161/console (admin/admin)

### Local Development

1. **Start external services**
   ```bash
   docker-compose up postgres redis activemq -d
   ```

2. **Run the application**
   ```bash
   ./mvnw spring-boot:run
   ```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "Bearer",
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "role": "USER"
}
```

### Product Endpoints

#### Get All Products
```http
GET /api/products?page=0&size=10&sortBy=name&sortDir=asc
```

#### Get Product by ID
```http
GET /api/products/{id}
```

#### Create Product (Admin only)
```http
POST /api/products
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "iPhone 15 Pro",
  "description": "Latest Apple smartphone",
  "price": 999.99,
  "stockQuantity": 50,
  "category": "Electronics",
  "brand": "Apple",
  "imageUrl": "https://example.com/iphone15pro.jpg"
}
```

### Order Endpoints

#### Create Order
```http
POST /api/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "items": [
    {
      "productId": 1,
      "quantity": 2
    }
  ],
  "shippingAddress": "123 Main St, Anytown, USA 12345"
}
```

#### Get User Orders
```http
GET /api/orders?page=0&size=10
Authorization: Bearer {token}
```

#### Get Order by ID
```http
GET /api/orders/{id}
Authorization: Bearer {token}
```

#### Cancel Order
```http
PUT /api/orders/{id}/cancel
Authorization: Bearer {token}
```

## 🏗️ Architecture Overview

### Project Structure
```
src/
├── main/
│   ├── java/com/example/orderapi/
│   │   ├── config/          # Configuration classes
│   │   ├── controller/      # REST controllers
│   │   ├── dto/            # Data transfer objects
│   │   ├── entity/         # JPA entities
│   │   ├── exception/      # Exception handling
│   │   ├── jms/           # Message listeners
│   │   ├── repository/     # Data repositories
│   │   ├── security/       # Security components
│   │   └── service/        # Business logic
│   └── resources/
│       ├── application.yml # Configuration
│       └── data.sql       # Sample data
└── test/                  # Test classes
```

### Database Schema

#### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Encrypted)
- firstName, lastName
- role (USER/ADMIN)
- enabled
- createdAt, updatedAt

#### Products Table
- id (Primary Key)
- name (Unique)
- description
- price
- stockQuantity
- category, brand
- imageUrl
- active
- createdAt, updatedAt

#### Orders Table
- id (Primary Key)
- userId (Foreign Key)
- status (PENDING/CONFIRMED/PROCESSING/SHIPPED/DELIVERED/CANCELLED)
- totalAmount
- shippingAddress
- orderDate, shippedDate, deliveredDate
- createdAt, updatedAt

#### Order Items Table
- id (Primary Key)
- orderId (Foreign Key)
- productId (Foreign Key)
- quantity
- unitPrice, totalPrice
- createdAt, updatedAt

## 🔧 Configuration

### Application Properties

Key configuration properties in `application.yml`:

```yaml
app:
  jwt:
    secret: mySecretKey123456789012345678901234567890
    expiration: 86400000 # 24 hours
  
  cache:
    product-ttl: 3600 # 1 hour
    user-ttl: 1800 # 30 minutes
```

### Environment Variables

For Docker deployment:
- `SPRING_PROFILES_ACTIVE=docker`
- `SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/orderdb`
- `SPRING_DATA_REDIS_HOST=redis`
- `SPRING_ACTIVEMQ_BROKER_URL=tcp://activemq:61616`

## 🧪 Testing

### Run All Tests
```bash
./mvnw test
```

### Run Integration Tests
```bash
./mvnw test -Dtest="*IntegrationTest"
```

### Test Coverage
The project includes:
- Unit tests for services and components
- Integration tests for controllers and repositories
- Test containers for database testing
- Mock-based testing for external dependencies

## 📊 Monitoring and Health Checks

### Health Check Endpoint
```http
GET /api/actuator/health
```

### Metrics Endpoint
```http
GET /api/actuator/metrics
```

### Application Info
```http
GET /api/actuator/info
```

## 🔒 Security

### Authentication Flow
1. User registers or logs in with credentials
2. Server validates credentials and returns JWT token
3. Client includes token in Authorization header for protected endpoints
4. Server validates token and extracts user information

### Authorization Levels
- **Public**: Product browsing, user registration/login
- **User**: Order management, profile access
- **Admin**: Product management, order administration, user management

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up --build -d

# Scale the application
docker-compose up --scale order-api=3 -d

# View logs
docker-compose logs -f order-api
```

### Production Considerations
- Use environment-specific configuration files
- Set up proper logging and monitoring
- Configure SSL/TLS certificates
- Set up database connection pooling
- Configure Redis clustering for high availability
- Set up load balancing for multiple instances

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or support, please open an issue in the repository or contact the development team.
