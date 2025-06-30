# Prompt Orchestration Architecture

## Overview

The v2 Code Conversion Studio implements a sophisticated prompt orchestration system that combines agent-specific capabilities with target framework-specific implementation details. This creates a clean separation of concerns and enables reusable, modular prompt sequences.

## Key Concepts

### 1. Agent Prompts
- **Purpose**: Define WHAT needs to be done from the agent's perspective
- **Focus**: Agent's role and responsibilities
- **Location**: `/v2/prompts/{agent}/{capability}/`
- **Example**: Code Architect analyzes project structure and creates migration plan

### 2. Target Prompts
- **Purpose**: Define HOW to implement for specific target frameworks
- **Focus**: Framework-specific patterns and best practices
- **Location**: `/v2/prompts/targets/{framework}/`
- **Example**: Rust-specific implementation patterns for migration

### 3. Orchestration Sequences
- **Purpose**: Define the execution order mixing agent and target prompts
- **Managed by**: `PromptOrchestrator` class
- **Benefits**: 
  - Reusable agent logic across different targets
  - Target-specific implementation details stay isolated
  - Clear handoff points between analysis and implementation

## Architecture Flow

```
User Request
    ↓
ExecutionService
    ↓
PromptOrchestrator.get_prompt_sequence()
    ↓
Returns ordered list of prompts:
    1. Agent Prompt (Analyze)
    2. Agent Prompt (Plan) 
    3. Target Prompt (Analyze target requirements)
    4. Target Prompt (Create target plan)
    5. Agent Prompt (Finalize architecture)
    ↓
Execute each prompt with Claude CLI
    ↓
Aggregate results
```

## Example: Code Architect Planning

When executing "Code Architect - Plan" for Java → Rust migration:

1. **Agent: 01_analyze_project_structure.md**
   - Analyzes Java Spring Boot structure
   - Identifies components, dependencies, patterns
   - Creates architecture overview

2. **Agent: 02_create_migration_plan.md**
   - Creates high-level migration strategy
   - Identifies what needs to be migrated
   - Prepares context for target prompts

3. **Target: rust/01_analyze.md**
   - Analyzes Rust-specific requirements
   - Maps Java patterns to Rust idioms
   - Identifies Rust libraries and frameworks

4. **Target: rust/02_plan.md**
   - Creates Rust-specific implementation plan
   - Details how to implement in idiomatic Rust
   - Specifies Rust best practices

5. **Agent: 03_design_target_architecture.md**
   - Finalizes architecture with target details
   - Ensures coherent design
   - Prepares for implementation phase

## Orchestration Patterns

### 1. Analysis Pattern
```python
"analyze": {
    "sequence": [
        {"type": "agent", "prompts": ["01_analyze_codebase.md"]},
        {"type": "target", "prompt": "01_analyze.md"}
    ]
}
```

### 2. Migration Pattern
```python
"migrate": {
    "sequence": [
        {"type": "agent", "prompts": ["01_setup_target_project.md"]},
        {"type": "target", "prompt": "03_migrate.md"},
        {"type": "agent", "prompts": ["02_migrate_data_models.md"]}
    ]
}
```

### 3. Validation Pattern
```python
"validate": {
    "sequence": [
        {"type": "target", "prompt": "04_validate.md"},
        {"type": "agent", "prompts": ["01_run_validation_suite.md"]}
    ]
}
```

## Benefits

1. **Modularity**: Agent prompts are reusable across different targets
2. **Specialization**: Target prompts contain framework-specific expertise
3. **Flexibility**: Easy to add new targets without changing agent logic
4. **Clarity**: Clear separation between "what" (agent) and "how" (target)
5. **Maintainability**: Updates to target patterns don't affect agent logic

## Adding New Orchestrations

To add a new orchestration pattern:

1. Update `prompt_orchestrator.py` with the new sequence
2. Create agent prompts in `/prompts/{agent}/{capability}/`
3. Ensure target prompts exist in `/prompts/targets/{framework}/`
4. Test the orchestration flow

Example:
```python
"new_capability": {
    "description": "Description of the capability",
    "sequence": [
        {"type": "agent", "prompts": ["01_task.md"], "purpose": "Initial task"},
        {"type": "target", "prompt": "01_analyze.md", "purpose": "Target analysis"},
        {"type": "agent", "prompts": ["02_finalize.md"], "purpose": "Finalize"}
    ]
}
```

## Viewing Orchestrations

Access the orchestration viewer at: `http://localhost:5000/orchestration`

This provides a visual representation of all configured orchestration sequences.

## API Endpoints

### Get Orchestration Info
```
GET /api/orchestration/info
```

### Validate Orchestration
```
POST /api/orchestration/validate
{
    "agent": "code_architect",
    "capability": "plan",
    "targets": ["rust", "python", "go"]
}
```

## Best Practices

1. **Agent Prompts**:
   - Focus on analysis and strategy
   - Avoid target-specific implementation details
   - Prepare context for target prompts
   - Mark handoff points clearly

2. **Target Prompts**:
   - Implement framework-specific patterns
   - Reference agent analysis results
   - Follow target framework best practices
   - Provide idiomatic solutions

3. **Orchestration Design**:
   - Start with agent analysis
   - Insert target prompts at implementation points
   - End with agent validation/finalization
   - Keep sequences logical and efficient