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
    bio: str = ""
    avatar_color: str = "#667eea"
    friends: list = None
    friend_requests: list = None
    role: str = "user"  # "user" or "admin"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.friends is None:
            self.friends = []
        if self.friend_requests is None:
            self.friend_requests = []


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
    
    # ============ Friends System ============
    
    def send_friend_request(self, from_user: str, to_user: str) -> tuple[bool, str]:
        """Send a friend request."""
        if not self.user_exists(from_user):
            return False, "From user not found"
        
        if not self.user_exists(to_user):
            return False, "To user not found"
        
        if from_user == to_user:
            return False, "Cannot send friend request to yourself"
        
        # Check if already friends
        if to_user in self.users[from_user].friends:
            return False, "Already friends"
        
        # Check if request already sent
        if to_user in self.users[from_user].friend_requests:
            return False, "Friend request already sent"
        
        # Add to recipient's incoming requests
        if from_user not in self.users[to_user].friend_requests:
            self.users[to_user].friend_requests.append(from_user)
        
        return True, f"Friend request sent to {to_user}"
    
    def accept_friend_request(self, from_user: str, to_user: str) -> tuple[bool, str]:
        """Accept a friend request."""
        if not self.user_exists(from_user):
            return False, "From user not found"
        
        if not self.user_exists(to_user):
            return False, "To user not found"
        
        # Check if request exists
        if from_user not in self.users[to_user].friend_requests:
            return False, "No friend request from this user"
        
        # Add each other to friends list
        if from_user not in self.users[to_user].friends:
            self.users[to_user].friends.append(from_user)
        if to_user not in self.users[from_user].friends:
            self.users[from_user].friends.append(to_user)
        
        # Remove the request
        self.users[to_user].friend_requests.remove(from_user)
        
        return True, f"Friend request from {from_user} accepted"
    
    def reject_friend_request(self, from_user: str, to_user: str) -> tuple[bool, str]:
        """Reject a friend request."""
        if from_user not in self.users[to_user].friend_requests:
            return False, "No friend request from this user"
        
        self.users[to_user].friend_requests.remove(from_user)
        return True, "Friend request rejected"
    
    def remove_friend(self, username: str, friend: str) -> tuple[bool, str]:
        """Remove a friend."""
        if not self.user_exists(username):
            return False, "User not found"
        
        if friend not in self.users[username].friends:
            return False, "Not friends with this user"
        
        self.users[username].friends.remove(friend)
        if username in self.users[friend].friends:
            self.users[friend].friends.remove(username)
        
        return True, f"Removed {friend} from friends"
    
    def get_friends(self, username: str) -> list:
        """Get list of friends."""
        if not self.user_exists(username):
            return []
        
        return self.users[username].friends
    
    def get_friend_requests(self, username: str) -> list:
        """Get list of incoming friend requests."""
        if not self.user_exists(username):
            return []
        
        return self.users[username].friend_requests
    
    def are_friends(self, user1: str, user2: str) -> bool:
        """Check if two users are friends."""
        if not self.user_exists(user1) or not self.user_exists(user2):
            return False
        
        return user2 in self.users[user1].friends
    
    # ============ Profile System ============
    
    def update_profile(self, username: str, bio: str = None, avatar_color: str = None) -> tuple[bool, str]:
        """Update user profile."""
        if not self.user_exists(username):
            return False, "User not found"
        
        user = self.users[username]
        
        if bio is not None:
            if len(bio) > 500:
                return False, "Bio too long (max 500 characters)"
            user.bio = bio
        
        if avatar_color is not None:
            # Simple validation for hex color
            if not (avatar_color.startswith("#") and len(avatar_color) == 7):
                return False, "Invalid color format"
            user.avatar_color = avatar_color
        
        return True, "Profile updated"
    
    def get_profile(self, username: str) -> Optional[dict]:
        """Get user profile information."""
        if not self.user_exists(username):
            return None
        
        user = self.users[username]
        return {
            "username": user.username,
            "bio": user.bio,
            "avatar_color": user.avatar_color,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
            "friend_count": len(user.friends)
        }
    
    def search_users(self, query: str) -> list:
        """Search for users by username (case-insensitive)."""
        query_lower = query.lower()
        results = []
        
        for username in self.users.keys():
            if query_lower in username.lower():
                results.append(self.get_profile(username))
        
        return results
    
    # ============ Role System ============
    
    def set_role(self, username: str, role: str) -> tuple[bool, str]:
        """Set user role (admin, user, etc)."""
        if not self.user_exists(username):
            return False, "User not found"
        
        if role not in ["user", "admin", "moderator"]:
            return False, "Invalid role"
        
        self.users[username].role = role
        return True, f"Role set to {role}"
    
    def get_role(self, username: str) -> Optional[str]:
        """Get user role."""
        if not self.user_exists(username):
            return None
        
        return self.users[username].role
    
    def is_admin(self, username: str) -> bool:
        """Check if user is an admin."""
        return self.get_role(username) == "admin"
