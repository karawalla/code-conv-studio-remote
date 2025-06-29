#!/usr/bin/env python3
"""
Generate basic prompt templates for all target frameworks
"""
import os
import json

# Define the 6 prompt types
PROMPT_TYPES = [
    ("01_analyze.md", "Analyze"),
    ("02_plan.md", "Plan"), 
    ("03_migrate.md", "Migrate"),
    ("04_validate.md", "Validate"),
    ("05_fix.md", "Fix"),
    ("06_discuss.md", "Discuss")
]

# Basic template for each prompt type
TEMPLATES = {
    "Analyze": """# Analyze - {target} Target

## Objective
Analyze the source code to understand its architecture and prepare for migration to {target}.

## Context
- Source: {{{{source_name}}}} ({{{{source_type}}}})
- Target: {target}
- Focus on identifying patterns and {target} equivalents

## Analysis Instructions
1. Identify architectural patterns
2. Map dependencies to {target} ecosystem
3. Analyze data models and types
4. Review API patterns
5. Identify migration challenges

## Output Format
Provide detailed analysis with {target}-specific recommendations.
""",
    
    "Plan": """# Plan - {target} Migration

## Objective
Create a comprehensive migration plan from {{{{source_name}}}} to {target}.

## Context
- Analysis completed
- Target: {target} with modern best practices
- Define clear migration phases

## Planning Instructions
1. Define migration strategy
2. Design target architecture
3. Select {target} frameworks and libraries
4. Create phase-by-phase timeline
5. Identify risks and mitigation

## Output Format
Detailed migration plan with milestones and deliverables.
""",
    
    "Migrate": """# Migrate - {target} Implementation

## Objective
Convert the source code to idiomatic {target} while maintaining functionality.

## Context
- Follow the migration plan
- Implement {target} best practices
- Ensure code quality and performance

## Migration Instructions
1. Set up {target} project structure
2. Implement data models
3. Port business logic
4. Create API endpoints
5. Add tests and documentation

## Output Format
Working {target} code with explanatory comments.
""",
    
    "Validate": """# Validate - {target} Code Quality

## Objective
Validate the migrated {target} code for correctness and best practices.

## Context
- Migrated code ready for review
- Ensure production readiness
- Verify {target} idioms applied correctly

## Validation Instructions
1. Run linting and formatting tools
2. Execute test suite
3. Check performance metrics
4. Review security practices
5. Validate {target} conventions

## Output Format
Validation report with test results and recommendations.
""",
    
    "Fix": """# Fix - {target} Code Issues

## Objective
Fix identified issues in the migrated {target} code.

## Context
- Issues found during validation
- Apply {target} best practices
- Optimize for production use

## Fix Instructions
1. Address linting errors
2. Fix failing tests
3. Optimize performance bottlenecks
4. Resolve security vulnerabilities
5. Improve code documentation

## Output Format
Fixed code with change explanations.
""",
    
    "Discuss": """# Discuss - {target} Migration Strategy

## Objective
Discuss architectural decisions, trade-offs, and long-term strategy for {target}.

## Context
- Migration completed
- Evaluate decisions made
- Plan for maintenance and evolution

## Discussion Topics
1. Architecture decisions and trade-offs
2. Framework and library choices
3. Performance optimization strategies
4. Team adoption and training
5. Long-term maintenance plan

## Output Format
Strategic recommendations and best practices guide.
"""
}

def create_target_prompts(target_name, target_dir):
    """Create all 6 prompt files for a target"""
    os.makedirs(target_dir, exist_ok=True)
    
    for filename, prompt_type in PROMPT_TYPES:
        filepath = os.path.join(target_dir, filename)
        if not os.path.exists(filepath):
            content = TEMPLATES[prompt_type].format(target=target_name)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Created: {filepath}")

def main():
    # Define targets
    targets = [
        ("Python", "python"),
        ("Java", "java"),
        ("JavaScript", "javascript"),
        ("C#/.NET", "csharp_dotnet"),
        ("Ruby", "ruby"),
        ("PHP", "php"),
        ("Go", "go"),
        ("Rust", "rust"),
        ("Kotlin", "kotlin"),
        ("Swift", "swift"),
        ("TypeScript", "typescript"),
        ("Scala", "scala"),
        ("Elixir", "elixir"),
        ("Clojure", "clojure"),
        ("Haskell", "haskell")
    ]
    
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts", "targets")
    
    for target_name, target_folder in targets:
        target_dir = os.path.join(prompts_dir, target_folder)
        create_target_prompts(target_name, target_dir)
    
    print(f"\nCreated prompt templates for {len(targets)} targets")

if __name__ == "__main__":
    main()