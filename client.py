"""
Interactive CLI client for the messaging system.
"""

import asyncio
from messaging_system import MessagingSystem, Message


class ChatClient:
    """Interactive chat client for the messaging system."""
    
    def __init__(self, user_id: str, messaging_system: MessagingSystem):
        self.user_id = user_id
        self.messaging_system = messaging_system
        self.current_channel = None
        self.subscribed_channels = set()
        self.running = True
    
    async def message_callback(self, message: Message):
        """Callback for receiving messages."""
        print(f"\n{message}")
        print(f"{self.user_id}> ", end="", flush=True)
    
    def join_channel(self, channel_name: str):
        """Join a channel."""
        if channel_name in self.subscribed_channels:
            print(f"Already in channel: {channel_name}")
            return
        
        self.messaging_system.subscribe_to_channel(
            self.user_id, channel_name, self.message_callback
        )
        self.subscribed_channels.add(channel_name)
        self.current_channel = channel_name
        
        # Show message history
        channel = self.messaging_system.get_channel(channel_name)
        history = channel.get_history(10)
        
        if history:
            print(f"\n--- Message history for {channel_name} ---")
            for msg in history:
                print(msg)
            print("--- End of history ---\n")
        else:
            print(f"Joined channel: {channel_name} (no history)")
    
    def leave_channel(self, channel_name: str):
        """Leave a channel."""
        if channel_name not in self.subscribed_channels:
            print(f"Not in channel: {channel_name}")
            return
        
        self.messaging_system.unsubscribe_from_channel(self.user_id, channel_name)
        self.subscribed_channels.discard(channel_name)
        
        if self.current_channel == channel_name:
            self.current_channel = None
        
        print(f"Left channel: {channel_name}")
    
    async def send_message(self, content: str):
        """Send a message to the current channel."""
        if not self.current_channel:
            print("Not in any channel. Use /join <channel> first.")
            return
        
        await self.messaging_system.send_message(
            self.user_id, self.current_channel, content
        )
    
    def list_channels(self):
        """List all channels."""
        channels = self.messaging_system.list_channels()
        if not channels:
            print("No active channels")
            return
        
        print("\nActive channels:")
        for channel in channels:
            stats = self.messaging_system.get_channel_stats(channel)
            is_member = "✓" if channel in self.subscribed_channels else " "
            print(f"  [{is_member}] {channel} ({stats['message_count']} messages, {stats['subscribers']} subscribers)")
        print()
    
    def show_current(self):
        """Show current channel and subscriptions."""
        if self.current_channel:
            print(f"Current channel: {self.current_channel}")
        else:
            print("Not in any channel")
        
        if self.subscribed_channels:
            print(f"Subscribed to: {', '.join(sorted(self.subscribed_channels))}")
        else:
            print("Not subscribed to any channels")
    
    def show_help(self):
        """Show available commands."""
        print("""
Available commands:
  /join <channel>        - Join a channel
  /leave <channel>       - Leave a channel
  /channels              - List all channels
  /current               - Show current channel and subscriptions
  /help                  - Show this help message
  /quit                  - Exit the application
  
Type a message to send it to the current channel.
        """)
    
    async def run(self):
        """Run the interactive client."""
        print(f"\nWelcome to Simple Chat, {self.user_id}!")
        print("Type /help for available commands.\n")
        
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Read input in a non-blocking way
                user_input = await loop.run_in_executor(None, input, f"{self.user_id}> ")
                
                if not user_input:
                    continue
                
                if user_input.startswith("/"):
                    await self.handle_command(user_input)
                else:
                    # Regular message
                    await self.send_message(user_input)
            
            except EOFError:
                print("\nGoodbye!")
                self.running = False
            except KeyboardInterrupt:
                print("\nGoodbye!")
                self.running = False
    
    async def handle_command(self, command: str):
        """Handle client commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        
        if cmd == "/join":
            if not arg:
                print("Usage: /join <channel>")
            else:
                self.join_channel(arg)
        
        elif cmd == "/leave":
            if not arg:
                print("Usage: /leave <channel>")
            else:
                self.leave_channel(arg)
        
        elif cmd == "/channels":
            self.list_channels()
        
        elif cmd == "/current":
            self.show_current()
        
        elif cmd == "/help":
            self.show_help()
        
        elif cmd == "/quit":
            self.running = False
            print("Goodbye!")
        
        else:
            print(f"Unknown command: {cmd}. Use /help for available commands.")


async def main():
    """Main entry point."""
    # Create messaging system
    messaging_system = MessagingSystem()
    
    # Get user ID
    user_id = input("Enter your username: ").strip()
    if not user_id:
        user_id = "Anonymous"
    
    # Create and run client
    client = ChatClient(user_id, messaging_system)
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
