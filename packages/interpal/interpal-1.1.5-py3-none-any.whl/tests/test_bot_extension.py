"""
Tests for the Bot extension (interpal.ext.commands).
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from interpal.ext.commands import Bot, Context, Command, Cog, command, listener


class TestCommand:
    """Test Command class"""
    
    def test_command_creation(self):
        """Test basic command creation"""
        async def test_func(ctx):
            pass
        
        cmd = Command(test_func, name='test')
        assert cmd.name == 'test'
        assert cmd.callback == test_func
        assert cmd.enabled is True
        assert cmd.hidden is False
    
    def test_command_with_aliases(self):
        """Test command with aliases"""
        async def test_func(ctx):
            pass
        
        cmd = Command(test_func, name='test', aliases=['t', 'testing'])
        assert cmd.name == 'test'
        assert 't' in cmd.aliases
        assert 'testing' in cmd.aliases
    
    def test_command_help_from_docstring(self):
        """Test help text from docstring"""
        async def test_func(ctx):
            """This is help text"""
            pass
        
        cmd = Command(test_func)
        assert cmd.help == "This is help text"
        assert cmd.brief == "This is help text"
    
    def test_command_params_parsing(self):
        """Test parameter parsing"""
        async def test_func(ctx, arg1, arg2: int = 5):
            pass
        
        cmd = Command(test_func)
        assert 'arg1' in cmd.params
        assert 'arg2' in cmd.params
        assert cmd.params['arg1']['required'] is True
        assert cmd.params['arg2']['required'] is False
        assert cmd.params['arg2']['default'] == 5


class TestContext:
    """Test Context class"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot"""
        bot = Mock(spec=Bot)
        bot.send_message = AsyncMock()
        return bot
    
    @pytest.fixture
    def mock_message(self):
        """Create a mock message"""
        return {
            'thread_id': '12345',
            'sender': {
                'name': 'TestUser',
                'id': 'user123'
            },
            'content': '!test arg1 arg2'
        }
    
    @pytest.fixture
    def mock_command(self):
        """Create a mock command"""
        async def test_func(ctx):
            pass
        return Command(test_func, name='test')
    
    def test_context_creation(self, mock_bot, mock_message, mock_command):
        """Test context initialization"""
        ctx = Context(
            bot=mock_bot,
            message=mock_message,
            command=mock_command,
            prefix='!',
            invoked_with='test'
        )
        
        assert ctx.bot == mock_bot
        assert ctx.thread_id == '12345'
        assert ctx.sender_name == 'TestUser'
        assert ctx.sender_id == 'user123'
        assert ctx.content == '!test arg1 arg2'
        assert ctx.prefix == '!'
        assert ctx.invoked_with == 'test'
    
    @pytest.mark.asyncio
    async def test_context_send(self, mock_bot, mock_message, mock_command):
        """Test sending a message through context"""
        ctx = Context(
            bot=mock_bot,
            message=mock_message,
            command=mock_command,
            prefix='!',
            invoked_with='test'
        )
        
        await ctx.send("Test message")
        mock_bot.send_message.assert_called_once_with('12345', "Test message")


class TestBot:
    """Test Bot class"""
    
    @pytest.fixture
    def bot(self):
        """Create a test bot (without actual auth)"""
        with patch('interpal.ext.commands.AsyncInterpalClient.__init__', return_value=None):
            bot = Bot(command_prefix='!')
            bot.auth = Mock()
            bot.http = Mock()
            bot._ws_client = None
            bot.send_message = AsyncMock()
            bot.get_self = AsyncMock(return_value=Mock(name="TestBot"))
            return bot
    
    def test_bot_initialization(self, bot):
        """Test bot initialization"""
        assert bot.command_prefix == ['!']
        assert bot.case_insensitive is True
        assert isinstance(bot._commands, dict)
        assert isinstance(bot._cogs, dict)
    
    def test_command_decorator(self, bot):
        """Test command decorator"""
        @bot.command(name='test')
        async def test_command(ctx):
            """Test command"""
            await ctx.send("Test")
        
        assert 'test' in bot._commands
        assert bot._commands['test'].name == 'test'
    
    def test_command_with_aliases(self, bot):
        """Test command with aliases"""
        @bot.command(name='test', aliases=['t', 'testing'])
        async def test_command(ctx):
            pass
        
        assert 'test' in bot._commands
        assert 't' in bot._commands
        assert 'testing' in bot._commands
        # All should point to the same command
        assert bot._commands['test'] == bot._commands['t']
        assert bot._commands['test'] == bot._commands['testing']
    
    def test_case_insensitive(self, bot):
        """Test case insensitive commands"""
        @bot.command(name='Test')
        async def test_command(ctx):
            pass
        
        # Should be stored as lowercase
        assert 'test' in bot._commands
    
    def test_get_command(self, bot):
        """Test getting a command"""
        @bot.command(name='test')
        async def test_command(ctx):
            pass
        
        cmd = bot.get_command('test')
        assert cmd is not None
        assert cmd.name == 'test'
    
    def test_remove_command(self, bot):
        """Test removing a command"""
        @bot.command(name='test')
        async def test_command(ctx):
            pass
        
        assert 'test' in bot._commands
        bot.remove_command('test')
        assert 'test' not in bot._commands
    
    @pytest.mark.asyncio
    async def test_command_parsing(self, bot):
        """Test command message parsing"""
        @bot.command(name='test')
        async def test_command(ctx):
            await ctx.send("Executed")
        
        # Simulate message
        message_data = {
            'thread_id': '123',
            'sender': {'name': 'User', 'id': 'user1'},
            'content': '!test'
        }
        
        await bot._handle_message(message_data)
        # Should invoke the command


