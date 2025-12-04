"""Registration repository for data access"""
from typing import Optional, List, Dict

from registrations.models import Registration, RegistrationStatus


class RegistrationRepository:
    """Repository for registration data access"""
    
    def __init__(self):
        self._registrations: Dict[str, Registration] = {}
    
    def save(self, registration: Registration) -> None:
        """Persist a registration"""
        key = f"{registration.user_id}:{registration.event_id}"
        self._registrations[key] = registration
    
    def delete(self, user_id: str, event_id: str) -> None:
        """Remove a registration"""
        key = f"{user_id}:{event_id}"
        if key in self._registrations:
            del self._registrations[key]
    
    def find_by_user_and_event(self, user_id: str, event_id: str) -> Optional[Registration]:
        """Find specific registration"""
        key = f"{user_id}:{event_id}"
        return self._registrations.get(key)
    
    def find_by_user(self, user_id: str) -> List[Registration]:
        """Find all registrations for a user"""
        return [
            reg for reg in self._registrations.values()
            if reg.user_id == user_id
        ]
    
    def find_by_event(self, event_id: str) -> List[Registration]:
        """Find all registrations for an event"""
        return [
            reg for reg in self._registrations.values()
            if reg.event_id == event_id
        ]
    
    def count_active_by_event(self, event_id: str) -> int:
        """Count ACTIVE registrations for an event"""
        return sum(
            1 for reg in self._registrations.values()
            if reg.event_id == event_id and reg.status == RegistrationStatus.ACTIVE
        )
    
    def get_waitlist(self, event_id: str) -> List[Registration]:
        """Returns waitlisted registrations ordered by position"""
        waitlisted = [
            reg for reg in self._registrations.values()
            if reg.event_id == event_id and reg.status == RegistrationStatus.WAITLISTED
        ]
        return sorted(waitlisted, key=lambda r: r.waitlist_position or 0)
