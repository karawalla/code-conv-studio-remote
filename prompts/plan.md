# Spring Boot to MuleSoft Repository-Level Migration Plan Prompt

## Objective
Generate a comprehensive repository-level migration plan for converting a Spring Boot application to MuleSoft, providing project overview, structure analysis, and phased conversion strategy.

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
├── controller     → REST API endpoints
├── service       → Business logic layer
├── repository    → Data access layer
├── model/entity  → Domain objects
├── config        → Configuration classes
├── exception     → Custom exceptions
├── util          → Utility classes
└── dto           → Data transfer objects
```

#### C. File Type Distribution
Count files by type to understand project complexity:
- Controllers (REST endpoints)
- Services (business logic)
- Repositories (data access)
- Entities (domain models)
- Configuration files
- Properties/YAML files

### 2. Current Spring Boot Project Tree

Generate a visual tree structure showing:
```
SpringBootApp/
├── pom.xml (or build.gradle)
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       ├── SampleSpringBootAppApplication.java
│   │   │       ├── controller/
│   │   │       │   └── [Controller files]
│   │   │       ├── service/
│   │   │       │   └── [Service files]
│   │   │       ├── repository/
│   │   │       │   └── [Repository files]
│   │   │       └── model/
│   │   │           └── [Entity files]
│   │   └── resources/
│   │       ├── application.properties
│   │       ├── static/
│   │       └── templates/
│   └── test/
│       └── java/
└── target/
```

### 3. Proposed MuleSoft Project Structure

Design the target Mule application structure:
```
mule-app/
├── mule-artifact.json
├── pom.xml
├── src/
│   ├── main/
│   │   ├── mule/
│   │   │   ├── global/
│   │   │   │   ├── global-config.xml
│   │   │   │   ├── http-config.xml
│   │   │   │   └── db-config.xml
│   │   │   ├── api/
│   │   │   │   ├── [entity]-api-flows.xml
│   │   │   │   └── api-error-handler.xml
│   │   │   ├── business/
│   │   │   │   └── [entity]-business-logic.xml
│   │   │   ├── data/
│   │   │   │   └── [entity]-data-access.xml
│   │   │   └── common/
│   │   │       ├── transformations.dwl
│   │   │       └── error-handling.xml
│   │   ├── resources/
│   │   │   ├── api/
│   │   │   │   └── [api-spec].raml
│   │   │   ├── properties/
│   │   │   │   ├── application.properties
│   │   │   │   ├── application-dev.properties
│   │   │   │   └── application-prod.properties
│   │   │   ├── schemas/
│   │   │   │   └── [entity]-schema.json
│   │   │   └── log4j2.xml
│   │   └── java/
│   │       └── com/example/
│   │           └── [Custom Java classes if needed]
│   └── test/
│       └── munit/
│           ├── [entity]-api-test-suite.xml
│           └── [entity]-business-test-suite.xml
└── exchange-docs/
    └── home.md
```

### 4. Project Summary Template

Generate a summary following this structure:

```markdown
# [Project Name] Migration Summary

## Application Overview
- **Purpose**: [Brief description of what the application does]
- **Type**: [REST API / Web Application / Microservice]
- **Current Stack**: Spring Boot [version], Java [version]
- **Target Stack**: MuleSoft 4.x, Anypoint Platform

## Functional Domains
[List the main functional areas, e.g., User Management, Order Processing]

## API Endpoints Summary
- Total Endpoints: [count]
- HTTP Methods Used: [GET, POST, PUT, DELETE, etc.]
- Base Path: [e.g., /api]
- Main Resources: [e.g., /users, /orders]

## Data Persistence
- Database Type: [MySQL/PostgreSQL/Oracle/etc.]
- Connection Details: [host:port/database]
- Tables/Entities: [count and list]

## External Integrations
[List any external systems, APIs, or services integrated]

## Configuration Overview
- Profiles: [dev, test, prod]
- Port: [8080]
- Key Properties: [list important configurations]
```

### 5. Migration Strategy Plan

#### Phase 1: Foundation Setup (Week 1)
```
Tasks:
□ Create Mule project structure
□ Set up mule-artifact.json
□ Configure Maven/Gradle build
□ Set up property files
□ Configure logging (log4j2.xml)
□ Create global configuration files
  - HTTP listener configuration
  - Database configuration
  - Error handling strategy
```

#### Phase 2: Data Layer (Week 2)
```
Tasks:
□ Create DataWeave type definitions for entities
□ Implement database sub-flows for each repository
  - Create [entity]-data-access.xml files
  - Map CRUD operations to DB connectors
  - Handle transactions
