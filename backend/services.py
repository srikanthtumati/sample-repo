"""Service layer for business logic"""
import uuid
from typing import Optional, List, Dict, Any
from models import User, Registration, RegistrationStatus
from repositories import UserRepository, RegistrationRepository


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


class UserService:
    """Service for user operations"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_id: str, name: str) -> User:
        """Creates a new user with validation"""
        # Validate inputs
        if not user_id or not user_id.strip():
            raise ValidationError("userId cannot be empty")
        if not name or not name.strip():
            raise ValidationError("name cannot be empty")
        
        # Check for duplicates
        if self.user_repo.exists(user_id):
            raise DuplicateError(f"User with ID {user_id} already exists")
        
        user = User(user_id=user_id, name=name)
        self.user_repo.save(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieves a user by ID"""
        return self.user_repo.find_by_id(user_id)


class RegistrationService:
    """Service for registration operations"""
    
    def __init__(
        self,
        registration_repo: RegistrationRepository,
        user_repo: UserRepository,
        events_table
    ):
        self.registration_repo = registration_repo
        self.user_repo = user_repo
        self.events_table = events_table
    
    def register_user(self, user_id: str, event_id: str) -> Registration:
        """
        Registers a user for an event.
        Returns ACTIVE registration if capacity available.
        Returns WAITLISTED registration if full and waitlist enabled.
        Raises error if full and no waitlist.
        """
        # Check if user exists
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        # Check if event exists and get details
        try:
            response = self.events_table.get_item(Key={'eventId': event_id})
            if 'Item' not in response:
                raise NotFoundError(f"Event {event_id} not found")
            event = response['Item']
        except Exception as e:
            raise NotFoundError(f"Event {event_id} not found: {str(e)}")
        
        # Check for duplicate registration
        existing = self.registration_repo.find_by_user_and_event(user_id, event_id)
        if existing:
            raise DuplicateError(f"User {user_id} is already registered for event {event_id}")
        
        # Get capacity and waitlist settings
        capacity = event.get('capacity', 0)
        has_waitlist = event.get('waitlistEnabled', False)
        
        # Count active registrations
        active_count = self.registration_repo.count_active_by_event(event_id)
        
        # Determine registration status
        if active_count < capacity:
            # Create ACTIVE registration
            registration = Registration(
                registration_id=str(uuid.uuid4()),
                user_id=user_id,
                event_id=event_id,
                status=RegistrationStatus.ACTIVE,
                waitlist_position=None
            )
        elif has_waitlist:
            # Create WAITLISTED registration
            waitlist = self.registration_repo.get_waitlist(event_id)
            next_position = len(waitlist) + 1
            registration = Registration(
                registration_id=str(uuid.uuid4()),
                user_id=user_id,
                event_id=event_id,
                status=RegistrationStatus.WAITLISTED,
                waitlist_position=next_position
            )
        else:
            # Event is full and no waitlist
            raise CapacityError(f"Event {event_id} is at full capacity")
        
        self.registration_repo.save(registration)
        return registration
    
    def unregister_user(self, user_id: str, event_id: str) -> None:
        """
        Unregisters a user from an event.
        Promotes first waitlisted user if applicable.
        """
        # Find registration
        registration = self.registration_repo.find_by_user_and_event(user_id, event_id)
        if not registration:
            raise NotFoundError(f"Registration not found for user {user_id} and event {event_id}")
        
        was_active = registration.status == RegistrationStatus.ACTIVE
        
        # Delete the registration
        self.registration_repo.delete(user_id, event_id)
        
        # If was ACTIVE, promote first waitlisted user
        if was_active:
            waitlist = self.registration_repo.get_waitlist(event_id)
            if waitlist:
                # Promote first user
                first_waitlisted = waitlist[0]
                first_waitlisted.status = RegistrationStatus.ACTIVE
                first_waitlisted.waitlist_position = None
                self.registration_repo.save(first_waitlisted)
                
                # Reorder remaining waitlist
                for i, reg in enumerate(waitlist[1:], start=1):
                    reg.waitlist_position = i
                    self.registration_repo.save(reg)
    
    def get_user_registrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Returns all events where user has ACTIVE registration"""
        registrations = self.registration_repo.find_by_user(user_id)
        
        # Filter to only ACTIVE registrations
        active_registrations = [
            reg for reg in registrations
            if reg.status == RegistrationStatus.ACTIVE
        ]
        
        # Get event details for each registration
        events = []
        for reg in active_registrations:
            try:
                response = self.events_table.get_item(Key={'eventId': reg.event_id})
                if 'Item' in response:
                    events.append(response['Item'])
            except Exception:
                continue
        
        return events
    
    def get_event_registrations(self, event_id: str) -> List[Dict[str, Any]]:
        """Returns all registrations for an event"""
        registrations = self.registration_repo.find_by_event(event_id)
        
        # Convert to dict format
        result = []
        for reg in registrations:
            reg_dict = {
                'registrationId': reg.registration_id,
                'userId': reg.user_id,
                'eventId': reg.event_id,
                'status': reg.status.value
            }
            if reg.waitlist_position is not None:
                reg_dict['waitlistPosition'] = reg.waitlist_position
            result.append(reg_dict)
        
        return result
