# Spring Boot to Ship Format Transformation Guide

## Executive Summary

This guide focuses on transforming Spring Boot applications into Ship format JSON, which serves as an intermediate representation for importing into MuleSoft Anypoint Studio. The Ship format captures integration flows, components, and configurations in a structured JSON that can be validated and imported into integration platforms.

## Java Project Overview

### Sample Project: File Processor HTTP Listener

**Core Technologies:**
- Spring Boot 2.x (REST API framework)
- Spring Data JPA (Database access)
- Spring JMS (Message queue integration)
- Java 8+ (Core language)
- Maven/Gradle (Build tools)

**Project Structure:**
```
fileProcessorHttpListener/
├── src/main/java/com/example/demo/
│   ├── FileProcessorHttpListenerApplication.java
│   ├── Controller/
│   │   └── FileProcessorController.java (@PostMapping)
│   ├── Service/
│   │   ├── FileProcessingService.java
│   │   ├── OrderFileService.java
│   │   ├── InvoiceFileService.java
│   │   └── InventoryFileService.java
│   ├── Repository/
│   │   └── OrderRepository.java
│   ├── Model/
│   │   └── OrderEntity.java
│   ├── Messaging/
│   │   └── JmsProducer.java
│   └── AppConfig/
│       └── AppConfig.java
└── src/main/resources/
    └── application.properties
```

## Spring Boot to MuleSoft Component Mapping

### Controllers → HTTP Listeners
```java
@PostMapping("/api/files/process")
public ResponseEntity<String> processFile(@RequestParam String filePath)
```
**Transforms to:**
- HTTP Listener component (entry point)
- Transform Message (parameter extraction)
- Flow structure for business logic

### Services → Flows/Sub-flows
```java
@Service
public class OrderFileService {
    public boolean process(String filePath) { ... }
}
```
**Transforms to:**
- Separate flow (order-processing-flow)
- Flow Reference component for invocation
- Business logic as connected components

### Repository → Database Operations
```java
@Repository
public interface OrderRepository extends JpaRepository<OrderEntity, Long> {
    save(OrderEntity entity);
}
```
**Transforms to:**
- Database Insert component
- Database Configuration (global element)
- SQL with parameter mapping

### JMS Operations → JMS Components
```java
jmsTemplate.convertAndSend(queueName, message);
```
**Transforms to:**
- JMS Publish component
- JMS Configuration (global element)
- Message body transformation

### File Operations → File Components
```java
File file = new File(filePath);
if (file.exists()) { ... }
```
**Transforms to:**
- File Read component (for existence check)
- File Write component (for output)
- File Configuration (global element)

## Ship Format Structure Breakdown

### 1. flows[] - Integration Flows
The heart of the Ship format, containing arrays of flows that represent:
- **Main flows**: HTTP endpoints, scheduled tasks
- **Sub-flows**: Reusable business logic (called via flow-ref)

Each flow contains:
```json
{
  "flowName": "file-processor-main-flow",
  "isSubFlow": false,
  "components": [...],  // Array of activities
  "links": [...]        // Connection logic between components
}
```

### 2. components[] - Flow Components
Individual activities within flows, each containing:
```json
{
  "activityType": "HTTP_Listener",      // Component type
  "activityConfig": "httpListenerConfig", // Reference to global config
  "code": "<http:listener .../>",        // Actual Mule XML
  "name": "File Processor Listener",     // Display name
  "parentId": [0],                       // Parent component reference
  "sequenceId": 1,                       // Unique ID within flow
  "start": "true",                       // Entry point indicator
  "summary": {                           // Migration metadata
    "sourceType": "@PostMapping",
    "simType": "HTTP_Listener",
    "simFound": true,
    "codeGenerated": true
  }
}
```

### 3. links[] - Flow Control
Defines how components connect and branch:
```json
{
  "conditionType": "xpath",              // always, xpath, otherwise, error
  "description": "Check file type",
  "from": 7,                             // Source sequenceId
  "to": 8,                               // Target sequenceId
  "xpath": "contains(vars.fileType, 'order')" // Condition expression
}
```

### 4. globalElements[] - Shared Configurations
Reusable configuration elements:
- HTTP Listener Configuration (port, host)
- Database Configuration (connection details)
- JMS Configuration (broker URL, credentials)
- File Configuration (working directory)
- HTTP Request Configuration (external APIs)

