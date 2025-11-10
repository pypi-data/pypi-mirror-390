"""
Pytest configuration and fixtures for chuk-acp-agent tests.
"""

from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent._mcp_config = None
    return agent


@pytest.fixture
def sample_mcp_config():
    """Sample MCP configuration for testing."""
    from chuk_acp_agent.models.mcp import MCPConfig, MCPServerConfig

    return MCPConfig(
        mcpServers={
            "echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo", "stdio"], env={})
        },
        namespace="mcp",
        enable_caching=True,
        cache_ttl=300,
        default_timeout=30,
        max_retries=3,
    )


@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    from chuk_acp_agent.agent.context import Context

    ctx = Mock(spec=Context)
    ctx.session_id = "test_session"
    ctx.cwd = "/test/dir"
    ctx.memory = Mock()
    ctx.emit = AsyncMock()
    return ctx


@pytest.fixture
def mock_tool_result():
    """Create a mock tool result."""
    result = Mock()
    result.content = [{"type": "text", "text": "Test response"}]
    result.isError = False
    result.meta = {"duration": 0.001}
    return result
