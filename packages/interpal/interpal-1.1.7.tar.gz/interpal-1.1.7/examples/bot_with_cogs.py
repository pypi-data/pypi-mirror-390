"""
Advanced bot example using Cogs (command groups).

Cogs are a way to organize commands into groups, similar to discord.py.
This makes it easier to manage large bots with many commands.
"""

import asyncio
from datetime import datetime
from interpal.ext.commands import Bot, Cog, Context, command, listener


# ============================================================================
# Define Cogs (Command Groups)
# ============================================================================

class GeneralCog(Cog):
    """General purpose commands"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.start_time = datetime.now()
    
    @command(name='ping')
    async def ping_command(self, ctx: Context):
        """Check if the bot is responsive"""
        await ctx.send("🏓 Pong!")
    
    @command(aliases=['info'])
    async def about(self, ctx: Context):
        """Get information about the bot"""
        profile = await self.bot.get_self()
        uptime = datetime.now() - self.start_time
        
        info_text = f"""
**Bot Information**
👤 Name: {profile.name}
📍 Location: {getattr(profile, 'city', 'N/A')}, {getattr(profile, 'country', 'N/A')}
⏱️ Uptime: {str(uptime).split('.')[0]}
⚡ Commands: {len(self.bot._commands)}
        """
        await ctx.send(info_text.strip())
    
    @listener('on_ready')
    async def on_ready(self):
        """Called when bot is ready"""
        print("✅ GeneralCog loaded and ready!")


class FunCog(Cog):
    """Fun and entertainment commands"""
    
    @command()
    async def joke(self, ctx: Context):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the bicycle fall over? It was two-tired!"
        ]
        
        import random
        joke = random.choice(jokes)
        await ctx.send(f"😄 {joke}")
    
    @command()
    async def roll(self, ctx: Context, dice: str = "1d6"):
        """
        Roll dice (e.g., 1d6, 2d20)
        
        Usage: !roll [dice notation]
        Example: !roll 2d6
        """
        try:
            count, sides = dice.lower().split('d')
            count = int(count)
            sides = int(sides)
            
            if count < 1 or count > 100:
                await ctx.send("Number of dice must be between 1 and 100!")
                return
            
            if sides < 2 or sides > 1000:
                await ctx.send("Number of sides must be between 2 and 1000!")
                return
            
            import random
            rolls = [random.randint(1, sides) for _ in range(count)]
            total = sum(rolls)
            
            result = f"🎲 Rolling {dice}:\n"
            result += f"Results: {', '.join(map(str, rolls))}\n"
            result += f"Total: {total}"
            
            await ctx.send(result)
        except ValueError:
            await ctx.send("Invalid dice format! Use format like: 1d6, 2d20, etc.")
    
    @command(aliases=['flip'])
    async def coinflip(self, ctx: Context):
        """Flip a coin"""
        import random
        result = random.choice(['Heads', 'Tails'])
        await ctx.send(f"🪙 The coin landed on: **{result}**!")
    
    @command()
    async def choose(self, ctx: Context, *choices):
        """
        Choose randomly from given options
        
        Usage: !choose option1 option2 option3
        """
        if len(choices) < 2:
            await ctx.send("Please provide at least 2 options!")
            return
        
        import random
        choice = random.choice(choices)
        await ctx.send(f"🤔 I choose: **{choice}**")


class SocialCog(Cog):
    """Social and user interaction commands"""
    
    @command()
    async def threads(self, ctx: Context):
        """Show your message threads"""
        await ctx.send("Fetching your message threads...")
        
        try:
            threads = await self.bot.get_threads()
            
            if threads:
                result = f"💬 You have {len(threads)} message threads:\n\n"
                for i, thread in enumerate(threads[:5], 1):
                    # Get last message info
                    last_msg = getattr(thread, 'last_message', None)
                    unread = getattr(thread, 'unread_count', 0)
                    
                    if last_msg:
                        preview = getattr(last_msg, 'content', '')[:30]
                        result += f"{i}. Thread {thread.id} "
                        if unread > 0:
                            result += f"({unread} unread) "
                        result += f"- {preview}...\n"
                    else:
                        result += f"{i}. Thread {thread.id}\n"
                
                if len(threads) > 5:
                    result += f"\n...and {len(threads) - 5} more!"
            else:
                result = "You don't have any message threads."
            
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"Failed to fetch threads: {str(e)}")
    
    @command()
    async def notifications(self, ctx: Context):
        """Check your notifications"""
        await ctx.send("Checking notifications...")
        
        try:
            notifs = await self.bot.get_notifications()
            
            if notifs:
                result = f"🔔 You have {len(notifs)} notifications:\n\n"
                for i, notif in enumerate(notifs[:5], 1):
                    notif_type = getattr(notif, 'type', 'unknown')
                    message = getattr(notif, 'message', 'No message')
                    result += f"{i}. [{notif_type}] {message}\n"
                
                if len(notifs) > 5:
                    result += f"\n...and {len(notifs) - 5} more!"
            else:
                result = "You don't have any notifications."
            
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"Failed to fetch notifications: {str(e)}")
    
    @command(aliases=['find'])
    async def search(self, ctx: Context, country: str = None):
        """
        Search for users by country
        
        Usage: !search <country>
        """
        if not country:
            await ctx.send("Please specify a country! Usage: !search <country>")
            return
        
        await ctx.send(f"🔍 Searching for users in {country}...")
        
        try:
            users = await self.bot.search_users(country=country)
            
            if users:
                result = f"Found {len(users)} users in {country}:\n\n"
                for i, user in enumerate(users[:5], 1):
                    name = getattr(user, 'name', 'Unknown')
                    age = getattr(user, 'age', '?')
                    city = getattr(user, 'city', 'Unknown')
                    result += f"{i}. {name}, {age} - {city}\n"
                
                if len(users) > 5:
                    result += f"\n...and {len(users) - 5} more!"
            else:
                result = f"No users found in {country}"
            
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"Search failed: {str(e)}")


class UtilityCog(Cog):
    """Utility commands"""
    
    @command()
    async def time(self, ctx: Context):
        """Get the current time"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%B %d, %Y")
        day_str = now.strftime("%A")
        
        result = f"⏰ **Current Time**\n"
        result += f"Time: {time_str}\n"
        result += f"Date: {date_str}\n"
        result += f"Day: {day_str}"
        
        await ctx.send(result)
    
    @command(aliases=['calc'])
    async def calculate(self, ctx: Context, *expression):
        """
        Calculate a math expression
        
        Usage: !calculate 2 + 2
        """
        if not expression:
            await ctx.send("Please provide a math expression!")
            return
        
        expr = ' '.join(expression)
        
        try:
            # Safe eval using only numbers and basic operators
            allowed_chars = set('0123456789+-*/().  ')
            if not all(c in allowed_chars for c in expr):
                await ctx.send("Invalid characters in expression! Only use: + - * / ( ) and numbers")
                return
            
            result = eval(expr)
            await ctx.send(f"🧮 Result: {expr} = **{result}**")
        except Exception as e:
            await ctx.send(f"Calculation failed: {str(e)}")
    
    @command()
    async def countdown(self, ctx: Context, seconds: int = 5):
        """
        Start a countdown
        
        Usage: !countdown [seconds]
        """
        if seconds < 1 or seconds > 60:
            await ctx.send("Countdown must be between 1 and 60 seconds!")
            return
        
        await ctx.send(f"⏳ Starting countdown from {seconds}...")
        
        for i in range(seconds, 0, -1):
            if i <= 3:
                await ctx.send(f"{i}...")
            await asyncio.sleep(1)
        
        await ctx.send("🎉 Time's up!")


