# Analyze - Rust Target

## Objective
Analyze the source code to understand its architecture, patterns, and prepare for migration to Rust.

## Context
- Source: {{source_name}} ({{source_type}})
- Target: Rust
- Focus on identifying patterns that will need special attention during migration

## Analysis Instructions

### 1. Architecture Assessment
- Identify the application type (web service, CLI tool, library, etc.)
- Map the overall architecture pattern (MVC, microservices, event-driven, etc.)
- Document the entry points and main execution flow
- Identify concurrent/parallel processing patterns

### 2. Dependencies Analysis
- List all external dependencies and their Rust equivalents:
  - Web frameworks → Actix-web, Rocket, Axum, Warp
  - Database ORMs → Diesel, SQLx, SeaORM
  - HTTP clients → reqwest, hyper
  - Serialization → serde, bincode
  - Async runtime → tokio, async-std

### 3. Memory Management Patterns
- Identify shared state and mutability patterns
- Document object lifecycle and ownership flows
- Find potential borrowing/lifetime challenges
- Identify reference counting or garbage collection dependencies

### 4. Error Handling Patterns
- Document current error handling approach
- Identify exception types → Result<T, E> mapping
- Find error propagation patterns
- Document recovery and fallback mechanisms

### 5. Type System Mapping
- Dynamic typing patterns that need static alternatives
- Null/None handling → Option<T> patterns
- Union types → Rust enums
- Inheritance hierarchies → trait-based design

### 6. Concurrency Patterns
- Thread usage → Rust threading model
- Async/await patterns → tokio/async-std
- Shared mutable state → Arc<Mutex<T>> patterns
- Message passing patterns → channels

### 7. Performance Considerations
- Identify performance-critical paths
- Memory allocation patterns
- I/O bound vs CPU bound operations
- Caching strategies

## Output Format
Provide a detailed analysis report with:
1. Architecture overview diagram (ASCII/text)
2. Dependency mapping table
3. Key migration challenges
4. Rust-specific opportunities (zero-cost abstractions, memory safety)
5. Risk assessment for complex patterns