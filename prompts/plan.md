# Spring Boot to Ship Format Repository-Level Migration Plan Prompt

## Objective
Generate a comprehensive repository-level migration plan for converting a Spring Boot application to Ship format JSON, providing project overview, structure analysis, and phased conversion strategy.

## Instructions for Plan Generation

### 1. Project Discovery and Analysis

#### A. Project Structure Scan
Analyze the Spring Boot project directory to understand:
- **Project Type**: Maven or Gradle based on presence of pom.xml or build.gradle
- **Source Structure**: Standard Maven/Gradle layout (src/main/java, src/main/resources)
- **Test Structure**: Presence and organization of tests
- **Resource Files**: Configuration files, static resources, templates

#### B. Package Inventory
List all packages and infer their purpose from naming:
```
com.example.demo
├── controller     → REST API endpoints (→ HTTP Listener flows)
├── service       → Business logic layer (→ Transform/Flow Reference)
├── repository    → Data access layer (→ Database operations)
├── model/entity  → Domain objects (→ DataWeave schemas)
├── config        → Configuration classes (→ Global elements)
├── exception     → Custom exceptions (→ Error handling)
├── messaging     → JMS/MQ operations (→ JMS Publish)
├── scheduled     → Scheduled tasks (→ Scheduler flows)
└── util          → Utility classes (→ DataWeave functions)
```

#### C. File Type Distribution
Count files by type to understand project complexity:
- Controllers (REST endpoints) → Number of flows needed
- Services (business logic) → Sub-flows/Flow references
- Repositories (data access) → Database components
- Entities (domain models) → DataWeave transformations
- Scheduled tasks → Scheduler-triggered flows
- Configuration files → Global elements
- Properties/YAML files → globalVariables entries

### 2. Current Spring Boot Project Tree

Generate a visual tree structure showing:
```
SpringBootApp/
├── pom.xml (or build.gradle)
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       ├── [Application].java
│   │   │       ├── controller/
│   │   │       │   └── [REST Controllers]
│   │   │       ├── service/
│   │   │       │   └── [Service classes]
│   │   │       ├── repository/
│   │   │       │   └── [Repository interfaces]
│   │   │       ├── model/
│   │   │       │   └── [Entity classes]
│   │   │       ├── messaging/
│   │   │       │   └── [JMS producers/consumers]
│   │   │       └── scheduled/
│   │   │           └── [Scheduled tasks]
│   │   └── resources/
│   │       ├── application.properties
│   │       ├── application-{profile}.properties
│   │       └── static/
│   └── test/
│       └── java/
└── target/
```

### 3. Proposed Ship Format Structure

Design the Ship format output structure:
```
ship-output/
├── ship_output.json
│   ├── flows[]
│   │   ├── HTTP endpoint flows
│   │   ├── Scheduled task flows
│   │   └── Sub-flows for services
│   ├── globalElements[]
│   │   ├── HTTP_Listener_Configuration
│   │   ├── Database_Configuration
│   │   ├── File_Configuration
│   │   ├── JMS_Configuration
│   │   └── HTTP_Request_Configuration
│   ├── globalConfig[]
│   │   └── [Mirror of globalElements configs]
│   ├── globalVariables{}
│   │   └── [All application.properties as structured objects]
│   └── projectInformation{}
│       ├── sourceProjectType: "SpringBoot"
│       ├── destinationPlatform: "mule"
│       └── summary{}
└── documentation/
    ├── component-mapping.md
    ├── flow-documentation.md
    └── migration-notes.md
```

### 4. Project Summary Template

Generate a summary following this structure:

```markdown
# [Project Name] Ship Format Migration Summary

## Application Overview
- **Purpose**: [Brief description of what the application does]
- **Type**: [REST API / Web Application / Microservice / Batch Processing]
- **Current Stack**: Spring Boot [version], Java [version]
- **Target Format**: Ship JSON format for integration platform import

## Functional Domains
[List the main functional areas, e.g., File Processing, Order Management, User Services]

## API Endpoints Summary
- Total Endpoints: [count]
- HTTP Methods Used: [GET, POST, PUT, DELETE, etc.]
- Base Path: [e.g., /api]
- Main Resources: [e.g., /files/process, /orders, /users]

## Scheduled Tasks Summary
- Total Scheduled Tasks: [count]
- Types: [Fixed delay, Fixed rate, Cron expressions]
- Purpose: [File cleanup, batch processing, etc.]

## Data Persistence
- Database Type: [MySQL/PostgreSQL/Oracle/etc.]
- Connection Pattern: [JPA/JDBC]
- Tables/Entities: [count and list]

## Integration Points
- File Operations: [Read/Write patterns]
- JMS/ActiveMQ: [Queues/Topics used]
- External HTTP Services: [REST API calls]

## Configuration Overview
- Profiles: [dev, test, prod]
- Port: [8080]
- Key Properties: [list all properties for globalVariables]
```

