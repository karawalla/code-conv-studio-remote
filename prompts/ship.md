# Ship Format JSON Schema - Complete Specification

## Purpose
Generate a JSON file in the "ship format" that represents a complete MuleSoft integration project converted from Spring Boot. This format captures flows, components, configurations, and their interconnections in a structure that can be imported into integration platforms.

## CRITICAL UUID GENERATION REQUIREMENT
**EVERY doc:id attribute MUST be a valid UUID v4. The format is: XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX**

**MANDATORY UUID RULES:**
1. Length: Must be exactly 36 characters (32 hex digits + 4 hyphens)
2. Format: 8-4-4-4-12 (number of hex digits in each segment)
3. Version: The 13th character (after 2nd hyphen) MUST be "4"
4. Variant: The 17th character (after 3rd hyphen) MUST be one of: 8, 9, a, or b
5. All other positions: RANDOM hexadecimal digits (0-9, a-f)
6. NEVER use sequential patterns (a1b2c3d4, 12345678, abcdef12)
7. NEVER copy UUID examples from this document
8. Each component MUST have a UNIQUE UUID

**CHECK YOUR UUIDS: Count the characters in each segment: 8-4-4-4-12**

## Core JSON Structure
```json
{
  "flows": [],           // Array of integration flows (one per REST endpoint)
  "globalElements": [],  // Reusable configuration elements
  "globalConfig": [],    // Mirror of globalElements for XML generation
  "globalVariables": {}, // Application-wide variables from properties (structured format with type always "string")
  "projectInformation": {
    "customization": {},
    "destinationPlatform": "mule",
    "processFiles": [],
    "projectName": "string",
    "sourceProjectType": "SpringBoot",
    "summary": {
      "totalComponents": number,                // total activity count
      "totalActivitiesCount": number,           // total activity count
      "totalFlowCount": number,                 // total activity count
      "totalGroupActivitiesCount": number,      // total group activities count
      "totalGlobalComponentsCount": number,     // total global components count
      "totalSIMFound": 0,
      "totalCodeFound": 0,
      "totalPackageFound": 0,
      "totalFunctionFound": 0,
      "fullyMigrated": total activity count,    // total activity count
      "partiallyMigrated": 0,
      "notMigrated": 0,
      "fullMigratedActivities": [],
      "partiallyMigratedActivities": [],
      "notMigratedActivities": []
    }      // Migration statistics
  }
}
```

## Flow Structure
Each flow in the flows array represents one complete integration pipeline:

```json
{
  "name": "flowNameInCamelCase",  // e.g., "getUserByIdFlow"
  "components": [],               // Ordered array of activities
  "groupActivities": [],          // Sub-flows or grouped activities (usually empty)
  "links": []                     // Connections between components
}
```

## Component Structure
Each component in a flow MUST contain ALL these fields IN THIS EXACT ORDER:

```json
{
  "activityType": "string",        // Mule component type (e.g., "HTTP Listener", "Transform Message")
  "activityConfig": "string",      // Brief description of what this component does
  "config": "string",              // Reference to globalElement name OR config value (e.g., "httpListenerConfig")
  "code": "string",                // COMPLETE Mule XML code with escaped quotes
  "inputBindings": "",             // Always empty string ""
  "outputBindings": "",            // Always empty string ""
  "name": "string",                // Unique camelCase identifier (e.g., "getUserByIdListener")
  "parentId": [number],            // Array with single number: [0] for first, [previousSequenceId] for others
  "sequenceId": number,            // Unique sequential ID starting from 1
  "start": "string",               // "true" for first component, "false" for all others (STRING not boolean)
  "type": "activity",              // Always "activity" for regular components
  "activityDescription": "string", // Human-readable description of component's purpose
  "summary": {                     // Migration tracking (ALL fields required)
    "sourceType": "string",        // Same as activityType
    "simType": "string",           // Same as activityType
    "target type": "string",       // Same as activityType (note the space in "target type")
    "simFound": true,              // Always true
    "codeGenerated": true,         // Always true
    "packageFound": true,          // Always true
    "functionFound": true          // Always true
  },
  "category": "string",            // Same as activityType
  "function": "string"             // Same as activityType
}
```

## Link Structure
Links define flow control between components:

```json
{
  "conditionType": "always|xpath|otherwise",  // Type of connection
  "description": "string",                     // What this link does
  "from": number,                              // Source component's sequenceId
  "to": number,                                // Target component's sequenceId
  "xpath": "string"                            // ONLY include for xpath type
}
```

## Global Variables Structure
**IMPORTANT**: All properties from application.properties or application.yml must be placed under "globalVariables" in the MuleSoft JSON with this EXACT format:

```json
"globalVariables": {
    "http.port": {
        "source": "",
        "type": "string",  // CRITICAL: Always "string", never "sring"
        "value": "8085"
    },
    "http.host": {
        "source": "",
        "type": "string",  // CRITICAL: Always "string", never "sring"
        "value": "0.0.0.0"
    },
    "jms.broker.url": {
        "source": "",
        "type": "string",  // CRITICAL: Always "string", never "sring"
        "value": "tcp://localhost:61616"
    }
}
```

**CRITICAL**: Every variable in globalVariables MUST have:
- `"source": ""` (always empty string)
- `"type": "string"` (ALWAYS spelled "string" - never "sring" or any other variation)
- `"value": "actual-value"` (the property value as string)

**Usage in Components**: Reference these variables using ${propertyName} syntax:
```xml
<http:listener-connection host="${http.host}" port="${http.port}"/>
```

## Global Element Structure (globalElements array)
```json
{
  "config": "string",              // Complete XML configuration with escaped quotes and ${property} references
  "activityType": "string",        // Type with underscores (e.g., "HTTP_Listener_Configuration", "Database_Configuration")
  "name": "string",                // Name referenced in component's config field
  "type": "globalElement",         // Always "globalElement"
  "activityDescription": "string"  // Description of configuration purpose
}
```

## Global Config Structure (globalConfig array)
This is a SEPARATE array that mirrors globalElements but with ONLY the config field:
```json
[
  {
    "config": "<http:listener-config name=\"httpListenerConfig\" doc:name=\"HTTP Listener Config\" doc:id=\"f5d8e2f0-3b24-4c56-9abc-def012345678\"><http:listener-connection host=\"0.0.0.0\" port=\"8086\"/></http:listener-config>"
  },
  {
    "config": "<db:config name=\"dbConfig\" doc:name=\"Database Config\" doc:id=\"a5b9c3e1-7f2d-4e8a-b6c9-123456789abc\"><db:my-sql-connection host=\"jdbc:mysql://localhost\" port=\"3306\" user=\"root\" password=\"password\" database=\"dbname\" driverClassName=\"com.mysql.cj.jdbc.Driver\"/></db:config>"
  }
]
```

