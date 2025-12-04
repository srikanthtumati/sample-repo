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

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User creation stores all fields correctly
*For any* valid userId and name, creating a user should result in a User record that can be retrieved with the same userId and name values.
**Validates: Requirements 1.1, 1.4, 1.5**

### Property 2: Invalid user input is rejected
*For any* user creation request with empty or whitespace-only userId or name, the system should reject the request with a validation error.
**Validates: Requirements 1.3**

### Property 3: Event creation stores capacity correctly
*For any* valid event parameters including a positive capacity value, creating an event should result in an Event record with the specified capacity constraint.
**Validates: Requirements 2.1**

### Property 4: Events with waitlist start empty
*For any* event created with waitlist enabled, querying the waitlist immediately after creation should return an empty list.
**Validates: Requirements 2.2**

### Property 5: Invalid capacity is rejected
*For any* event creation request with zero, negative, or non-integer capacity, the system should reject the request with a validation error.
**Validates: Requirements 2.4, 2.5**

### Property 6: Registration succeeds when capacity available
*For any* event with available capacity (active registrations < capacity) and any valid user, registration should create an ACTIVE registration.
**Validates: Requirements 3.1**

### Property 7: Waitlist registration when full
*For any* event at full capacity with waitlist enabled, registering a new user should create a WAITLISTED registration with the correct position.
**Validates: Requirements 3.3**

### Property 8: Unregistration removes registration
*For any* user with an active registration for an event, unregistering should result in that registration no longer existing.
**Validates: Requirements 4.1**

### Property 9: Waitlist promotion on unregistration
*For any* event with active registrations at capacity and a non-empty waitlist, when an active user unregisters, the first waitlisted user should be promoted to ACTIVE status.
**Validates: Requirements 4.2**

### Property 10: Waitlist unregistration removes entry
*For any* user with a waitlisted registration, unregistering should remove that user from the waitlist.
**Validates: Requirements 4.3**

### Property 11: Waitlist order preserved after promotion
*For any* event with multiple waitlisted users, after promoting the first user to active, the remaining users should maintain their relative order with decremented positions.
**Validates: Requirements 4.5**

### Property 12: Registration list contains only active registrations
*For any* user, the registration list should include all and only events where the user has an ACTIVE registration, excluding any waitlisted events.
**Validates: Requirements 5.1, 5.2**

### Property 13: Registration list includes event details
*For any* user with active registrations, each event in the registration list should contain complete event details (event_id, name, capacity, has_waitlist).
**Validates: Requirements 5.4**

### Property 14: Registration list order is consistent
*For any* user, calling get_user_registrations multiple times without modifications should return events in the same order.
**Validates: Requirements 5.5**

## Error Handling

The system defines specific error types for different failure scenarios:

### Error Types

1. **ValidationError**: Raised when input data fails validation rules
   - Empty or whitespace-only required fields
   - Invalid capacity values (zero, negative, non-integer)
   - Malformed identifiers

2. **DuplicateError**: Raised when attempting to create a resource that already exists
   - Duplicate userId
   - Duplicate event_id
   - Duplicate registration (user already registered for event)

3. **NotFoundError**: Raised when referencing non-existent resources
   - User not found
   - Event not found
   - Registration not found

4. **CapacityError**: Raised when registration cannot be completed due to capacity constraints
   - Event at full capacity with no waitlist

### Error Handling Strategy

- All service methods validate inputs before processing
- Repository methods assume valid inputs (validation at service layer)
- Errors include descriptive messages for debugging
- API layer translates errors to appropriate HTTP status codes:
  - ValidationError → 400 Bad Request
  - DuplicateError → 409 Conflict
  - NotFoundError → 404 Not Found
  - CapacityError → 409 Conflict

## Testing Strategy

The system will employ a dual testing approach combining unit tests and property-based tests to ensure comprehensive coverage and correctness.

### Property-Based Testing

Property-based testing will be implemented using **Hypothesis** for Python. This approach verifies that universal properties hold across a wide range of randomly generated inputs.

**Configuration:**
- Each property-based test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate valid and invalid inputs
- Each property-based test will be tagged with a comment referencing the specific correctness property from this design document
- Tag format: `# Feature: user-registration, Property {number}: {property_text}`

**Property Test Coverage:**
- Property 1: User creation round-trip (create and retrieve)
- Property 2: Invalid user input rejection
- Property 3: Event creation with capacity
- Property 4: Empty waitlist initialization
- Property 5: Invalid capacity rejection
- Property 6: Registration with available capacity
- Property 7: Waitlist registration when full
- Property 8: Unregistration removes registration
- Property 9: Waitlist promotion on unregistration
- Property 10: Waitlist unregistration
- Property 11: Waitlist order preservation
- Property 12: Active-only registration list
- Property 13: Registration list event details
- Property 14: Registration list consistency

### Unit Testing

Unit tests will verify specific examples, edge cases, and integration points:

**User Service Tests:**
- Creating users with valid data
- Duplicate userId rejection
- Empty field validation

**Event Service Tests:**
- Creating events with various capacity values
- Waitlist enabled/disabled configurations
- Boundary capacity values (1, large numbers)

**Registration Service Tests:**
- Registration flow with available capacity
- Full event without waitlist (denial)
- Full event with waitlist (waitlist addition)
- Duplicate registration attempts
- Unregistration with and without waitlist promotion
- Edge case: Empty registration list
- Edge case: Single user on waitlist
- Edge case: Multiple users on waitlist

**Repository Tests:**
- CRUD operations for each repository
- Query methods return correct results
- Count and ordering operations

### Test Data Strategies

**Hypothesis Strategies:**
```python
# Generate valid user IDs (non-empty strings)
user_ids = st.text(min_size=1).filter(lambda s: s.strip())

# Generate valid names
names = st.text(min_size=1).filter(lambda s: s.strip())

# Generate valid capacities
capacities = st.integers(min_value=1, max_value=1000)

# Generate invalid capacities
invalid_capacities = st.integers(max_value=0)

# Generate waitlist flags
waitlist_flags = st.booleans()
```

### Testing Workflow

1. **Implementation-first approach**: Implement features before writing corresponding tests
2. **Property tests alongside implementation**: Write property-based tests as each component is completed
3. **Unit tests for edge cases**: Add unit tests for specific scenarios and boundary conditions
4. **Integration validation**: Ensure all components work together correctly
5. **Continuous validation**: Run all tests after each change to catch regressions early

### Success Criteria

- All property-based tests pass with 100+ iterations
- All unit tests pass
- Code coverage > 90% for service and repository layers
- No unhandled error cases
- All acceptance criteria validated by at least one test
