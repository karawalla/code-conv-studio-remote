# Spring Boot to Ship Format Developer Notes Generation Prompt

## Objective
For each Spring Boot Java file, create a comprehensive developer notes file that documents the current functionality, identifies complexities, and provides a detailed conversion strategy to Ship format JSON.

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
  - Scheduled Tasks (`@Scheduled`)
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
  - Scheduled tasks (`@Scheduled`)
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

#### For Scheduled Tasks:
- **@Scheduled Methods**:
  - Cron expressions
  - Fixed delay/rate configurations
  - Initial delay settings
  - Task processing logic

#### For Entities:
- **Table Mapping**: Table name, schema
- **Field Mappings**: Column names, types, constraints
- **Relationships**: OneToMany, ManyToOne, ManyToMany
- **Validations**: Field-level constraints
- **Lifecycle Callbacks**: PrePersist, PostLoad, etc.

#### For Configuration:
- **Beans Defined**: List all `@Bean` methods
- **Properties Used**: `@Value` annotations, application.properties
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
- **JMS/ActiveMQ Operations**: Message publishing, queue management
- **Caching Logic**: Cache management, eviction

### 4. Ship Format Transformation Strategy

#### Component Mapping:
- **Spring Component → Ship Component**:
  - Controller endpoint → HTTP Listener + Flow
  - Service method → Transform Message / Set Variable / Sub-flow / Flow Reference
  - Repository call → Database Select/Insert/Update/Delete
  - Entity → DataWeave transformation schema
  - Configuration → Global elements and globalVariables
  - Logger statements → Logger component
  - File operations → File Read/Write/List
  - JMS operations → JMS Publish
  - @Scheduled → Scheduler component
  - HTTP calls → HTTP Request component

#### Ship Format Component Structure:
Each component in a flow MUST include ALL these fields IN THIS EXACT ORDER:
```json
{
  "activityType": "string",        // Ship component type (e.g., "HTTP Listener", "Transform Message")
  "activityConfig": "string",      // Brief description of what this component does
  "config": "string",              // Reference to globalElement name OR config value
  "code": "string",                // COMPLETE XML code with escaped quotes and valid UUIDs
  "inputBindings": "",             // Always empty string ""
  "outputBindings": "",            // Always empty string ""
  "name": "string",                // Unique camelCase identifier
  "parentId": [number],            // Array: [0] for first, [previousSequenceId] for others
  "sequenceId": number,            // Unique sequential ID starting from 1
  "start": "string",               // "true" for first component, "false" for all others
  "type": "activity",              // Always "activity" for regular components
  "activityDescription": "string", // Human-readable description
  "summary": {                     // Migration tracking (ALL fields required)
    "sourceType": "string",        // Same as activityType
    "simType": "string",           // Same as activityType
    "target type": "string",       // Same as activityType (note the space)
    "simFound": true,              // Always true
    "codeGenerated": true,         // Always true
    "packageFound": true,          // Always true
    "functionFound": true          // Always true
  },
  "category": "string",            // Same as activityType
  "function": "string"             // Same as activityType
}
```

#### CRITICAL UUID Generation Rules:
- **EVERY doc:id MUST be a valid UUID v4**: Format XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX
- **UUID Requirements**:
  - Length: Exactly 36 characters (32 hex + 4 hyphens)
  - Format: 8-4-4-4-12 segments
  - 13th character MUST be "4" (version 4)
  - 17th character MUST be one of: 8, 9, a, or b
  - Use ONLY random hex digits (0-9, a-f)
  - NEVER use sequential patterns or text identifiers
  - Each component MUST have a UNIQUE UUID

#### Flow Control Pattern (Critical):
**IMPORTANT: Ship format does NOT use choice components. Use link-based flow control:**
- **Links Structure**: Connect components using links array with:
  - `conditionType`: "always" (unconditional), "xpath" (conditional), or "otherwise" (default)
  - `from`: Source component's sequenceId
  - `to`: Target component's sequenceId
  - `description`: What this link does
  - `xpath`: Required for xpath type (e.g., "sizeOf(payload) == 0", "vars.fileName contains 'order'")
- **All components MUST be linked** - no orphan components allowed
- **Pattern for if/else**:
  1. Create components for each branch with same parentId
  2. Use xpath link for condition check
  3. Use otherwise link for else case

#### Flow Design:
- **Main Flow Structure**:
  - Entry point (HTTP Listener or Scheduler)
  - Request/trigger processing components
  - Business logic implementation
  - Response formatting or result handling
  - Error handling strategy
- **Flow Naming**: camelCase + "Flow" (e.g., processFileFlow, scheduledTaskFlow)
- **One flow per endpoint/scheduled task**

#### Data Transformation Patterns:

##### Query Parameter Extraction:
```xml
<ee:transform doc:name="Transform Message" doc:id="[VALID-UUID]">
  <ee:message>
    <ee:set-payload><![CDATA[%dw 2.0 output application/json --- payload]]></ee:set-payload>
  </ee:message>
  <ee:variables>
    <ee:set-variable variableName="filePath"><![CDATA[attributes.queryParams.filePath]]></ee:set-variable>
    <ee:set-variable variableName="fileName"><![CDATA[lower((vars.filePath splitBy "/")[-1])]]></ee:set-variable>
  </ee:variables>
</ee:transform>
```

