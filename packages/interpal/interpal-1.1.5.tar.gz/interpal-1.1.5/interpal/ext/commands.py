"""
Discord.py-style command framework for Interpal bots.

This module provides a command framework similar to discord.py's commands extension,
making it easy to create command-based bots with decorators.

Example:
    from interpal.ext.commands import Bot

    bot = Bot(command_prefix='!', session_cookie='your_cookie')

    @bot.command()
    async def hello(ctx, name=None):
        '''Say hello to someone'''
        if name:
            await ctx.send(f'Hello {name}!')
        else:
            await ctx.send('Hello!')

    @bot.event
    async def on_ready():
        print('Bot is ready!')

    bot.run()
"""

import asyncio
import inspect
import shlex
from typing import Optional, Callable, Dict, List, Any, Union, get_origin, get_args
from ..client import AsyncInterpalClient
from ..models.events import ThreadNewMessageEvent
from ..models.user import User


class Context:
    """
    Represents the context in which a command is being invoked.
    
    Attributes:
        bot: The bot instance
        message: The message data that triggered the command (dict or ThreadNewMessageEvent)
        event: The ThreadNewMessageEvent if available
        command: The command being invoked
        args: List of arguments passed to the command
        kwargs: Dict of keyword arguments
        prefix: The prefix used to invoke the command
        invoked_with: The alias used to invoke the command
        sender: User object or dict with sender information
        sender_id: ID of the user who sent the message
        sender_name: Name of the user who sent the message
        thread_id: ID of the message thread
        content: The message content
    """
    
    def __init__(
        self,
        bot: 'Bot',
        message: Union[Dict[str, Any], ThreadNewMessageEvent],
        command: 'Command',
        prefix: str,
        invoked_with: str,
        args: List[str] = None,
        kwargs: Dict[str, Any] = None
    ):
        self.bot = bot
        self.message = message
        self.command = command
        self.prefix = prefix
        self.invoked_with = invoked_with
        self.args = args or []
        self.kwargs = kwargs or {}
        
        # Check if message is the new ThreadNewMessageEvent model
        if isinstance(message, ThreadNewMessageEvent):
            self.event = message
            self.sender: Union[User, Dict[str, Any]] = message.sender
            self.sender_id = message.sender.id if message.sender else None
            self.sender_name = message.sender.name if message.sender else 'Unknown'
            self.thread_id = message.data.thread_id if message.data else None
            self.content = message.data.message if message.data else ''
            self.counters = message.counters
            self.click_url = message.click_url
        else:
            # Legacy dict format support
            self.event = None
            self.thread_id = message.get('thread_id')
            # Handle both formats: nested sender dict or flat sender_id
            self.sender = message.get('sender', {})
            self.sender_id = message.get('sender_id') or (self.sender.get('id') if isinstance(self.sender, dict) else None)
            self.sender_name = self.sender.get('name', 'Unknown') if isinstance(self.sender, dict) else 'Unknown'
            self.content = message.get('message', message.get('content', ''))
            self.counters = None
            self.click_url = None
    
    async def send(self, content: str):
        """Send a message to the same thread."""
        if self.thread_id:
            await self.bot.send_message(self.thread_id, content)
    
    async def reply(self, content: str):
        """Reply to the message (same as send in Interpal)."""
        await self.send(content)
    
    async def typing(self):
        """Send typing indicator."""
        if self.thread_id:
            # Assuming there's a set_typing method
            try:
                await self.bot.messages.set_typing(self.thread_id)
            except:
                pass
    
    @property
    def has_event(self) -> bool:
        """Check if this context has a ThreadNewMessageEvent."""
        return self.event is not None
    
    @property
    def author(self) -> Union[User, Dict[str, Any], None]:
        """Alias for sender (discord.py compatibility)."""
        return self.sender
    
    def get_sender_avatar(self, size: str = 'medium') -> Optional[str]:
        """
        Get sender's avatar URL.
        
        Args:
            size: Avatar size ('small', 'medium', 'large', or 'url' for full size)
        
        Returns:
            Avatar URL or None
        """
        if isinstance(self.sender, User):
            if size == 'small':
                return self.sender.avatar_thumb_small
            elif size == 'large':
                return self.sender.avatar_thumb_large
            elif size == 'url':
                return self.sender.avatar_url
            else:  # medium
                return self.sender.avatar_thumb_medium or self.sender.avatar_url
        return None


