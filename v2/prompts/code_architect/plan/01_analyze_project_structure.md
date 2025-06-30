# Analyze Project Structure

## Objective
Analyze the source project structure to understand the current architecture and identify key components for migration planning.

## Context
- Source: {{source_name}} ({{source_type}})
- Target: {{target_name}}
- Job: {{job_name}}

## Instructions

1. **Examine the project root directory**
   - List all top-level directories and files
   - Identify the project type and framework
   - Locate configuration files (package.json, pom.xml, build.gradle, etc.)

2. **Analyze the source code structure**
   - Identify main source directories
   - Map out the module/package organization
   - Find entry points and main application files

3. **Identify key architectural patterns**
   - MVC, microservices, monolithic, etc.
   - Dependency injection frameworks
   - Database/ORM patterns
   - API design patterns (REST, GraphQL, etc.)

4. **List all dependencies**
   - External libraries and frameworks
   - Version information
   - Development vs production dependencies

5. **Document findings**
   Create a structured summary including:
   - Project type and main framework
   - Directory structure overview
   - Key architectural patterns identified
   - Dependencies list with versions
   - Entry points and main components

## Output Format
Provide a detailed markdown report with clear sections for each finding.