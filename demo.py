"""
Demo/example of using the messaging system.
"""

import asyncio
from messaging_system import MessagingSystem, Message


async def demo():
    """Run a simple demo of the messaging system."""
    
    print("=== Simple Messaging System Demo ===\n")
    
    # Create messaging system
    system = MessagingSystem()
    
    # Create some channels
    print("1. Creating channels: #general, #random, #announcements")
    system.create_channel("general")
    system.create_channel("random")
    system.create_channel("announcements")
    print(f"   Active channels: {system.list_channels()}\n")
    
    # Define message handlers for different users
    messages_received = {"alice": [], "bob": [], "charlie": []}
    
    async def alice_handler(msg: Message):
        messages_received["alice"].append(msg)
        print(f"  [ALICE received] {msg}")
    
    async def bob_handler(msg: Message):
        messages_received["bob"].append(msg)
        print(f"  [BOB received] {msg}")
    
    async def charlie_handler(msg: Message):
        messages_received["charlie"].append(msg)
        print(f"  [CHARLIE received] {msg}")
    
    # Subscribe users to channels
    print("2. Subscribing users to channels:")
    system.subscribe_to_channel("alice", "general", alice_handler)
    system.subscribe_to_channel("bob", "general", bob_handler)
    system.subscribe_to_channel("alice", "random", alice_handler)
    system.subscribe_to_channel("charlie", "announcements", charlie_handler)
    print("   Alice: #general, #random")
    print("   Bob: #general")
    print("   Charlie: #announcements\n")
    
    # Send some messages
    print("3. Sending messages:")
    await system.send_message("alice", "general", "Hey everyone!")
    await asyncio.sleep(0.1)
    await system.send_message("bob", "general", "Hi Alice!")
    await asyncio.sleep(0.1)
    await system.send_message("alice", "random", "This is a random thought")
    await asyncio.sleep(0.1)
    await system.send_message("admin", "announcements", "Channel announcements coming soon!")
    print()
    
    # Show channel statistics
    print("4. Channel statistics:")
    for channel_name in system.list_channels():
        stats = system.get_channel_stats(channel_name)
        print(f"   {channel_name}: {stats['message_count']} messages, {stats['subscribers']} subscribers")
    print()
    
    # Show messages received by each user
    print("5. Messages received by each user:")
    for user, msgs in messages_received.items():
        print(f"   {user}: {len(msgs)} messages")
        for msg in msgs:
            print(f"      - {msg}")
    print()
    
    # Show message history
    print("6. Message history for #general:")
    general_channel = system.get_channel("general")
    for msg in general_channel.get_history():
        print(f"   {msg}")
    print()
    
    # Unsubscribe and test
    print("7. Alice leaves #general:")
    system.unsubscribe_from_channel("alice", "general")
    await system.send_message("bob", "general", "Alice left, but this message should still be in history")
    await asyncio.sleep(0.1)
    print(f"   Alice received {len(messages_received['alice'])} messages (no new ones)\n")
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo())