class Command:
    """
    Represents a bot command.
    
    Attributes:
        name: The command name
        callback: The function to call
        aliases: Alternative names for the command
        help: Help text for the command
        brief: Brief description
        enabled: Whether the command is enabled
        hidden: Whether to hide from help
    """
    
    def __init__(
        self,
        callback: Callable,
        name: str = None,
        aliases: List[str] = None,
        help: str = None,
        brief: str = None,
        enabled: bool = True,
        hidden: bool = False,
        **kwargs
    ):
        self.callback = callback
        self.name = name or callback.__name__
        self.aliases = aliases or []
        self.help = help or inspect.getdoc(callback) or 'No help available'
        self.brief = brief or self.help.split('\n')[0]
        self.enabled = enabled
        self.hidden = hidden
        self.params = self._parse_params()
        self.cog = None  # Set when added to a cog
        
    def _parse_params(self) -> Dict[str, Any]:
        """Parse function parameters."""
        sig = inspect.signature(self.callback)
        params = {}
        
        for name, param in sig.parameters.items():
            if name in ('self', 'ctx'):
                continue
            
            params[name] = {
                'name': name,
                'default': param.default if param.default != inspect.Parameter.empty else None,
                'annotation': param.annotation if param.annotation != inspect.Parameter.empty else None,
                'required': param.default == inspect.Parameter.empty
            }
        
        return params
    
    async def invoke(self, ctx: Context, *args, **kwargs):
        """Invoke the command."""
        if not self.enabled:
            await ctx.send(f"Command `{self.name}` is currently disabled.")
            return
        
        try:
            if self.cog:
                await self.callback(self.cog, ctx, *args, **kwargs)
            else:
                await self.callback(ctx, *args, **kwargs)
        except Exception as e:
            await self._handle_error(ctx, e)
    
    async def _handle_error(self, ctx: Context, error: Exception):
        """Handle command errors."""
        error_msg = f"Error in command `{self.name}`: {str(error)}"
        await ctx.send(error_msg)
        
        # Also raise to bot error handler
        if hasattr(ctx.bot, 'on_command_error'):
            await ctx.bot.on_command_error(ctx, error)


class Cog:
    """
    A cog is a collection of commands and listeners.
    
    Example:
        class MyCog(Cog):
            def __init__(self, bot):
                self.bot = bot
            
            @command()
            async def mycommand(self, ctx):
                await ctx.send('Hello from cog!')
    """
    
    def __init__(self, bot: 'Bot' = None):
        self.bot = bot
        self._commands = {}
        self._listeners = {}
        
        # Auto-register commands and listeners
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '__command__'):
                cmd = method.__command__
                cmd.cog = self
                self._commands[cmd.name] = cmd
            elif hasattr(method, '__listener__'):
                event_name = method.__listener__
                if event_name not in self._listeners:
                    self._listeners[event_name] = []
                self._listeners[event_name].append(method)
    
    def get_commands(self) -> List[Command]:
        """Get all commands in this cog."""
        return list(self._commands.values())


