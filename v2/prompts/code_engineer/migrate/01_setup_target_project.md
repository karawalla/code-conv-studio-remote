# Setup Target Project

## Objective
Initialize the target {{target_name}} project with proper structure and dependencies.

## Context
- Target framework: {{target_name}}
- Architecture design completed
- Migration plan available

## Instructions

1. **Create project structure**
   - Initialize new {{target_name}} project
   - Create directory structure as per architecture design
   - Set up version control (.gitignore, etc.)

2. **Configure build system**
   - Set up appropriate build configuration
   - Define project metadata (name, version, description)
   - Configure compilation/build settings

3. **Add core dependencies**
   Based on the migration plan, add required dependencies:
   - Web framework (if applicable)
   - Database drivers/ORM
   - Logging framework
   - Testing frameworks
   - Utility libraries

4. **Create configuration files**
   - Application configuration templates
   - Environment-specific settings
   - Database configuration
   - Logging configuration

5. **Set up development environment**
   - Create README with setup instructions
   - Add development scripts/commands
   - Configure IDE settings (if applicable)

6. **Implement basic application skeleton**
   - Main entry point
   - Basic error handling
   - Health check endpoint (if web application)
   - Logging initialization

## Output Format
1. Generated project structure
2. List of installed dependencies with versions
3. Configuration file templates
4. Setup instructions documentation