##### Path Parameter Extraction:
```xml
<ee:transform doc:name="Transform Message" doc:id="[VALID-UUID]">
  <ee:variables>
    <ee:set-variable variableName="userId"><![CDATA[attributes.uriParams.id]]></ee:set-variable>
  </ee:variables>
</ee:transform>
```

##### Request Mapping:
- Path parameters → `attributes.uriParams.paramName`
- Query parameters → `attributes.queryParams.paramName`
- Headers → `attributes.headers.headerName`
- Body → `payload`

#### Global Variables Structure (from application.properties):
```json
"globalVariables": {
    "http.port": {
        "source": "",
        "type": "string",
        "value": "8085"
    },
    "file.working.dir": {
        "source": "",
        "type": "string",
        "value": "/working"
    },
    "jms.queue.name": {
        "source": "",
        "type": "string",
        "value": "orderQueue"
    }
}
```
**CRITICAL**: Always use `"type": "string"` (never "sring" or other variations)

#### Database Operation Mapping:
| JPA Method | Ship Operation | SQL Pattern |
|------------|----------------|-------------|
| `findById(id)` | Database Select | `SELECT * FROM table WHERE id = :id` |
| `save(entity)` | Database Insert | `INSERT INTO table (...) VALUES (...)` |
| `deleteById(id)` | Database Delete | `DELETE FROM table WHERE id = :id` |
| `findAll()` | Database Select | `SELECT * FROM table` |

#### File Operation Patterns:
- **File existence check**: Use File List with `sizeOf(payload) > 0` condition
- **File read**: Use File Read component
- **File write**: Use File Write with proper content formatting
- **NO advanced file operations** (copy, move, rename) - use basic read/write

#### JMS/ActiveMQ Patterns:
```xml
<jms:publish doc:name="Publish" doc:id="[VALID-UUID]" config-ref="jmsConfig" destination="${jms.queue.name}">
  <jms:message>
    <jms:body><![CDATA[%dw 2.0 output application/json --- payload]]></jms:body>
  </jms:message>
</jms:publish>
```

#### Scheduler Pattern (for @Scheduled):
```xml
<scheduler doc:name="Scheduler" doc:id="[VALID-UUID]">
  <scheduling-strategy>
    <fixed-frequency frequency="60000" timeUnit="MILLISECONDS"/>
  </scheduling-strategy>
</scheduler>
```

#### Error Handling Strategy:
- **Exception Mapping**:
  - Spring exceptions → Raise Error component
  - Error types: VALIDATION:NULL, VALIDATION:INVALID_INPUT, DB:CONNECTIVITY
  - Format: `<raise-error doc:name="Raise Error" doc:id="[UUID]" type="VALIDATION:NULL" description="Error message"/>`
- **CRITICAL**: Use "description" attribute, NOT "message"

### 5. Component Naming Conventions

- **Flows**: camelCase + "Flow" (e.g., `processFileFlow`, `scheduledCleanupFlow`)
- **HTTP Listeners**: endpoint + "Listener" (e.g., `processFileListener`)
- **Transform Components**: "transform" + Purpose or "extract" + Parameter (e.g., `extractFilePathParameter`)
- **Database Operations**: "db" + Operation + Entity (e.g., `dbInsertOrder`)
- **File Operations**: "check" + Purpose, "read" + File (e.g., `checkFileExists`, `readOrderFile`)
- **Flow References**: "routeTo" + Target (e.g., `routeToOrderProcessing`)
- **Set Payload**: "setPayload" + Purpose (e.g., `setPayloadUnknownFileType`)
- **Raise Error**: "raiseError" + Condition (e.g., `raiseErrorFileNotFound`)
- **JMS Publish**: "publish" + Destination (e.g., `publishToOrderQueue`)

### 6. Global Elements Structure

Each global element must include:
```json
{
  "config": "string",              // Complete XML configuration with escaped quotes
  "activityType": "string",        // Type with underscores (e.g., "HTTP_Listener_Configuration")
  "name": "string",                // Name referenced in component's config field
  "type": "globalElement",         // Always "globalElement"
  "activityDescription": "string"  // Description of configuration purpose
}
```

Common Global Elements:
```xml
<!-- HTTP Listener Config -->
<http:listener-config name="httpListenerConfig" doc:name="HTTP Listener Config" doc:id="[UUID]">
  <http:listener-connection host="${http.host}" port="${http.port}"/>
</http:listener-config>

<!-- Database Config -->
<db:config name="dbConfig" doc:name="Database Config" doc:id="[UUID]">
  <db:my-sql-connection host="${db.host}" port="${db.port}" user="${db.user}" password="${db.password}" database="${db.database}"/>
</db:config>

<!-- File Config -->
<file:config name="fileConfig" doc:name="File Config" doc:id="[UUID]">
  <file:connection workingDir="${file.working.dir}"/>
</file:config>

<!-- JMS Config -->
<jms:config name="jmsConfig" doc:name="JMS Config" doc:id="[UUID]">
  <jms:active-mq-connection username="${activemq.user}" password="${activemq.password}" specification="JMS_1_1">
    <jms:factory-configuration brokerUrl="${activemq.broker.url}"/>
  </jms:active-mq-connection>
</jms:config>

<!-- HTTP Request Config (for external calls) -->
<http:request-config name="HTTP_Request_configuration" doc:name="HTTP Request configuration" doc:id="[UUID]">
  <http:request-connection host="${external.service.host}" port="${external.service.port}"/>
</http:request-config>
```

