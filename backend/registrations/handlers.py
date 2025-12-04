"""Registration API handlers"""
from fastapi import APIRouter, HTTPException, status, Depends

from registrations.models import RegistrationRequest
from registrations.service import RegistrationService
from common.exceptions import ValidationError, DuplicateError, NotFoundError, CapacityError


router = APIRouter(tags=["registrations"])


def get_registration_service() -> RegistrationService:
    """Dependency injection for RegistrationService"""
    from config import get_registration_service
    return get_registration_service()


@router.post("/events/{event_id}/registrations", status_code=status.HTTP_201_CREATED)
async def register_for_event(
    event_id: str,
    request: RegistrationRequest,
    service: RegistrationService = Depends(get_registration_service)
):
    """Register a user for an event"""
    try:
        registration = service.register_user(request.userId, event_id)
        result = {
            "registrationId": registration.registration_id,
            "userId": registration.user_id,
            "eventId": registration.event_id,
            "status": registration.status.value
        }
        if registration.waitlist_position is not None:
            result["waitlistPosition"] = registration.waitlist_position
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except CapacityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/events/{event_id}/registrations")
async def get_event_registrations(
    event_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Get all registrations for an event"""
    registrations = service.get_event_registrations(event_id)
    return {
        "registrations": registrations,
        "count": len(registrations)
    }


@router.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_from_event(
    event_id: str,
    user_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Unregister a user from an event"""
    try:
        service.unregister_user(user_id, event_id)
        return None
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/users/{user_id}/registrations")
async def get_user_registrations(
    user_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Get all active registrations for a user"""
    events = service.get_user_registrations(user_id)
    return {
        "events": events,
        "count": len(events)
    }
