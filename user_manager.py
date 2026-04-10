"""
User management and authentication system.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
import hashlib


@dataclass
class User:
    """Represents a user account."""
    username: str
    password_hash: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class UserManager:
    """Manages user accounts and authentication."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Register a new user.
        Returns: (success, message)
        """
        # Validate inputs
        if not username or not password:
            return False, "Username and password are required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Check if user exists
        if username in self.users:
            return False, "Username already exists"
        
        # Create user
        password_hash = self.hash_password(password)
        self.users[username] = User(username=username, password_hash=password_hash)
        
        return True, "User registered successfully"
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user.
        Returns: (success, message)
        """
        if username not in self.users:
            return False, "Invalid username or password"
        
        user = self.users[username]
        password_hash = self.hash_password(password)
        
        if user.password_hash != password_hash:
            return False, "Invalid username or password"
        
        return True, "Login successful"
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        return username in self.users
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.users.get(username)
    
    def delete_user(self, username: str) -> bool:
        """Delete a user account."""
        if username in self.users:
            del self.users[username]
            return True
        return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change a user's password."""
        if not self.user_exists(username):
            return False, "User not found"
        
        # Verify old password
        success, _ = self.login(username, old_password)
        if not success:
            return False, "Current password is incorrect"
        
        # Validate new password
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        # Update password
        password_hash = self.hash_password(new_password)
        self.users[username].password_hash = password_hash
        
        return True, "Password changed successfully"
