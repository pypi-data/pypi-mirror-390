"""Tests for InteractiveAgent."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from chuk_acp_agent.agent.context import Context
from chuk_acp_agent.agent.interactive import InteractiveAgent
from chuk_acp_agent.models.tool import Tool


class TestInteractiveAgent:
    """Test InteractiveAgent class."""

    @pytest.fixture
    def agent(self):
        """Create test agent."""
        return InteractiveAgent()

    @pytest.fixture
    def agent_with_config(self):
        """Create test agent with MCP config."""
        agent = InteractiveAgent()
        agent.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")
        return agent

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        ctx = MagicMock(spec=Context)
        ctx.emit = AsyncMock()
        ctx.tools = MagicMock()
        ctx.tools.list = AsyncMock(return_value=[])
        ctx.tools.call = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_on_new_session_no_config(self, agent, mock_context):
        """Test on_new_session without MCP config."""
        await agent.on_new_session(mock_context)

        # Should emit welcome message
        mock_context.emit.assert_any_await("Interactive Agent Ready!\n\n")
        mock_context.emit.assert_any_await("No MCP servers configured.\n")
        mock_context.emit.assert_any_await("Use --mcp-config-file to load MCP servers.\n\n")

    @pytest.mark.asyncio
    async def test_on_new_session_with_config(self, agent_with_config, mock_context):
        """Test on_new_session with MCP config."""
        # Mock tool list
        mock_context.tools.list = AsyncMock(
            return_value=[
                Tool(name="echo_text", description="Echo text"),
                Tool(name="echo_uppercase", description="Echo in uppercase"),
            ]
        )

        await agent_with_config.on_new_session(mock_context)

        # Should emit welcome and tool count
        mock_context.emit.assert_any_await("Interactive Agent Ready!\n\n")
        # The message is emitted in parts due to f-string formatting
        mock_context.emit.assert_any_await("Loaded 2 MCP tools from ")
        mock_context.emit.assert_any_await("1 servers\n\n")
        mock_context.emit.assert_any_await("Commands:\n")

    @pytest.mark.asyncio
    async def test_on_new_session_with_config_no_tools(self, agent_with_config, mock_context):
        """Test on_new_session with config but no tools."""
        mock_context.tools.list = AsyncMock(return_value=[])

        await agent_with_config.on_new_session(mock_context)

        # Should emit warning
        mock_context.emit.assert_any_await("No tools available. Check your MCP config.\n\n")

    @pytest.mark.asyncio
    async def test_on_new_session_with_error(self, agent_with_config, mock_context):
        """Test on_new_session handles errors gracefully."""
        mock_context.tools.list = AsyncMock(side_effect=Exception("Tool loading failed"))

        await agent_with_config.on_new_session(mock_context)

        # Should emit warning with error message
        calls = [call[0][0] for call in mock_context.emit.await_args_list]
        assert any("Warning: Could not initialize MCP tools" in call for call in calls)

    @pytest.mark.asyncio
    async def test_on_prompt_empty(self, agent, mock_context):
        """Test on_prompt with empty input."""
        result = []
        async for chunk in agent.on_prompt(mock_context, ""):
            result.append(chunk)

        assert "Usage:" in "".join(result)

    @pytest.mark.asyncio
    async def test_on_prompt_list_command(self, agent_with_config, mock_context):
        """Test list command."""
        mock_context.tools.list = AsyncMock(
            return_value=[
                Tool(name="echo_text", description="Echo text"),
                Tool(name="echo_uppercase", description=None),
            ]
        )

        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "list"):
            result.append(chunk)

        # Should call list_tools
        mock_context.tools.list.assert_awaited_once()
        mock_context.emit.assert_any_await("Available tools (2):\n\n")
        mock_context.emit.assert_any_await("  • echo_text - Echo text\n")
        mock_context.emit.assert_any_await("  • echo_uppercase\n")

    @pytest.mark.asyncio
    async def test_on_prompt_list_no_tools(self, agent_with_config, mock_context):
        """Test list command with no tools."""
        mock_context.tools.list = AsyncMock(return_value=[])

        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "list"):
            result.append(chunk)

        mock_context.emit.assert_any_await("No tools available.\n")

    @pytest.mark.asyncio
    async def test_on_prompt_list_error(self, agent_with_config, mock_context):
        """Test list command with error."""
        mock_context.tools.list = AsyncMock(side_effect=Exception("Failed to list"))

        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "list"):
            result.append(chunk)

        mock_context.emit.assert_any_await("Error listing tools: Failed to list\n")

    @pytest.mark.asyncio
    async def test_on_prompt_call_command_success(self, agent_with_config, mock_context):
        """Test call command with successful tool call."""
        mock_result = MagicMock()
        mock_result.text = "Hello, world!"
        mock_context.tools.call = AsyncMock(return_value=mock_result)

        result = []
        async for chunk in agent_with_config.on_prompt(
            mock_context, 'call echo_text {"message": "test"}'
        ):
            result.append(chunk)

        mock_context.tools.call.assert_awaited_once_with("echo_text", message="test")
        mock_context.emit.assert_any_await("Calling echo_text...\n\n")
        mock_context.emit.assert_any_await("--- Tool Result ---\n")
        mock_context.emit.assert_any_await("Hello, world!")
        mock_context.emit.assert_any_await("\n--- End ---\n")

    @pytest.mark.asyncio
    async def test_on_prompt_call_command_no_args(self, agent_with_config, mock_context):
        """Test call command without arguments."""
        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "call"):
            result.append(chunk)

        output = "".join(result)
        assert "Usage: call <tool_name> <json_args>" in output
        assert "Example:" in output

    @pytest.mark.asyncio
    async def test_on_prompt_call_command_invalid_json(self, agent_with_config, mock_context):
        """Test call command with invalid JSON."""
        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "call echo_text invalid json"):
            result.append(chunk)

        mock_context.emit.assert_any_await(
            "Invalid JSON arguments: Expecting value: line 1 column 1 (char 0)\n"
        )
        mock_context.emit.assert_any_await('Example: call echo_text {"message": "hello"}\n')

    @pytest.mark.asyncio
    async def test_on_prompt_call_command_tool_error(self, agent_with_config, mock_context):
        """Test call command with tool execution error."""
        mock_context.tools.call = AsyncMock(side_effect=Exception("Tool failed"))

        result = []
        async for chunk in agent_with_config.on_prompt(
            mock_context, 'call echo_text {"message": "test"}'
        ):
            result.append(chunk)

        mock_context.emit.assert_any_await("Error calling tool: Tool failed\n")

    @pytest.mark.asyncio
    async def test_on_prompt_help_command(self, agent_with_config, mock_context):
        """Test help command."""
        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "help"):
            result.append(chunk)

        mock_context.emit.assert_any_await("Interactive Agent Commands:\n\n")
        mock_context.emit.assert_any_await("  list\n")
        mock_context.emit.assert_any_await("  call <tool_name> <json_args>\n")
        mock_context.emit.assert_any_await("  help\n")

    @pytest.mark.asyncio
    async def test_on_prompt_unknown_command(self, agent_with_config, mock_context):
        """Test unknown command."""
        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "unknown command"):
            result.append(chunk)

        mock_context.emit.assert_any_await("You said: unknown command\n\n")
        mock_context.emit.assert_any_await("Available commands: list, call, help\n")

    @pytest.mark.asyncio
    async def test_on_prompt_case_insensitive(self, agent_with_config, mock_context):
        """Test commands are case insensitive."""
        mock_context.tools.list = AsyncMock(return_value=[])

        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "LIST"):
            result.append(chunk)

        mock_context.tools.list.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_on_prompt_exception_handling(self, agent_with_config, mock_context):
        """Test exception handling in on_prompt."""
        mock_context.tools.list = AsyncMock(side_effect=RuntimeError("Unexpected error"))

        result = []
        async for chunk in agent_with_config.on_prompt(mock_context, "list"):
            result.append(chunk)

        # Should yield empty string to signal completion
        assert "" in result