□ Test database connectivity
□ Validate query operations
```

#### Phase 3: Business Logic Layer (Week 3)
```
Tasks:
□ Convert service classes to business sub-flows
  - Create [entity]-business-logic.xml files
  - Implement validation logic
  - Handle business exceptions
□ Create reusable DataWeave modules
□ Implement cross-cutting concerns
```

#### Phase 4: API Layer (Week 4)
```
Tasks:
□ Convert REST controllers to API flows
  - Create [entity]-api-flows.xml files
  - Configure HTTP listeners for each endpoint
  - Map request/response transformations
□ Implement API error handling
□ Add RAML/OAS documentation
```

#### Phase 5: Testing & Validation (Week 5)
```
Tasks:
□ Create MUnit test suites
□ Migrate unit tests to MUnit
□ Integration testing
□ Performance testing
□ Security validation
```

### 6. Component Mapping Summary

Generate a high-level mapping table:

| Spring Component | Count | Mule Component | Files |
|-----------------|-------|----------------|-------|
| @RestController | X | HTTP Listener + Flow | api/*.xml |
| @Service | X | Sub-flow | business/*.xml |
| @Repository | X | DB Connector | data/*.xml |
| @Entity | X | DataWeave Types | schemas/*.json |
| @Configuration | X | Global Elements | global/*.xml |

### 7. Risk Assessment Matrix

| Risk Category | Description | Impact | Mitigation Strategy |
|--------------|-------------|---------|-------------------|
| **Technical Risks** |
| Spring AOP | Aspects need manual conversion | Medium | Use Mule interceptors |
| Custom Annotations | No direct equivalent | Low | Document and refactor |
| Spring Security | Different security model | High | Implement Mule security |
| **Integration Risks** |
| External Libraries | May not be compatible | Medium | Find Mule alternatives |
| Database Transactions | Different handling | Medium | Use Mule transaction scope |
| **Performance Risks** |
| Large payloads | Memory management differs | Medium | Implement streaming |
| Concurrent requests | Thread model different | Low | Configure Mule threads |

### 8. Dependency Analysis

List external dependencies and their Mule equivalents:

| Spring Dependency | Purpose | Mule Alternative |
|------------------|---------|------------------|
| spring-boot-starter-web | REST API | HTTP Connector |
| spring-boot-starter-data-jpa | Database ORM | Database Connector |
| spring-boot-starter-mail | Email sending | Email Connector |
| jackson | JSON processing | DataWeave |
| lombok | Code generation | Native Java |

### 9. Migration Checklist Generator

Create a comprehensive checklist:

```markdown
## Pre-Migration Checklist
- [ ] Inventory all endpoints
- [ ] Document business logic
- [ ] List all external integrations
- [ ] Identify security requirements
- [ ] Plan data migration strategy

## Migration Execution Checklist
- [ ] Set up development environment
- [ ] Create project structure
- [ ] Migrate configurations
- [ ] Convert data access layer
- [ ] Convert business logic
- [ ] Convert API layer
- [ ] Implement security
- [ ] Create tests
- [ ] Performance optimization
- [ ] Documentation

## Post-Migration Checklist
- [ ] Functional testing complete
- [ ] Performance benchmarking
- [ ] Security audit
- [ ] Documentation updated
- [ ] Deployment procedures defined
- [ ] Monitoring configured
```

### 10. Output Format

The migration plan should be generated as a structured markdown document:

```markdown
# [Application Name] Spring Boot to MuleSoft Migration Plan

## Executive Summary
[High-level overview of the migration project]

## Current State Analysis
[Include project tree, package analysis, component counts]

## Target Architecture
[Include proposed Mule structure, component mapping]

## Migration Strategy
[Phased approach with timelines]

## Risk Assessment
[Technical, integration, and performance risks]

## Resource Requirements
[Team, tools, timeline, budget estimates]

## Success Criteria
[Measurable outcomes and acceptance criteria]

## Appendices
- Component Mapping Details
- Dependency Analysis
- Configuration Mapping
- Testing Strategy
```

## Usage Instructions

1. Run this analysis on the Spring Boot project root directory
2. Use file system scanning to gather project structure (avoid reading file contents)
3. Generate counts and summaries based on file names and directory structure
4. Create visual tree representations using ASCII art
5. Output a comprehensive migration plan document
6. Focus on high-level strategy rather than implementation details

This prompt ensures efficient repository-level planning without the overhead of analyzing individual file contents, providing a clear roadmap for the Spring Boot to MuleSoft migration project.