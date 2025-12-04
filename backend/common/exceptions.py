"""Shared exception classes for the Events API"""


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class DuplicateError(Exception):
    """Raised when attempting to create duplicate resource"""
    pass


class NotFoundError(Exception):
    """Raised when resource not found"""
    pass


class CapacityError(Exception):
    """Raised when event is at capacity"""
    pass
