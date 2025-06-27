#!/usr/bin/env python3
"""Initialize default targets for the Any-to-Any Conversion Studio"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import TargetsService

def init_targets():
    """Create default targets"""
    targets_service = TargetsService('data')
    
    # Check if targets already exist
    existing = targets_service.get_all_targets()
    if existing:
        print(f"Found {len(existing)} existing targets. Skipping initialization.")
        return
    
    print("Creating default targets...")
    
    # Python target
    python_prompts = {
        'analyze': 'Analyze the Python source code architecture, identify frameworks (Django, FastAPI, Flask), patterns, dependencies, and project structure.',
        'plan': 'Create a detailed migration plan to convert from the source framework to Python {framework}, including steps, timeline, dependency mapping, and potential challenges.',
        'migrate': 'Convert the following code from the source framework to Python {framework}, maintaining functionality while following Python best practices and {framework} conventions.',
        'validate': 'Validate the migrated Python code for correctness, performance, PEP 8 compliance, and adherence to {framework} conventions. Identify any issues or improvements.',
        'fix': 'Fix the identified issues in the migrated Python code and ensure it follows {framework} best practices, proper error handling, and Pythonic patterns.',
        'discuss': 'Discuss the migration approach to Python {framework}, trade-offs between different Python frameworks, and alternative solutions for complex scenarios.'
    }
    
    python_target = targets_service.create_target(
        name='Python',
        description='Python frameworks and libraries including Django, FastAPI, Flask, SQLAlchemy, Celery',
        prompts=python_prompts
    )
    
    if python_target:
        print("✓ Created Python target")
    
    # Java target
    java_prompts = {
        'analyze': 'Analyze the Java source code architecture, identify frameworks (Spring Boot, Spring MVC, Jakarta EE), design patterns, dependencies, and build configuration.',
        'plan': 'Create a detailed migration plan to convert from the source framework to Java {framework}, including dependency migration, configuration changes, and testing strategy.',
        'migrate': 'Convert the following code from the source framework to Java {framework}, maintaining functionality while following Java best practices and {framework} conventions.',
        'validate': 'Validate the migrated Java code for correctness, performance, thread safety, and adherence to {framework} conventions. Check for proper exception handling and resource management.',
        'fix': 'Fix the identified issues in the migrated Java code and ensure it follows {framework} best practices, SOLID principles, and proper Java patterns.',
        'discuss': 'Discuss the migration approach to Java {framework}, considerations for microservices architecture, dependency injection patterns, and performance optimization strategies.'
    }
    
    java_target = targets_service.create_target(
        name='Java',
        description='Java frameworks including Spring Boot, Spring MVC, Jakarta EE, Micronaut, Quarkus',
        prompts=java_prompts
    )
    
    if java_target:
        print("✓ Created Java target")
    
    # JavaScript target
    js_prompts = {
        'analyze': 'Analyze the JavaScript/TypeScript source code, identify frameworks (React, Vue, Angular, Express, Next.js), state management, and architectural patterns.',
        'plan': 'Create a migration plan to convert from the source framework to {framework}, including component structure, state management migration, and build tool configuration.',
        'migrate': 'Convert the following code to {framework}, maintaining functionality while following modern JavaScript/TypeScript best practices and {framework} conventions.',
        'validate': 'Validate the migrated code for correctness, performance, accessibility, and adherence to {framework} best practices. Check for proper typing if using TypeScript.',
        'fix': 'Fix issues in the migrated code and ensure it follows {framework} best practices, proper component lifecycle, and modern JavaScript patterns.',
        'discuss': 'Discuss the migration approach to {framework}, state management options, SSR vs CSR considerations, and bundling optimization strategies.'
    }
    
    js_target = targets_service.create_target(
        name='JavaScript',
        description='JavaScript/TypeScript frameworks including React, Vue, Angular, Node.js, Express, Next.js',
        prompts=js_prompts
    )
    
    if js_target:
        print("✓ Created JavaScript target")
    
    # C#/.NET target
    csharp_prompts = {
        'analyze': 'Analyze the C#/.NET source code architecture, identify frameworks (ASP.NET Core, Blazor, WPF, MAUI), design patterns, NuGet packages, and solution structure.',
        'plan': 'Create a detailed migration plan to convert from the source framework to C#/.NET {framework}, including package migration, dependency injection setup, and testing approach.',
        'migrate': 'Convert the following code from the source framework to C#/.NET {framework}, maintaining functionality while following C# best practices and {framework} conventions.',
        'validate': 'Validate the migrated C# code for correctness, performance, async/await patterns, and adherence to .NET conventions. Check for proper null handling and LINQ optimizations.',
        'fix': 'Fix the identified issues in the migrated C# code and ensure it follows .NET best practices, async patterns, proper exception handling, and SOLID principles.',
        'discuss': 'Discuss the migration approach to C#/.NET {framework}, microservices vs monolith considerations, Azure integration options, and performance optimization strategies.'
    }
    
    csharp_target = targets_service.create_target(
        name='C#/.NET',
        description='C#/.NET frameworks including ASP.NET Core, Blazor, WPF, MAUI, Entity Framework, SignalR',
        prompts=csharp_prompts
    )
    
    if csharp_target:
        print("✓ Created C#/.NET target")
    
    # Ruby target
    ruby_prompts = {
        'analyze': 'Analyze the Ruby source code architecture, identify frameworks (Rails, Sinatra, Hanami), gems, database patterns, and project structure.',
        'plan': 'Create a detailed migration plan to convert from the source framework to Ruby {framework}, including gem migration, database setup, and testing framework selection.',
        'migrate': 'Convert the following code from the source framework to Ruby {framework}, maintaining functionality while following Ruby conventions and {framework} patterns.',
        'validate': 'Validate the migrated Ruby code for correctness, performance, proper use of blocks/procs, and adherence to Ruby style guide. Check for N+1 queries and security issues.',
        'fix': 'Fix the identified issues in the migrated Ruby code and ensure it follows Ruby best practices, proper metaprogramming patterns, and idiomatic Ruby conventions.',
        'discuss': 'Discuss the migration approach to Ruby {framework}, API vs full-stack considerations, background job processing options, and caching strategies.'
    }
    
    ruby_target = targets_service.create_target(
        name='Ruby',
        description='Ruby frameworks including Ruby on Rails, Sinatra, Hanami, Roda, Grape API',
        prompts=ruby_prompts
    )
    
    if ruby_target:
        print("✓ Created Ruby target")
    
    # PHP target
    php_prompts = {
        'analyze': 'Analyze the PHP source code architecture, identify frameworks (Laravel, Symfony, Slim, CodeIgniter), Composer packages, and application structure.',
        'plan': 'Create a detailed migration plan to convert from the source framework to PHP {framework}, including package migration, database abstraction, and PSR standards adoption.',
        'migrate': 'Convert the following code from the source framework to PHP {framework}, maintaining functionality while following PSR standards and {framework} conventions.',
        'validate': 'Validate the migrated PHP code for correctness, performance, security vulnerabilities, and adherence to PSR standards. Check for SQL injection and XSS issues.',
        'fix': 'Fix the identified issues in the migrated PHP code and ensure it follows PHP best practices, proper type declarations, and modern PHP patterns.',
        'discuss': 'Discuss the migration approach to PHP {framework}, traditional vs API-first architecture, caching strategies, and deployment considerations.'
    }
    
    php_target = targets_service.create_target(
        name='PHP',
        description='PHP frameworks including Laravel, Symfony, Slim, CodeIgniter, Laminas, Phalcon',
        prompts=php_prompts
    )
    
    if php_target:
        print("✓ Created PHP target")
    
    # Go target
    go_prompts = {
        'analyze': 'Analyze the Go source code architecture, identify frameworks (Gin, Echo, Fiber, Beego), package structure, and concurrency patterns.',
        'plan': 'Create a detailed migration plan to convert from the source framework to Go {framework}, including module setup, dependency management, and goroutine design.',
        'migrate': 'Convert the following code from the source framework to Go {framework}, maintaining functionality while following Go idioms and {framework} patterns.',
        'validate': 'Validate the migrated Go code for correctness, performance, proper error handling, and goroutine safety. Check for race conditions and channel usage.',
        'fix': 'Fix the identified issues in the migrated Go code and ensure it follows Go best practices, proper context usage, and idiomatic Go patterns.',
        'discuss': 'Discuss the migration approach to Go {framework}, microservices architecture, gRPC vs REST, and deployment strategies for Go applications.'
    }
    
    go_target = targets_service.create_target(
        name='Go',
        description='Go frameworks including Gin, Echo, Fiber, Beego, Chi, and standard library net/http',
        prompts=go_prompts
    )
    
    if go_target:
        print("✓ Created Go target")
    
    # Rust target
    rust_prompts = {
        'analyze': 'Analyze the Rust source code architecture, identify frameworks (Actix-web, Rocket, Axum, Warp), crate dependencies, and ownership patterns.',
        'plan': 'Create a detailed migration plan to convert from the source framework to Rust {framework}, including memory safety considerations, async runtime selection, and error handling strategy.',
        'migrate': 'Convert the following code from the source framework to Rust {framework}, ensuring memory safety while following Rust patterns and {framework} conventions.',
        'validate': 'Validate the migrated Rust code for correctness, memory safety, performance, and adherence to Rust idioms. Check for proper lifetime usage and error handling.',
        'fix': 'Fix the identified issues in the migrated Rust code and ensure it follows Rust best practices, proper trait usage, and idiomatic error handling patterns.',
        'discuss': 'Discuss the migration approach to Rust {framework}, async vs sync runtime considerations, zero-cost abstractions, and FFI integration strategies.'
    }
    
    rust_target = targets_service.create_target(
        name='Rust',
        description='Rust frameworks including Actix-web, Rocket, Axum, Warp, Tide, and async ecosystem',
        prompts=rust_prompts
    )
    
    if rust_target:
        print("✓ Created Rust target")
    
    print("\nInitialization complete!")

if __name__ == '__main__':
    init_targets()