# Design Target Architecture

## Objective
Design the target architecture for {{target_name}} that will accommodate the migrated application while following best practices.

## Context
- Migration plan has been created
- Target technology: {{target_name}}
- Must maintain feature parity with source

## Instructions

1. **Design the project structure**
   ```
   Create a recommended directory structure for {{target_name}}:
   /
   ├── src/
   │   ├── [appropriate subdirectories]
   ├── tests/
   ├── config/
   ├── docs/
   └── [framework-specific directories]
   ```

2. **Define architectural layers**
   - Presentation layer (API/Web)
   - Business logic layer
   - Data access layer
   - Cross-cutting concerns (logging, security, etc.)

3. **Design key components**
   - Entry point and application initialization
   - Routing/Controller structure
   - Service layer organization
   - Data models and repository pattern
   - Error handling strategy
   - Configuration management

4. **Plan for cross-cutting concerns**
   - Authentication and authorization
   - Logging and monitoring
   - Error handling and validation
   - Caching strategy
   - Database connection management

5. **Define coding standards**
   - Naming conventions
   - File organization
   - Documentation standards
   - Testing approach

6. **Create architecture diagrams**
   - High-level component diagram
   - Data flow diagram
   - Deployment architecture

## Output Format
Provide:
1. Detailed project structure
2. Architecture design document
3. Component interaction diagrams (in text/ASCII format)
4. Coding standards guide
5. Technology stack decisions with justifications