# Simple Messaging System

A lightweight, real-time chat system with channel support and user authentication written in Python.

## Features

- **User Authentication**: Secure username and password registration and login
- **Multiple Channels**: Create and manage separate channels for different conversations
- **Real-time Delivery**: Messages are broadcast instantly to all subscribers via WebSocket
- **Message History**: Access recent message history for each channel
- **Web Interface**: Beautiful, responsive HTML/CSS/JavaScript UI
- **Async Support**: Built with asyncio for non-blocking operations
- **CLI Client**: Interactive command-line interface for advanced users

## Components

### 1. `messaging_system.py`
Core messaging engine with:
- `Message` class: Represents a single message with sender, content, channel, and timestamp
- `Channel` class: Manages subscribers and message history for a channel
- `MessagingSystem` class: Main system managing all channels and message routing

### 2. `user_manager.py`
User authentication and account management:
- `User` class: Stores user account information
- `UserManager` class: Handles registration, login, password hashing, and user management
- Password hashing using SHA-256
- Support for password changes and account deletion

### 3. `server.py`
Flask server with WebSocket support:
- REST API endpoints for authentication (/api/auth/login, /api/auth/register)
- WebSocket events for real-time messaging (register_user, send_message, etc.)
- Channel management endpoints
- Message history retrieval

### 4. `index.html`
Modern web interface with:
- User registration and login screens
- Real-time chat interface
- Channel management (create, join, leave)
- User presence notifications
- Responsive design with gradient styling

### 5. `client.py`
Interactive CLI client with commands:
- `/join <channel>` - Subscribe to a channel
- `/leave <channel>` - Unsubscribe from a channel
- `/channels` - List all active channels
- `/current` - Show current channel and subscriptions
- `/help` - Show available commands
- `/quit` - Exit the application

### 6. `demo.py`
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

A modern web-based chat interface with user authentication and real-time WebSocket support.

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

- **User Authentication**: Secure login and registration system
- Beautiful, responsive UI with gradient styling
- Real-time message delivery via WebSocket
- Channel management (create, join, leave)
- User presence notifications
- Message history per channel
- Status indicator for connection
- Logout functionality

### Getting Started

1. **Register/Login**: 
   - Create a new account with username and password (min 6 characters)
   - Or login with existing credentials
   
2. **Create/Join Channels**: 
   - Use the "New Channel" button to create a channel
   - Or select from the list of existing channels
   
3. **Chat**: 
   - Type messages in real-time with other users in the channel
   - Messages are instantly delivered to all subscribers
   
4. **Manage Account**: 
   - Click "Logout" to securely disconnect and return to login screen

### Architecture

```
HTML/JS Client (index.html)
      ↓ REST API + WebSocket (Socket.IO)
Flask Server (server.py)
      ↓
UserManager (user_manager.py) + MessagingSystem (messaging_system.py)
      ↓
User Accounts + Channels + Message History
```

### Authentication API Endpoints

**REST API:**
- `POST /api/auth/register` - Register a new user (username, password)
- `POST /api/auth/login` - Authenticate user (username, password)
- `GET /api/channels` - List all channels with stats
- `POST /api/channels` - Create a new channel
- `GET /api/channels/<name>/history` - Get message history
- `DELETE /api/channels/<name>` - Delete a channel

**WebSocket Events:**
- `register_user` - Register authenticated username for WebSocket
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
