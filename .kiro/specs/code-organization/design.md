# Design Document: Code Organization Refactoring

## Overview

This design document outlines the refactoring of the Events API backend to achieve clean separation of concerns through a layered architecture. The refactoring will organize code into domain-specific modules (events, users, registrations) with clear boundaries between API handlers, business logic services, and data access repositories. The design ensures all existing functionality remains intact while improving maintainability, testability, and code clarity.

## Architecture

### Layered Architecture

The application will follow a three-tier layered architecture:

```
┌─────────────────────────────────────┐
│     API Layer (Handlers)            │
│  - Request validation               │
│  - Response formatting              │
│  - HTTP concerns                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Service Layer (Business Logic)  │
│  - Domain rules                     │
│  - Workflow orchestration           │
│  - Cross-domain coordination        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Repository Layer (Data Access)  │
│  - Database operations              │
│  - Query construction               │
│  - Data persistence                 │
└─────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── main.py                      # FastAPI app setup and configuration
├── config.py                    # Configuration and dependency injection
├── common/
│   ├── __init__.py
│   ├── exceptions.py            # Shared exception classes
│   └── types.py                 # Shared type definitions
├── events/
│   ├── __init__.py
│   ├── models.py                # Event data models
│   ├── repository.py            # Event repository
│   ├── service.py               # Event business logic
│   └── handlers.py              # Event API endpoints
├── users/
│   ├── __init__.py
│   ├── models.py                # User data models
│   ├── repository.py            # User repository
│   ├── service.py               # User business logic
│   └── handlers.py              # User API endpoints
└── registrations/
    ├── __init__.py
    ├── models.py                # Registration data models
    ├── repository.py            # Registration repository
    ├── service.py               # Registration business logic
    └── handlers.py              # Registration API endpoints
```

## Components and Interfaces

### Common Module

#### Exceptions (`common/exceptions.py`)

```python
class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class DuplicateError(Exception):
    """Raised when attempting to create duplicate resource"""
    pass

class NotFoundError(Exception):
    """Raised when resource not found"""
    pass

class CapacityError(Exception):
    """Raised when event is at capacity"""
    pass
```

### Events Domain

#### Event Models (`events/models.py`)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Event(BaseModel):
    eventId: Optional[str] = None
    title: str
    description: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: str
    waitlistEnabled: Optional[bool] = False
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    organizer: Optional[str] = None
    status: Optional[str] = None
    waitlistEnabled: Optional[bool] = None
```

#### Event Repository (`events/repository.py`)

```python
class EventRepository:
    def __init__(self, table):
        self.table = table
    
    def create(self, event_data: dict) -> dict
    def find_by_id(self, event_id: str) -> Optional[dict]
    def find_all(self, status_filter: Optional[str] = None) -> List[dict]
    def update(self, event_id: str, update_data: dict) -> dict
    def delete(self, event_id: str) -> None
    def exists(self, event_id: str) -> bool
```

#### Event Service (`events/service.py`)

```python
class EventService:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo
    
    def create_event(self, event: Event) -> dict
    def get_event(self, event_id: str) -> dict
    def list_events(self, status: Optional[str] = None) -> List[dict]
    def update_event(self, event_id: str, event_update: EventUpdate) -> dict
    def delete_event(self, event_id: str) -> None
```

#### Event Handlers (`events/handlers.py`)

```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event: Event, service: EventService = Depends(get_event_service))

@router.get("/")
async def list_events(status: Optional[str] = None, service: EventService = Depends(get_event_service))

@router.get("/{event_id}")
async def get_event(event_id: str, service: EventService = Depends(get_event_service))

@router.put("/{event_id}")
async def update_event(event_id: str, event_update: EventUpdate, service: EventService = Depends(get_event_service))

@router.delete("/{event_id}")
async def delete_event(event_id: str, service: EventService = Depends(get_event_service))
```

### Users Domain

#### User Models (`users/models.py`)

```python
from pydantic import BaseModel, Field
from dataclasses import dataclass

class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)

@dataclass
class User:
    user_id: str
    name: str
```

#### User Repository (`users/repository.py`)

```python
class UserRepository:
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    def save(self, user: User) -> None
    def find_by_id(self, user_id: str) -> Optional[User]
    def exists(self, user_id: str) -> bool
```

#### User Service (`users/service.py`)

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_id: str, name: str) -> User
    def get_user(self, user_id: str) -> Optional[User]
```

#### User Handlers (`users/handlers.py`)

```python
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service))

@router.get("/{user_id}")
async def get_user(user_id: str, service: UserService = Depends(get_user_service))
```

### Registrations Domain

#### Registration Models (`registrations/models.py`)

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class RegistrationStatus(Enum):
    ACTIVE = "active"
    WAITLISTED = "waitlisted"

class RegistrationRequest(BaseModel):
    userId: str = Field(..., min_length=1)

@dataclass
class Registration:
    registration_id: str
    user_id: str
    event_id: str
    status: RegistrationStatus
    waitlist_position: Optional[int] = None
