"""Configuration and dependency injection for the Events API"""
import os
import boto3

from users.repository import UserRepository
from users.service import UserService
from registrations.repository import RegistrationRepository
from registrations.service import RegistrationService
from events.repository import EventRepository
from events.service import EventService


# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('EVENTS_TABLE_NAME', 'Events')
events_table = dynamodb.Table(table_name)

# Repository instances (singletons)
_user_repo = None
_registration_repo = None
_event_repo = None


def get_user_repository() -> UserRepository:
    """Get or create UserRepository singleton"""
    global _user_repo
    if _user_repo is None:
        _user_repo = UserRepository()
    return _user_repo


def get_registration_repository() -> RegistrationRepository:
    """Get or create RegistrationRepository singleton"""
    global _registration_repo
    if _registration_repo is None:
        _registration_repo = RegistrationRepository()
    return _registration_repo


def get_event_repository() -> EventRepository:
    """Get or create EventRepository singleton"""
    global _event_repo
    if _event_repo is None:
        _event_repo = EventRepository(events_table)
    return _event_repo


# Service factory functions
def get_user_service() -> UserService:
    """Create UserService with dependencies"""
    return UserService(get_user_repository())


def get_event_service() -> EventService:
    """Create EventService with dependencies"""
    return EventService(get_event_repository())


def get_registration_service() -> RegistrationService:
    """Create RegistrationService with dependencies"""
    return RegistrationService(
        get_registration_repository(),
        get_user_service(),
        get_event_service()
    )
