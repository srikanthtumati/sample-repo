# Design Document: User Registration System

## Overview

The User Registration System is a backend service that manages users, events, and registrations with capacity constraints and waitlist functionality. The system provides APIs for creating users and events, handling registration requests with automatic capacity checking, managing waitlists when events are full, and allowing users to view their registered events.

The design emphasizes data integrity, clear separation of concerns, and robust validation to ensure correct handling of capacity constraints and waitlist operations.

## Architecture

The system follows a layered architecture with clear separation between data models, business logic, and API interfaces:

```
┌─────────────────────────────────────┐
│         API Layer (REST)            │
│  - User endpoints                   │
│  - Event endpoints                  │
│  - Registration endpoints           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Service Layer                 │
│  - UserService                      │
│  - EventService                     │
│  - RegistrationService              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Repository Layer              │
│  - UserRepository                   │
│  - EventRepository                  │
│  - RegistrationRepository           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Data Storage                  │
│  - In-memory storage (initial)      │
│  - Extensible to database           │
└─────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Repository Pattern**: Abstracts data access to enable easy switching between storage implementations
2. **Service Layer**: Encapsulates business logic including capacity validation and waitlist management
3. **Immutable Operations**: Registration operations are atomic to prevent race conditions
4. **Clear Error Handling**: Distinct error types for validation failures, capacity issues, and not-found scenarios

## Components and Interfaces

### Data Models

#### User
```python
@dataclass
class User:
    user_id: str
    name: str
```

#### Event
```python
@dataclass
class Event:
    event_id: str
    name: str
    capacity: int
    has_waitlist: bool
```

#### Registration
```python
@dataclass
class Registration:
    registration_id: str
    user_id: str
    event_id: str
    status: RegistrationStatus  # ACTIVE or WAITLISTED
    waitlist_position: Optional[int]  # Only for WAITLISTED status
```

#### RegistrationStatus
```python
class RegistrationStatus(Enum):
    ACTIVE = "active"
    WAITLISTED = "waitlisted"
```

### Service Interfaces

#### UserService
```python
class UserService:
    def create_user(self, user_id: str, name: str) -> User:
        """Creates a new user with validation"""
        
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieves a user by ID"""
```

#### EventService
```python
class EventService:
    def create_event(self, event_id: str, name: str, capacity: int, 
                     has_waitlist: bool) -> Event:
        """Creates a new event with capacity and waitlist configuration"""
        
    def get_event(self, event_id: str) -> Optional[Event]:
        """Retrieves an event by ID"""
```

#### RegistrationService
```python
class RegistrationService:
    def register_user(self, user_id: str, event_id: str) -> Registration:
        """
        Registers a user for an event.
        Returns ACTIVE registration if capacity available.
        Returns WAITLISTED registration if full and waitlist enabled.
        Raises error if full and no waitlist.
        """
        
    def unregister_user(self, user_id: str, event_id: str) -> None:
        """
        Unregisters a user from an event.
        Promotes first waitlisted user if applicable.
        """
        
    def get_user_registrations(self, user_id: str) -> List[Event]:
        """Returns all events where user has ACTIVE registration"""
        
    def get_event_registrations(self, event_id: str) -> List[Registration]:
        """Returns all registrations for an event"""
```

### Repository Interfaces

#### UserRepository
```python
class UserRepository:
    def save(self, user: User) -> None:
        """Persists a user"""
        
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Retrieves user by ID"""
        
    def exists(self, user_id: str) -> bool:
        """Checks if user exists"""
```

#### EventRepository
```python
class EventRepository:
    def save(self, event: Event) -> None:
        """Persists an event"""
        
    def find_by_id(self, event_id: str) -> Optional[Event]:
        """Retrieves event by ID"""
```

#### RegistrationRepository
```python
class RegistrationRepository:
    def save(self, registration: Registration) -> None:
        """Persists a registration"""
        
    def delete(self, user_id: str, event_id: str) -> None:
        """Removes a registration"""
        
    def find_by_user_and_event(self, user_id: str, event_id: str) -> Optional[Registration]:
        """Finds specific registration"""
        
    def find_by_user(self, user_id: str) -> List[Registration]:
        """Finds all registrations for a user"""
        
    def find_by_event(self, event_id: str) -> List[Registration]:
        """Finds all registrations for an event"""
        
    def count_active_by_event(self, event_id: str) -> int:
        """Counts ACTIVE registrations for an event"""
        
    def get_waitlist(self, event_id: str) -> List[Registration]:
        """Returns waitlisted registrations ordered by position"""
```

## Data Models

### User Model
- **user_id**: Unique string identifier (primary key)
- **name**: String representing the user's name

**Validation Rules:**
- user_id must be non-empty and unique
- name must be non-empty

### Event Model
- **event_id**: Unique string identifier (primary key)
- **name**: String representing the event name
- **capacity**: Positive integer representing maximum active registrations
- **has_waitlist**: Boolean indicating if waitlist is enabled

**Validation Rules:**
- event_id must be non-empty and unique
- capacity must be a positive integer (> 0)
- has_waitlist is a boolean flag

### Registration Model
- **registration_id**: Unique string identifier (primary key)
- **user_id**: Foreign key to User
- **event_id**: Foreign key to Event
- **status**: Enum (ACTIVE or WAITLISTED)
- **waitlist_position**: Optional integer (only for WAITLISTED status)

**Validation Rules:**
- user_id and event_id must reference existing entities
- A user can only have one registration per event
- waitlist_position must be set for WAITLISTED status and null for ACTIVE status
- waitlist_position must be positive and sequential

### Business Logic Rules

#### Registration Logic
1. Check if user and event exist
2. Check if user already has a registration for this event
3. Count active registrations for the event
4. If count < capacity: Create ACTIVE registration
5. If count >= capacity and has_waitlist: Create WAITLISTED registration with next position
6. If count >= capacity and !has_waitlist: Reject with error

#### Unregistration Logic
1. Find user's registration for the event
2. If not found: Return error
3. Delete the registration
4. If registration was ACTIVE and waitlist has entries:
   - Get first waitlisted user
   - Promote to ACTIVE status
   - Reorder remaining waitlist positions

#### Waitlist Promotion
When an ACTIVE registration is removed:
1. Query waitlist ordered by position
2. Take first entry (position 1)
3. Update status to ACTIVE and clear waitlist_position
4. Decrement waitlist_position for all remaining entries

