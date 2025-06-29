# Analyze - Python Target

## Objective
Analyze the source code to understand its architecture and prepare for migration to Python.

## Context
- Source: {{source_name}} ({{source_type}})
- Target: Python (Django/FastAPI/Flask)
- Focus on identifying patterns and Python equivalents

## Analysis Instructions

### 1. Framework Mapping
Identify source framework and map to Python equivalent:
- Spring Boot → FastAPI/Django
- Express.js → Flask/FastAPI
- Ruby on Rails → Django
- ASP.NET → Django/FastAPI

### 2. Architecture Patterns
- MVC → Django MTV or FastAPI + Templates
- Microservices → FastAPI + Celery
- REST API → Django REST Framework or FastAPI
- GraphQL → Graphene or Strawberry

### 3. Dependencies Analysis
Map dependencies to Python packages:
- ORM → SQLAlchemy, Django ORM, Tortoise ORM
- HTTP Client → requests, httpx, aiohttp
- Testing → pytest, unittest, Django test
- Task Queue → Celery, RQ, Dramatiq
- Caching → Redis, Memcached, Django cache

### 4. Data Types Mapping
- Static types → Python type hints
- Nullable types → Optional[T]
- Collections → List, Dict, Set, Tuple
- Custom types → dataclasses, Pydantic models

### 5. Async Patterns
- Callbacks → async/await
- Promises → asyncio
- Threads → asyncio, threading, multiprocessing
- Event loops → asyncio event loop

## Output Format
Provide detailed analysis including framework recommendations and migration complexity assessment.