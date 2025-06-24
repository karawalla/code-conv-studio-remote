# Spring Boot to Ship JSON Validation Rules

## Objective
Validate that every Spring Boot component and functionality has been correctly captured in the ship output JSON file. This validation ensures complete migration coverage from Spring Boot to MuleSoft format.

## Input Requirements
1. **Spring Boot Application**: Analyze all Java files in the input folder
2. **Ship Format Specification**: Review ship.md for the target format rules
3. **Ship Output JSON**: Examine output/ship_output.json for the generated migration

## Validation Process

### 1. Spring Boot Component Inventory
Scan and catalog all Spring Boot components:
- **Controllers**: All @RestController and @Controller classes
- **Services**: All @Service classes and business logic
- **Repositories**: All @Repository, JpaRepository interfaces
- **Entities**: All @Entity classes
- **Configurations**: All @Configuration classes
- **Scheduled Tasks**: All @Scheduled methods
- **Event Listeners**: All @EventListener methods
- **Properties**: All application.properties/yml values

### 2. Ship JSON Coverage Analysis
For each Spring Boot component, verify presence in ship_output.json:

#### Controller Validation
- Every @GetMapping, @PostMapping, @PutMapping, @DeleteMapping endpoint has a corresponding flow
- Path mappings match exactly
- Request/response handling is preserved
- Path variables and request parameters are extracted correctly

#### Service Layer Validation
- Business logic is represented in Transform Message or Set Payload components
- Method calls are mapped to appropriate Mule components
- Conditional logic (if/else) is represented through links with xpath conditions
- Exception handling is mapped to Raise Error components

#### Repository Validation
- All database queries are mapped to Database Select/Insert/Update/Delete components
- Query parameters are properly bound
- Entity mappings are preserved
- Transaction boundaries are respected

#### Configuration Validation
- All application.properties values exist in globalVariables section
- Property structure follows {source: "", type: "string", value: "actual-value"}
- Database configurations are in globalElements
- HTTP listener configurations use property placeholders

#### Scheduled Tasks Validation
- @Scheduled methods have flows starting with Scheduler component
- Scheduling frequency matches Spring Boot configuration
- Task logic is fully migrated

### 3. Detailed Coverage Report Format

## Output: validation_results.md

Generate the validation report in the following format:

```markdown
# Spring Boot to Ship JSON Validation Report
Generated: [timestamp]

## Executive Summary
- Total Spring Boot Components Found: X
- Successfully Migrated: X
- Not Covered: X
- Coverage Percentage: X%

## Detailed Component Analysis

### Controllers Coverage
| Controller Class | Method | Endpoint | Status | Ship Flow Name | Issues/Notes |
|-----------------|--------|----------|---------|----------------|--------------|
| UserController | getUserById | GET /api/users/{id} | ✅ Covered | getUserByIdFlow | - |
| UserController | createUser | POST /api/users | ❌ Not Covered | - | Missing flow for user creation |
| OrderController | getOrders | GET /api/orders | ⚠️ Partial | getOrdersFlow | Missing pagination logic |

### Services Coverage
| Service Class | Method | Business Logic | Status | Ship Components | Issues/Notes |
|--------------|--------|----------------|---------|-----------------|--------------|
| UserService | validateUser | User validation | ✅ Covered | Transform Message + Raise Error | - |
| OrderService | calculateTotal | Price calculation | ❌ Not Covered | - | Complex calculation logic missing |

### Repositories Coverage
| Repository Interface | Method | Query Type | Status | Ship Component | Issues/Notes |
|--------------------|--------|------------|---------|----------------|--------------|
| UserRepository | findById | SELECT | ✅ Covered | Database Select | - |
| UserRepository | findByEmail | SELECT | ❌ Not Covered | - | Custom query not migrated |

### Entities Coverage
| Entity Class | Fields | Relationships | Status | Notes |
|-------------|--------|---------------|---------|-------|
| User | id, name, email | OneToMany: orders | ✅ Mapped | All fields present in DB queries |
| Order | id, total, status | ManyToOne: user | ⚠️ Partial | Missing user relationship in queries |

### Configuration Coverage
| Property Key | Spring Value | Ship globalVariables | Status | Notes |
|-------------|--------------|---------------------|---------|-------|
| server.port | 8080 | ✅ Present | ✅ Valid | Correct structure |
| spring.datasource.url | jdbc:mysql://localhost:3306/db | ✅ Present | ✅ Valid | - |
| custom.api.key | abc123 | ❌ Missing | ❌ Not Found | Add to globalVariables |

### Scheduled Tasks Coverage
| Class | Method | Schedule | Status | Ship Component | Notes |
|-------|--------|----------|---------|----------------|-------|
| ReportService | generateDailyReport | @Scheduled(cron="0 0 * * *") | ✅ Covered | Scheduler | - |
| CleanupService | cleanOldFiles | @Scheduled(fixedDelay=3600000) | ❌ Not Covered | - | Missing scheduled flow |

## Critical Issues Found

### 1. Missing Components
List all Spring Boot components not found in ship JSON:
- **UserController.createUser**: POST endpoint not migrated
- **OrderService.calculateTotal**: Complex business logic missing
- **CleanupService**: Entire scheduled task flow missing

### 2. Incorrect Mappings
Components present but incorrectly mapped:
- **Database configurations**: Missing proper JDBC URL format
- **Error handling**: Using 'message' instead of 'description' attribute
- **UUID format**: Invalid doc:id values found

### 3. Property Mismatches
Properties not properly migrated:
- Missing custom properties in globalVariables
- Incorrect property reference syntax
- Hardcoded values instead of property placeholders

## Validation Rules Applied

### Ship Format Compliance
- ✅ UUID v4 format validation for all doc:id attributes
- ✅ Database configuration format (host="jdbc:mysql://...")
- ✅ Error handling with type and description attributes
- ✅ Global variables structure validation
- ✅ Component type restrictions (allowed types only)

### Spring Boot Pattern Recognition
- ✅ REST endpoint mapping validation
- ✅ Service method to component mapping
- ✅ Repository query mapping
- ✅ Scheduled task recognition
- ✅ Configuration property extraction

## Recommendations

### High Priority (Must Fix)
1. Add missing flows for uncovered endpoints
2. Fix invalid UUID formats in doc:id attributes
3. Correct database configuration format
4. Add missing properties to globalVariables

### Medium Priority (Should Fix)
1. Implement complex business logic transformations
2. Add missing error handling for edge cases
3. Complete entity relationship mappings

### Low Priority (Nice to Have)
1. Add logging components for better debugging
2. Optimize DataWeave transformations
3. Add documentation comments

## Migration Score

### Overall Coverage: [X]%
- Controllers: [X]% covered
- Services: [X]% covered  
- Repositories: [X]% covered
- Configurations: [X]% covered
- Scheduled Tasks: [X]% covered

### Quality Score: [X]%
- Valid UUID format: [X]%
- Proper error handling: [X]%
- Configuration compliance: [X]%
- Pattern adherence: [X]%

## Next Steps
1. Address all "Not Covered" components
2. Fix critical format issues (UUIDs, database config)
3. Complete partial migrations
4. Validate against ship.md requirements
5. Re-run validation after fixes
```

## Validation Implementation Steps

1. **Parse Spring Boot Code**
   - Use AST parsing to identify all annotations
   - Extract method signatures and endpoints
   - Catalog all components systematically

2. **Parse Ship JSON**
   - Load ship_output.json
   - Index all flows by name
   - Map components to Spring Boot origins

3. **Cross-Reference Analysis**
   - Match Spring components to ship flows
   - Identify gaps and mismatches
   - Generate coverage metrics

4. **Generate Report**
   - Create markdown table format
   - Use clear status indicators (✅, ❌, ⚠️)
   - Provide actionable feedback

5. **Save Results**
   - Create output/validations/validation_results.md
   - Include timestamp and summary
   - Format for easy reading and action

## Key Validation Checks

1. **Every @RestController method** → Has a corresponding flow
2. **Every @Service method with logic** → Has Transform/Set Payload components  
3. **Every @Repository method** → Has Database component
4. **Every application property** → Exists in globalVariables
5. **Every @Scheduled method** → Has flow with Scheduler
6. **Every try-catch block** → Has Raise Error component
7. **Every if-else block** → Has xpath/otherwise links
8. **Every external call** → Has HTTP Request component
9. **Every file operation** → Has File Read/Write component
10. **Every JMS operation** → Has JMS Publish component