## Full Migrated Activities Structure (fullMigratedActivities array)
fullMigratedActivities array in summary in projectInformation should contain the unqiue activity type and its count.
```json
[
  {
          "mule_activity": "HTTP Listener",   // Target Activity Type
          "SB_activity": "HTTP Listener",     // Source Activity Type
          "count": 1                          // Total Count of particular activity type
        },
        {
          "mule_activity": "File Write",
          "SB_activity": "File Write",
          "count": 3
        }
]
```

## Critical Rules

### 0. UUID Requirements for doc:id
- **CRITICAL**: All doc:id attributes MUST contain valid UUID version 4 format
- UUID v4 format: XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX where:
  - X = any hexadecimal digit (0-9, a-f)
  - 4 = version 4 indicator
  - Y = one of 8, 9, a, or b
- MUST use RANDOM hexadecimal values, NOT sequential patterns
- Do NOT use text identifiers like "processFileListener" or "transformGetUserById"
- Do NOT use sequential patterns like "a1b2c3d4" or "12345678"
- Generate unique RANDOM UUIDs for each component's doc:id attribute
- Example VALID UUIDs (these are properly randomized):
  - `doc:id="550e8400-e29b-41d4-a716-446655440000"` ✅
  - `doc:id="6ba7b810-9dad-41d4-adf4-362877b8d91f"` ✅
  - `doc:id="f47ac10b-58cc-4372-a567-0e02b2c3d479"` ✅
- Example INVALID UUIDs:
  - `doc:id="getUserByIdListener"` ❌ (text identifier)
  - `doc:id="a1b2c3d4-5e6f-7a8b-9c0d-e1f2a3b4c5d6"` ❌ (sequential pattern, not random)
  - `doc:id="12345678-1234-1234-1234-123456789012"` ❌ (repeating pattern, not random)
  - `doc:id="b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7"` ❌ (contains invalid letters g-z)

### UUID Generation Algorithm (MANDATORY)
When generating doc:id values, you MUST:
1. Generate 32 random hexadecimal characters (0-9, a-f)
2. Format as: XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX
3. The 13th character MUST be "4" (UUID version 4)
4. The 17th character MUST be one of: 8, 9, a, or b
5. All other positions must be RANDOM hex digits
6. NEVER use sequential patterns or incrementing values
7. NEVER reuse UUIDs from examples or other components

**CORRECT UUID v4 Examples for Reference (DO NOT COPY - GENERATE NEW ONES):**
- `f7a2c4e8-9b3d-4a6e-8c1f-2d5a7b9e3f5c` ✅ (8-4-4-4-12 format, 13th char is 4, 17th is 8)
- `a5b7d3e9-4c8f-4d6a-9e2b-7f3c5a8d9b4e` ✅ (random hex, proper format)
- `c9e8f2a5-7b4d-4a8c-9f1e-3d6b8c4a7e5f` ✅ (13th position has 4, 17th has 9)

**COMMON MISTAKES TO AVOID:**
- `c8e9fa6-dbac-4aaf-e7c9-bdab9faa8ebc` ❌ (first segment only 7 chars, should be 8)
- `eabcd8-fdce-4cbc-a9eb-dfcdbbcccaee` ❌ (first segment only 6 chars, should be 8)
- `a1b2c3d4-5e6f-7a8b-9c0d-e1f2a3b4c5d6` ❌ (sequential pattern)
- `12345678-1234-5678-9012-123456789012` ❌ (not UUID v4 format, missing 4 in 13th position)

### 1. Parent-Child Relationships
- First component: `"parentId": [0]`
- All others: `"parentId": [previousComponentSequenceId]`
- For branching: multiple components can have same parentId

### 2. Sequence IDs
- Start from 1 in each flow
- Must be unique within a flow
- Increment sequentially (but gaps allowed for branching)

### 3. Branching Logic (CRITICAL)
- **NO CHOICE COMPONENTS** - use links instead
- **if/else pattern**:
  ```
  Component A (sequenceId: 3)
    ├─[xpath: condition]→ Component B (sequenceId: 4, parentId: [3])
    └─[otherwise]→ Component C (sequenceId: 5, parentId: [3])
  ```

### 4. Understanding parentId and sequenceId in Branching

#### Basic Sequential Flow
In a simple sequential flow, each component's parentId points to the previous component's sequenceId:
```
Component 1: sequenceId: 1, parentId: [0]     (start component)
Component 2: sequenceId: 2, parentId: [1]     (follows component 1)
Component 3: sequenceId: 3, parentId: [2]     (follows component 2)
```

#### Branching Pattern (if/else)
When implementing conditional logic, multiple components share the same parentId:

```
Database Select: sequenceId: 3, parentId: [2]
    |
    ├─→ Raise Error: sequenceId: 4, parentId: [3]    (if branch)
    |
    └─→ Set Payload: sequenceId: 5, parentId: [3]    (else branch)
```

**Key Points:**
- Both components 4 and 5 have `parentId: [3]` because they both branch from component 3
- The sequenceIds (4 and 5) are still unique and sequential
- Links determine which branch executes based on conditions

#### Complex Branching Example
Spring Boot code:
```java
User user = userRepository.findById(id);
if (user == null) {
    throw new NotFoundException("User not found");
} else if (user.isDeleted()) {
    throw new BadRequestException("User is deleted");
} else {
    return user;
}
```

Component structure:
```
1. HTTP Listener: sequenceId: 1, parentId: [0]
2. Transform Message: sequenceId: 2, parentId: [1]
3. Database Select: sequenceId: 3, parentId: [2]
   |
   ├─→ 4. Raise Error (NOT_FOUND): sequenceId: 4, parentId: [3]
   |
   ├─→ 5. Raise Error (DELETED): sequenceId: 5, parentId: [3]
   |
   └─→ 6. Set Payload: sequenceId: 6, parentId: [3]
```

Links for this pattern:
```json
[
  {"from": 1, "to": 2, "conditionType": "always"},
  {"from": 2, "to": 3, "conditionType": "always"},
  {"from": 3, "to": 4, "conditionType": "xpath", "xpath": "isEmpty(payload)"},
  {"from": 3, "to": 5, "conditionType": "xpath", "xpath": "payload.deleted == true"},
  {"from": 3, "to": 6, "conditionType": "otherwise"}
]
```

#### Merge Pattern (Multiple Paths Converging)
When multiple branches need to converge:

```
3. Check Condition: sequenceId: 3, parentId: [2]
   |
   ├─→ 4. Process A: sequenceId: 4, parentId: [3]
   |      |
   |      └─→ 6. Logger: sequenceId: 6, parentId: [4]
   |
   └─→ 5. Process B: sequenceId: 5, parentId: [3]
          |
          └─→ 6. Logger: sequenceId: 6, parentId: [5]  ❌ WRONG!
```

**Important:** You cannot have the same sequenceId (6) twice. Instead:

