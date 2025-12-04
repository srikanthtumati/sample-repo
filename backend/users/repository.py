"""User repository for data access"""
from typing import Optional, Dict

from users.models import User


class UserRepository:
    """Repository for user data access"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    def save(self, user: User) -> None:
        """Persist a user"""
        self._users[user.user_id] = user
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID"""
        return self._users.get(user_id)
    
    def exists(self, user_id: str) -> bool:
        """Check if user exists"""
        return user_id in self._users
