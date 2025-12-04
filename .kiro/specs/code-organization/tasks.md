# Implementation Plan

- [ ] 1. Create directory structure and common modules
  - Create domain directories: `backend/events/`, `backend/users/`, `backend/registrations/`, `backend/common/`
  - Create `__init__.py` files in each directory
  - Create `backend/common/exceptions.py` with shared exception classes (ValidationError, DuplicateError, NotFoundError, CapacityError)
  - _Requirements: 3.1, 3.3, 6.2_

- [ ] 2. Extract and organize event domain
  - [ ] 2.1 Create event models module
    - Move Event and EventUpdate Pydantic models to `backend/events/models.py`
    - Include all validators for status and date fields
    - _Requirements: 3.1, 3.3, 6.1_

  - [ ] 2.2 Implement event repository
    - Create `backend/events/repository.py` with EventRepository class
    - Implement methods: create, find_by_id, find_all, update, delete, exists
    - Extract all DynamoDB operations from main.py handlers
    - _Requirements: 2.1, 2.2, 2.3, 7.2_

  - [ ] 2.3 Implement event service
    - Create `backend/events/service.py` with EventService class
    - Implement business logic methods: create_event, get_event, list_events, update_event, delete_event
    - Extract business logic from main.py handlers
    - _Requirements: 1.3, 7.1_

  - [ ] 2.4 Create event handlers
    - Create `backend/events/handlers.py` with FastAPI router
    - Implement endpoints: POST /, GET /, GET /{event_id}, PUT /{event_id}, DELETE /{event_id}
    - Use dependency injection for EventService
    - Translate service exceptions to HTTP responses
    - _Requirements: 1.1, 1.2, 4.1, 4.2_

- [ ] 3. Extract and organize user domain
  - [ ] 3.1 Create user models module
    - Move User dataclass and create UserCreate Pydantic model to `backend/users/models.py`
    - _Requirements: 3.1, 3.3, 6.1_

  - [ ] 3.2 Move user repository
    - Move UserRepository class to `backend/users/repository.py`
    - Update imports to use common exceptions
    - _Requirements: 2.1, 7.2_

  - [ ] 3.3 Move user service
    - Move UserService class to `backend/users/service.py`
    - Update imports to use common exceptions and user models
    - _Requirements: 1.3, 7.1_

  - [ ] 3.4 Create user handlers
    - Create `backend/users/handlers.py` with FastAPI router
    - Implement endpoints: POST /, GET /{user_id}
    - Use dependency injection for UserService
    - Translate service exceptions to HTTP responses
    - _Requirements: 1.1, 1.2, 4.1, 4.2_

- [ ] 4. Extract and organize registration domain
  - [ ] 4.1 Create registration models module
    - Move Registration dataclass, RegistrationStatus enum, and RegistrationRequest to `backend/registrations/models.py`
    - _Requirements: 3.1, 3.3, 6.1_

  - [ ] 4.2 Move registration repository
    - Move RegistrationRepository class to `backend/registrations/repository.py`
    - Update imports to use registration models
    - _Requirements: 2.1, 7.2_

  - [ ] 4.3 Refactor registration service
    - Move RegistrationService class to `backend/registrations/service.py`
    - Update to depend on UserService and EventService instead of direct repository/table access
    - Update imports to use common exceptions and registration models
    - _Requirements: 1.3, 5.2, 7.1, 7.4_

  - [ ] 4.4 Create registration handlers
    - Create `backend/registrations/handlers.py` with FastAPI router
    - Implement endpoints: POST /events/{event_id}/registrations, GET /events/{event_id}/registrations, DELETE /events/{event_id}/registrations/{user_id}, GET /users/{user_id}/registrations
    - Use dependency injection for RegistrationService
    - Translate service exceptions to HTTP responses
    - _Requirements: 1.1, 1.2, 4.1, 4.2_

- [ ] 5. Create configuration and dependency injection
  - Create `backend/config.py` with dependency injection functions
  - Implement get_user_repository, get_registration_repository, get_event_repository
  - Implement get_user_service, get_event_service, get_registration_service
  - Set up DynamoDB client and table initialization
  - Use singleton pattern for repository instances
  - _Requirements: 5.1, 5.2, 5.3, 8.4_

- [ ] 6. Refactor main application file
  - Update `backend/main.py` to only contain FastAPI app setup, CORS middleware, and router registration
  - Import routers from events.handlers, users.handlers, registrations.handlers
  - Register all routers with app.include_router()
  - Keep root and health check endpoints
  - Remove all business logic, models, services, and repositories
  - Ensure file is under 200 lines
  - _Requirements: 8.1, 8.2, 8.3, 8.5_

- [ ] 7. Checkpoint - Verify refactoring preserves functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 8. Write property-based tests for correctness properties
  - [ ]* 8.1 Write property test for API endpoint behavioral equivalence
    - **Property 1: API Endpoint Behavioral Equivalence**
    - **Validates: Requirements 4.1**
    - Use Hypothesis to generate valid requests for each endpoint
    - Verify responses match expected behavior
    - Run minimum 100 iterations

  - [ ]* 8.2 Write property test for request/response schema compatibility
    - **Property 2: Request/Response Schema Compatibility**
    - **Validates: Requirements 4.2**
    - Use Hypothesis to generate edge cases for request validation
    - Verify all valid requests are accepted and invalid requests are rejected
    - Run minimum 100 iterations

  - [ ]* 8.3 Write property test for error response consistency
    - **Property 3: Error Response Consistency**
    - **Validates: Requirements 4.4**
    - Use Hypothesis to generate invalid inputs
    - Verify error status codes and message formats are consistent
    - Run minimum 100 iterations

  - [ ]* 8.4 Write property test for registration workflow preservation
    - **Property 4: Registration Workflow Preservation**
    - **Validates: Requirements 4.5**
    - Use Hypothesis to generate sequences of registration operations
    - Verify capacity checks, waitlist ordering, and status transitions
    - Run minimum 100 iterations

  - [ ]* 8.5 Write property test for event capacity logic preservation
    - **Property 5: Event Capacity Logic Preservation**
    - **Validates: Requirements 4.5**
    - Use Hypothesis to generate events with various capacities and registration attempts
    - Verify capacity enforcement and waitlist behavior
    - Run minimum 100 iterations

- [ ] 9. Clean up old files
  - Remove old `backend/models.py` file
  - Remove old `backend/services.py` file
  - Remove old `backend/repositories.py` file
  - Verify no broken imports remain
  - _Requirements: 3.1, 3.3_

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
