"""Registration service for business logic"""
import uuid
from typing import List, Dict, Any

from registrations.models import Registration, RegistrationStatus
from registrations.repository import RegistrationRepository
from users.service import UserService
from events.service import EventService
from common.exceptions import ValidationError, DuplicateError, NotFoundError, CapacityError


class RegistrationService:
    """Service for registration operations"""
    
    def __init__(
        self,
        registration_repo: RegistrationRepository,
        user_service: UserService,
        event_service: EventService
    ):
        self.registration_repo = registration_repo
        self.user_service = user_service
        self.event_service = event_service
    
    def register_user(self, user_id: str, event_id: str) -> Registration:
        """
        Registers a user for an event.
        Returns ACTIVE registration if capacity available.
        Returns WAITLISTED registration if full and waitlist enabled.
        Raises error if full and no waitlist.
        """
        # Check if user exists
        user = self.user_service.get_user(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        # Check if event exists and get details
        try:
            event = self.event_service.get_event(event_id)
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
                event = self.event_service.get_event(reg.event_id)
                events.append(event)
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
