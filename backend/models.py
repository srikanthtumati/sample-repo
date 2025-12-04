"""Data models for the user registration system"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RegistrationStatus(Enum):
    """Status of a registration"""
    ACTIVE = "active"
    WAITLISTED = "waitlisted"


@dataclass
class User:
    """User model"""
    user_id: str
    name: str


@dataclass
class Registration:
    """Registration model linking users to events"""
    registration_id: str
    user_id: str
    event_id: str
    status: RegistrationStatus
    waitlist_position: Optional[int] = None