### 7. Code Snippets and Examples

#### Example: Spring Boot File Processor to Ship Format

Spring Boot:
```java
@PostMapping("/process")
public ResponseEntity<String> processFile(@RequestParam String filePath) {
    File file = new File(filePath);
    if (!file.exists()) {
        return ResponseEntity.badRequest().body("File not found");
    }
    boolean status = fileProcessingService.routeFile(file);
    return ResponseEntity.ok("File processed: " + (status ? "Success" : "Failure"));
}
```

Ship Format Components:
1. HTTP Listener (sequenceId: 1, start: "true")
2. Transform Message - Extract filePath (sequenceId: 2)
3. File List - Check existence (sequenceId: 3)
4. Raise Error - File not found (sequenceId: 4, parentId: [3])
5. Flow Reference - Route to processing (sequenceId: 5, parentId: [3])
6. Transform Message - Format response (sequenceId: 6, parentId: [5])

Links:
```json
[
  {"conditionType": "always", "from": 1, "to": 2},
  {"conditionType": "always", "from": 2, "to": 3},
  {"conditionType": "xpath", "from": 3, "to": 4, "xpath": "sizeOf(payload) == 0"},
  {"conditionType": "otherwise", "from": 3, "to": 5},
  {"conditionType": "always", "from": 5, "to": 6}
]
```

#### Example: Scheduled Task to Ship Format

Spring Boot:
```java
@Scheduled(fixedDelay = 60000)
public void cleanupOldFiles() {
    // cleanup logic
}
```

Ship Format Flow:
1. Scheduler (sequenceId: 1, start: "true") - 60000ms frequency
2. File List - Find old files (sequenceId: 2)
3. Transform Message - Process file list (sequenceId: 3)
4. File Write - Archive files (sequenceId: 4)

### 8. Migration Checklist

- [ ] All endpoints mapped to flows with proper naming
- [ ] All @Scheduled methods converted to Scheduler-triggered flows
- [ ] Component structure follows Ship format requirements
- [ ] All components properly linked (no orphans)
- [ ] All doc:id attributes contain valid UUID v4 values
- [ ] Request/response transformations use correct patterns
- [ ] Database operations use proper connection config
- [ ] File operations use only basic read/write/list
- [ ] JMS operations properly configured
- [ ] Error handling uses Raise Error with "description" attribute
- [ ] Conditional logic uses xpath/otherwise links (not choice)
- [ ] All XML properly escaped in code field
- [ ] Global configurations defined with property references
- [ ] Global variables include all application.properties
- [ ] Component naming follows conventions
- [ ] DataWeave scripts use proper CDATA sections
- [ ] No java:invoke or advanced components used
- [ ] HTTP Request config included for external calls
- [ ] All property references have corresponding globalVariables entries

### 9. Additional Considerations

#### Ship Format Specific Requirements:
- **Restricted component set**: Only use allowed components
- **No sub-flows in components array**: Reference via Flow Reference
- **Proper sequencing**: Components must follow execution order
- **Complete JSON structure**: Include flows, globalElements, globalConfig, globalVariables, projectInformation
- **Migration statistics**: Track in projectInformation.summary

#### Common Pitfalls to Avoid:
- ❌ Using choice components for conditionals
- ❌ Missing UUID validation in doc:id
- ❌ Using "message" instead of "description" in Raise Error
- ❌ Forgetting to escape quotes in XML code
- ❌ Using advanced file operations (copy, move, rename)
- ❌ Missing globalVariables entries for ${property} references
- ❌ Incorrect parentId for branching logic
- ❌ Using "sring" instead of "string" in globalVariables type

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

## Ship Format Conversion Strategy
[Detailed strategy following section 4 above]

## Component Structure
[List all components with sequenceId, type, and purpose]

## Flow Control
[Document all links and conditional logic]

## Required Global Elements
[List all global configurations needed]

## Required Global Variables
[List all properties that need globalVariables entries]

## Implementation Examples
[Code snippets showing Spring → Ship conversion]

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
5. Map each Spring component to Ship format equivalent
6. Design flow with proper sequencing and links
7. Generate valid UUIDs for all doc:id attributes
8. Provide complete XML examples with escaped quotes
9. Ensure all property references have globalVariables
10. Create actionable checklist items
11. Add specific recommendations for successful migration

This prompt ensures consistent, thorough analysis of each Spring Boot file and provides actionable guidance for Ship format conversion following the specification requirements.