"""Event service for business logic"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError

from events.repository import EventRepository
from events.models import Event, EventUpdate
from common.exceptions import NotFoundError


class EventService:
    """Service for event business logic"""
    
    def __init__(self, event_repo: EventRepository):
        """
        Initialize service with event repository
        
        Args:
            event_repo: EventRepository instance
        """
        self.event_repo = event_repo
    
    def create_event(self, event: Event) -> Dict[str, Any]:
        """
        Create a new event
        
        Args:
            event: Event model with event data
            
        Returns:
            Dictionary containing created event data
            
        Raises:
            Exception: If event creation fails
        """
        try:
            # Use provided eventId or generate new one
            event_id = event.eventId if event.eventId else str(uuid.uuid4())
            event_data = event.dict()
            event_data['eventId'] = event_id
            event_data['createdAt'] = datetime.utcnow().isoformat()
            event_data['updatedAt'] = datetime.utcnow().isoformat()
            
            return self.event_repo.create(event_data)
        except ClientError as e:
            raise Exception(f"Failed to create event: {str(e)}")
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get an event by ID
        
        Args:
            event_id: The event ID to retrieve
            
        Returns:
            Dictionary containing event data
            
        Raises:
            NotFoundError: If event not found
            Exception: If retrieval fails
        """
        try:
            event = self.event_repo.find_by_id(event_id)
            
            if not event:
                raise NotFoundError(f"Event with ID {event_id} not found")
            
            return event
        except ClientError as e:
            raise Exception(f"Failed to get event: {str(e)}")
    
    def list_events(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List all events, optionally filtered by status
        
        Args:
            status: Optional status filter
            
        Returns:
            Dictionary with events list and count
            
        Raises:
            Exception: If listing fails
        """
        try:
            events = self.event_repo.find_all(status_filter=status)
            return {"events": events, "count": len(events)}
        except ClientError as e:
            raise Exception(f"Failed to list events: {str(e)}")
    
    def update_event(self, event_id: str, event_update: EventUpdate) -> Dict[str, Any]:
        """
        Update an existing event
        
        Args:
            event_id: The event ID to update
            event_update: EventUpdate model with fields to update
            
        Returns:
            Dictionary containing updated event data
            
        Raises:
            NotFoundError: If event not found
            Exception: If update fails
        """
        try:
            # Check if event exists
            if not self.event_repo.exists(event_id):
                raise NotFoundError(f"Event with ID {event_id} not found")
            
            # Build update data
            update_data = event_update.dict(exclude_unset=True)
            if not update_data:
                raise Exception("No fields to update")
            
            update_data['updatedAt'] = datetime.utcnow().isoformat()
            
            return self.event_repo.update(event_id, update_data)
        except ClientError as e:
            raise Exception(f"Failed to update event: {str(e)}")
    
    def delete_event(self, event_id: str) -> None:
        """
        Delete an event
        
        Args:
            event_id: The event ID to delete
            
        Raises:
            NotFoundError: If event not found
            Exception: If deletion fails
        """
        try:
            # Check if event exists
            if not self.event_repo.exists(event_id):
                raise NotFoundError(f"Event with ID {event_id} not found")
            
            self.event_repo.delete(event_id)
        except ClientError as e:
            raise Exception(f"Failed to delete event: {str(e)}")
