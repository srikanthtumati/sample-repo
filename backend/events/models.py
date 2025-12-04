"""Event data models"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class Event(BaseModel):
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    date: str = Field(..., description="ISO format date (YYYY-MM-DD)")
    location: str = Field(..., min_length=1, max_length=500)
    capacity: int = Field(..., gt=0, description="Must be greater than 0")
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., description="Event status")
    waitlistEnabled: Optional[bool] = False

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'scheduled', 'ongoing', 'completed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    date: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None
    waitlistEnabled: Optional[bool] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'scheduled', 'ongoing', 'completed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('date')
    def validate_date(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v
