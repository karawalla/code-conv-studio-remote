# Migrate - Rust Implementation

## Objective
Convert the source code from {{source_name}} to idiomatic Rust, maintaining functionality while leveraging Rust's safety and performance features.

## Context
- Follow the migration plan created in previous step
- Implement Rust best practices and idioms
- Ensure memory safety without garbage collection

## Migration Instructions

### 1. Type System Migration

#### Primitive Types
```rust
// Source → Rust mapping examples
// int/Integer → i32, i64, usize
// float/double → f32, f64  
// string → String (owned) or &str (borrowed)
// boolean → bool
// null/nil → Option<T>
// array → Vec<T> or [T; N]
// map/dict → HashMap<K, V> or BTreeMap<K, V>
```

#### Custom Types
- Classes → Structs with impl blocks
- Interfaces → Traits
- Enums → Rust enums (more powerful)
- Generics → Rust generics with trait bounds

### 2. Memory Management Patterns

#### Ownership Rules
```rust
// Single owner pattern
struct User {
    name: String,
    email: String,
}

// Borrowing for read access
fn print_user(user: &User) {
    println!("{}: {}", user.name, user.email);
}

// Mutable borrowing for modifications
fn update_email(user: &mut User, new_email: String) {
    user.email = new_email;
}

// Transfer ownership
fn consume_user(user: User) -> String {
    format!("Processed: {}", user.name)
}
```

#### Shared Ownership
```rust
use std::sync::{Arc, Mutex};
use std::rc::Rc;

// Single-threaded shared ownership
let shared_data = Rc::new(data);

// Multi-threaded shared ownership
let thread_safe_data = Arc::new(Mutex::new(data));
```

### 3. Error Handling

#### Result Type Pattern
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    
    #[error("Validation error: {0}")]
    Validation(String),
    
    #[error("Not found: {0}")]
    NotFound(String),
}

// Function returning Result
pub async fn get_user(id: i64) -> Result<User, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_one(&pool)
        .await?;
    
    Ok(user)
}

// Error propagation with ?
pub async fn process_user(id: i64) -> Result<String, AppError> {
    let user = get_user(id).await?;
    let result = validate_user(&user)?;
    Ok(format!("Processed: {}", user.name))
}
```

### 4. Async/Await Patterns

#### Async Functions
```rust
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Concurrent execution
    let (result1, result2) = tokio::join!(
        fetch_data_1(),
        fetch_data_2()
    );
    
    // Sequential async
    let data = fetch_data().await?;
    process_data(data).await?;
    
    Ok(())
}

// Async trait implementation
#[async_trait]
impl DataService for MyService {
    async fn get_data(&self, id: u64) -> Result<Data, Error> {
        // Implementation
    }
}
```

### 5. Web Framework Patterns

#### Actix-web Example
```rust
use actix_web::{web, App, HttpResponse, HttpServer, Result};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct CreateUserRequest {
    name: String,
    email: String,
}

async fn create_user(
    data: web::Json<CreateUserRequest>,
    pool: web::Data<PgPool>,
) -> Result<HttpResponse> {
    let user = User::create(&pool, &data.name, &data.email)
        .await
        .map_err(ErrorInternalServerError)?;
    
    Ok(HttpResponse::Created().json(&user))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let pool = create_pool().await;
    
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .route("/users", web::post().to(create_user))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

### 6. Database Integration

#### SQLx Example
```rust
use sqlx::{PgPool, FromRow};

#[derive(FromRow, Serialize)]
struct User {
    id: i64,
    name: String,
    email: String,
    created_at: chrono::DateTime<chrono::Utc>,
}

impl User {
    pub async fn find_by_id(pool: &PgPool, id: i64) -> Result<Self, sqlx::Error> {
        sqlx::query_as!(
            User,
            r#"SELECT id, name, email, created_at FROM users WHERE id = $1"#,
            id
        )
        .fetch_one(pool)
        .await
    }
    
    pub async fn create(
        pool: &PgPool,
        name: &str,
        email: &str,
    ) -> Result<Self, sqlx::Error> {
        sqlx::query_as!(
            User,
            r#"
            INSERT INTO users (name, email, created_at)
            VALUES ($1, $2, NOW())
            RETURNING id, name, email, created_at
            "#,
            name,
            email
        )
        .fetch_one(pool)
        .await
    }
}
```

### 7. Testing Patterns

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_user_creation() {
        let user = User::new("Test", "test@example.com");
        assert_eq!(user.name, "Test");
    }
    
    #[tokio::test]
    async fn test_async_operation() {
        let result = async_function().await;
        assert!(result.is_ok());
    }
    
    #[test]
    fn test_error_handling() {
        let result = risky_operation();
        assert!(matches!(result, Err(AppError::Validation(_))));
    }
}
```

## Migration Checklist
- [ ] All unsafe operations are properly justified and documented
- [ ] No unnecessary cloning or allocations
- [ ] Proper error handling with Result<T, E>
- [ ] Lifetimes are correctly specified where needed
- [ ] Concurrent access is properly synchronized
- [ ] All tests pass including property-based tests
- [ ] Documentation is complete with examples
- [ ] Clippy warnings are addressed
- [ ] Code is formatted with rustfmt

## Output Format
Provide:
1. Migrated Rust code with inline comments explaining key decisions
2. Mapping document showing source → Rust conversions
3. Performance comparison metrics
4. List of any functional differences or improvements