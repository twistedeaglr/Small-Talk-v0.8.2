"""
Simple real-time messaging system with channel support.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable
import asyncio
import json


@dataclass
class Message:
    """Represents a single message."""
    sender: str
    content: str
    channel: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __str__(self):
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] {self.sender} ({self.channel}): {self.content}"


class Channel:
    """Represents a message channel."""
    
    def __init__(self, name: str):
        self.name = name
        self.subscribers: Dict[str, Callable] = {}
        self.message_history: List[Message] = []
    
    def subscribe(self, user_id: str, callback: Callable):
        """Subscribe a user to this channel with a callback for new messages."""
        self.subscribers[user_id] = callback
    
    def unsubscribe(self, user_id: str):
        """Unsubscribe a user from this channel."""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
    
    async def broadcast(self, message: Message):
        """Broadcast a message to all subscribers."""
        self.message_history.append(message)
        
        # Notify all subscribers
        for user_id, callback in self.subscribers.items():
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                print(f"Error notifying {user_id}: {e}")
    
    def get_history(self, limit: int = 50) -> List[Message]:
        """Get recent message history."""
        return self.message_history[-limit:]


class MessagingSystem:
    """Main messaging system managing channels and real-time delivery."""
    
    def __init__(self, log_file: str = 'data/messages.log'):
        self.channels: Dict[str, Channel] = {}
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.write_text('', encoding='utf-8')
        self._load_messages()
    
    def _load_messages(self):
        try:
            with self.log_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    timestamp = None
                    if data.get('timestamp'):
                        try:
                            timestamp = datetime.fromisoformat(data['timestamp'])
                        except ValueError:
                            timestamp = None

                    message = Message(
                        sender=data.get('sender', ''),
                        content=data.get('content', ''),
                        channel=data.get('channel', ''),
                        timestamp=timestamp
                    )
                    channel = self.get_channel(message.channel)
                    channel.message_history.append(message)
        except Exception as e:
            print(f"Error loading message log: {e}")

    def create_channel(self, channel_name: str) -> Channel:
        """Create a new channel if it doesn't exist."""
        if channel_name not in self.channels:
            self.channels[channel_name] = Channel(channel_name)
        return self.channels[channel_name]
    
    def get_channel(self, channel_name: str) -> Channel:
        """Get a channel, creating it if necessary."""
        return self.create_channel(channel_name)
    
    def delete_channel(self, channel_name: str) -> bool:
        """Delete a channel."""
        if channel_name in self.channels:
            del self.channels[channel_name]
            return True
        return False
    
    def list_channels(self) -> List[str]:
        """List all active channels."""
        return list(self.channels.keys())
    
    def get_channel_stats(self, channel_name: str) -> dict:
        """Get statistics about a channel."""
        channel = self.channels.get(channel_name)
        if not channel:
            return None
        
        return {
            "name": channel_name,
            "subscribers": len(channel.subscribers),
            "message_count": len(channel.message_history),
            "subscriber_list": list(channel.subscribers.keys())
        }
    
    async def send_message(self, sender: str, channel_name: str, content: str):
        """Send a message to a channel."""
        channel = self.get_channel(channel_name)
        message = Message(sender=sender, content=content, channel=channel_name)
        self._log_message(message)
        await channel.broadcast(message)
        return message

    def _log_message(self, message: Message):
        entry = {
            'timestamp': message.timestamp.isoformat(),
            'sender': message.sender,
            'channel': message.channel,
            'content': message.content
        }
        with self.log_file.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def subscribe_to_channel(self, user_id: str, channel_name: str, callback: Callable):
        """Subscribe a user to a channel."""
        channel = self.get_channel(channel_name)
        channel.subscribe(user_id, callback)
    
    def unsubscribe_from_channel(self, user_id: str, channel_name: str):
        """Unsubscribe a user from a channel."""
        if channel_name in self.channels:
            self.channels[channel_name].unsubscribe(user_id)
