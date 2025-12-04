"""Registration data models"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RegistrationStatus(Enum):
    """Status of a registration"""
    ACTIVE = "active"
    WAITLISTED = "waitlisted"


class RegistrationRequest(BaseModel):
    """Pydantic model for registration requests"""
    userId: str = Field(..., min_length=1)


@dataclass
class Registration:
    """Registration model linking users to events"""
    registration_id: str
    user_id: str
    event_id: str
    status: RegistrationStatus
    waitlist_position: Optional[int] = None