```
3. Check Condition: sequenceId: 3, parentId: [2]
   |
   ├─→ 4. Process A: sequenceId: 4, parentId: [3]
   |      |
   |      └─→ 6. Set Variable: sequenceId: 6, parentId: [4]
   |
   └─→ 5. Process B: sequenceId: 5, parentId: [3]
          |
          └─→ 7. Set Variable: sequenceId: 7, parentId: [5]

8. Logger: sequenceId: 8, parentId: [6,7]  ❌ WRONG! parentId must be single value array
```

**Correct approach:** Use separate components or sub-flows for merging logic.

#### Nested Conditions Pattern
For nested if statements:

```
3. First Check: sequenceId: 3, parentId: [2]
   |
   ├─→ 4. Second Check: sequenceId: 4, parentId: [3]
   |      |
   |      ├─→ 5. Action A: sequenceId: 5, parentId: [4]
   |      |
   |      └─→ 6. Action B: sequenceId: 6, parentId: [4]
   |
   └─→ 7. Default Action: sequenceId: 7, parentId: [3]
```

### 5. Visual Branching Examples

#### Example 1: Simple if/else
```
Spring Boot:                     Ship Format Structure:
if (x > 0) {                    Component 3 (Check)
    doA();                      ├─[xpath: x > 0]→ Component 4 (doA) parentId:[3]
} else {                        └─[otherwise]→ Component 5 (doB) parentId:[3]
    doB();
}

Components:
- Component 3: sequenceId: 3, parentId: [2] (decision point)
- Component 4: sequenceId: 4, parentId: [3] (true branch)
- Component 5: sequenceId: 5, parentId: [3] (false branch)
```

#### Example 2: Multiple Conditions (if/else if/else)
```
Spring Boot:                     Ship Format Structure:
if (status == "NEW") {          Component 3 (Check)
    processNew();               ├─[xpath: status=="NEW"]→ Component 4 parentId:[3]
} else if (status == "PENDING") {├─[xpath: status=="PENDING"]→ Component 5 parentId:[3]
    processPending();           └─[otherwise]→ Component 6 parentId:[3]
} else {
    processOther();
}

Components:
- Component 3: sequenceId: 3, parentId: [2] (decision point)
- Component 4: sequenceId: 4, parentId: [3] (NEW case)
- Component 5: sequenceId: 5, parentId: [3] (PENDING case)
- Component 6: sequenceId: 6, parentId: [3] (default case)
```

#### Example 3: Sequential Checks (Guard Clauses)
```
Spring Boot:                     Ship Format Structure:
if (user == null) {             Component 3 (DB Select)
    throw new NotFound();       ├─[xpath: isEmpty(payload)]→ Component 4 (Raise Error) parentId:[3]
}                               └─[otherwise]→ Component 5 (Check Active) parentId:[3]
if (!user.isActive()) {                        ├─[xpath: !payload.active]→ Component 6 (Raise Error) parentId:[5]
    throw new Forbidden();                     └─[otherwise]→ Component 7 (Return User) parentId:[5]
}
return user;

Components:
- Component 3: sequenceId: 3, parentId: [2] (DB select)
- Component 4: sequenceId: 4, parentId: [3] (NotFound error)
- Component 5: sequenceId: 5, parentId: [3] (Check active - continues flow)
- Component 6: sequenceId: 6, parentId: [5] (Forbidden error)
- Component 7: sequenceId: 7, parentId: [5] (Return user)
```

### 6. Common Branching Mistakes to Avoid

1. **Duplicate sequenceIds**: Each component must have a unique sequenceId
2. **Multiple values in parentId**: parentId must always be an array with a single value
3. **Missing links**: Every branch must have corresponding link definitions
4. **No otherwise link**: When using xpath conditions, always provide an otherwise link
5. **Circular references**: A component cannot have itself or a later component as parent

### 7. Component Type Mappings (RESTRICTED SET)

| Spring Boot Pattern | activityType | Mule XML Element |
|-------------------|--------------|------------------|
| @GetMapping, @PostMapping | HTTP Listener | `<http:listener>` |
| @Scheduled | Scheduler | `<scheduler>` |
| Extract parameters/body | Transform Message | `<ee:transform>` |
| Repository.findById() | Database Select | `<db:select>` |
| Repository.save() | Database Insert | `<db:insert>` |
| throw Exception | Raise Error | `<raise-error>` |
| return data | Set Payload | `<set-payload>` |
| JmsTemplate.send() | JMS Publish | `<jms:publish>` |
| File operations | File Read | `<file:read>` |
| RestTemplate/WebClient | HTTP Request | `<http:request>` |

**ALLOWED COMPONENT TYPES ONLY**:
- HTTP Listener
- Scheduler (for @Scheduled methods)
- Transform Message
- Database Select
- Database Insert
- Database Update (rarely)
- Database Delete (rarely)
- Raise Error
- Set Payload
- Set Variable (rarely)
- JMS Publish
- File Read
- File Write (basic only)
- HTTP Request (for external calls)
- Logger
- Flow Reference

**DO NOT USE**:
- Try
- Choice (use links instead)
- File List, File Copy, File Rename, File Move (use basic File Read/Write only)
- Advanced file operations beyond basic read/write
- Any advanced components

### 8. XML Code Templates (for the "code" field)

IMPORTANT: These XML snippets go in the "code" field with all quotes escaped!

#### HTTP Listener
```xml
<http:listener doc:name="Listener" doc:id="550e8400-e29b-41d4-a716-446655440000" config-ref="httpListenerConfig" path="/api/users/{id}" allowedMethods="GET"/>
```
In JSON "code" field:
```json
"code": "<http:listener doc:name=\"Listener\" doc:id=\"a7b9c1d3-5e7f-4a9c-8b1d-def012345678\" config-ref=\"httpListenerConfig\" path=\"/api/users/{id}\" allowedMethods=\"GET\"/>"

#### Transform Message (GET parameters)
```xml
<ee:transform doc:name="Transform Message" doc:id="6ba7b810-9dad-41d4-adf4-362877b8d91f">
  <ee:message>
    <ee:set-payload><![CDATA[%dw 2.0 output application/json --- payload]]></ee:set-payload>
  </ee:message>
  <ee:variables>
    <ee:set-variable variableName="userId"><![CDATA[attributes.uriParams.id]]></ee:set-variable>
  </ee:variables>
</ee:transform>
```
In JSON "code" field:
```json
"code": "<ee:transform doc:name=\"Transform Message\" doc:id=\"6ba7b810-9dad-41d4-adf4-362877b8d91f\"><ee:message><ee:set-payload><![CDATA[%dw 2.0 output application/json --- payload]]></ee:set-payload></ee:message><ee:variables><ee:set-variable variableName=\"userId\"><![CDATA[attributes.uriParams.id]]></ee:set-variable></ee:variables></ee:transform>"