class Bot(AsyncInterpalClient):
    """
    A bot client with command handling capabilities.
    
    This extends AsyncInterpalClient with a command framework similar to discord.py.
    Supports structured WebSocket event models for type-safe message handling.
    
    Example:
        bot = Bot(command_prefix='!', username='user', password='pass')
        
        @bot.command()
        async def hello(ctx):
            # ctx.sender is now a User object with full information
            await ctx.send(f'Hello {ctx.sender.name}!')
        
        @bot.event
        async def on_message(event: ThreadNewMessageEvent):
            # Receive structured event data
            print(f"Message from {event.sender.name}: {event.message}")
        
        bot.run()
    """
    
    def __init__(
        self,
        command_prefix: Union[str, List[str], Callable] = '!',
        description: str = None,
        help_command: bool = True,
        case_insensitive: bool = True,
        **kwargs
    ):
        """
        Initialize the bot.
        
        Args:
            command_prefix: The command prefix (e.g., '!' or ['!', '?'])
            description: Bot description for help command
            help_command: Whether to add default help command
            case_insensitive: Whether commands are case insensitive
            **kwargs: Additional arguments passed to AsyncInterpalClient
        """
        super().__init__(**kwargs)
        
        self.command_prefix = command_prefix if isinstance(command_prefix, list) else [command_prefix]
        self.description = description or "Interpal Bot"
        self.case_insensitive = case_insensitive
        self._commands: Dict[str, Command] = {}
        self._cogs: Dict[str, Cog] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._bot_user_id: Optional[Union[int, str]] = self._normalize_bot_id(self.bot_id)
        self._user_on_message_handlers: List[Callable] = []  # User-defined on_message handlers
        
        # Register built-in message handler (supports ThreadNewMessageEvent)
        # Use internal event name to avoid conflicts
        if self._ws_client is None:
            from ..websocket import WebSocketClient
            self._ws_client = WebSocketClient(self.auth)
        self._ws_client.register_event('on_message', self._handle_message)
        
        # Add default help command
        if help_command:
            self.add_command(Command(self._default_help_command, name='help'))
    
        if self._bot_user_id is not None:
            self.bot_id = str(self._bot_user_id)

    def command(
        self,
        name: str = None,
        aliases: List[str] = None,
        **kwargs
    ):
        """
        Decorator to register a command.
        
        Example:
            @bot.command(name='greet', aliases=['hello', 'hi'])
            async def greet_command(ctx, user=None):
                '''Greet a user'''
                await ctx.send(f'Hello {user or ctx.sender_name}!')
        """
        def decorator(func: Callable) -> Callable:
            cmd = Command(func, name=name, aliases=aliases, **kwargs)
            self.add_command(cmd)
            func.__command__ = cmd
            return func
        return decorator
    
    def event(self, name_or_func: Union[str, Callable, None] = None):
        """
        Decorator to register an event handler.
        
        Can be used with or without parentheses:
        
        Example:
            @bot.event
            async def on_ready():
                print('Bot is ready!')
            
            @bot.event()
            async def on_message(event: ThreadNewMessageEvent):
                print(f"Message: {event.message}")
            
            @bot.event('on_message')
            async def my_handler(event):
                print(f"Message: {event.message}")
        """
        # Handle both @bot.event and @bot.event() syntax
        def decorator(func: Callable) -> Callable:
            # Determine event name
            if callable(name_or_func):
                # Called as @bot.event without parentheses - name_or_func is the function
                event_name = func.__name__
            elif isinstance(name_or_func, str):
                # Called as @bot.event('name')
                event_name = name_or_func
            else:
                # Called as @bot.event() - use function name
                event_name = func.__name__
            
            # Special handling for on_message - store separately to call after command processing
            if event_name == 'on_message':
                self._user_on_message_handlers.append(func)
                return func
            
            # Ensure WebSocket client exists
            if self._ws_client is None:
                from ..websocket import WebSocketClient
                self._ws_client = WebSocketClient(self.auth)
            
            # Register with WebSocket client's event system
            self._ws_client.register_event(event_name, func)
            
            # Also track in our handlers
            if event_name not in self._event_handlers:
                self._event_handlers[event_name] = []
            self._event_handlers[event_name].append(func)
            
            return func
        
        # If called without parentheses (@bot.event), name_or_func is the function
        if callable(name_or_func):
            return decorator(name_or_func)
        
        # Otherwise return decorator to be called with the function
        return decorator
    
    def add_command(self, command: Command):
        """Add a command to the bot."""
        if self.case_insensitive:
            command.name = command.name.lower()
            command.aliases = [a.lower() for a in command.aliases]
        
        self._commands[command.name] = command
        
        # Add aliases
        for alias in command.aliases:
            self._commands[alias] = command
    
    def remove_command(self, name: str) -> Optional[Command]:
        """Remove a command."""
        name = name.lower() if self.case_insensitive else name
        return self._commands.pop(name, None)
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by name."""
        name = name.lower() if self.case_insensitive else name
        return self._commands.get(name)
    
    def add_cog(self, cog: Cog):
        """Add a cog to the bot."""
        cog.bot = self
        self._cogs[cog.__class__.__name__] = cog
        
        # Register cog commands
        for cmd in cog.get_commands():
            self.add_command(cmd)
        
        # Register cog listeners
        for event_name, listeners in cog._listeners.items():
            for listener in listeners:
                if event_name not in self._event_handlers:
                    self._event_handlers[event_name] = []
                self._event_handlers[event_name].append(listener)
    
    def remove_cog(self, name: str) -> Optional[Cog]:
        """Remove a cog."""
        cog = self._cogs.pop(name, None)
        if cog:
            # Remove cog commands
            for cmd in cog.get_commands():
                self.remove_command(cmd.name)
        return cog
    
    def get_cog(self, name: str) -> Optional[Cog]:
        """Get a cog by name."""
        return self._cogs.get(name)
    
    def set_bot_user_id(self, user_id: Union[int, str]):
        """
        Manually set the bot's user ID to prevent it from responding to its own messages.
        
        Args:
            user_id: The bot's user ID
        """
        self._bot_user_id = self._normalize_bot_id(user_id)
        if self._bot_user_id is not None:
            self.bot_id = str(self._bot_user_id)

    @staticmethod
    def _normalize_bot_id(value: Optional[Any]) -> Optional[Union[int, str]]:
        """Normalize bot ID storing ints where possible and falling back to strings."""
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return str(value)
            except Exception:
                return None
    
    async def _handle_message(self, event: Union[Dict[str, Any], ThreadNewMessageEvent]):
        """
        Handle incoming messages and process commands.
        
        Args:
            event: Either a ThreadNewMessageEvent (new format) or dict (legacy format)
        """
        # Extract content and sender_id from event
        if isinstance(event, ThreadNewMessageEvent):
            content = event.message or ''
            sender_id = event.sender.id if event.sender else None
            sender_name = event.sender.name if event.sender else 'Unknown'
        else:
            content = event.get('message', event.get('content', ''))
            sender = event.get('sender', {})
            sender_id = event.get('sender_id') or (sender.get('id') if isinstance(sender, dict) else None)
        
        # Get bot's user ID if not already stored
        if self._bot_user_id is None and self.bot_id is not None:
            self._bot_user_id = self._normalize_bot_id(self.bot_id)

        if self._bot_user_id is None:
            try:
                user_profile = await self.get_self()
                if user_profile and hasattr(user_profile, 'id'):
                    self._bot_user_id = self._normalize_bot_id(user_profile.id)
                elif user_profile and isinstance(user_profile, dict) and 'id' in user_profile:
                    self._bot_user_id = self._normalize_bot_id(user_profile['id'])
                if self._bot_user_id is not None:
                    self.bot_id = str(self._bot_user_id)
            except Exception as e:
                print(f"⚠️  Could not fetch bot user ID: {e}")
        
        # Ignore messages from the bot itself
        if sender_id and self._bot_user_id and str(sender_id) == str(self._bot_user_id):
            return
        
        # Call user-defined on_message handlers FIRST (for all messages)
        for handler in self._user_on_message_handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"❌ Error in on_message handler: {e}")
                import traceback
                traceback.print_exc()
        
        # Check if message starts with any prefix (for command processing)
        prefix_used = None
        for prefix in self.command_prefix:
            if content.startswith(prefix):
                prefix_used = prefix
                break
        
        if not prefix_used:
            return
        
        # Parse command
        content_without_prefix = content[len(prefix_used):].strip()
        
        try:
            # Use shlex to properly parse quoted strings
            parts = shlex.split(content_without_prefix)
        except ValueError:
            # Fallback to simple split if shlex fails
            parts = content_without_prefix.split()
        
        if not parts:
            return
        
        command_name = parts[0]
        if self.case_insensitive:
            command_name = command_name.lower()
        
        command = self.get_command(command_name)
        if not command:
            return
        
        # Parse arguments
        args = parts[1:]
        
        # Create context with event data
        ctx = Context(
            bot=self,
            message=event,
            command=command,
            prefix=prefix_used,
            invoked_with=command_name,
            args=args
        )
        
        # Invoke command
        await self._invoke_command(ctx, command, args)
    
    async def _invoke_command(self, ctx: Context, command: Command, args: List[str]):
        """Invoke a command with proper argument parsing."""
        try:
            # Simple argument parsing
            # Convert args to match function signature
            sig = inspect.signature(command.callback)
            params = [p for name, p in sig.parameters.items() if name not in ('self', 'ctx')]
            
            parsed_args = []
            for i, param in enumerate(params):
                # Check if this is the last parameter and it's a string
                # If so, join all remaining args (for multi-word arguments)
                is_last_param = (i == len(params) - 1)
                
                # Check if parameter is a string type (handles Optional[str] too)
                param_type = param.annotation
                is_string_param = (
                    param_type == inspect.Parameter.empty or 
                    param_type == str or
                    (get_origin(param_type) is Union and str in get_args(param_type))
                )
                
                if is_last_param and is_string_param and i < len(args):
                    # Join all remaining arguments with spaces
                    arg_value = ' '.join(args[i:])
                    parsed_args.append(arg_value)
                    break
                
                if i < len(args):
                    arg_value = args[i]
                    
                    # Try to convert to annotation type
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            if param.annotation == int:
                                arg_value = int(arg_value)
                            elif param.annotation == float:
                                arg_value = float(arg_value)
                            elif param.annotation == bool:
                                arg_value = arg_value.lower() in ('true', 'yes', '1', 'on')
                        except ValueError:
                            pass
                    
                    parsed_args.append(arg_value)
                elif param.default != inspect.Parameter.empty:
                    parsed_args.append(param.default)
                else:
                    # Missing required argument
                    await ctx.send(f"Missing required argument: `{param.name}`")
                    return
            
            await command.invoke(ctx, *parsed_args)
            
        except Exception as e:
            await self.on_command_error(ctx, e)
    
    async def on_command_error(self, ctx: Context, error: Exception):
        """
        Default error handler for commands.
        Override this method to customize error handling.
        """
        error_msg = f"❌ Error: {str(error)}"
        await ctx.send(error_msg)
        
        # Print to console for debugging
        print(f"Command error in {ctx.command.name}: {error}")
        import traceback
        traceback.print_exc()
    
    async def _default_help_command(self, ctx: Context, command_name: str = None):
        """
        Default help command implementation.
        
        Usage: !help [command]
        """
        if command_name:
            # Show help for specific command
            cmd = self.get_command(command_name)
            if not cmd or cmd.hidden:
                await ctx.send(f"Command `{command_name}` not found.")
                return
            
            help_text = f"**{ctx.prefix}{cmd.name}**"
            if cmd.aliases:
                help_text += f" (aliases: {', '.join(cmd.aliases)})"
            help_text += f"\n\n{cmd.help}"
            
            # Show parameters
            if cmd.params:
                help_text += "\n\n**Parameters:**"
                for param_name, param_info in cmd.params.items():
                    required = "required" if param_info['required'] else "optional"
                    default = f" (default: {param_info['default']})" if param_info['default'] is not None else ""
                    help_text += f"\n  • {param_name} - {required}{default}"
            
            await ctx.send(help_text)
        else:
            # Show all commands
            help_text = f"**{self.description}**\n\n"
            help_text += f"**Available Commands:** (prefix: {ctx.prefix})\n\n"
            
            # Group commands (skip aliases and hidden)
            shown_commands = {}
            for name, cmd in self._commands.items():
                if cmd.name == name and not cmd.hidden:
                    shown_commands[name] = cmd
            
            for name, cmd in sorted(shown_commands.items()):
                help_text += f"• **{name}** - {cmd.brief}\n"
            
            help_text += f"\n\nUse `{ctx.prefix}help <command>` for more info on a command."
            
            await ctx.send(help_text)
    
    async def start(self):
        """
        Override start() to ensure our WebSocket client is used.
        """
        # Make sure WebSocket client exists (should already exist from __init__)
        if self._ws_client is None:
            from ..websocket import WebSocketClient
            self._ws_client = WebSocketClient(self.auth)
            self._ws_client.register_event('on_message', self._handle_message)
        
        await self._ws_client.start()
    
    def run(self):
        """
        Start the bot and run indefinitely.
        
        This is a blocking call that will run until interrupted.
        """
        try:
            print(f"🤖 Starting {self.description}...")
            
            # Ensure authentication before starting
            if not self.is_authenticated:
                if self._username and self._password:
                    print("🔐 Logging in...")
                    self.login()
                else:
                    raise Exception("Not authenticated. Please provide username/password or session_cookie.")
            
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")
            raise


def command(name: str = None, **kwargs):
    """
    Decorator to create a command (can be used outside Bot class).
    
    Example:
        @command(name='test')
        async def my_test_command(ctx):
            await ctx.send('Test!')
    """
    def decorator(func: Callable) -> Callable:
        cmd = Command(func, name=name, **kwargs)
        func.__command__ = cmd
        return func
    return decorator


def listener(name: str = None):
    """
    Decorator to mark a method as an event listener in a Cog.
    
    Example:
        class MyCog(Cog):
            @listener('on_message')
            async def handle_message(self, data):
                print('Message received!')
    """
    def decorator(func: Callable) -> Callable:
        func.__listener__ = name or func.__name__
        return func
    return decorator

