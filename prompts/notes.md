# Spring Boot to MuleSoft Developer Notes Generation Prompt

## Objective
For each Spring Boot Java file, create a comprehensive developer notes file that documents the current functionality, identifies complexities, and provides a detailed conversion strategy to MuleSoft.

## Analysis Framework for Each File

### 1. File Identification and Context
- **File Path**: Record the full path relative to project root
- **File Type**: Identify the Spring Boot component type
  - Controller (`@RestController`, `@Controller`)
  - Service (`@Service`)
  - Repository (`@Repository`, extends `JpaRepository`)
  - Entity (`@Entity`)
  - Configuration (`@Configuration`)
  - Component (`@Component`)
  - Exception Handler (`@ControllerAdvice`)
  - Utility/Helper class
- **Package Structure**: Note the package hierarchy and its purpose
- **Dependencies**: List all imports and their categories
  - Spring Framework imports
  - Java standard library imports
  - Third-party library imports
  - Internal project imports

### 2. Current Spring Boot Functionality Analysis

#### For Controllers:
- **Endpoints Inventory**:
  - HTTP method (GET, POST, PUT, DELETE, PATCH)
  - Path mapping with variables
  - Request parameters (`@RequestParam`)
  - Path variables (`@PathVariable`)
  - Request body structure (`@RequestBody`)
  - Response type and status codes
  - Content type (JSON, XML, etc.)
- **Authentication/Authorization**: Note any security annotations
- **Validation**: Document any `@Valid`, `@Validated` annotations
- **Exception Handling**: Local `@ExceptionHandler` methods

#### For Services:
- **Business Logic Methods**:
  - Method signature and purpose
  - Transaction boundaries (`@Transactional`)
  - Caching annotations (`@Cacheable`)
  - Async processing (`@Async`)
- **External Service Calls**: REST clients, SOAP calls
- **Data Transformations**: Object mapping, calculations
- **Business Rules**: Conditional logic, validations

#### For Repositories:
- **Data Access Methods**:
  - Standard JPA methods (findById, save, delete)
  - Custom query methods (`@Query`)
  - Named queries
  - Specifications/Criteria queries
- **Entity Relationships**: Note joins and fetch strategies
- **Database Operations**: CRUD operations, batch operations

#### For Entities:
- **Table Mapping**: Table name, schema
- **Field Mappings**: Column names, types, constraints
- **Relationships**: OneToMany, ManyToOne, ManyToMany
- **Validations**: Field-level constraints
- **Lifecycle Callbacks**: PrePersist, PostLoad, etc.

#### For Configuration:
- **Beans Defined**: List all `@Bean` methods
- **Properties Used**: `@Value` annotations
- **Conditional Configuration**: `@ConditionalOn*` annotations
- **External Configurations**: Property files referenced

### 3. Complexity Assessment

#### Technical Complexities:
- **Nested Logic**: Deep if-else chains, complex switch statements
- **Loop Structures**: For loops, while loops, stream operations
- **Exception Hierarchies**: Multiple catch blocks, custom exceptions
- **Concurrency**: Thread management, synchronized blocks
- **Reflection Usage**: Dynamic class/method invocation
- **Generic Types**: Complex generic signatures

#### Business Logic Complexities:
- **Multi-step Processes**: Workflows spanning multiple methods
- **State Management**: Stateful operations
- **Complex Validations**: Cross-field validations, business rules
- **Data Aggregations**: GroupBy operations, calculations

#### Integration Complexities:
- **External System Calls**: REST, SOAP, messaging
- **Database Transactions**: Distributed transactions, rollback scenarios
- **File Operations**: File I/O, streaming
- **Caching Logic**: Cache management, eviction

### 4. MuleSoft Transformation Strategy

#### Component Mapping:
- **Spring Component → Mule Component**:
  - Controller endpoint → HTTP Listener + Flow
  - Service method → Transform Message / Set Variable / Sub-flow
  - Repository call → Database connector operation
  - Entity → DataWeave transformation schema
  - Configuration → Global elements
  - Logger statements → Logger component with level and message
  - Mail sending → email:send operation

#### MuleSoft Component Structure:
Each component in a flow must include these fields:
- **sequenceId**: Sequential integer starting at 1, unique per flow
- **parentId**: Array format - [0] for first component, else [previous sequenceId]
- **activityType**: Valid Mule component type (HTTP Listener, Transform Message, Database Select, etc.)
- **activityConfig**: Reference to original Spring Boot logic
- **config**: Valid, non-empty reference to global configuration
- **code**: Complete Mule XML snippet with doc:id and doc:name attributes
- **name**: Unique camelCase identifier following naming conventions
- **start**: "true" only for first component, "false" for all others
- **type**: "activity" or "group"
- **summary**: Migration tracking with:
  - sourceType: Original Spring component type
  - simType: Simulation type (usually same as sourceType)
  - targetType: Generated Mule component type
  - simFound: true
  - codeGenerated: true
  - packageFound: true
  - functionFound: true