#### Transform Message (POST body)
```xml
<ee:transform doc:name="Transform Message" doc:id="c8d9e0f1-2345-4678-9abc-def012345678">
  <ee:message>
    <ee:set-payload>
      <![CDATA[%dw 2.0
output application/json
---
payload]]>
    </ee:set-payload>
  </ee:message>
</ee:transform>
```

#### Database Select
```xml
<db:select doc:name="Database Select" doc:id="f47ac10b-58cc-4372-a567-0e02b2c3d479" config-ref="dbConfig">
  <db:sql><![CDATA[SELECT * FROM User WHERE id = :userId]]></db:sql>
  <db:input-parameters><![CDATA[#[{userId: vars.userId}]]]></db:input-parameters>
</db:select>
```
In JSON "code" field:
```json
"code": "<db:select doc:name=\"Database Select\" doc:id=\"c8d0e2f4-6a8c-4c8e-9a2c-012345678901\" config-ref=\"dbConfig\"><db:sql><![CDATA[SELECT * FROM User WHERE id = :userId]]></db:sql><db:input-parameters><![CDATA[#[{userId: vars.userId}]]]></db:input-parameters></db:select>"

#### Database Insert
```xml
<db:insert doc:name="Insert" doc:id="d9e0f1a2-3456-4789-abcd-ef0123456789" config-ref="dbConfig">
  <db:sql><![CDATA[INSERT INTO table (col1, col2) VALUES (:val1, :val2)]]></db:sql>
  <db:input-parameters><![CDATA[#[{val1: payload.field1, val2: payload.field2}]]]></db:input-parameters>
</db:insert>
```

#### Raise Error
```xml
<raise-error doc:name="Raise Error" doc:id="123e4567-e89b-42d3-a456-556642440000" type="VALIDATION:NULL" description="User not found"/>
```
In JSON "code" field:
```json
"code": "<raise-error doc:name=\"Raise Error\" doc:id=\"d9e1f3a5-7b9d-4d9f-0b3d-123456789012\" type=\"VALIDATION:NULL\" description=\"User not found\"/>"
```
**CRITICAL REQUIREMENTS**: 
- **MUST include BOTH "type" AND "description" attributes** - Both are mandatory
- **MUST use "description" attribute, NOT "message"** - This is a critical requirement
- Error types must follow namespace:identifier format (e.g., VALIDATION:NULL, DB:CONNECTIVITY, VALIDATION:INVALID_INPUT)
- Common error types: VALIDATION:NULL, VALIDATION:INVALID_INPUT, DB:CONNECTIVITY, SECURITY:UNAUTHORIZED

#### Set Payload
```xml
<set-payload doc:name="Set Payload" doc:id="9b2c1fc8-2fd5-4861-a83f-155c8e1d8f3e"><![CDATA[%dw 2.0 output application/json --- payload]]></set-payload>
```
In JSON "code" field:
```json
"code": "<set-payload doc:name=\"Set Payload\" doc:id=\"e0f2a4b6-8c0e-4e0a-1c4e-234567890123\"><![CDATA[%dw 2.0 output application/json --- payload]]></set-payload>"
```
Note: Use CDATA section for DataWeave expressions

#### JMS Publish
```xml
<jms:publish doc:name="Publish" doc:id="7c9e2100-abcd-4fed-b823-192837465001" config-ref="jmsConfig" destination="${jms.queue.name}">
  <jms:message>
    <jms:body><![CDATA[%dw 2.0 output application/json --- payload]]></jms:body>
  </jms:message>
</jms:publish>
```
In JSON "code" field:
```json
"code": "<jms:publish doc:name=\"Publish\" doc:id=\"7c9e2100-abcd-4fed-b823-192837465001\" config-ref=\"jmsConfig\" destination=\"${jms.queue.name}\"><jms:message><jms:body><![CDATA[%dw 2.0 output application/json --- payload]]></jms:body></jms:message></jms:publish>"
```

#### Scheduler (for @Scheduled methods)
**CRITICAL**: If any method in the Spring Boot project contains the @Scheduled annotation, the corresponding MuleSoft flow MUST begin with a Scheduler component starting from that @Scheduled method.

```xml
<scheduler doc:name="Scheduler" doc:id="f1a3b5c7-9e2b-4d6f-8a1c-345678901234">
  <scheduling-strategy>
    <fixed-frequency frequency="60000" timeUnit="MILLISECONDS"/>
  </scheduling-strategy>
</scheduler>
```
In JSON "code" field:
```json
"code": "<scheduler doc:name=\"Scheduler\" doc:id=\"f5d8e2f0-3b24-4c56-9abc-def012345678\"><scheduling-strategy><fixed-frequency frequency=\"60000\" timeUnit=\"MILLISECONDS\"/></scheduling-strategy></scheduler>"
```
**MANDATORY Structure Requirements**:
- The scheduler tag MUST contain the inline tag `<scheduling-strategy>`
- The `<scheduling-strategy>` tag MUST contain the inline tag `<fixed-frequency>`
- The `<fixed-frequency>` tag MUST include both attributes: `frequency` and `timeUnit`
- Common timeUnit values: MILLISECONDS, SECONDS, MINUTES, HOURS, DAYS
- The frequency should match the Spring Boot @Scheduled configuration
- **Flow Structure**: @Scheduled method → Scheduler component → rest of the flow logic

#### File Read
```xml
<file:read doc:name="Read" doc:id="8a5f6e20-b123-4cd5-9876-543210fedcba" config-ref="fileConfig" path="${file.input.path}"/>
```
In JSON "code" field:
```json
"code": "<file:read doc:name=\"Read\" doc:id=\"b2c3d4e5-6f7a-8b9c-0d1e-2f3a4b5c6d7e\" config-ref=\"fileConfig\" path=\"${file.input.path}\"/>"
```

#### File Write
```xml
<file:write doc:name="Write" doc:id="e832f41c-7a8d-4925-b6c1-987654321098" config-ref="fileConfig" path="${file.output.path}/output.txt">
  <file:content><![CDATA[#[payload]]]></file:content>
</file:write>
```
In JSON "code" field:
```json
"code": "<file:write doc:name=\"Write\" doc:id=\"c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f\" config-ref=\"fileConfig\" path=\"${file.output.path}/output.txt\"><file:content><![CDATA[#[payload]]]></file:content></file:write>"
```

**CRITICAL FILE OPERATION RULES**:
- **ONLY use file:read and file:write** - Do not use file:list, file:copy, file:rename, file:move
- For file copying: Use file:read then file:write to different path
- For file archiving: Use file:read then file:write to archive directory
- For file processing status: Use file:write to create status files or use JMS/DB for tracking
- **No advanced file operations** - Keep it simple with basic read/write only

#### HTTP Request (for external/internal service calls)
**CRITICAL**: If the Spring Boot application makes HTTP calls (via RestTemplate, WebClient, or Feign), you MUST generate HTTP Request components.

```xml
<http:request method="POST" doc:name="Request" doc:id="e4f5g6h7-8i9j-0k1l-2m3n-o4p5q6r7s8t9" config-ref="HTTP_Request_configuration" path="/createOrder">
  <http:body><![CDATA[#[payload]]]></http:body>
</http:request>
```
In JSON "code" field:
```json
"code": "<http:request method=\"POST\" doc:name=\"Request\" doc:id=\"a2b4c6d8-1234-4abc-8def-0123456789ab\" config-ref=\"HTTP_Request_configuration\" path=\"/createOrder\"><http:body><![CDATA[#[payload]]]></http:body></http:request>"
```
**MANDATORY Requirements**:
- The `<http:request>` tag MUST include:
  - `method` attribute based on the original call (GET, POST, PUT, DELETE, PATCH)
  - `doc:name="Request"` and a unique `doc:id`
  - `config-ref` pointing to the HTTP request configuration (e.g., "HTTP_Request_configuration")
  - `path` attribute reflecting the endpoint being called
- Must include inline `<http:body>` tag with `<![CDATA[#[payload]]]>` for request payload (for POST/PUT/PATCH)
- For GET requests, omit the `<http:body>` tag

### 9. Global Configuration Examples

#### HTTP Listener Config (in globalElements array)
```json
{
  "config": "<http:listener-config name=\"httpListenerConfig\" doc:name=\"HTTP Listener Config\" doc:id=\"f5d8e2f0-3b24-4c56-9abc-def012345678\"><http:listener-connection host=\"${http.host}\" port=\"${http.port}\"/></http:listener-config>",
  "activityType": "HTTP_Listener_Configuration",
  "name": "httpListenerConfig",
  "type": "globalElement",
  "activityDescription": "Global HTTP Listener configuration for handling requests"
}
```

#### Database Config (in globalElements array)
```json
{
  "config": "<db:config name=\"dbConfig\" doc:name=\"Database Config\" doc:id=\"a5b9c3e1-7f2d-4e8a-b6c9-123456789abc\"><db:my-sql-connection host=\"${db.host}\" port=\"${db.port}\" user=\"${db.user}\" password=\"${db.password}\" database=\"${db.database}\"/></db:config>",
  "activityType": "Database_Configuration",
  "name": "dbConfig",
  "type": "globalElement",
  "activityDescription": "Global Database configuration for MySQL connection"
}
```

#### JMS Config (in globalElements array)
**CRITICAL**: Required when Spring Boot uses JMS messaging (JmsTemplate or ActiveMQ).

```json
{
  "config": "<jms:config name=\"jmsConfig\" doc:name=\"JMS Config\" doc:id=\"b7c9d1e3-5a2f-4e8b-9c6d-ef1234567890\"><jms:active-mq-connection username=\"${activemq.user}\" password=\"${activemq.password}\" specification=\"JMS_1_1\"><jms:factory-configuration brokerUrl=\"${activemq.broker.url}\"/></jms:active-mq-connection></jms:config>",
  "activityType": "JMS_Configuration",
  "name": "jmsConfig",
  "type": "globalElement",
  "activityDescription": "Global JMS configuration for ActiveMQ connection"
}
```
**MANDATORY JMS Configuration Structure**:
- The tag must be `<jms:config>` with attributes: `name`, `doc:name`, and `doc:id`
- Must contain inline tag `<jms:active-mq-connection>` with attributes: `username`, `password`, `specification`
- Inside `<jms:active-mq-connection>`, must include `<jms:factory-configuration>` with attribute `brokerUrl`
- The `brokerUrl` MUST be inside `<jms:factory-configuration>`, NOT in the parent tag
```
**JMS Configuration Structure**:
- The `<jms:config>` tag must have attributes: `name`, `doc:name`, and `doc:id`
- Must contain inline tag `<jms:active-mq-connection>` with attributes: `username`, `password`, `specification`
- Inside `<jms:active-mq-connection>`, include `<jms:factory-configuration>` with `brokerUrl` attribute

#### File Config (in globalElements array)
```json
{
  "config": "<file:config name=\"fileConfig\" doc:name=\"File Config\" doc:id=\"d5e7f9a1-3c5e-4a7c-8e1a-567890abcdef\"><file:connection workingDir=\"${file.working.dir}\"/></file:config>",
  "activityType": "File_Configuration", 
  "name": "fileConfig",
  "type": "globalElement",
  "activityDescription": "Global File configuration for file operations"
}
```

#### HTTP Request Config (in globalElements array)
**CRITICAL**: MUST be generated when Spring Boot makes HTTP calls to external/internal services.

```json
{
  "config": "<http:request-config name=\"HTTP_Request_configuration\" doc:name=\"HTTP Request configuration\" doc:id=\"e6f8a0b2-4d6f-4b8d-9f2b-678901bcdef0\"><http:request-connection host=\"localhost\" port=\"8082\"/></http:request-config>",
  "activityType": "HTTP_Request_Configuration",
  "name": "HTTP_Request_configuration",
  "type": "globalElement",
  "activityDescription": "Global HTTP Request configuration for outbound HTTP calls"
}
```
**MANDATORY HTTP Request Configuration Structure**:
- The `<http:request-config>` block MUST be placed in the global configuration section
- Must have attributes: `name="HTTP_Request_configuration"`, `doc:name="HTTP Request configuration"`, and unique `doc:id`
- Must contain `<http:request-connection>` with:
  - `host` attribute reflecting the target system (e.g., "localhost", "api.example.com", or `${external.service.host}`)
  - `port` attribute reflecting the target port (e.g., "8082", "443", or `${external.service.port}`)
- This configuration is referenced by all HTTP Request components via `config-ref`

#### Important Notes on Global Configurations:
1. The `host` attribute in db:my-sql-connection should include the full JDBC URL prefix (e.g., "jdbc:mysql://localhost")
2. The `port` attribute is separate from the host
3. All quotes within the XML must be escaped with backslashes in the JSON
4. **DO NOT include driverClassName attribute** in MySQL connections - it's not required
5. **Always use ${propertyName} references** for configuration values instead of hardcoding them
6. **DO NOT include doc:name attribute** inside connection elements (e.g., http:listener-connection, file:connection)
7. **JMS Configuration** must use the proper structure with jms:active-mq-connection

## Complete Flow Example

This example shows the EXACT format required, including the critical "code" field:

Spring Boot:
```java
@GetMapping("/api/users/{id}")
public User getUserById(@PathVariable Long id) {
    User user = userRepository.findById(id).orElse(null);
    if (user == null) {
        throw new NotFoundException("User not found");
    }
    return user;
}
```

Ship Format JSON (EXACT format with all required fields):
```json
{
  "name": "getUserByIdFlow",
  "components": [
    {
      "activityType": "HTTP Listener",
      "activityConfig": "GET /api/users/{id}",
      "config": "httpListenerConfig",
      "code": "<http:listener doc:name=\"Listener\" doc:id=\"a7b9c1d3-5e7f-4a9c-8b1d-def012345678\" config-ref=\"httpListenerConfig\" path=\"/api/users/{id}\" allowedMethods=\"GET\"/>",
      "inputBindings": "",
      "outputBindings": "",
      "name": "getUserByIdListener",
      "parentId": [0],
      "sequenceId": 1,
      "start": "true",
      "type": "activity",
      "activityDescription": "Receives HTTP GET request for user by ID",
      "summary": {
        "sourceType": "HTTP Listener",
        "simType": "HTTP Listener",
        "target type": "HTTP Listener",
        "simFound": true,
        "codeGenerated": true,
        "packageFound": true,
        "functionFound": true
      },
      "category": "HTTP Listener",
      "function": "HTTP Listener"
    },
    {
      "activityType": "Transform Message",
      "activityConfig": "Extract ID from URI",
      "config": "transformConfig",
      "code": "<ee:transform doc:name=\"Transform Message\" doc:id=\"6ba7b810-9dad-41d4-adf4-362877b8d91f\"><ee:message><ee:set-payload><![CDATA[%dw 2.0 output application/json --- payload]]></ee:set-payload></ee:message><ee:variables><ee:set-variable variableName=\"userId\"><![CDATA[attributes.uriParams.id]]></ee:set-variable></ee:variables></ee:transform>",
      "inputBindings": "",
      "outputBindings": "",
      "name": "transformGetUserById",
      "parentId": [1],
      "sequenceId": 2,
      "start": "false",
      "type": "activity",
      "activityDescription": "Transforms and extracts user ID from URI parameters",
      "summary": {
        "sourceType": "Transform Message",
        "simType": "Transform Message",
        "target type": "Transform Message",
        "simFound": true,
        "codeGenerated": true,
        "packageFound": true,
        "functionFound": true
      },
      "category": "Transform Message",
      "function": "Transform Message"
    },
    {
      "activityType": "Database Select",
      "activityConfig": "Find user by ID",
      "config": "dbConfig",
      "code": "<db:select doc:name=\"Database Select\" doc:id=\"c8d0e2f4-6a8c-4c8e-9a2c-012345678901\" config-ref=\"dbConfig\"><db:sql><![CDATA[SELECT * FROM User WHERE id = :userId]]></db:sql><db:input-parameters><![CDATA[#[{userId: vars.userId}]]]></db:input-parameters></db:select>",
      "inputBindings": "",
      "outputBindings": "",
      "name": "dbSelectUserById",
      "parentId": [2],
      "sequenceId": 3,
      "start": "false",
      "type": "activity",
      "activityDescription": "Selects user from database by ID",
      "summary": {
        "sourceType": "Database Select",
        "simType": "Database Select",
        "target type": "Database Select",
        "simFound": true,
        "codeGenerated": true,
        "packageFound": true,
        "functionFound": true
      },
      "category": "Database Select",
      "function": "Database Select"
    },
    {
      "activityType": "Raise Error",
      "activityConfig": "User not found",
      "config": "errorConfig",
      "code": "<raise-error doc:name=\"Raise Error\" doc:id=\"d9e1f3a5-7b9d-4d9f-0b3d-123456789012\" type=\"VALIDATION:NULL\" description=\"User not found\"/>",
      "inputBindings": "",
      "outputBindings": "",
      "name": "raiseErrorUserNotFound",
      "parentId": [3],
      "sequenceId": 4,
      "start": "false",
      "type": "activity",
      "activityDescription": "Raises error if user is not found",
      "summary": {
        "sourceType": "Raise Error",
        "simType": "Raise Error",
        "target type": "Raise Error",
        "simFound": true,
        "codeGenerated": true,
        "packageFound": true,
        "functionFound": true
      },
      "category": "Raise Error",
      "function": "Raise Error"
    },
    {
      "activityType": "Set Payload",
      "activityConfig": "Return user data",
      "config": "setPayloadConfig",
      "code": "<set-payload doc:name=\"Set Payload\" doc:id=\"e0f2a4b6-8c0e-4e0a-1c4e-234567890123\"><![CDATA[%dw 2.0 output application/json --- payload]]></set-payload>",
      "inputBindings": "",
      "outputBindings": "",
      "name": "setPayloadUserData",
      "parentId": [3],
      "sequenceId": 5,
      "start": "false",
      "type": "activity",
      "activityDescription": "Sets the payload with user data",
      "summary": {
        "sourceType": "Set Payload",
        "simType": "Set Payload",
        "target type": "Set Payload",
        "simFound": true,
        "codeGenerated": true,
        "packageFound": true,
        "functionFound": true
      },
      "category": "Set Payload",
      "function": "Set Payload"
    }
  ],
  "groupActivities": [],
  "links": [
    {
      "conditionType": "always",
      "description": "Link from HTTP Listener to Transform Message",
      "from": 1,
      "to": 2
    },
    {
      "conditionType": "always",
      "description": "Link from Transform Message to Database Select",
      "from": 2,
      "to": 3
    },
    {
      "conditionType": "xpath",
      "description": "Check if user is found",
      "from": 3,
      "to": 4,
      "xpath": "payload == null"
    },
    {
      "conditionType": "otherwise",
      "description": "User found, set payload",
      "from": 3,
      "to": 5
    }
  ]
}
```

## CRITICAL: The "code" Field

The "code" field is **MANDATORY** and must contain:
1. **Complete Mule XML** - The entire XML element, not just a fragment
2. **Escaped quotes** - All double quotes must be escaped with backslashes
3. **Proper attributes** - Include doc:name, doc:id, config-ref as needed
4. **CDATA sections** - For DataWeave expressions and SQL queries
5. **Valid Mule 4 syntax** - Must be parseable by Anypoint Studio
6. **SIMPLE COMPONENTS ONLY** - No advanced features

Examples of correct "code" field values:
```json
"code": "<http:listener doc:name=\"Listener\" doc:id=\"a7b9c1d3-5e7f-4a9c-8b1d-def012345678\" config-ref=\"httpListenerConfig\" path=\"/api/users/{id}\" allowedMethods=\"GET\"/>"

"code": "<db:select doc:name=\"Database Select\" doc:id=\"c8d0e2f4-6a8c-4c8e-9a2c-012345678901\" config-ref=\"dbConfig\"><db:sql><![CDATA[SELECT * FROM User WHERE id = :userId]]></db:sql><db:input-parameters><![CDATA[#[{userId: vars.userId}]]]></db:input-parameters></db:select>"

"code": "<set-payload doc:name=\"Set Payload\" doc:id=\"e0f2a4b6-8c0e-4e0a-1c4e-234567890123\"><![CDATA[%dw 2.0 output application/json --- payload]]></set-payload>"
```

## IMPORTANT CONSTRAINTS FOR COMPATIBILITY

To ensure compatibility with external processing tools, follow these STRICT rules:

### 1. PROHIBITED Features (DO NOT USE):
- ❌ External DWL imports (e.g., `import from dwl::user-transformations`)
- ❌ Try blocks or error handling scopes
- ❌ HTTP response configurations in listeners
- ❌ CORS interceptors or any interceptors
- ❌ Connection pooling in database configs
- ❌ Sub-flows (inline all logic in main flows)
- ❌ Property placeholders in components (only use in global configurations)
- ❌ Choice components in the component list
- ❌ Complex DataWeave functions
- ❌ External file references

### 2. ALLOWED Components Only:
✅ **HTTP Listener** - Basic only
```xml
<http:listener doc:name="Listener" doc:id="[GENERATE-RANDOM-UUID]" config-ref="httpListenerConfig" path="/path" allowedMethods="GET"/>
```

✅ **Transform Message** - Inline DataWeave only
```xml
<ee:transform doc:name="Transform Message" doc:id="[GENERATE-RANDOM-UUID]">
  <ee:message>
    <ee:set-payload><![CDATA[%dw 2.0 output application/json --- payload]]></ee:set-payload>
  </ee:message>
  <ee:variables>
    <ee:set-variable variableName="varName"><![CDATA[expression]]></ee:set-variable>
  </ee:variables>
</ee:transform>
```

✅ **Database Operations**
- Database Select
- Database Insert
- Database Update (rarely)
- Database Delete (rarely)

✅ **Raise Error** - Simple only
```xml
<raise-error doc:name="Raise Error" doc:id="[GENERATE-RANDOM-UUID]" type="ERROR_TYPE" message="Error message"/>
```

✅ **Set Payload** - Simple expressions
```xml
<set-payload doc:name="Set Payload" doc:id="[GENERATE-RANDOM-UUID]"><![CDATA[%dw 2.0 output application/json --- payload]]></set-payload>
```

✅ **Set Variable** (use sparingly)
```xml
<set-variable doc:name="Set Variable" doc:id="[GENERATE-RANDOM-UUID]" variableName="varName" value="#[expression]"/>
```

✅ **Logger**
```xml
<logger level="INFO" doc:name="DB Insert" doc:id="dbb164e1-7c9a-401b-86f1-68d15a6f3254" message=""Saved Successfully""/>
```

✅ **Flow Ref**
```xml
<flow-ref doc:name="Process Order" doc:id="4d2084e0-3e80-4891-bb65-22cca07f2e81" name="processOrderFileFlow"/>
```

### 3. Branching Rules:
- Use xpath/otherwise links for conditional logic
- NO choice components in the component list
- Simple conditions only (e.g., `payload == null`, `vars.userId == null`)
- Always provide both xpath and otherwise branches

### 4. Naming Conventions:
- Component names: camelCase (e.g., `getUserByIdListener`, `transformUserData`)
- Flow names: camelCase ending with "Flow" (e.g., `getUserByIdFlow`)
- Doc IDs: Must be valid UUIDs

### 5. Configuration Rules:
- **USE property placeholders** for all configuration values (e.g., ${http.port}, ${db.host})
- HTTP Listener Config: `host="${http.host}" port="${http.port}"`
- Database Config: `host="${db.host}" port="${db.port}" user="${db.user}" password="${db.password}"`
- No connection pooling
- Simple configurations only

### 6. DataWeave Constraints:
- Inline expressions only
- No external module imports
- Simple transformations only
- Basic operators and functions
- Always use `output application/json` instead of `output application/java`
- **CRITICAL**: Quote ALL reserved words in JSON data when used as object keys
- **CRITICAL FOR TRANSFORM MESSAGE**: When creating JSON objects in DataWeave, ALWAYS quote keys that are reserved words like "type", "class", "function" etc. This prevents MuleSoft parsing errors
- Reserved words that MUST be quoted: type, class, function, import, var, if, else, match, case, default, namespace, module, output, input
- Example CORRECT usage:
  ```dataweave
  %dw 2.0
  output application/json
  ---
  {
    "type": "JSON",           // ✅ Quoted because "type" is reserved
    "class": "UserData",      // ✅ Quoted because "class" is reserved
    "function": "process",    // ✅ Quoted because "function" is reserved
    status: "active",         // ✅ Not reserved, quotes optional
    fileType: vars.fileType   // ✅ Variable name usage is fine
  }
  ```
- Example INCORRECT usage:
  ```dataweave
  %dw 2.0
  output application/json
  ---
  {
    type: "JSON",            // ❌ "type" is reserved, must be quoted
    class: "UserData",       // ❌ "class" is reserved, must be quoted
    function: "process"      // ❌ "function" is reserved, must be quoted
  }
  ```
- Note: Using reserved words in variable names (like `vars.fileType`) is valid and doesn't require special handling

### 7. SQL Patterns:
- Use direct SQL (no stored procedures)
- Simple parameter binding with `:paramName`
- Basic SELECT, INSERT, UPDATE, DELETE only

### 8. Component Order:
1. HTTP Listener (always first)
2. Transform Message (extract parameters)
3. Database operation or business logic
4. Branching with Raise Error for failures
5. Set Payload for response

### 9. Summary Rules:
- All boolean fields in summary must be `true`
- sourceType, simType, and "target type" should match activityType
- Note the space in "target type"

### 10. General Principles:
- Keep it simple - if in doubt, use the simpler approach
- Inline all logic - no sub-flows or references
- Direct implementation - no abstraction layers
- Minimal components - only what's necessary
- Clear flow - sequential with simple branching

## CRITICAL FIXES FOR COMPATIBILITY

### Missing Component Patterns (MUST FIX)

1. **JMS Operations**: When Spring Boot code contains JmsTemplate.send() or @JmsListener, you MUST include JMS Publish components:
   - Add JMS Publish component with proper destination reference: `destination="${jms.queue.name}"`
   - Include JMS configuration in globalElements array
   - **For error notifications**: Use JMS Publish for status messages, NOT for replacing Raise Error components

2. **File Operations**: When Spring Boot code contains File objects or FileUtils, you MUST use basic File operations:
   - Replace `File file = new File(filePath)` patterns with `<file:read>` components
   - **ONLY use file:read and file:write** - No file:list, file:copy, file:rename, file:move
   - For copying files: Use file:read source, then file:write to destination
   - For archiving: Use file:read original, then file:write to archive directory
   - Add File configuration in globalElements array with workingDir property

3. **HTTP Response Handling**: For REST endpoints that return different status codes:
   - **DO NOT use HTTPResponse tags** (invalid in Mule)
   - Use Set Variable to set httpStatus variable
   - Configure response in HTTP Listener's Responses tab
   - Example pattern: `<ee:set-variable variableName="httpStatus"><![CDATA[400]]></ee:set-variable>`

4. **Variable Simplification**: In DataWeave expressions:
   - Use `#[lower(vars.file)]` instead of `#[lower(vars.file.getName())]`
   - The `.getName()` method call is not required

5. **Error Type Format and Error Handling**: All error scenarios must be handled properly:
   - **ALWAYS use Raise Error components** for exception handling, not JMS notifications
   - **CRITICAL: Raise Error MUST use "description" attribute, NOT "message"**
   - Use `type="VALIDATION:NULL"` instead of `type="NOT_FOUND"`
   - Use `type="VALIDATION:INVALID_INPUT"` instead of `type="BAD_REQUEST"`
   - Use `type="DB:CONNECTIVITY"` for database errors
   - Use `type="SECURITY:UNAUTHORIZED"` for auth errors
   - **Error vs Notification**: Use Raise Error for stopping flow execution; use JMS Publish for status notifications
   - **When to use each**:
     - Raise Error: File not found, invalid input, business rule violations
     - JMS Publish: Success notifications, processing status updates, audit trails

### Flow and Sub-Flow Rules

6. **No Sub-Flows in Components**: Never include sub-flows in the component arrays
   - Remove any `doc:name` attributes from Flow and SubFlow elements
   - Inline all logic within main flows

7. **Error Scope Requirements**: When using error handling, include all required attributes:
   ```xml
   <on-error-propagate enableNotifications="true" logException="true" doc:name="On Error Propagate" doc:id="[GENERATE-RANDOM-UUID]" type="VALIDATION:NULL">
   </on-error-propagate>
   ```

## Key Points to Remember

1. **"code" field is CRITICAL** - Contains the actual Mule XML that will be executed
2. **Every field is required** - No optional fields in components
3. **Branching via links** - Never use choice components
4. **Sequential parentId** - Except for branches
5. **Valid XML in code** - Must be parseable Mule XML with escaped quotes
6. **Unique names** - Within each flow
7. **Start flag** - Only first component is "true" (as string, not boolean)
8. **Empty strings** - Use "" not null for empty fields
9. **Array for parentId** - Even with single value [0] or [3]
10. **Complete summary** - All boolean fields must be present
11. **Consistent naming** - camelCase for flow and component names
12. **Config references** - Can be globalElement name OR a config value string
13. **UUIDs for doc:id** - All doc:id attributes must be valid UUIDs
14. **Structured globalVariables** - Use source, type, value format
15. **Property references** - Use ${propertyName} in global configurations

## FINAL COMPATIBILITY CHECKLIST

Before generating the ship JSON, ensure ALL these requirements are met:

### ✅ Required Components for Spring Boot Patterns:
- [ ] JMS Publish components for any JmsTemplate.send() operations
- [ ] File Read components for any File object or FileUtils usage  
- [ ] Transform Message for JMS payload formatting
- [ ] Proper error types with namespace:identifier format (VALIDATION:NULL, etc.)

### ✅ Required Global Configurations:
- [ ] HTTP Listener Config with ${http.host} and ${http.port} references
- [ ] JMS Config with ActiveMQ connection (if JMS operations exist)
- [ ] File Config with workingDir property (if file operations exist)
- [ ] Database Config without driverClassName attribute
- [ ] All configs mirrored in both globalElements and globalConfig arrays

### ✅ Required Global Variables:
- [ ] All application.properties values in structured format with source/type/value
- [ ] Reference variables using ${propertyName} syntax in configurations
- [ ] Include all JMS-related properties (broker.url, username, password, queue names)
- [ ] Include all file-related properties (working.dir, input.path, etc.)

### ✅ DataWeave and XML Requirements:
- [ ] Quote all reserved words in JSON payloads ("type" not type, "class" not class, "function" not function)
- [ ] Use application/json output, never application/java
- [ ] **CRITICAL: All doc:id attributes MUST contain valid RANDOM UUIDs**
  - [ ] UUID format: XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX (UUID v4)
  - [ ] Generate RANDOM hex values - NO sequential patterns like "a1b2c3d4"
  - [ ] No invalid characters (g-z) in UUIDs
  - [ ] No text identifiers as doc:id values
  - [ ] Each component must have a unique RANDOMLY generated UUID
- [ ] Remove .getName() method calls from file variables
- [ ] Escape all quotes in code field XML
- [ ] Use CDATA sections for DataWeave and SQL content
- [ ] **CRITICAL: Check and quote ALL reserved words when used as object keys in JSON**:
  - [ ] Reserved words to check: type, class, function, import, var, if, else, match, case, default, namespace, module, output, input
  - [ ] Example: Use `{"type": "value"}` not `{type: "value"}`
  - [ ] Note: Variable names like `vars.fileType` are valid and don't need special handling

### ✅ Error Handling Requirements:
- [ ] Use Raise Error components for actual errors that stop flow execution
- [ ] Use JMS Publish for status notifications and audit trails (not error replacement)
- [ ] Error types use namespace:identifier format (VALIDATION:NULL, DB:CONNECTIVITY)
- [ ] All on-error elements include enableNotifications="true" and logException="true" (if used)
- [ ] No HTTPResponse tags (use Set Variable for status codes)
- [ ] **Raise Error MUST include BOTH "type" AND "description" attributes**
- [ ] **Raise Error MUST use "description" attribute, NOT "message"**
- [ ] No doc:name in connection sub-elements

### ✅ File Operation Requirements:
- [ ] ONLY use file:read and file:write components
- [ ] NO file:list, file:copy, file:rename, file:move operations
- [ ] Implement copying as: file:read source → file:write destination
- [ ] Implement archiving as: file:read original → file:write archive location
- [ ] Use file:write with <file:content> for output operations

### ✅ Scheduler Requirements (for @Scheduled methods):
- [ ] If Spring Boot has @Scheduled methods, flow MUST begin with Scheduler component
- [ ] Scheduler MUST contain inline <scheduling-strategy> tag
- [ ] <scheduling-strategy> MUST contain inline <fixed-frequency> tag
- [ ] <fixed-frequency> MUST have both "frequency" and "timeUnit" attributes
- [ ] Flow starts from the @Scheduled method logic

### ✅ JMS Configuration Requirements:
- [ ] If Spring Boot uses JMS (JmsTemplate/ActiveMQ), MUST generate <jms:config>
- [ ] <jms:config> MUST have: name, doc:name, and doc:id attributes
- [ ] MUST contain <jms:active-mq-connection> with: username, password, specification
- [ ] <jms:active-mq-connection> MUST contain <jms:factory-configuration> with brokerUrl
- [ ] brokerUrl MUST be inside <jms:factory-configuration>, NOT in parent tag

### ✅ HTTP Request Requirements (for external/internal calls):
- [ ] If Spring Boot makes HTTP calls, MUST generate <http:request> components
- [ ] <http:request> MUST have: method, doc:name="Request", doc:id, config-ref, path
- [ ] Include <http:body> with CDATA payload for POST/PUT/PATCH
- [ ] MUST generate corresponding <http:request-config> in globalElements
- [ ] <http:request-config> MUST contain <http:request-connection> with host and port

This checklist ensures your ship JSON will be compatible with external processing tools and follows all Mule 4 best practices.