# Simple Messaging System

A lightweight, real-time chat system with channel support written in Python.

## Features

- **Multiple Channels**: Create and manage separate channels for different conversations
- **Real-time Delivery**: Messages are broadcast instantly to all subscribers
- **Message History**: Access recent message history for each channel
- **Async Support**: Built with asyncio for non-blocking operations
- **Simple API**: Easy to integrate into other applications

## Components

### 1. `messaging_system.py`
Core messaging engine with:
- `Message` class: Represents a single message with sender, content, channel, and timestamp
- `Channel` class: Manages subscribers and message history for a channel
- `MessagingSystem` class: Main system managing all channels and message routing

### 2. `client.py`
Interactive CLI client with commands:
- `/join <channel>` - Subscribe to a channel
- `/leave <channel>` - Unsubscribe from a channel
- `/channels` - List all active channels
- `/current` - Show current channel and subscriptions
- `/help` - Show available commands
- `/quit` - Exit the application

### 3. `demo.py`
Demonstration script showing how to use the system programmatically

## Quick Start

### Run the Interactive Client
```bash
python client.py
```

Then use commands like:
```
Username: alice
/join general
/channels
Hello everyone!
/join random
This is random
/quit
```

### Run the Demo
```bash
python demo.py
```

This shows:
- Creating channels
- Subscribing users
- Sending messages
- Viewing statistics and history

## Usage Examples

### Programmatic Usage

```python
import asyncio
from messaging_system import MessagingSystem

async def main():
    # Create system
    system = MessagingSystem()
    
    # Create channels
    system.create_channel("general")
    system.create_channel("random")
    
    # Define a message handler
    async def on_message(message):
        print(f"{message.sender}: {message.content}")
    
    # Subscribe to channel
    system.subscribe_to_channel("user1", "general", on_message)
    
    # Send a message
    await system.send_message("user2", "general", "Hello!")
    
    # Get channel stats
    stats = system.get_channel_stats("general")
    print(stats)  # {'name': 'general', 'subscribers': 1, 'message_count': 1, ...}

asyncio.run(main())
```

### Key API Methods

**MessagingSystem:**
- `create_channel(channel_name)` - Create or get a channel
- `send_message(sender, channel_name, content)` - Send a message
- `subscribe_to_channel(user_id, channel_name, callback)` - Subscribe to a channel
- `unsubscribe_from_channel(user_id, channel_name)` - Unsubscribe from a channel
- `list_channels()` - Get all channel names
- `get_channel_stats(channel_name)` - Get channel information

**Channel:**
- `broadcast(message)` - Broadcast a message to subscribers
- `subscribe(user_id, callback)` - Add a subscriber
- `unsubscribe(user_id)` - Remove a subscriber
- `get_history(limit=50)` - Get recent messages

## Architecture

```
MessagingSystem
├── channels: Dict[str, Channel]
│   ├── Channel("general")
│   │   ├── subscribers: Dict[str, Callable]
│   │   └── message_history: List[Message]
│   ├── Channel("random")
│   └── Channel("announcements")
```

## How Real-time Delivery Works

1. User sends a message via `send_message()`
2. Message is added to channel history
3. Channel calls callback for each subscriber
4. All subscribers receive the message immediately through their callbacks

This is done asynchronously, so sending doesn't block other operations.

## Extending the System

### Add Persistence
```python
# Save messages to a database
async def broadcast(self, message):
    self.message_history.append(message)
    await save_to_database(message)  # Add this
    for user_id, callback in self.subscribers.items():
        await callback(message)
```

### Add User Presence
```python
class Channel:
    def __init__(self, name):
        self.online_users = set()
    
    def mark_online(self, user_id):
        self.online_users.add(user_id)
    
    def get_online_count(self):
        return len(self.online_users)
```

### Add Message Reactions
```python
@dataclass
class Message:
    reactions: Dict[str, List[str]] = None  # emoji -> [user_ids]
    
    def add_reaction(self, emoji: str, user_id: str):
        if self.reactions is None:
            self.reactions = {}
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        self.reactions[emoji].append(user_id)
```

## Web Interface (Flask + WebSocket)

A modern web-based chat interface is included with real-time WebSocket support.

### Installation

```bash
pip install -r requirements.txt
```

### Running the Server

```bash
python server.py
```

Then open your browser to `http://localhost:5000`

### Features

- Beautiful, responsive UI
- Real-time message delivery via WebSocket
- Channel management (create, join, leave)
- User presence notifications
- Message history per channel
- Status indicator for connection

### How It Works

1. **Login**: Enter your username to connect
2. **Create/Join Channels**: Use the "New Channel" button or select from the list
3. **Chat**: Type messages in real-time with other users in the channel
4. **Leave**: Click "Leave" to unsubscribe from a channel

### Architecture

```
index.html (WebSocket Client)
         ↓ Socket.IO
Flask Server (server.py)
         ↓
MessagingSystem (messaging_system.py)
         ↓
Channels + Message History
```

### API Endpoints

**REST API:**
- `GET /api/channels` - List all channels with stats
- `POST /api/channels` - Create a new channel
- `GET /api/channels/<name>/history` - Get message history
- `DELETE /api/channels/<name>` - Delete a channel

**WebSocket Events:**
- `register_user` - Register username
- `join_channel` - Join a channel
- `leave_channel` - Leave a channel
- `send_message` - Send a message
- `receive_message` - Receive a message (broadcasted)
- `get_channels` - Request channel list
- `channel_history` - Receive message history

## Requirements

- Python 3.7+
- Flask (for web interface)
- Flask-SocketIO (for WebSocket support)
- Modern web browser (for UI)

See `requirements.txt` for exact versions.

## License

MIT