### 5. globalVariables{} - Application Properties
All Spring Boot properties transformed to structured format:
```json
"http.port": {
  "source": "",
  "type": "string",
  "value": "8085"
}
```

### 6. projectInformation{} - Metadata
Project-level information and migration statistics:
```json
{
  "sourceProjectType": "SpringBoot",
  "destinationPlatform": "mule",
  "summary": {
    "totalComponents": 34,
    "fullyMigrated": 34,
    "fullMigratedActivities": ["HTTP_Listener", "Transform_Message", ...]
  }
}
```

## MuleSoft Architecture Constraints & Considerations

### 1. Component Limitations
- **No imperative code**: All logic must be declarative components
- **Limited component set**: Only specific MuleSoft components allowed
- **No direct Java execution**: Business logic via DataWeave/components

### 2. Flow Control Differences
- **No if/else blocks**: Use link-based branching with xpath conditions
- **No loops**: Use DataWeave map/filter operations
- **No try-catch**: Error handling via error scopes (not in basic Ship)

### 3. Data Transformation
- **DataWeave required**: All transformations use DataWeave 2.0
- **Type safety**: Explicit output types (application/json, etc.)
- **Reserved words**: Must be quoted in JSON ("type", "class")

### 4. Configuration Management
- **Property placeholders**: ${property.name} syntax everywhere
- **No hardcoding**: All values via globalVariables
- **Environment-specific**: Profiles become property files

## Transformation Risks & Mitigation

### High-Risk Areas

1. **UUID Generation**
   - Risk: Invalid UUIDs block MuleSoft import
   - Mitigation: Validate UUID v4 format for all doc:id

2. **Complex Business Logic**
   - Risk: Java loops/conditions don't map directly
   - Mitigation: Redesign using DataWeave and flow branching

3. **Database Transactions**
   - Risk: @Transactional doesn't translate directly
   - Mitigation: Use proper error handling and rollback strategies

4. **Advanced File Operations**
   - Risk: File.list(), File.copy() not supported
   - Mitigation: Use only basic read/write operations

5. **Stateful Operations**
   - Risk: Session/state management different
   - Mitigation: Use object store or external state management

### Medium-Risk Areas

1. **Property References**
   - Risk: Missing globalVariables entries
   - Mitigation: Scan all ${} references systematically

2. **Error Handling**
   - Risk: Exception hierarchy doesn't translate
   - Mitigation: Map to MuleSoft error types

3. **External Service Calls**
   - Risk: RestTemplate patterns need transformation
   - Mitigation: Use HTTP Request with proper config

### Low-Risk Areas

1. **Simple CRUD Operations**
   - Well-defined mapping to database components

2. **Basic File I/O**
   - Direct mapping to file components

3. **JMS Publishing**
   - Clear transformation to JMS components

## Ship Format Validation Requirements

### Critical Validations
1. **UUID Format**: All doc:id must be valid UUID v4
2. **Component Structure**: All required fields in exact order
3. **Parent-Child Relations**: Proper parentId references
4. **Link Connectivity**: No orphan components
5. **Global Variables**: All ${} references have entries

### Structural Validations
1. **Flow Names**: Unique and descriptive
2. **Component Types**: Only allowed MuleSoft components
3. **Configuration References**: Valid config-ref values
4. **Expression Syntax**: Proper #[] usage
5. **DataWeave Output**: Valid output types

### Best Practices
1. **Modular Design**: Separate flows for distinct functions
2. **Reusable Logic**: Sub-flows for common patterns
3. **Clear Naming**: Descriptive component names
4. **Property Usage**: No hardcoded values
5. **Error Handling**: Comprehensive error scenarios

## Conclusion

The Ship format serves as a critical bridge between Spring Boot applications and MuleSoft integration platforms. Success depends on:

1. **Accurate Mapping**: Every Spring component must map to valid MuleSoft equivalent
2. **Structural Integrity**: Ship JSON must follow exact specification
3. **Complete Coverage**: All endpoints, properties, and configurations included
4. **Validation Compliance**: Pass all format requirements

By following this guide and understanding the constraints, risks, and transformation patterns, Spring Boot applications can be successfully converted to Ship format for MuleSoft import.