# ============================================================================
# Bot Setup
# ============================================================================

def create_bot():
    """Create and configure the bot"""
    bot = Bot(
        command_prefix='!',
        description='Advanced Interpal Bot with Cogs',
        session_cookie='your_session_cookie_here',
        # username='your_username',
        # password='your_password',
        persist_session=True
    )
    
    # Add cogs
    bot.add_cog(GeneralCog(bot))
    bot.add_cog(FunCog(bot))
    bot.add_cog(SocialCog(bot))
    bot.add_cog(UtilityCog(bot))
    
    # Global event handlers
    @bot.event
    async def on_ready():
        print("🤖 Bot is online and ready!")
        profile = await bot.get_self()
        print(f"   Logged in as: {profile.name}")
        print(f"   Commands loaded: {len(bot._commands)}")
        print(f"   Cogs loaded: {len(bot._cogs)}")
        print("\n   Available cogs:")
        for cog_name in bot._cogs.keys():
            print(f"     • {cog_name}")
    
    @bot.event
    async def on_notification(data):
        """Log notifications"""
        notif_type = data.get('type', 'unknown')
        print(f"🔔 New notification: {notif_type}")
    
    return bot


def main():
    """Run the bot"""
    print("=" * 60)
    print("Advanced Interpal Bot with Cogs")
    print("=" * 60)
    
    bot = create_bot()
    
    # Check authentication
    if not bot.is_authenticated:
        print("\n⚠️  Please set your session_cookie or username/password in the code!")
        print("   Edit this file and add your credentials.\n")
        return
    
    # Run the bot
    print("\nStarting bot...\n")
    bot.run()


if __name__ == "__main__":
    main()

