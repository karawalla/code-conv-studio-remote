# Validate - Rust Code Quality

## Objective
Validate the migrated Rust code for correctness, safety, performance, and adherence to Rust best practices.

## Context
- Migrated code from {{source_name}} to Rust
- Ensure the code is production-ready
- Verify Rust idioms and patterns are properly applied

## Validation Instructions

### 1. Compilation and Safety Checks

#### Compiler Warnings
```bash
# Build with all warnings
cargo build --all-features
cargo build --release

# Check for any warnings
cargo check --all-targets

# Ensure no unsafe code without justification
grep -r "unsafe" src/ --include="*.rs"
```

#### Clippy Lints
```bash
# Run clippy with pedantic lints
cargo clippy -- -W clippy::all -W clippy::pedantic

# Common issues to check:
# - unnecessary_cast
# - redundant_clone  
# - inefficient_to_string
# - needless_borrow
# - unused_async
```

### 2. Memory Safety Validation

#### Ownership Patterns
- Verify no unnecessary Rc/Arc usage
- Check for proper lifetime annotations
- Ensure no memory leaks with cyclic references
- Validate drop implementations

#### Borrowing Rules
```rust
// Check for these anti-patterns:

// ❌ Unnecessary cloning
let data = expensive_data.clone(); // Should borrow instead

// ✅ Proper borrowing
let data = &expensive_data;

// ❌ Multiple mutable borrows
let mut1 = &mut data;
let mut2 = &mut data; // Compiler error

// ✅ Scoped borrows
{
    let mut1 = &mut data;
    // use mut1
} // mut1 dropped
let mut2 = &mut data; // OK
```

### 3. Error Handling Validation

#### Result Usage
- All fallible operations return Result
- No unwrap() in production code (except with justification)
- Proper error propagation with ?
- Meaningful error messages with context

```rust
// ❌ Bad error handling
let value = some_operation().unwrap();

// ✅ Good error handling  
let value = some_operation()
    .context("Failed to perform operation")?;

// ✅ With custom error
let value = some_operation()
    .map_err(|e| AppError::OperationFailed(e.to_string()))?;
```

### 4. Performance Validation

#### Benchmarks
```rust
#[bench]
fn bench_critical_function(b: &mut Bencher) {
    b.iter(|| {
        critical_function(test::black_box(input))
    });
}

// Run benchmarks
cargo bench

// Compare with baseline
cargo bench -- --baseline master
```

#### Common Performance Issues
- Unnecessary allocations in hot paths
- Missing #[inline] for small functions
- Inefficient string operations
- Suboptimal collection usage
- Missing const/static where applicable

### 5. Concurrency Validation

#### Thread Safety
```rust
// Verify Send + Sync implementations
fn is_send<T: Send>() {}
fn is_sync<T: Sync>() {}

// Test your types
is_send::<YourType>();
is_sync::<YourSharedType>();
```

#### Data Race Detection
```bash
# Run tests with thread sanitizer
RUSTFLAGS="-Z sanitizer=thread" cargo test --target x86_64-unknown-linux-gnu

# Use loom for concurrency testing
#[cfg(loom)]
#[test]
fn test_concurrent_access() {
    loom::model(|| {
        // Test concurrent scenarios
    });
}
```

### 6. API Design Validation

#### Rust API Guidelines
- Types implement common traits (Debug, Clone where appropriate)
- Functions follow naming conventions
- Modules have clear organization
- Public API is properly documented
- Examples provided for complex APIs

```rust
// Check trait implementations
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct User { /* ... */ }

// Builder pattern for complex types
#[derive(Default)]
pub struct UserBuilder { /* ... */ }

// Iterators over collections
impl IntoIterator for Users { /* ... */ }
```

### 7. Testing Coverage

#### Test Categories
```bash
# Unit tests
cargo test --lib

# Integration tests  
cargo test --test '*'

# Doc tests
cargo test --doc

# Coverage report
cargo tarpaulin --out Html

# Property-based tests with proptest
#[cfg(test)]
mod proptests {
    use proptest::prelude::*;
    
    proptest! {
        #[test]
        fn test_parse_never_panics(s: String) {
            let _ = parse_input(&s); // Should not panic
        }
    }
}
```

### 8. Documentation Validation

```rust
// Check for missing docs
#![warn(missing_docs)]

// Verify examples compile
/// # Example
/// ```
/// use my_crate::User;
/// 
/// let user = User::new("Alice");
/// assert_eq!(user.name(), "Alice");
/// ```
pub struct User { /* ... */ }

// Run doc tests
cargo test --doc
```

### 9. Security Audit

```bash
# Check for known vulnerabilities
cargo audit

# Review dependencies
cargo tree --duplicate

# Check for outdated dependencies
cargo outdated
```

## Validation Checklist

### Compilation
- [ ] No compiler warnings
- [ ] No clippy warnings (or justified)
- [ ] Builds on all target platforms
- [ ] Release build optimizations enabled

### Safety
- [ ] No unsafe without safety comments
- [ ] No data races possible
- [ ] Proper Send/Sync implementations
- [ ] Memory usage is bounded

### Performance  
- [ ] Benchmarks meet requirements
- [ ] No performance regressions
- [ ] Efficient memory usage
- [ ] Optimized for target architecture

### Quality
- [ ] >80% test coverage
- [ ] All public APIs documented
- [ ] Examples provided
- [ ] Error messages are helpful

### Security
- [ ] No known vulnerabilities
- [ ] Dependencies are minimal
- [ ] Input validation is comprehensive
- [ ] No hardcoded secrets

## Output Format
Provide:
1. Validation report with all check results
2. Performance benchmark comparison
3. Code coverage report
4. List of issues found with severity
5. Recommendations for improvements