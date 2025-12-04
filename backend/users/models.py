"""User data models"""
from dataclasses import dataclass
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Pydantic model for user creation requests"""
    userId: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


@dataclass
class User:
    """User domain model"""
    user_id: str
    name: str