class TestCog:
    """Test Cog functionality"""
    
    def test_cog_creation(self):
        """Test basic cog creation"""
        class TestCog(Cog):
            def __init__(self, bot):
                super().__init__(bot)
        
        bot_mock = Mock(spec=Bot)
        cog = TestCog(bot_mock)
        assert cog.bot == bot_mock
    
    def test_cog_with_commands(self):
        """Test cog with commands"""
        class TestCog(Cog):
            @command(name='test')
            async def test_command(self, ctx):
                """Test command"""
                pass
        
        bot_mock = Mock(spec=Bot)
        cog = TestCog(bot_mock)
        
        commands = cog.get_commands()
        assert len(commands) == 1
        assert commands[0].name == 'test'
    
    def test_cog_with_listener(self):
        """Test cog with event listener"""
        class TestCog(Cog):
            @listener('on_ready')
            async def ready_handler(self):
                pass
        
        bot_mock = Mock(spec=Bot)
        cog = TestCog(bot_mock)
        
        assert 'on_ready' in cog._listeners
    
    @pytest.fixture
    def bot_with_cog(self):
        """Create a bot with a test cog"""
        with patch('interpal.ext.commands.AsyncInterpalClient.__init__', return_value=None):
            bot = Bot(command_prefix='!')
            bot.auth = Mock()
            bot.http = Mock()
            
            class TestCog(Cog):
                @command(name='cogtest')
                async def test_command(self, ctx):
                    await ctx.send("From cog")
            
            bot.add_cog(TestCog(bot))
            return bot
    
    def test_bot_add_cog(self, bot_with_cog):
        """Test adding cog to bot"""
        assert 'TestCog' in bot_with_cog._cogs
        assert 'cogtest' in bot_with_cog._commands
    
    def test_bot_remove_cog(self, bot_with_cog):
        """Test removing cog from bot"""
        bot_with_cog.remove_cog('TestCog')
        assert 'TestCog' not in bot_with_cog._cogs
        assert 'cogtest' not in bot_with_cog._commands


class TestCommandDecorator:
    """Test standalone command decorator"""
    
    def test_command_decorator(self):
        """Test command decorator creates Command object"""
        @command(name='test')
        async def test_func(ctx):
            """Test function"""
            pass
        
        assert hasattr(test_func, '__command__')
        assert isinstance(test_func.__command__, Command)
        assert test_func.__command__.name == 'test'


class TestListenerDecorator:
    """Test listener decorator"""
    
    def test_listener_decorator(self):
        """Test listener decorator marks method"""
        @listener('on_message')
        async def test_listener(data):
            pass
        
        assert hasattr(test_listener, '__listener__')
        assert test_listener.__listener__ == 'on_message'


class TestCommandInvocation:
    """Test command invocation and argument parsing"""
    
    @pytest.fixture
    def bot(self):
        """Create a test bot"""
        with patch('interpal.ext.commands.AsyncInterpalClient.__init__', return_value=None):
            bot = Bot(command_prefix='!')
            bot.auth = Mock()
            bot.http = Mock()
            bot.send_message = AsyncMock()
            return bot
    
    @pytest.mark.asyncio
    async def test_simple_command_invocation(self, bot):
        """Test invoking a simple command"""
        executed = []
        
        @bot.command(name='test')
        async def test_command(ctx):
            executed.append(True)
        
        message_data = {
            'thread_id': '123',
            'sender': {'name': 'User', 'id': 'user1'},
            'content': '!test'
        }
        
        await bot._handle_message(message_data)
        assert len(executed) == 1
    
    @pytest.mark.asyncio
    async def test_command_with_args(self, bot):
        """Test command with arguments"""
        received_args = []
        
        @bot.command(name='test')
        async def test_command(ctx, arg1, arg2):
            received_args.extend([arg1, arg2])
        
        message_data = {
            'thread_id': '123',
            'sender': {'name': 'User', 'id': 'user1'},
            'content': '!test hello world'
        }
        
        await bot._handle_message(message_data)
        assert received_args == ['hello', 'world']
    
    @pytest.mark.asyncio
    async def test_command_type_conversion(self, bot):
        """Test automatic type conversion"""
        received_args = []
        
        @bot.command(name='test')
        async def test_command(ctx, num: int):
            received_args.append(num)
        
        message_data = {
            'thread_id': '123',
            'sender': {'name': 'User', 'id': 'user1'},
            'content': '!test 42'
        }
        
        await bot._handle_message(message_data)
        assert received_args == [42]
        assert isinstance(received_args[0], int)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

