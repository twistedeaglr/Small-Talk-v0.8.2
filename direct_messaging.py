"""
Direct messaging system for 1-on-1 chat between users.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Callable
import asyncio


@dataclass
class DirectMessage:
    """Represents a direct message between two users."""
    sender: str
    recipient: str
    content: str
    timestamp: datetime = None
    read: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __str__(self):
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] {self.sender}: {self.content}"


class DirectMessageThread:
    """Represents a 1-on-1 chat thread between two users."""
    
    def __init__(self, user1: str, user2: str):
        # Always store in sorted order for consistency
        self.users = tuple(sorted([user1, user2]))
        self.user1, self.user2 = self.users
        self.messages: List[DirectMessage] = []
        self.subscribers: Dict[str, Callable] = {}
    
    def subscribe(self, user_id: str, callback: Callable):
        """Subscribe a user to this thread."""
        self.subscribers[user_id] = callback
    
    def unsubscribe(self, user_id: str):
        """Unsubscribe a user from this thread."""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
    
    async def broadcast(self, message: DirectMessage):
        """Broadcast a message to both users."""
        self.messages.append(message)
        
        # Notify both users
        for user_id, callback in self.subscribers.items():
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                print(f"Error notifying {user_id}: {e}")
    
    def get_history(self, limit: int = 50) -> List[DirectMessage]:
        """Get message history."""
        return self.messages[-limit:]
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread messages for a user."""
        return sum(1 for msg in self.messages if msg.recipient == user_id and not msg.read)
    
    def mark_as_read(self, user_id: str):
        """Mark all messages for a user as read."""
        for msg in self.messages:
            if msg.recipient == user_id:
                msg.read = True


class DirectMessagingSystem:
    """Manages direct messages between users."""
    
    def __init__(self):
        self.threads: Dict[tuple, DirectMessageThread] = {}
    
    def _get_thread_key(self, user1: str, user2: str) -> tuple:
        """Get consistent key for thread."""
        return tuple(sorted([user1, user2]))
    
    def get_or_create_thread(self, user1: str, user2: str) -> DirectMessageThread:
        """Get or create a direct message thread."""
        key = self._get_thread_key(user1, user2)
        
        if key not in self.threads:
            self.threads[key] = DirectMessageThread(user1, user2)
        
        return self.threads[key]
    
    async def send_message(self, sender: str, recipient: str, content: str) -> DirectMessage:
        """Send a direct message."""
        thread = self.get_or_create_thread(sender, recipient)
        message = DirectMessage(sender=sender, recipient=recipient, content=content)
        await thread.broadcast(message)
        return message
    
    def subscribe_to_thread(self, user1: str, user2: str, user_id: str, callback: Callable):
        """Subscribe to a DM thread."""
        thread = self.get_or_create_thread(user1, user2)
        thread.subscribe(user_id, callback)
    
    def unsubscribe_from_thread(self, user1: str, user2: str, user_id: str):
        """Unsubscribe from a DM thread."""
        key = self._get_thread_key(user1, user2)
        if key in self.threads:
            self.threads[key].unsubscribe(user_id)
    
    def get_thread_history(self, user1: str, user2: str, limit: int = 50) -> List[DirectMessage]:
        """Get message history for a DM thread."""
        thread = self.get_or_create_thread(user1, user2)
        return thread.get_history(limit)
    
    def get_conversations(self, user_id: str) -> List[dict]:
        """Get all active conversations for a user with latest message."""
        conversations = []
        
        for thread in self.threads.values():
            if user_id in (thread.user1, thread.user2):
                other_user = thread.user2 if user_id == thread.user1 else thread.user1
                latest_msg = thread.messages[-1] if thread.messages else None
                unread = thread.get_unread_count(user_id)
                
                conversations.append({
                    "user": other_user,
                    "last_message": latest_msg.content if latest_msg else None,
                    "last_message_time": latest_msg.timestamp.isoformat() if latest_msg else None,
                    "last_message_sender": latest_msg.sender if latest_msg else None,
                    "unread_count": unread
                })
        
        # Sort by most recent first
        conversations.sort(
            key=lambda x: x['last_message_time'] or '', 
            reverse=True
        )
        
        return conversations
