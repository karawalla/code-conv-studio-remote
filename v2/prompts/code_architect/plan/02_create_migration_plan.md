# Create Migration Plan

## Objective
Create a comprehensive migration plan from {{source_name}} to {{target_name}} based on the project analysis.

## Context
- Previous analysis results available
- Target framework: {{target_name}}
- Migration complexity: To be determined

## Instructions

1. **Define migration strategy**
   - Determine if this will be a complete rewrite or gradual migration
   - Identify components that can be directly ported vs. those needing redesign
   - Plan for data migration if applicable

2. **Map source patterns to target patterns**
   - Controllers/Routes → Target equivalent
   - Services/Business Logic → Target patterns
   - Data Models/Entities → Target ORM/Data layer
   - Configuration → Target configuration approach

3. **Create component mapping**
   ```
   Source Component → Target Component
   Example:
   - Spring @RestController → Rust Actix-web handlers
   - JPA Entities → Diesel models
   - Spring Services → Rust service modules
   ```

4. **Identify migration challenges**
   - Language-specific features that don't have direct equivalents
   - Library dependencies that need alternatives
   - Performance considerations
   - Testing strategy changes

5. **Define migration phases**
   - Phase 1: Core infrastructure setup
   - Phase 2: Data models and database layer
   - Phase 3: Business logic migration
   - Phase 4: API/Controller layer
   - Phase 5: Testing and validation
   - Phase 6: Deployment configuration

6. **Estimate effort and timeline**
   - Complexity rating for each component
   - Estimated hours/days per phase
   - Risk factors and mitigation strategies

## Output Format
Produce a detailed migration plan document with:
- Executive summary
- Technical approach
- Component mapping table
- Phase-by-phase breakdown
- Risk assessment
- Timeline estimates