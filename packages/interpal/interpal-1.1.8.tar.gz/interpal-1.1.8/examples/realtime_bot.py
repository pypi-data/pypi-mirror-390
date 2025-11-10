"""
Real-time bot example using WebSocket events.
This demonstrates how to build a bot that responds to messages in real-time.
"""

import asyncio
from interpal import AsyncInterpalClient


class InterpalBot:
    """
    A simple bot that responds to messages.
    """
    
    def __init__(self, session_cookie: str):
        self.client = AsyncInterpalClient(session_cookie=session_cookie)
        self.bot_name = None
        
        # Register event handlers
        self.client.event('on_ready')(self.on_ready)
        self.client.event('on_message')(self.on_message)
        self.client.event('on_typing')(self.on_typing)
        self.client.event('on_notification')(self.on_notification)
        self.client.event('on_user_online')(self.on_user_online)
        self.client.event('on_disconnect')(self.on_disconnect)
    
    async def on_ready(self, data=None):
        """Called when the bot is connected and ready."""
        print("🤖 Bot is connected and ready!")
        
        # Get bot profile
        profile = await self.client.get_self()
        self.bot_name = profile.name
        print(f"   Logged in as: {self.bot_name}")
    
    async def on_message(self, data):
        """Called when a new message is received."""
        print(f"\n📨 New message received:")
        print(f"   From: {data.get('sender', {}).get('name', 'Unknown')}")
        print(f"   Content: {data.get('content', '')}")
        
        # Parse message data
        content = data.get('content', '').lower()
        thread_id = data.get('thread_id')
        sender_name = data.get('sender', {}).get('name', 'User')
        
        # Bot commands
        if 'hello' in content or 'hi' in content:
            response = f"Hello {sender_name}! How can I help you today?"
            await self.send_reply(thread_id, response)
        
        elif 'help' in content:
            response = (
                "I'm a bot that can help you with:\n"
                "- Greeting: Say 'hello' or 'hi'\n"
                "- Time: Ask 'what time is it'\n"
                "- Weather: Ask 'weather'\n"
                "- Profile: Ask 'who are you'"
            )
            await self.send_reply(thread_id, response)
        
        elif 'time' in content:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            response = f"The current time is {current_time}"
            await self.send_reply(thread_id, response)
        
        elif 'who are you' in content or 'your name' in content:
            response = f"I'm {self.bot_name}, an automated bot to assist you!"
            await self.send_reply(thread_id, response)
        
        elif 'bye' in content or 'goodbye' in content:
            response = f"Goodbye {sender_name}! Have a great day!"
            await self.send_reply(thread_id, response)
    
    async def send_reply(self, thread_id: str, message: str):
        """Send a reply message."""
        try:
            await self.client.send_message(thread_id, message)
            print(f"✅ Sent reply: {message[:50]}...")
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    async def on_typing(self, data):
        """Called when someone is typing."""
        user_name = data.get('user', {}).get('name', 'Someone')
        print(f"✍️  {user_name} is typing...")
    
    async def on_notification(self, data):
        """Called when a new notification is received."""
        notif_type = data.get('type', 'unknown')
        message = data.get('message', '')
        print(f"🔔 Notification ({notif_type}): {message}")
    
    async def on_user_online(self, data):
        """Called when a user comes online."""
        user_name = data.get('user', {}).get('name', 'Someone')
        print(f"🟢 {user_name} is now online")
    
    async def on_disconnect(self, data=None):
        """Called when WebSocket disconnects."""
        print("⚠️  Disconnected from WebSocket")
    
    async def start(self):
        """Start the bot."""
        print("🚀 Starting bot...")
        await self.client.start()


async def simple_event_listener():
    """
    Simple example of listening to real-time events.
    """
    client = AsyncInterpalClient(
        username="your_username",
        password="your_password"
    )
    
    # Login
    client.login()
    
    # Register event handlers using decorators
    @client.event('on_ready')
    async def on_ready(data=None):
        print("✅ Connected to Interpals!")
        profile = await client.get_self()
        print(f"   Logged in as: {profile.name}")
    
    @client.event('on_message')
    async def on_message(data):
        sender = data.get('sender', {}).get('name', 'Unknown')
        content = data.get('content', '')
        print(f"📨 {sender}: {content}")
    
    @client.event('on_notification')
    async def on_notification(data):
        notif_type = data.get('type', 'unknown')
        print(f"🔔 New {notif_type} notification")
    
    # Start listening (this will run indefinitely)
    print("👂 Listening for events...")
    await client.start()


async def auto_responder():
    """
    Auto-responder that replies to all messages.
    """
    client = AsyncInterpalClient(session_cookie="your_session_cookie")
    
    @client.event('on_message')
    async def on_message(data):
        thread_id = data.get('thread_id')
        sender = data.get('sender', {}).get('name', 'Unknown')
        content = data.get('content', '')
        
        print(f"Received: {sender}: {content}")
        
        # Auto-reply
        reply = f"Thanks for your message! I'll get back to you soon."
        await client.send_message(thread_id, reply)
        print(f"Sent auto-reply to {sender}")
    
    await client.start()


def main():
    """
    Run the bot.
    """
    print("=" * 50)
    print("Interpals Bot - Real-time Message Handler")
    print("=" * 50)
    
    # Get session cookie (replace with your actual session)
    session_cookie = input("Enter your session cookie: ").strip()
    
    if not session_cookie:
        print("❌ Session cookie required!")
        return
    
    # Create and start bot
    bot = InterpalBot(session_cookie)
    
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")


if __name__ == "__main__":
    # Run the bot
    main()
    
    # Or run one of the other examples:
    # asyncio.run(simple_event_listener())
    # asyncio.run(auto_responder())