```

#### Registration Repository (`registrations/repository.py`)

```python
class RegistrationRepository:
    def __init__(self):
        self._registrations: Dict[str, Registration] = {}
    
    def save(self, registration: Registration) -> None
    def delete(self, user_id: str, event_id: str) -> None
    def find_by_user_and_event(self, user_id: str, event_id: str) -> Optional[Registration]
    def find_by_user(self, user_id: str) -> List[Registration]
    def find_by_event(self, event_id: str) -> List[Registration]
    def count_active_by_event(self, event_id: str) -> int
    def get_waitlist(self, event_id: str) -> List[Registration]
```

#### Registration Service (`registrations/service.py`)

```python
class RegistrationService:
    def __init__(
        self,
        registration_repo: RegistrationRepository,
        user_service: UserService,
        event_service: EventService
    ):
        self.registration_repo = registration_repo
        self.user_service = user_service
        self.event_service = event_service
    
    def register_user(self, user_id: str, event_id: str) -> Registration
    def unregister_user(self, user_id: str, event_id: str) -> None
    def get_user_registrations(self, user_id: str) -> List[dict]
    def get_event_registrations(self, event_id: str) -> List[dict]
```

#### Registration Handlers (`registrations/handlers.py`)

```python
router = APIRouter(tags=["registrations"])

@router.post("/events/{event_id}/registrations", status_code=status.HTTP_201_CREATED)
async def register_for_event(event_id: str, request: RegistrationRequest, service: RegistrationService = Depends(get_registration_service))

@router.get("/events/{event_id}/registrations")
async def get_event_registrations(event_id: str, service: RegistrationService = Depends(get_registration_service))

@router.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_from_event(event_id: str, user_id: str, service: RegistrationService = Depends(get_registration_service))

@router.get("/users/{user_id}/registrations")
async def get_user_registrations(user_id: str, service: RegistrationService = Depends(get_registration_service))
```

### Configuration Module

#### Dependency Injection (`config.py`)

```python
import os
import boto3
from functools import lru_cache

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('EVENTS_TABLE_NAME', 'Events')
events_table = dynamodb.Table(table_name)

# Repository instances
_user_repo = None
_registration_repo = None
_event_repo = None

def get_user_repository() -> UserRepository:
    global _user_repo
    if _user_repo is None:
        _user_repo = UserRepository()
    return _user_repo

def get_registration_repository() -> RegistrationRepository:
    global _registration_repo
    if _registration_repo is None:
        _registration_repo = RegistrationRepository()
    return _registration_repo

def get_event_repository() -> EventRepository:
    global _event_repo
    if _event_repo is None:
        _event_repo = EventRepository(events_table)
    return _event_repo

# Service instances
def get_user_service() -> UserService:
    return UserService(get_user_repository())

def get_event_service() -> EventService:
    return EventService(get_event_repository())

def get_registration_service() -> RegistrationService:
    return RegistrationService(
        get_registration_repository(),
        get_user_service(),
        get_event_service()
    )
```

### Main Application (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from events.handlers import router as events_router
from users.handlers import router as users_router
from registrations.handlers import router as registrations_router

app = FastAPI(title="Events API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(events_router)
app.include_router(users_router)
app.include_router(registrations_router)

@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app)
```

## Data Models

### Event Data Model

- **eventId**: Unique identifier (UUID)
- **title**: Event title (1-200 characters)
- **description**: Event description (1-2000 characters)
- **date**: ISO format date string
- **location**: Event location (1-500 characters)
- **capacity**: Maximum attendees (positive integer)
- **organizer**: Organizer name (1-200 characters)
- **status**: Event status (active, scheduled, ongoing, completed, cancelled)
- **waitlistEnabled**: Boolean flag for waitlist feature
- **createdAt**: ISO timestamp of creation
- **updatedAt**: ISO timestamp of last update

### User Data Model

- **user_id**: Unique user identifier (string)
- **name**: User's name (string)

### Registration Data Model

- **registration_id**: Unique registration identifier (UUID)
- **user_id**: Reference to user
- **event_id**: Reference to event
- **status**: Registration status (ACTIVE or WAITLISTED)
- **waitlist_position**: Position in waitlist (optional, only for WAITLISTED status)


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, most requirements for this refactoring are structural (about code organization) rather than functional. However, we have identified critical functional properties that must be preserved during refactoring:

### Property 1: API Endpoint Behavioral Equivalence

*For any* existing API endpoint and valid request, the refactored system should produce identical responses (status codes, response bodies, headers) as the original system.

**Validates: Requirements 4.1**

### Property 2: Request/Response Schema Compatibility

*For any* existing API endpoint, all previously valid request formats should remain valid, and all response formats should maintain the same structure and field types.

**Validates: Requirements 4.2**

### Property 3: Error Response Consistency

*For any* error scenario (invalid input, not found, conflict, capacity exceeded), the refactored system should return the same HTTP status codes and error message formats as the original system.

**Validates: Requirements 4.4**

### Property 4: Registration Workflow Preservation

*For any* sequence of registration operations (register, unregister, waitlist promotion), the refactored system should maintain identical business logic including capacity checks, waitlist ordering, and status transitions.

**Validates: Requirements 4.5**

### Property 5: Event Capacity Logic Preservation