### 5. Migration Strategy Plan

#### Stage 1: Foundation Analysis
```
Tasks:
□ Scan project structure and create inventory
□ Identify all Spring Boot components
□ Map application.properties to globalVariables structure
□ Identify all external configurations needed
□ Document all integration patterns (DB, JMS, File, HTTP)
□ Count and categorize all endpoints and scheduled tasks
```

#### Stage 2: Global Configuration Setup
```
Tasks:
□ Create globalElements array with all configurations:
  - HTTP_Listener_Configuration
  - Database_Configuration (if DB operations exist)
  - File_Configuration (if file operations exist)
  - JMS_Configuration (if messaging exists)
  - HTTP_Request_Configuration (if external calls exist)
□ Mirror configurations in globalConfig array
□ Convert all properties to globalVariables with proper structure:
  - source: ""
  - type: "string" (always)
  - value: "[actual value]"
□ Ensure all ${property} references have corresponding entries
```

#### Stage 3: Flow Design and Component Mapping
```
Tasks:
□ Design flows for each REST endpoint:
  - HTTP Listener as entry point
  - Transform Message for parameter extraction
  - Business logic components
  - Response formatting
□ Design flows for each @Scheduled method:
  - Scheduler as entry point
  - Processing logic components
□ Map Spring patterns to Ship components:
  - @GetMapping/@PostMapping → HTTP Listener
  - @RequestParam → attributes.queryParams extraction
  - @PathVariable → attributes.uriParams extraction
  - @Scheduled → Scheduler component
  - Repository methods → Database operations
  - File operations → File Read/Write/List
  - JmsTemplate → JMS Publish
  - RestTemplate/WebClient → HTTP Request
```

#### Stage 4: Component Structure Implementation
```
Tasks:
□ Implement proper component structure for each flow:
  - All required fields in exact order
  - Valid UUID v4 for all doc:id attributes
  - Proper sequenceId progression
  - Correct parentId relationships
  - Accurate activityType assignments
□ Create branching logic using links:
  - xpath conditions for if/else patterns
  - otherwise links for default cases
  - No choice components
□ Implement error handling:
  - Raise Error with "description" attribute
  - Proper error types (VALIDATION:NULL, etc.)
```

#### Stage 5: Business Logic Conversion
```
Tasks:
□ Convert service methods to appropriate patterns:
  - Simple logic → Transform Message
  - Complex logic → Flow Reference to sub-flow
  - Conditional logic → Link-based branching
□ Handle data transformations:
  - Entity mappings → DataWeave in Transform Message
  - JSON processing → DataWeave scripts
□ Convert validation logic:
  - Bean validation → DataWeave validation
  - Custom validators → Transform Message with conditions
```

#### Stage 6: Data Access Layer Conversion
```
Tasks:
□ Map repository operations to Database components:
  - findById() → Database Select with parameters
  - save() → Database Insert/Update
  - delete() → Database Delete
  - Custom queries → Database Select with SQL
□ Handle transactions:
  - @Transactional → Proper flow error handling
□ Convert entity relationships:
  - JPA mappings → DataWeave transformations
```

#### Stage 7: Integration Components
```
Tasks:
□ Convert file operations:
  - new File() checks → File List with sizeOf(payload)
  - File reading → File Read
  - File writing → File Write with proper content
□ Convert JMS operations:
  - JmsTemplate.send() → JMS Publish
  - Message formatting → Transform Message before publish
□ Convert external HTTP calls:
  - RestTemplate/WebClient → HTTP Request
  - Request/Response handling → Transform Message
```

#### Stage 8: Testing and Validation
```
Tasks:
□ Validate JSON structure:
  - All required fields present
  - Proper data types
  - Valid UUID formats
□ Verify flow connectivity:
  - All components linked
  - No orphan components
  - Proper branching logic
□ Check completeness:
  - All endpoints converted
  - All scheduled tasks included
  - All properties in globalVariables
□ Validate component naming:
  - Follows camelCase conventions
  - Descriptive and unique names
```

### 6. Component Mapping Summary

Generate a high-level mapping table:

| Spring Component | Count | Ship Component | Flow Pattern |
|-----------------|-------|----------------|--------------|
| @RestController | X | HTTP Listener + Flow | One flow per endpoint |
| @GetMapping | X | HTTP Listener | Extract path/query params |
| @PostMapping | X | HTTP Listener | Process request body |
| @Scheduled | X | Scheduler | Scheduler-triggered flow |
| @Service | X | Transform/Flow Reference | Business logic pattern |
| @Repository | X | Database operations | DB Select/Insert/Update |
| @Entity | X | DataWeave schemas | Transform Message |
| JmsTemplate | X | JMS Publish | Message publishing |
| File operations | X | File Read/Write/List | File handling |
| @Value | X | globalVariables | Property references |

### 7. Risk Assessment Matrix

| Risk Category | Description | Impact | Mitigation Strategy |
|--------------|-------------|---------|-------------------|
| **Conversion Risks** |
| Complex Logic | Nested conditions/loops | Medium | Use proper link branching |
| UUID Generation | Invalid doc:id values | High | Validate UUID v4 format |
| Property References | Missing globalVariables | Medium | Scan all ${} references |
| **Component Risks** |
| Advanced Operations | Using restricted components | High | Stick to allowed set |
| Branching Logic | Choice component usage | Medium | Use link-based control |
| File Operations | Advanced file operations | Low | Use basic read/write only |
| **Structure Risks** |
| Component Order | Wrong sequencing | Medium | Follow execution flow |
| Parent-Child Relations | Incorrect parentId | High | Validate relationships |
| Link Connectivity | Orphan components | High | Verify all links |

### 8. Validation Checklist Generator

Create a comprehensive validation checklist:

```markdown
## Pre-Conversion Checklist
- [ ] Inventory all REST endpoints
- [ ] List all scheduled tasks
- [ ] Document all external integrations
- [ ] Extract all application properties
- [ ] Identify file operation patterns
- [ ] List JMS/messaging usage

## Conversion Execution Checklist
- [ ] Create proper JSON structure
- [ ] Generate valid UUIDs for all doc:id
- [ ] Map all endpoints to flows
- [ ] Convert all scheduled tasks
- [ ] Include all global configurations
- [ ] Add all properties to globalVariables
- [ ] Implement proper error handling
- [ ] Create link-based branching
- [ ] Validate component structure
- [ ] Check naming conventions

## Post-Conversion Checklist
- [ ] JSON structure validation
- [ ] UUID format verification
- [ ] Flow connectivity check
- [ ] Component completeness
- [ ] Global variable coverage
- [ ] Error handling review
- [ ] Documentation complete
```

### 9. Common Patterns Reference

#### REST Endpoint Pattern:
```
1. HTTP Listener (start: "true")
2. Transform Message (extract parameters)
3. Business logic components
4. Database/File/JMS operations
5. Response formatting
```

#### Scheduled Task Pattern:
```
1. Scheduler (start: "true")
2. Trigger logic components
3. Processing operations
4. Result handling
```

#### Error Handling Pattern:
```
- Validation failure → Raise Error (VALIDATION:NULL)
- Not found → Raise Error (VALIDATION:NULL)
- Database error → Raise Error (DB:CONNECTIVITY)
```

#### File Processing Pattern:
```
1. File List (check existence)
2. Conditional branching (xpath: sizeOf(payload))
3. File Read (if exists)
4. Process content
5. File Write (results)
```

### 10. Output Format

The migration plan should be generated as a structured markdown document:

```markdown
# [Application Name] Spring Boot to Ship Format Migration Plan

## Executive Summary
[High-level overview of the migration to Ship format]

## Current State Analysis
[Include project tree, component counts, integration patterns]

## Target Ship Format Structure
[JSON structure overview, component mapping]

## Migration Strategy
[Staged approach without specific timelines]

## Component Mapping Details
[Detailed mapping of Spring to Ship components]

## Global Configuration Requirements
[List of globalElements, globalVariables needed]

## Risk Assessment
[Technical and structural risks with mitigation]

## Validation Criteria
[Checklist for ensuring correct Ship format]

## Appendices
- Complete Component Inventory
- Property Mapping Table
- Flow Design Patterns
- Common Conversion Examples
```

## Usage Instructions

1. Run this analysis on the Spring Boot project root directory
2. Use file system scanning to gather project structure
3. Generate counts and summaries based on file names and patterns
4. Create component mapping based on Spring annotations
5. Design Ship format JSON structure following specification
6. Focus on structural conversion rather than timeline-based phases
7. Emphasize validation and correctness of Ship format output

This prompt ensures efficient repository-level planning for Spring Boot to Ship format conversion, providing a clear roadmap without timeline constraints while maintaining focus on the specific requirements of the Ship JSON specification.