#### Flow Control Pattern (Critical):
**IMPORTANT: Mule does NOT use choice components for conditionals. Use link-based flow control:**
- **Links Structure**: Connect components using links array with:
  - `conditionType`: "always" (unconditional), "xpath" (conditional), or "otherwise" (default case)
  - `from`: Source component's sequenceId
  - `to`: Target component's sequenceId
  - `description`: What this link does
  - `xpath`: Required for xpath type (e.g., "payload == null", "vars.num2 == 0")
- **All components MUST be linked** - no orphan components allowed
- **Pattern for if/else**:
  1. Create components for each branch
  2. Use xpath link for condition check
  3. Use otherwise link for else case

#### Flow Design:
- **Main Flow Structure**:
  - Entry point (HTTP Listener configuration)
  - Request processing components
  - Business logic implementation
  - Response formatting
  - Error handling strategy
- **Flow Naming**: camelCase + "Flow" (e.g., getUserByIdFlow, createUserFlow)
- **One flow per HTTP endpoint** - each @GetMapping, @PostMapping, etc. becomes a separate flow

#### Data Transformation Patterns:

##### GET Method Pattern:
```xml
<ee:transform doc:name="Transform Message" doc:id="transformGetUserById">
  <ee:variables>
    <ee:set-variable variableName="userId">
      <![CDATA[attributes.uriParams.id]]>
    </ee:set-variable>
  </ee:variables>
</ee:transform>
```

##### POST Method Pattern:
```xml
<ee:transform doc:name="Transform Message" doc:id="transformCreateUser">
  <ee:message>
    <ee:set-payload><![CDATA[
      %dw 2.0
      output application/json
      ---
      payload
    ]]></ee:set-payload>
  </ee:message>
</ee:transform>
```

##### Request Mapping:
- Path parameters → `attributes.uriParams.paramName`
- Query parameters → `attributes.queryParams.paramName`
- Headers → `attributes.headers.headerName`
- Body → `payload`

#### Database Configuration Mapping:
- **Spring properties to Mule DB Config**:
  ```properties
  spring.datasource.url=jdbc:mysql://localhost:3306/mydb
  spring.datasource.username=root
  spring.datasource.password=password
  ```
  Becomes:
  ```xml
  <db:config name="dbConfig" doc:name="Database Config" doc:id="dbConfig">
    <db:my-sql-connection 
      host="jdbc:mysql://localhost" 
      port="3306" 
      user="root" 
      password="password" 
      database="mydb" 
      driverClassName="com.mysql.cj.jdbc.Driver"/>
  </db:config>
  ```
- **Important**: The host attribute includes the full JDBC URL prefix

#### Database Operation Mapping:
| JPA Method | Mule Operation | SQL Pattern |
|------------|----------------|-------------|
| `findById(id)` | db:select | `SELECT * FROM table WHERE id = :id` |
| `save(entity)` | db:insert/update | `INSERT INTO table (...) VALUES (...)` |
| `deleteById(id)` | db:delete | `DELETE FROM table WHERE id = :id` |
| `findAll()` | db:select | `SELECT * FROM table` |
| Custom `@Query` | db:select | Use provided JPQL/SQL |

#### Error Handling Strategy:
- **Exception Mapping**:
  - Spring exceptions → raise-error component
  - Exception types: VALIDATION, NOT_FOUND, CUSTOM, INTERNAL_SERVER_ERROR
  - Format: `<raise-error type="NOT_FOUND" description="User not found"/>`
- **Try-catch blocks**: Convert to conditional links with xpath
- **Global exception handlers**: Convert to global error handlers

#### Common XML Patterns and Pitfalls:

##### Correct Patterns:
- Set Payload: `<set-payload value="#[payload]" doc:name="Set Payload"/>`
- Set Variable: `<set-variable variableName="userId" value="#[attributes.uriParams.id]" doc:name="Set userId"/>`
- Logger: `<logger level="INFO" message="Processing user: #[vars.userId]" doc:name="Logger"/>`
- HTTP Headers: Use `key` attribute, not `headerName`

##### Incorrect Patterns to Avoid:
- ❌ `<ee:set-payload><![CDATA[#[payload]]]></ee:set-payload>`
- ❌ `<http:header headerName="Content-Type" value="application/json"/>`
- ❌ Using `<java:invoke>` for any operations
- ❌ Using choice components for conditionals

### 5. Component Naming Conventions