*For any* event with defined capacity and registration attempts, the refactored system should enforce capacity limits and waitlist behavior identically to the original system.

**Validates: Requirements 4.5**

## Error Handling

### Error Translation Pattern

Each layer will handle errors appropriately:

1. **Repository Layer**: Raises storage-specific exceptions (ClientError from boto3)
2. **Service Layer**: Catches storage exceptions and translates to domain exceptions (ValidationError, NotFoundError, etc.)
3. **Handler Layer**: Catches domain exceptions and translates to HTTP responses with appropriate status codes

### Exception Mapping

```python
# In handlers
try:
    result = service.operation()
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except NotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except DuplicateError as e:
    raise HTTPException(status_code=409, detail=str(e))
except CapacityError as e:
    raise HTTPException(status_code=409, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

### Error Consistency

All error responses will maintain the FastAPI standard format:
```json
{
  "detail": "Error message"
}
```

## Testing Strategy

### Dual Testing Approach

This refactoring will use both unit testing and property-based testing to ensure correctness:

#### Unit Testing

Unit tests will verify:
- Individual repository methods correctly interact with storage
- Service methods correctly implement business rules
- Handler functions correctly format responses
- Error translation works at each layer boundary
- Dependency injection provides correct instances

Example unit tests:
- Test that `EventRepository.create()` correctly calls DynamoDB `put_item`
- Test that `UserService.create_user()` validates inputs and checks for duplicates
- Test that registration handlers return correct status codes

#### Property-Based Testing

Property-based tests will verify the correctness properties defined above. We will use **Hypothesis** as the property-based testing library for Python.

**Configuration**: Each property-based test will run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Tagging**: Each property-based test will include a comment explicitly referencing the correctness property from this design document using the format: `# Feature: code-organization, Property {number}: {property_text}`

Property tests will:
1. **API Endpoint Behavioral Equivalence**: Generate various valid requests for each endpoint and verify responses match between original and refactored code
2. **Request/Response Schema Compatibility**: Generate edge cases for request validation and verify schema compatibility
3. **Error Response Consistency**: Generate invalid inputs and verify error responses match
4. **Registration Workflow Preservation**: Generate sequences of registration operations and verify business logic consistency
5. **Event Capacity Logic Preservation**: Generate events with various capacities and registration attempts to verify capacity enforcement

### Integration Testing

Integration tests will verify:
- End-to-end flows through all layers
- Cross-domain operations (e.g., registration service using user and event services)
- Complete request/response cycles

### Regression Testing

The existing test suite (`backend/test_api.py`) will serve as regression tests. All existing tests must pass without modification after refactoring.

## Migration Strategy

### Phase 1: Create New Structure
1. Create domain directories (events, users, registrations, common)
2. Create empty module files with proper `__init__.py` files

### Phase 2: Extract Models
1. Move Event models to `events/models.py`
2. Move User models to `users/models.py`
3. Move Registration models to `registrations/models.py`
4. Create `common/exceptions.py` with shared exceptions

### Phase 3: Create Repositories
1. Implement `EventRepository` with DynamoDB operations
2. Keep existing `UserRepository` and move to `users/repository.py`
3. Keep existing `RegistrationRepository` and move to `registrations/repository.py`

### Phase 4: Create Services
1. Implement `EventService` with business logic extracted from handlers
2. Move existing `UserService` to `users/service.py`
3. Move existing `RegistrationService` to `registrations/service.py` and update to use other services

### Phase 5: Create Handlers
1. Create `events/handlers.py` with FastAPI router
2. Create `users/handlers.py` with FastAPI router
3. Create `registrations/handlers.py` with FastAPI router

### Phase 6: Create Configuration
1. Implement `config.py` with dependency injection functions
2. Set up singleton instances for repositories and services

### Phase 7: Update Main Application
1. Simplify `main.py` to only include app setup and router registration
2. Remove all business logic and data access code
3. Import and register domain routers

### Phase 8: Testing and Validation
1. Run existing test suite to verify no regressions
2. Add property-based tests for correctness properties
3. Verify all endpoints work identically

### Phase 9: Cleanup
1. Remove old code from `main.py`
2. Remove old `models.py`, `services.py`, `repositories.py` files
3. Update imports throughout codebase

## Dependency Flow

```
main.py
  ↓
config.py (dependency injection)
  ↓
handlers (events, users, registrations)
  ↓
services (events, users, registrations)
  ↓
repositories (events, users, registrations)
  ↓
models + storage clients (DynamoDB, in-memory)
```

**Key Principles:**
- Handlers depend only on services (via dependency injection)
- Services depend only on repositories and other services
- Repositories depend only on models and storage clients
- No circular dependencies
- No upward dependencies (lower layers don't know about upper layers)

## Benefits of This Design

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Testability**: Each component can be tested in isolation with mocks
3. **Maintainability**: Changes to one layer don't cascade to others
4. **Discoverability**: Clear directory structure makes code easy to find
5. **Scalability**: New domains can be added following the same pattern
6. **Flexibility**: Storage implementations can be swapped without affecting business logic
7. **Type Safety**: Strong typing throughout with Pydantic models and type hints
