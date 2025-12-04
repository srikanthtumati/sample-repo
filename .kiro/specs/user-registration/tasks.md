# Implementation Plan

- [ ] 1. Set up project structure and data models
  - Create directory structure for models, services, repositories, and tests
  - Define data model classes (User, Event, Registration, RegistrationStatus)
  - Implement validation logic for data models
  - _Requirements: 1.1, 1.4, 1.5, 2.1_

- [ ]* 1.1 Write property test for user creation
  - **Property 1: User creation stores all fields correctly**
  - **Validates: Requirements 1.1, 1.4, 1.5**

- [ ]* 1.2 Write property test for invalid user input
  - **Property 2: Invalid user input is rejected**
  - **Validates: Requirements 1.3**

- [ ]* 1.3 Write property test for event creation
  - **Property 3: Event creation stores capacity correctly**
  - **Validates: Requirements 2.1**

- [ ]* 1.4 Write property test for invalid capacity
  - **Property 5: Invalid capacity is rejected**
  - **Validates: Requirements 2.4, 2.5**

- [ ] 2. Implement repository layer
  - Create UserRepository with save, find_by_id, and exists methods
  - Create EventRepository with save and find_by_id methods
  - Create RegistrationRepository with save, delete, find, count, and waitlist query methods
  - Implement in-memory storage backend for all repositories
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [ ]* 2.1 Write unit tests for repository operations
  - Test CRUD operations for each repository
  - Test query methods and edge cases

- [ ] 3. Implement UserService
  - Implement create_user method with validation
  - Implement get_user method
  - Add duplicate userId checking
  - Add validation for empty/whitespace fields
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 3.1 Write unit tests for UserService
  - Test user creation with valid data
  - Test duplicate userId rejection
  - Test empty field validation

- [ ] 4. Implement EventService
  - Implement create_event method with capacity validation
  - Implement get_event method
  - Add validation for positive capacity values
  - Handle waitlist configuration
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 4.1 Write property test for empty waitlist initialization
  - **Property 4: Events with waitlist start empty**
  - **Validates: Requirements 2.2**

- [ ]* 4.2 Write unit tests for EventService
  - Test event creation with various capacity values
  - Test waitlist enabled/disabled configurations

- [ ] 5. Implement registration logic in RegistrationService
  - Implement register_user method with capacity checking
  - Add logic to create ACTIVE registrations when capacity available
  - Add logic to create WAITLISTED registrations when full with waitlist
  - Add logic to reject registrations when full without waitlist
  - Implement duplicate registration prevention
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 5.1 Write property test for registration with available capacity
  - **Property 6: Registration succeeds when capacity available**
  - **Validates: Requirements 3.1**

- [ ]* 5.2 Write property test for waitlist registration
  - **Property 7: Waitlist registration when full**
  - **Validates: Requirements 3.3**

- [ ]* 5.3 Write unit tests for registration edge cases
  - Test full event without waitlist (denial)
  - Test duplicate registration attempts
  - Test registration for non-existent event

- [ ] 6. Implement unregistration logic in RegistrationService
  - Implement unregister_user method
  - Add logic to remove ACTIVE registrations
  - Add logic to remove WAITLISTED registrations
  - Implement waitlist promotion when ACTIVE user unregisters
  - Implement waitlist reordering after promotion
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 6.1 Write property test for unregistration
  - **Property 8: Unregistration removes registration**
  - **Validates: Requirements 4.1**

- [ ]* 6.2 Write property test for waitlist promotion
  - **Property 9: Waitlist promotion on unregistration**
  - **Validates: Requirements 4.2**

- [ ]* 6.3 Write property test for waitlist unregistration
  - **Property 10: Waitlist unregistration removes entry**
  - **Validates: Requirements 4.3**

- [ ]* 6.4 Write property test for waitlist order preservation
  - **Property 11: Waitlist order preserved after promotion**
  - **Validates: Requirements 4.5**

- [ ]* 6.5 Write unit tests for unregistration edge cases
  - Test unregistration from non-existent registration
  - Test single user on waitlist promotion
  - Test multiple users on waitlist

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement registration list functionality in RegistrationService
  - Implement get_user_registrations method
  - Filter to return only ACTIVE registrations
  - Include complete event details for each registration
  - Ensure consistent ordering of results
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 8.1 Write property test for active-only registration list
  - **Property 12: Registration list contains only active registrations**
  - **Validates: Requirements 5.1, 5.2**

- [ ]* 8.2 Write property test for registration list event details
  - **Property 13: Registration list includes event details**
  - **Validates: Requirements 5.4**

- [ ]* 8.3 Write property test for registration list consistency
  - **Property 14: Registration list order is consistent**
  - **Validates: Requirements 5.5**

- [ ]* 8.4 Write unit tests for registration list edge cases
  - Test empty registration list
  - Test user with only waitlisted registrations

- [ ] 9. Implement API layer
  - Create FastAPI application structure
  - Implement POST /users endpoint for user creation
  - Implement GET /users/{user_id} endpoint
  - Implement POST /events endpoint for event creation
  - Implement GET /events/{event_id} endpoint
  - Implement POST /registrations endpoint for registration
  - Implement DELETE /registrations endpoint for unregistration
  - Implement GET /users/{user_id}/registrations endpoint
  - Add error handling and HTTP status code mapping
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 5.1_

- [ ]* 9.1 Write integration tests for API endpoints
  - Test complete user registration flow via API
  - Test error responses and status codes
  - Test waitlist flow end-to-end

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
