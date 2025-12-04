"""Event API handlers"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends

from events.models import Event, EventUpdate
from events.service import EventService
from common.exceptions import NotFoundError


router = APIRouter(prefix="/events", tags=["events"])


def get_event_service() -> EventService:
    """Dependency injection for EventService"""
    from config import get_event_service
    return get_event_service()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event: Event, service: EventService = Depends(get_event_service)):
    """Create a new event"""
    try:
        return service.create_event(event)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/")
async def list_events(
    event_status: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    """List all events, optionally filtered by status"""
    try:
        return service.list_events(status=event_status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{event_id}")
async def get_event(event_id: str, service: EventService = Depends(get_event_service)):
    """Get a specific event by ID"""
    try:
        return service.get_event(event_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{event_id}")
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    """Update an existing event"""
    try:
        return service.update_event(event_id, event_update)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        if "No fields to update" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{event_id}")
async def delete_event(event_id: str, service: EventService = Depends(get_event_service)):
    """Delete an event"""
    try:
        service.delete_event(event_id)
        return {"message": "Event deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
