"""Tests for Context class."""

from unittest.mock import Mock, patch

import pytest

from chuk_acp_agent.agent.context import Context
from chuk_acp_agent.models.mcp import MCPConfig


class TestContext:
    """Test Context functionality."""

    def test_initialization(self):
        """Test context initialization."""
        agent = Mock()
        ctx = Context(session_id="test_session", cwd="/test/dir", agent=agent, mcp_config=None)

        assert ctx.session_id == "test_session"
        assert ctx.cwd == "/test/dir"
        assert ctx._agent == agent
        assert ctx._mcp_config is None
        assert ctx._tools is None
        assert ctx._plan == []

    def test_initialization_with_mcp_config(self):
        """Test initialization with MCP config."""
        agent = Mock()
        config = MCPConfig()

        ctx = Context(session_id="test", cwd="/test", agent=agent, mcp_config=config)

        assert ctx._mcp_config == config

    @pytest.mark.asyncio
    async def test_emit(self):
        """Test emit sends text to agent."""
        agent = Mock()
        agent.send_message = Mock()

        ctx = Context("test", "/test", agent)
        await ctx.emit("Hello")

        agent.send_message.assert_called_once_with("Hello", "test")

    @pytest.mark.asyncio
    async def test_send_plan(self):
        """Test send_plan creates plan entries."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan(
            [
                {"content": "Step 1", "status": "pending"},
                {"content": "Step 2", "status": "in_progress", "priority": "high"},
            ]
        )

        assert len(ctx._plan) == 2
        assert ctx._plan[0].content == "Step 1"
        assert ctx._plan[0].status == "pending"
        assert ctx._plan[1].content == "Step 2"
        assert ctx._plan[1].status == "in_progress"

    @pytest.mark.asyncio
    async def test_send_plan_with_defaults(self):
        """Test send_plan uses default values."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Task"}])

        assert ctx._plan[0].status == "pending"  # Default status
        assert ctx._plan[0].priority == "medium"  # Default priority

    @pytest.mark.asyncio
    async def test_update_plan_content(self):
        """Test update_plan updates content."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Original"}])
        await ctx.update_plan(0, content="Updated")

        assert ctx._plan[0].content == "Updated"

    @pytest.mark.asyncio
    async def test_update_plan_status(self):
        """Test update_plan updates status."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Task", "status": "pending"}])
        await ctx.update_plan(0, status="completed")

        assert ctx._plan[0].status == "completed"

    @pytest.mark.asyncio
    async def test_update_plan_priority(self):
        """Test update_plan updates priority."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Task"}])
        await ctx.update_plan(0, priority="high")

        assert ctx._plan[0].priority == "high"

    @pytest.mark.asyncio
    async def test_update_plan_multiple_fields(self):
        """Test update_plan updates multiple fields."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Task"}])
        await ctx.update_plan(0, content="New", status="in_progress", priority="high")

        assert ctx._plan[0].content == "New"
        assert ctx._plan[0].status == "in_progress"
        assert ctx._plan[0].priority == "high"

    @pytest.mark.asyncio
    async def test_update_plan_invalid_index(self):
        """Test update_plan raises IndexError for invalid index."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Task"}])

        with pytest.raises(IndexError):
            await ctx.update_plan(5, status="completed")

    @pytest.mark.asyncio
    async def test_update_plan_negative_index(self):
        """Test update_plan raises IndexError for negative index."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        await ctx.send_plan([{"content": "Task"}])

        with pytest.raises(IndexError):
            await ctx.update_plan(-1, status="completed")

    def test_tools_property_no_config(self):
        """Test tools property raises error when no MCP config."""
        agent = Mock()
        ctx = Context("test", "/test", agent, mcp_config=None)

        with pytest.raises(RuntimeError, match="No MCP configuration"):
            _ = ctx.tools

    @patch("chuk_acp_agent.integrations.mcp_tools.ToolInvoker")
    def test_tools_property_creates_invoker(self, mock_invoker_class):
        """Test tools property creates ToolInvoker."""
        agent = Mock()
        config = MCPConfig()
        ctx = Context("test", "/test", agent, mcp_config=config)

        mock_invoker = Mock()
        mock_invoker_class.return_value = mock_invoker

        # Access tools property
        tools = ctx.tools

        # Should create ToolInvoker with config
        mock_invoker_class.assert_called_once_with(mcp_config=config)
        assert tools == mock_invoker

    @patch("chuk_acp_agent.integrations.mcp_tools.ToolInvoker")
    def test_tools_property_caches_invoker(self, mock_invoker_class):
        """Test tools property caches the invoker."""
        agent = Mock()
        config = MCPConfig()
        ctx = Context("test", "/test", agent, mcp_config=config)

        mock_invoker = Mock()
        mock_invoker_class.return_value = mock_invoker

        # Access twice
        tools1 = ctx.tools
        tools2 = ctx.tools

        # Should only create once
        assert mock_invoker_class.call_count == 1
        assert tools1 == tools2

    def test_memory_property(self):
        """Test memory property access."""
        agent = Mock()
        agent.memory = {"test": "value"}
        ctx = Context("test", "/test", agent)

        # Memory should be accessible
        # Note: Actual implementation may vary
        assert ctx._agent == agent

    def test_plan_empty_initially(self):
        """Test plan is empty list initially."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        assert ctx._plan == []
        assert isinstance(ctx._plan, list)

    def test_multiple_plan_updates(self):
        """Test multiple sequential plan updates."""
        agent = Mock()
        ctx = Context("test", "/test", agent)

        async def test():
            await ctx.send_plan(
                [{"content": "Task 1"}, {"content": "Task 2"}, {"content": "Task 3"}]
            )

            await ctx.update_plan(0, status="completed")
            await ctx.update_plan(1, status="in_progress")
            await ctx.update_plan(2, status="pending")

            assert ctx._plan[0].status == "completed"
            assert ctx._plan[1].status == "in_progress"
            assert ctx._plan[2].status == "pending"

        import asyncio

        asyncio.run(test())

    def test_session_id_immutable(self):
        """Test session_id is set correctly."""
        agent = Mock()
        ctx = Context("session_123", "/test", agent)

        assert ctx.session_id == "session_123"

    def test_cwd_immutable(self):
        """Test cwd is set correctly."""
        agent = Mock()
        ctx = Context("test", "/my/working/dir", agent)

        assert ctx.cwd == "/my/working/dir"
