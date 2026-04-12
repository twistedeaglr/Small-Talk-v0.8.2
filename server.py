"""
Flask server with WebSocket support for the messaging system.
Handles real-time message delivery and channel management.
"""

from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from messaging_system import MessagingSystem, Message
from user_manager import UserManager
from direct_messaging import DirectMessagingSystem
import asyncio
from threading import Thread
import os

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global messaging system and user manager
messaging_system = MessagingSystem()
user_manager = UserManager()
dm_system = DirectMessagingSystem()

# Set up default admin user
user_manager.register("elihunt", "admin123")
user_manager.set_role("elihunt", "admin")

# Track connected users
connected_users = {}


# ============ HTTP Routes ============

# ---- Authentication Endpoints ----

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    success, message = user_manager.register(username, password)
    
    if success:
        return jsonify({'success': True, 'message': message}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user."""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    success, message = user_manager.login(username, password)
    
    if success:
        user = user_manager.get_user(username)
        return jsonify({
            'success': True, 
            'message': message, 
            'username': username,
            'role': user.role
        }), 200
    else:
        return jsonify({'success': False, 'message': message}), 401


# ---- User Profile & Search Endpoints ----

@app.route('/api/users/search', methods=['GET'])
def search_users():
    """Search for users by username."""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 1:
        return jsonify([]), 200
    
    results = user_manager.search_users(query)
    return jsonify(results), 200


@app.route('/api/users/<username>/profile', methods=['GET'])
def get_user_profile(username):
    """Get a user's profile."""
    profile = user_manager.get_profile(username)
    
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(profile), 200


@app.route('/api/users/<username>/profile', methods=['PUT'])
def update_user_profile(username):
    """Update user profile."""
    data = request.json
    bio = data.get('bio')
    avatar_color = data.get('avatar_color')
    
    success, message = user_manager.update_profile(username, bio, avatar_color)
    
    if success:
        profile = user_manager.get_profile(username)
        return jsonify({'success': True, 'profile': profile}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400


# ---- Friends Endpoints ----

@app.route('/api/friends/<username>', methods=['GET'])
def get_friends(username):
    """Get list of friends."""
    friends = user_manager.get_friends(username)
    friend_profiles = [user_manager.get_profile(f) for f in friends]
    return jsonify(friend_profiles), 200


@app.route('/api/friends/<username>/requests', methods=['GET'])
def get_friend_requests(username):
    """Get incoming friend requests."""
    requests = user_manager.get_friend_requests(username)
    request_profiles = [user_manager.get_profile(r) for r in requests]
    return jsonify(request_profiles), 200


@app.route('/api/friends/request', methods=['POST'])
def send_friend_request_endpoint():
    """Send a friend request."""
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    
    success, message = user_manager.send_friend_request(from_user, to_user)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/friends/accept', methods=['POST'])
def accept_friend_request_endpoint():
    """Accept a friend request."""
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    
    success, message = user_manager.accept_friend_request(from_user, to_user)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/friends/reject', methods=['POST'])
def reject_friend_request_endpoint():
    """Reject a friend request."""
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    
    success, message = user_manager.reject_friend_request(from_user, to_user)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/friends/remove', methods=['POST'])
def remove_friend_endpoint():
    """Remove a friend."""
    data = request.json
    username = data.get('username')
    friend = data.get('friend')
    
    success, message = user_manager.remove_friend(username, friend)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400


# ---- Channel Endpoints ----

@app.route('/api/channels', methods=['GET'])
def get_channels():
    """Get list of all channels."""
    channels = messaging_system.list_channels()
    channel_data = []
    
    for channel_name in channels:
        stats = messaging_system.get_channel_stats(channel_name)
        channel_data.append(stats)
    
    return jsonify(channel_data)


@app.route('/api/channels/<channel_name>/history', methods=['GET'])
def get_channel_history(channel_name):
    """Get message history for a channel."""
    limit = request.args.get('limit', 50, type=int)
    channel = messaging_system.get_channel(channel_name)
    history = channel.get_history(limit)
    
    messages = [
        {
            'sender': msg.sender,
            'content': msg.content,
            'channel': msg.channel,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in history
    ]
    
    return jsonify(messages)


@app.route('/api/channels', methods=['POST'])
def create_channel():
    """Create a new channel."""
    data = request.json
    channel_name = data.get('name')
    
    if not channel_name:
        return jsonify({'error': 'Channel name required'}), 400
    
    messaging_system.create_channel(channel_name)
    return jsonify({'success': True, 'channel': channel_name}), 201


@app.route('/api/channels/<channel_name>', methods=['DELETE'])
def delete_channel(channel_name):
    """Delete a channel."""
    success = messaging_system.delete_channel(channel_name)
    
    if not success:
        return jsonify({'error': 'Channel not found'}), 404
    
    # Notify all connected clients
    socketio.emit('channel_deleted', {'channel': channel_name}, broadcast=True)
    return jsonify({'success': True})


# ============ WebSocket Events ============

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    sid = request.sid
    print(f"Client connected: {sid}")
    emit('connect_response', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    sid = request.sid
    user_info = connected_users.get(sid)
    
    if user_info:
        username = user_info['username']
        # Clean up any active channel subscriptions for this socket.
        for channel_name in list(user_info['channels']):
            messaging_system.unsubscribe_from_channel(sid, channel_name)

        print(f"Client disconnected: {sid} ({username})")
        del connected_users[sid]


@socketio.on('register_user')
def handle_register_user(data):
    """Register an authenticated user for WebSocket communication."""
    sid = request.sid
    username = data.get('username')
    
    # Verify user exists (they authenticated)
    if not username or not user_manager.user_exists(username):
        emit('error', {'message': 'Invalid username or not authenticated'})
        return
    
    connected_users[sid] = {
        'username': username,
        'channels': set()
    }
    
    print(f"User registered: {username} ({sid})")
    emit('user_registered', {'username': username})


@socketio.on('join_channel')
def handle_join_channel(data):
    """Handle user joining a channel."""
    sid = request.sid
    channel_name = data.get('channel')
    
    if sid not in connected_users:
        emit('error', {'message': 'User not registered'})
        return
    
    user_info = connected_users[sid]
    username = user_info['username']
    
    # Join Socket.IO room
    join_room(channel_name)
    user_info['channels'].add(channel_name)
    
    # Subscribe to messaging system
    async def on_message(msg):
        socketio.emit('receive_message', {
            'sender': msg.sender,
            'content': msg.content,
            'channel': msg.channel,
            'timestamp': msg.timestamp.isoformat()
        }, room=channel_name)
    
    messaging_system.subscribe_to_channel(sid, channel_name, on_message)
    
    # Notify room
    emit('user_joined', {
        'username': username,
        'channel': channel_name
    }, room=channel_name)
    
    # Send channel history to the user
    channel = messaging_system.get_channel(channel_name)
    history = channel.get_history(50)
    message_history = [
        {
            'sender': msg.sender,
            'content': msg.content,
            'channel': msg.channel,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in history
    ]
    
    emit('channel_history', {
        'channel': channel_name,
        'messages': message_history
    })


@socketio.on('leave_channel')
def handle_leave_channel(data):
    """Handle user leaving a channel."""
    sid = request.sid
    channel_name = data.get('channel')
    
    if sid not in connected_users:
        return
    
    user_info = connected_users[sid]
    username = user_info['username']
    
    # Leave Socket.IO room
    leave_room(channel_name)
    user_info['channels'].discard(channel_name)
    
    # Unsubscribe from messaging system
    messaging_system.unsubscribe_from_channel(sid, channel_name)
    
    # Notify room
    emit('user_left', {
        'username': username,
        'channel': channel_name
    }, room=channel_name)


@socketio.on('send_message')
def handle_send_message(data):
    """Handle user sending a message."""
    sid = request.sid
    
    if sid not in connected_users:
        emit('error', {'message': 'User not registered'})
        return
    
    user_info = connected_users[sid]
    username = user_info['username']
    channel_name = data.get('channel')
    content = data.get('content')
    
    if not channel_name or not content:
        emit('error', {'message': 'Channel and content required'})
        return
    
    if channel_name not in user_info['channels']:
        emit('error', {'message': 'Not in that channel'})
        return
    
    # Send message through messaging system
    async def send():
        await messaging_system.send_message(username, channel_name, content)
    
    # Run async function
    loop = asyncio.new_event_loop()
    loop.run_until_complete(send())
    loop.close()


@socketio.on('get_channels')
def handle_get_channels():
    """Send list of channels to client."""
    channels = messaging_system.list_channels()
    channel_data = []
    
    for channel_name in channels:
        stats = messaging_system.get_channel_stats(channel_name)
        channel_data.append(stats)
    
    emit('channels_list', {'channels': channel_data})


# ============ Direct Messaging Events ============

@socketio.on('open_dm')
def handle_open_dm(data):
    """Open a direct message conversation."""
    sid = request.sid
    
    if sid not in connected_users:
        emit('error', {'message': 'User not registered'})
        return
    
    current_user = connected_users[sid]['username']
    other_user = data.get('user')
    
    if not other_user:
        emit('error', {'message': 'User not specified'})
        return
    
    # Join a unique room for this conversation
    room = f"dm_{min(current_user, other_user)}_{max(current_user, other_user)}"
    join_room(room)
    
    # Subscribe to DM thread
    async def on_dm(msg):
        socketio.emit('receive_dm', {
            'sender': msg.sender,
            'recipient': msg.recipient,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }, room=room)
    
    dm_system.subscribe_to_thread(current_user, other_user, sid, on_dm)
    
    # Send message history
    history = dm_system.get_thread_history(current_user, other_user)
    messages = [
        {
            'sender': msg.sender,
            'recipient': msg.recipient,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in history
    ]
    
    emit('dm_history', {
        'user': other_user,
        'messages': messages
    })


@socketio.on('close_dm')
def handle_close_dm(data):
    """Close a direct message conversation."""
    sid = request.sid
    
    if sid not in connected_users:
        return
    
    current_user = connected_users[sid]['username']
    other_user = data.get('user')
    
    room = f"dm_{min(current_user, other_user)}_{max(current_user, other_user)}"
    leave_room(room)
    
    dm_system.unsubscribe_from_thread(current_user, other_user, sid)


@socketio.on('send_dm')
def handle_send_dm(data):
    """Send a direct message."""
    sid = request.sid
    
    if sid not in connected_users:
        emit('error', {'message': 'User not registered'})
        return
    
    current_user = connected_users[sid]['username']
    recipient = data.get('recipient')
    content = data.get('content')
    
    if not recipient or not content:
        emit('error', {'message': 'Recipient and content required'})
        return
    
    # Send DM
    async def send():
        await dm_system.send_message(current_user, recipient, content)
    
    loop = asyncio.new_event_loop()
    loop.run_until_complete(send())
    loop.close()


@socketio.on('get_conversations')
def handle_get_conversations():
    """Get list of active conversations."""
    sid = request.sid
    
    if sid not in connected_users:
        emit('error', {'message': 'User not registered'})
        return
    
    username = connected_users[sid]['username']
    conversations = dm_system.get_conversations(username)
    
    emit('conversations_list', {'conversations': conversations})


# ============ Utility Routes ============

@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    print("Starting Messaging Server...")
    print("Server running at http://localhost:5000")
    print("WebSocket endpoint: ws://localhost:5000/socket.io/")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