- **Flows**: camelCase + "Flow" (e.g., `getUserByIdFlow`, `createOrderFlow`)
- **HTTP Listeners**: endpoint + "Listener" (e.g., `getUserByIdListener`)
- **Transform Components**: "transform" + Purpose (e.g., `transformUserData`, `transformGetUserById`)
- **Database Operations**: "db" + Operation + Entity (e.g., `dbSelectUserById`, `dbInsertOrder`)
- **Set Variable**: "set" + VariableName (e.g., `setUserId`, `setOrderStatus`)
- **Logger**: "log" + Purpose (e.g., `logUserCreated`, `logError`)
- **Global Configs**: type + "Config" (e.g., `httpListenerConfig`, `dbConfig`, `emailConfig`)

### 6. Global Elements Structure

Each global element must include:
- **config**: Complete XML configuration snippet
- **activityType**: Component type (HTTP_Listener_Configuration, Database_Configuration, Email_Configuration)
- **name**: Unique identifier referenced in flows
- **type**: Always "globalElement"
- **activityDescription**: Human-readable description

Common Global Elements:
```xml
<!-- HTTP Listener Config -->
<http:listener-config name="httpListenerConfig" doc:name="HTTP Listener config">
  <http:listener-connection host="0.0.0.0" port="8080"/>
</http:listener-config>

<!-- Database Config -->
<db:config name="dbConfig" doc:name="Database Config">
  <db:my-sql-connection host="jdbc:mysql://localhost" port="3306" 
    user="username" password="password" database="dbname"/>
</db:config>

<!-- Email Config -->
<email:smtp-config name="emailConfig" doc:name="Email SMTP">
  <email:smtp-connection host="smtp.gmail.com" port="587"/>
</email:smtp-config>
```

### 7. Code Snippets and Examples

#### Current Spring Code Pattern:
```java
// Show the actual Spring pattern from the file
```

#### Proposed Mule Implementation:
```xml
<!-- Show the equivalent Mule XML configuration -->
```

#### DataWeave Transformation:
```dataweave
%dw 2.0
output application/json
---
// Show DataWeave script for data transformation
```

#### Example: Spring Controller to Mule Flow
Spring:
```java
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    return userRepository.findById(id)
        .orElseThrow(() -> new NotFoundException("User not found"));
}
```

Mule Components:
1. HTTP Listener (sequenceId: 1, start: "true")
2. Transform Message - Extract userId (sequenceId: 2)
3. Database Select (sequenceId: 3)
4. Raise Error - User not found (sequenceId: 4)
5. Set Payload - Return user (sequenceId: 5)

Links:
- always: 1→2→3
- xpath "payload == null": 3→4
- otherwise: 3→5

### 8. Migration Checklist

- [ ] All endpoints mapped to flows with proper naming
- [ ] Component structure follows MuleSoft requirements
- [ ] All components properly linked (no orphans)
- [ ] Request/response transformations use correct patterns
- [ ] Database operations use proper connection config
- [ ] Error handling uses raise-error components
- [ ] Conditional logic uses xpath/otherwise links (not choice)
- [ ] All XML includes doc:id and doc:name
- [ ] Global configurations defined and referenced
- [ ] Component naming follows conventions
- [ ] DataWeave scripts use proper CDATA sections
- [ ] No java:invoke components used
- [ ] Security requirements addressed
- [ ] Testing strategy defined (JUnit → MUnit)

### 9. Additional Considerations

#### Non-Functional Requirements:
- Performance expectations
- Scalability needs
- Security requirements
- Monitoring/logging needs

#### Integration Points:
- Upstream systems
- Downstream dependencies
- Shared resources
- Message formats

#### Deployment Considerations:
- Environment-specific configs
- Connection details
- Resource limits

## Output Format

For each Java file analyzed, create a markdown file with the following structure:

```markdown
# Developer Notes: [FileName.java]

## File Overview
- **Location**: [full path]
- **Type**: [Controller/Service/Repository/etc.]
- **Purpose**: [brief description]
- **Dependencies**: [key dependencies]

## Current Functionality
[Detailed analysis following sections 2-3 above]

## MuleSoft Conversion Strategy
[Detailed strategy following section 4 above]

## Component Structure
[List all components with sequenceId, type, and purpose]

## Flow Control
[Document all links and conditional logic]

## Focus Areas
[Critical items and gaps from section 5]

## Implementation Examples
[Code snippets showing Spring → Mule conversion]

## Migration Checklist
[Specific checklist items for this file]

## Notes and Recommendations
[Additional considerations specific to this file]
```

## Usage Instructions

1. Read the Java file completely
2. Identify the file type and purpose
3. Analyze each method/annotation systematically
4. Document complexities and special cases
5. Map each Spring component to Mule equivalent using proper patterns
6. Design flow with proper sequencing and links
7. Provide concrete XML examples with correct syntax
8. Highlight potential issues and gaps
9. Create actionable checklist items
10. Add specific recommendations for successful migration

This prompt ensures consistent, thorough analysis of each Spring Boot file and provides actionable guidance for MuleSoft conversion following Mule 4 best practices and patterns.