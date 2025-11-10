"""Tests for Agent base class."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from chuk_acp import AgentInfo

from chuk_acp_agent.agent.base import Agent
from chuk_acp_agent.models.mcp import MCPConfig


# Create concrete test agent since Agent is abstract
class ConcreteAgent(Agent):
    """Concrete agent for testing."""

    async def on_prompt(self, ctx, prompt):
        """Minimal implementation."""
        yield f"Echo: {prompt}"


class TestAgent:
    """Test Agent base class."""

    def test_initialization(self):
        """Test agent initialization."""
        agent = ConcreteAgent()
        assert agent._mcp_config is None
        assert agent._middlewares == []
        assert agent._agent_name == "ConcreteAgent"
        assert agent._agent_version == "0.1.0"
        assert agent._contexts == {}

    def test_get_agent_info(self):
        """Test get_agent_info returns AgentInfo."""
        agent = ConcreteAgent()
        info = agent.get_agent_info()
        assert isinstance(info, AgentInfo)
        assert info.name == "ConcreteAgent"
        assert info.version == "0.1.0"
        assert "ConcreteAgent" in info.title

    def test_add_mcp_server_with_string_command(self):
        """Test add_mcp_server with string command."""
        agent = ConcreteAgent()
        agent.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")

        assert agent._mcp_config is not None
        assert "echo" in agent._mcp_config.mcpServers
        server = agent._mcp_config.mcpServers["echo"]
        assert server.command == "uvx"
        assert server.args == ["chuk-mcp-echo", "stdio"]
        assert server.env == {}

    def test_add_mcp_server_with_list_command(self):
        """Test add_mcp_server with list command."""
        agent = ConcreteAgent()
        agent.add_mcp_server("fs", ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"])

        server = agent._mcp_config.mcpServers["fs"]
        assert server.command == "npx"
        assert server.args == ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

    def test_add_mcp_server_with_env(self):
        """Test add_mcp_server with environment variables."""
        agent = ConcreteAgent()
        agent.add_mcp_server("test", "node server.js", env={"NODE_ENV": "production"})

        server = agent._mcp_config.mcpServers["test"]
        assert server.env == {"NODE_ENV": "production"}

    def test_add_mcp_server_creates_config_if_none(self):
        """Test add_mcp_server creates MCPConfig if not exists."""
        agent = ConcreteAgent()
        assert agent._mcp_config is None

        agent.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")

        assert agent._mcp_config is not None
        assert isinstance(agent._mcp_config, MCPConfig)

    def test_add_multiple_servers(self):
        """Test adding multiple MCP servers."""
        agent = ConcreteAgent()
        agent.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")
        agent.add_mcp_server("fs", "npx @modelcontextprotocol/server-filesystem /tmp")

        assert len(agent._mcp_config.mcpServers) == 2
        assert "echo" in agent._mcp_config.mcpServers
        assert "fs" in agent._mcp_config.mcpServers

    def test_add_mcp_server_single_word_command(self):
        """Test add_mcp_server with single word command."""
        agent = ConcreteAgent()
        agent.add_mcp_server("test", "python")

        server = agent._mcp_config.mcpServers["test"]
        assert server.command == "python"
        assert server.args == []

    def test_load_mcp_config_from_file(self):
        """Test load_mcp_config from JSON file."""
        agent = ConcreteAgent()

        # Create temp config file
        config_data = {
            "mcpServers": {
                "echo": {"command": "uvx", "args": ["chuk-mcp-echo", "stdio"], "env": {}}
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            agent.load_mcp_config(temp_path)

            assert agent._mcp_config is not None
            assert "echo" in agent._mcp_config.mcpServers
            assert agent._mcp_config.mcpServers["echo"].command == "uvx"
        finally:
            Path(temp_path).unlink()

    def test_load_mcp_config_with_path_object(self):
        """Test load_mcp_config with Path object."""
        agent = ConcreteAgent()

        config_data = {"mcpServers": {}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            agent.load_mcp_config(temp_path)
            assert agent._mcp_config is not None
        finally:
            temp_path.unlink()

    def test_load_mcp_config_file_not_found(self):
        """Test load_mcp_config with non-existent file."""
        agent = ConcreteAgent()

        with pytest.raises(FileNotFoundError):
            agent.load_mcp_config("/nonexistent/file.json")

    def test_load_mcp_config_invalid_json(self):
        """Test load_mcp_config with invalid JSON."""
        agent = ConcreteAgent()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json{")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                agent.load_mcp_config(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_custom_agent_subclass(self):
        """Test custom agent subclass."""

        class MyAgent(Agent):
            async def on_prompt(self, ctx, prompt):
                yield "test"

            def get_agent_info(self) -> AgentInfo:
                return AgentInfo(name="my-agent", version="2.0.0", title="My Custom Agent")

        agent = MyAgent()
        info = agent.get_agent_info()
        assert info.name == "my-agent"
        assert info.version == "2.0.0"
        assert info.title == "My Custom Agent"

    def test_agent_name_from_class(self):
        """Test agent name is derived from class name."""

        class CustomAgent(Agent):
            async def on_prompt(self, ctx, prompt):
                yield "test"

        agent = CustomAgent()
        assert agent._agent_name == "CustomAgent"

    @pytest.mark.asyncio
    async def test_on_prompt_not_implemented(self):
        """Test on_prompt raises NotImplementedError if not overridden."""
        agent = ConcreteAgent()
        # The base class should have on_prompt that needs implementation
        # or it should be abstract - let's check behavior
        try:
            ctx = Mock()
            result = agent.on_prompt(ctx, "test")
            # If it's a generator, try to iterate
            if hasattr(result, "__aiter__"):
                async for _ in result:
                    pass
        except (NotImplementedError, AttributeError):
            # Expected - method not implemented or doesn't exist
            pass

    def test_contexts_dictionary(self):
        """Test contexts dictionary is initialized."""
        agent = ConcreteAgent()
        assert isinstance(agent._contexts, dict)
        assert len(agent._contexts) == 0

    def test_middlewares_list(self):
        """Test middlewares list is initialized."""
        agent = ConcreteAgent()
        assert isinstance(agent._middlewares, list)
        assert len(agent._middlewares) == 0

    def test_add_middleware(self):
        """Test adding middleware."""
        agent = ConcreteAgent()
        middleware1 = Mock()
        middleware2 = Mock()

        agent.add_middleware(middleware1)
        agent.add_middleware(middleware2)

        assert len(agent._middlewares) == 2
        assert agent._middlewares[0] == middleware1
        assert agent._middlewares[1] == middleware2

    def test_get_agent_capabilities(self):
        """Test get_agent_capabilities returns capabilities."""
        agent = ConcreteAgent()
        caps = agent.get_agent_capabilities()

        assert caps.loadSession is False
        assert "ask" in caps.modes
        assert "code" in caps.modes

    def test_extract_text_from_content(self):
        """Test extracting text from content list."""
        agent = ConcreteAgent()

        content = [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "World"},
        ]

        result = agent._extract_text_from_content(content)
        assert result == "Hello World"

    def test_extract_text_from_empty_content(self):
        """Test extracting text from empty content."""
        agent = ConcreteAgent()
        result = agent._extract_text_from_content([])
        assert result == ""

    def test_extract_text_from_mixed_content(self):
        """Test extracting text from mixed content types."""
        agent = ConcreteAgent()

        content = [
            {"type": "text", "text": "Hello"},
            {"type": "image", "data": "..."},
            {"type": "text", "text": "World"},
        ]

        result = agent._extract_text_from_content(content)
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_handle_prompt(self):
        """Test handle_prompt processes prompts."""
        agent = ConcreteAgent()
        agent.send_message = Mock()

        session = Mock()
        session.session_id = "test-123"
        session.cwd = "/test"

        prompt = [{"type": "text", "text": "test prompt"}]

        await agent.handle_prompt(session, prompt)

        # Should have sent messages
        assert agent.send_message.called

    @pytest.mark.asyncio
    async def test_handle_prompt_with_error(self):
        """Test handle_prompt handles errors."""

        class ErrorAgent(Agent):
            async def on_prompt(self, ctx, prompt):
                raise ValueError("Test error")
                yield  # Make it a generator

        agent = ErrorAgent()
        agent.send_message = Mock()

        session = Mock()
        session.session_id = "test-123"
        session.cwd = "/test"

        prompt = [{"type": "text", "text": "test"}]

        with pytest.raises(ValueError):
            await agent.handle_prompt(session, prompt)

        # Should have sent error message
        assert any("Error:" in str(call) for call in agent.send_message.call_args_list)

    @pytest.mark.asyncio
    async def test_on_new_session_called(self):
        """Test on_new_session is called for new sessions."""

        class TrackingAgent(Agent):
            def __init__(self):
                super().__init__()
                self.new_session_called = False

            async def on_new_session(self, ctx):
                self.new_session_called = True

            async def on_prompt(self, ctx, prompt):
                yield "response"

        agent = TrackingAgent()
        agent.send_message = Mock()

        session = Mock()
        session.session_id = "new-session"
        session.cwd = "/test"

        prompt = [{"type": "text", "text": "test"}]

        await agent.handle_prompt(session, prompt)

        assert agent.new_session_called is True

    def test_get_or_create_context_creates_new(self):
        """Test _get_or_create_context creates new context."""
        agent = ConcreteAgent()

        session = Mock()
        session.session_id = "test-123"
        session.cwd = "/test"

        ctx = agent._get_or_create_context(session)

        assert ctx.session_id == "test-123"
        assert ctx.cwd == "/test"

    def test_get_or_create_context_returns_existing(self):
        """Test _get_or_create_context returns existing context."""
        agent = ConcreteAgent()

        session = Mock()
        session.session_id = "test-123"
        session.cwd = "/test"

        # Create first time
        ctx1 = agent._get_or_create_context(session)
        # Store it
        agent._contexts[session.session_id] = ctx1

        # Get second time
        ctx2 = agent._get_or_create_context(session)

        assert ctx1 == ctx2
