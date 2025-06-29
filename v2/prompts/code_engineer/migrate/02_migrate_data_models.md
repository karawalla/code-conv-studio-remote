# Migrate Data Models

## Objective
Convert data models from {{source_name}} to {{target_name}} format while maintaining data integrity and relationships.

## Context
- Source models location: {{source_path}}/models (or equivalent)
- Target ORM/Data framework: To be determined based on {{target_name}}
- Database type: {{database_type}}

## Instructions

1. **Analyze source data models**
   - List all entity/model classes
   - Document fields and their types
   - Identify relationships (one-to-many, many-to-many, etc.)
   - Note any custom validations or constraints

2. **Map data types**
   Create a mapping table:
   ```
   Source Type → Target Type
   Example:
   - Java String → Rust String
   - Java Long → Rust i64
   - Java LocalDateTime → Rust chrono::DateTime
   ```

3. **Convert each model**
   For each source model:
   - Create equivalent target model
   - Map all fields with appropriate types
   - Implement relationships using target framework patterns
   - Add validations and constraints
   - Include serialization/deserialization logic

4. **Handle special cases**
   - Enums and constants
   - Computed fields
   - Database-specific features (sequences, triggers)
   - Custom types or converters

5. **Create database migrations**
   - Generate migration files for target framework
   - Ensure proper indexing
   - Set up foreign key constraints
   - Handle data seeding if required

6. **Implement repository/DAO layer**
   - Basic CRUD operations
   - Custom queries
   - Transaction management
   - Connection pooling setup

## Output Format
For each model, provide:
1. Converted model code
2. Migration file
3. Repository/DAO implementation
4. Unit tests for data operations
5. Documentation of any design decisions or limitations