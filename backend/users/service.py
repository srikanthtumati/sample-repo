"""User service for business logic"""
from typing import Optional

from users.models import User
from users.repository import UserRepository
from common.exceptions import ValidationError, DuplicateError


class UserService:
    """Service for user operations"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_id: str, name: str) -> User:
        """Creates a new user with validation"""
        # Validate inputs
        if not user_id or not user_id.strip():
            raise ValidationError("userId cannot be empty")
        if not name or not name.strip():
            raise ValidationError("name cannot be empty")
        
        # Check for duplicates
        if self.user_repo.exists(user_id):
            raise DuplicateError(f"User with ID {user_id} already exists")
        
        user = User(user_id=user_id, name=name)
        self.user_repo.save(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieves a user by ID"""
        return self.user_repo.find_by_id(user_id)
