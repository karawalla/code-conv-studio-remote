# Spring Boot to Ship Format Migration Guide

## Overview

This guide provides a focused approach to converting Spring Boot applications into the Ship format JSON structure - an intermediate representation for MuleSoft integration flows. The Ship format enables automated import into MuleSoft Anypoint Studio while maintaining the business logic and flow structure of the original Spring Boot application.

## High-Level MuleSoft Architecture

### Core MuleSoft Concepts

**1. Flows**
- Primary containers for integration logic
- Each flow represents an independent execution path
- Triggered by inbound endpoints (HTTP, JMS, File, Scheduler)

**2. Components**
- Individual processing units within flows
- Connected sequentially or conditionally
- Each performs a specific operation (transform, route, enrich)

**3. Global Configurations**
- Shared configuration elements
- Referenced by multiple components
- Include connectors, property placeholders, error handlers

**4. DataWeave**
- MuleSoft's transformation language
- Handles data mapping and transformation
- Replaces Java code logic with declarative expressions

### Architecture Principles

- **Message-Driven**: All processing based on message flow
- **Declarative**: Configuration over code
- **Stateless**: Each message processed independently
- **Event-Based**: Components react to message events

## Spring Boot to Ship Format Mapping

### Key Component Mappings

| Spring Boot | Ship Format Component | Purpose |
|------------|----------------------|---------|
| @RestController | HTTP Listener | API endpoint |
| @Service | Flow/Sub-flow | Business logic |
| @Repository | Database Operations | Data access |
| @Scheduled | Scheduler | Timed triggers |
| RestTemplate | HTTP Request | External calls |
| JmsTemplate | JMS Publish | Messaging |
| File operations | File Read/Write | File handling |

### Suggested MuleSoft Project Structure

```
mulesoft-project/
├── src/
│   ├── main/
│   │   ├── mule/
│   │   │   ├── main-flows.xml          # Primary API flows
│   │   │   ├── sub-flows.xml           # Reusable logic
│   │   │   ├── error-handling.xml      # Global error handlers
│   │   │   └── global-config.xml       # Configurations
│   │   └── resources/
│   │       ├── application.yaml        # Environment properties
│   │       ├── dev.yaml                # Dev environment
│   │       ├── test.yaml               # Test environment
│   │       └── prod.yaml               # Prod environment
│   └── test/
│       └── munit/                      # MUnit test files
├── pom.xml                             # Maven configuration
└── mule-artifact.json                  # Mule deployment descriptor
```

### Flow Organization Pattern

```
Main Flows (API Entry Points):
├── HTTP API Flows
│   ├── user-api-flow
│   ├── order-api-flow
│   └── product-api-flow
├── Scheduled Flows
│   ├── daily-batch-flow
│   └── hourly-sync-flow
└── Event Flows
    ├── jms-listener-flow
    └── file-watcher-flow

Sub-Flows (Reusable Logic):
├── Business Logic
│   ├── validate-user-subflow
│   ├── calculate-price-subflow
│   └── process-order-subflow
├── Data Access
│   ├── get-user-data-subflow
│   └── save-order-subflow
└── Integration
    ├── send-notification-subflow
    └── call-external-api-subflow
```

## Ship Format JSON Structure

### Core Structure
```json
{
  "flows": [],              // Array of flow definitions
  "globalElements": [],     // Shared configurations
  "globalConfig": [],       // Mirror of globalElements
  "globalVariables": {},    // Application properties
  "projectInformation": {}  // Metadata and statistics
}
```

### Flow Definition
```json
{
  "name": "processOrderFlow",
  "components": [
    {
      "activityType": "HTTP Listener",
      "sequenceId": 1,
      "parentId": [0],
      "start": "true",
      "code": "<http:listener .../>"
    }
  ],
  "groupActivities": [],
  "links": []
}
```

### Component Structure
Each component must include:
- `activityType`: MuleSoft component type
- `code`: Complete Mule XML with escaped quotes
- `sequenceId`: Unique identifier within flow
- `parentId`: Reference to parent component
- `summary`: Migration tracking metadata

### Link Structure
Defines flow control:
```json
{
  "conditionType": "xpath",
  "from": 3,
  "to": 4,
  "xpath": "payload.status == 'NEW'"
}
```

## Critical Migration Considerations

### 1. UUID Requirements
- Every `doc:id` must be valid UUID v4 format
- Format: `XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX`
- No sequential patterns or text identifiers

### 2. Database Configuration
```xml
<db:my-sql-connection 
  host="jdbc:mysql://localhost" 
  port="${db.port}" 
  user="${db.user}" 
  password="${db.password}" 
  database="${db.database}"/>
```

### 3. Error Handling
```xml
<raise-error 
  type="VALIDATION:NULL" 
  description="User not found"/>
```

### 4. Global Variables Format
```json
"http.port": {
  "source": "",
  "type": "string",
  "value": "8085"
}
```

## Transformation Approach

### 1. Analyze Spring Boot Structure
- Identify all REST endpoints
- Map service dependencies
- Document data flows
- List external integrations

### 2. Design MuleSoft Flows
- One flow per REST endpoint
- Sub-flows for reusable logic
- Global configurations for connections
- Error handling strategy

### 3. Component Mapping
- HTTP endpoints → HTTP Listeners
- Service methods → Transform/Flow-ref
- Repository calls → Database operations
- External calls → HTTP Request
- Message queues → JMS components

### 4. Handle Complex Logic
- Conditionals → Link-based branching
- Loops → DataWeave transformations
- Exception handling → Error scopes
- Transactions → Transactional scopes

## Best Practices

### 1. Flow Design
- Keep flows focused and single-purpose
- Use sub-flows for reusability
- Implement consistent error handling
- Document flow purpose clearly

### 2. Configuration Management
- Use property placeholders for all environments
- No hardcoded values in flows
- Centralize global configurations
- Version control property files

### 3. DataWeave Usage
- Quote reserved words in JSON
- Use appropriate output types
- Leverage built-in functions
- Keep transformations simple

### 4. Naming Conventions
- Flows: `<purpose>Flow` (camelCase)
- Components: Descriptive names
- Variables: Clear, meaningful names
- Properties: Dot notation

## Common Pitfalls to Avoid

1. **Invalid UUIDs**: Always generate proper UUID v4
2. **Hardcoded Values**: Use property placeholders
3. **Missing Error Handling**: Cover all failure scenarios
4. **Complex Logic in Flows**: Use DataWeave for transformations
5. **Improper Component Order**: Maintain logical sequence

## Summary

The Ship format provides a structured approach to migrating Spring Boot applications to MuleSoft. Success requires:

- Understanding MuleSoft's message-driven architecture
- Properly mapping Spring components to MuleSoft equivalents
- Following Ship format specifications exactly
- Validating all generated JSON structures
- Testing migrated flows thoroughly

This migration preserves business logic while adapting to MuleSoft's integration-focused paradigm, enabling scalable and maintainable integration solutions.