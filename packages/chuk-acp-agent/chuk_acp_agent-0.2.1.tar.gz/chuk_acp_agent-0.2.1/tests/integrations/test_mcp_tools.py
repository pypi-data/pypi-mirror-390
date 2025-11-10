"""Tests for MCP tools integration."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from chuk_acp_agent.exceptions import ToolExecutionError, ToolNotFoundError
from chuk_acp_agent.integrations.mcp_tools import ToolInvoker
from chuk_acp_agent.models.mcp import MCPConfig, MCPServerConfig
from chuk_acp_agent.models.tool import Tool
from chuk_acp_agent.models.tool_result import ToolResult


class TestToolInvoker:
    """Test ToolInvoker functionality."""

    def test_initialization(self):
        """Test ToolInvoker initialization."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        assert invoker._mcp_config == config
        assert invoker._processor is None
        assert invoker._stream_manager is None
        assert invoker._initialized is False
        assert invoker._temp_config_file is None

    @pytest.mark.asyncio
    async def test_ensure_initialized_import_error(self):
        """Test _ensure_initialized raises ImportError when chuk-tool-processor missing."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        with patch.dict("sys.modules", {"chuk_tool_processor.mcp": None}):
            with pytest.raises(ImportError, match="chuk-tool-processor"):
                await invoker._ensure_initialized()

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    async def test_ensure_initialized_creates_temp_file(self, mock_setup):
        """Test _ensure_initialized creates temporary config file."""
        config = MCPConfig(
            mcpServers={"echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo"])}
        )
        invoker = ToolInvoker(mcp_config=config)

        # Use AsyncMock for stream_manager since cleanup() is async
        mock_stream_manager = AsyncMock()
        mock_setup.return_value = (Mock(), mock_stream_manager)

        try:
            await invoker._ensure_initialized()

            # Verify temp file was created
            assert invoker._temp_config_file is not None
            assert invoker._temp_config_file.exists()
        finally:
            # Cleanup resources
            await invoker.close()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    async def test_ensure_initialized_calls_setup_with_config(self, mock_setup):
        """Test _ensure_initialized calls setup_mcp_stdio with correct parameters."""
        config = MCPConfig(
            mcpServers={"echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo"])},
            namespace="mcp",
            default_timeout=10.0,
            enable_caching=True,
            cache_ttl=300,
            max_retries=3,
        )
        invoker = ToolInvoker(mcp_config=config)

        mock_processor = Mock()
        mock_stream_manager = Mock()
        mock_setup.return_value = (mock_processor, mock_stream_manager)

        await invoker._ensure_initialized()

        # Verify setup was called with correct parameters
        mock_setup.assert_called_once()
        call_args = mock_setup.call_args
        assert call_args.kwargs["servers"] == ["echo"]
        assert call_args.kwargs["namespace"] == "mcp"
        assert call_args.kwargs["default_timeout"] == 10.0
        assert call_args.kwargs["enable_caching"] is True
        assert call_args.kwargs["cache_ttl"] == 300
        assert call_args.kwargs["max_retries"] == 3

        # Verify processor and stream manager were stored
        assert invoker._processor == mock_processor
        assert invoker._stream_manager == mock_stream_manager
        assert invoker._initialized is True

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    async def test_ensure_initialized_is_idempotent(self, mock_setup):
        """Test _ensure_initialized only initializes once."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        mock_setup.return_value = (Mock(), Mock())

        # Call twice
        await invoker._ensure_initialized()
        await invoker._ensure_initialized()

        # Should only be called once
        assert mock_setup.call_count == 1

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.models.tool_call.ToolCall")
    async def test_call_success(self, mock_tool_call_class, mock_setup):
        """Test successful tool call."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock processor
        mock_processor = Mock()
        mock_result = Mock()
        mock_result.error = None
        mock_result.result = Mock()
        mock_result.result.content = [{"type": "text", "text": "Success"}]
        mock_result.isError = False
        mock_processor.execute = AsyncMock(return_value=[mock_result])

        mock_setup.return_value = (mock_processor, Mock())

        # Execute call
        result = await invoker.call("echo_text", message="test")

        # Verify ToolCall was created
        mock_tool_call_class.assert_called_once_with(
            tool="mcp.echo_text", arguments={"message": "test"}
        )

        # Verify processor.execute was called
        mock_processor.execute.assert_called_once()

        # Verify result is ToolResult
        assert isinstance(result, ToolResult)
        assert result.text == "Success"

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.models.tool_call.ToolCall")
    async def test_call_with_execution_error(self, mock_tool_call_class, mock_setup):
        """Test tool call with execution error."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock processor
        mock_processor = Mock()
        mock_result = Mock()
        mock_result.error = {"message": "Tool execution failed"}
        mock_processor.execute = AsyncMock(return_value=[mock_result])

        mock_setup.return_value = (mock_processor, Mock())

        # Execute call - should raise ToolExecutionError
        with pytest.raises(ToolExecutionError, match="mcp.echo_text"):
            await invoker.call("echo_text", message="test")

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.models.tool_call.ToolCall")
    @patch("chuk_tool_processor.registry.ToolRegistryProvider")
    async def test_call_tool_not_found(
        self, mock_registry_provider, mock_tool_call_class, mock_setup
    ):
        """Test tool call with tool not found."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock processor returning empty results
        mock_processor = Mock()
        mock_processor.execute = AsyncMock(return_value=[])

        # Mock registry for tool listing
        mock_registry = Mock()
        mock_registry.list_tools.return_value = {
            "mcp.echo_text": Mock(),
            "mcp.echo_upper": Mock(),
        }
        mock_registry_provider.get_registry.return_value = mock_registry

        mock_setup.return_value = (mock_processor, Mock())

        # Execute call - should raise ToolNotFoundError with suggestions
        with pytest.raises(ToolNotFoundError) as exc_info:
            await invoker.call("ech", message="test")

        # Verify error has suggestions
        error = exc_info.value
        assert "ech" in str(error)

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.registry.ToolRegistryProvider")
    async def test_list_tools(self, mock_registry_provider, mock_setup):
        """Test list_tools returns raw registry."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        # Mock registry
        mock_registry = Mock()
        mock_tools = {
            "mcp.echo_text": Mock(),
            "mcp.echo_upper": Mock(),
        }
        mock_registry.list_tools.return_value = mock_tools
        mock_registry_provider.get_registry.return_value = mock_registry

        mock_setup.return_value = (Mock(), Mock())

        # List tools
        tools = await invoker.list_tools()

        assert tools == mock_tools

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.registry.ToolRegistryProvider")
    async def test_list_returns_tool_objects(self, mock_registry_provider, mock_setup):
        """Test list returns clean Tool objects."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock registry
        mock_registry = Mock()
        mock_tool1 = Mock()
        mock_tool1.description = "Echo text"
        mock_tool2 = Mock()
        mock_tool2.description = "Echo uppercase"

        mock_registry.list_tools.return_value = {
            "mcp.echo_text": mock_tool1,
            "mcp.echo_upper": mock_tool2,
        }
        mock_registry_provider.get_registry.return_value = mock_registry

        mock_setup.return_value = (Mock(), Mock())

        # List tools
        tools = await invoker.list()

        # Verify Tool objects were created
        assert len(tools) == 2
        assert all(isinstance(t, Tool) for t in tools)

        # Verify names stripped namespace
        assert tools[0].name == "echo_text"
        assert tools[1].name == "echo_upper"

        # Verify descriptions
        assert tools[0].description == "Echo text"
        assert tools[1].description == "Echo uppercase"

        # Verify sorted by name
        assert tools[0].name < tools[1].name

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    async def test_list_handles_registry_failure(self, mock_setup):
        """Test list returns empty list when registry fails."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        mock_setup.return_value = (Mock(), Mock())

        # Mock list_tools to raise AttributeError
        invoker.list_tools = AsyncMock(side_effect=AttributeError("Registry not available"))

        # List tools - should return empty list
        tools = await invoker.list()

        assert tools == []

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.models.tool_call.ToolCall")
    async def test_call_batch(self, mock_tool_call_class, mock_setup):
        """Test batch tool execution."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock processor
        mock_processor = Mock()
        mock_result1 = Mock()
        mock_result1.error = None
        mock_result1.result = Mock()
        mock_result1.result.content = [{"type": "text", "text": "Result 1"}]
        mock_result1.isError = False

        mock_result2 = Mock()
        mock_result2.error = None
        mock_result2.result = Mock()
        mock_result2.result.content = [{"type": "text", "text": "Result 2"}]
        mock_result2.isError = False

        mock_processor.execute = AsyncMock(return_value=[mock_result1, mock_result2])

        mock_setup.return_value = (mock_processor, Mock())

        # Execute batch
        results = await invoker.call_batch(
            [
                ("echo_text", {"message": "one"}),
                ("echo_upper", {"message": "two"}),
            ]
        )

        # Verify results
        assert len(results) == 2
        assert all(isinstance(r, ToolResult) for r in results)
        assert results[0].text == "Result 1"
        assert results[1].text == "Result 2"

        # Verify processor.execute was called with both tool calls
        mock_processor.execute.assert_called_once()

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    def test_find_similar_tools(self):
        """Test fuzzy tool name matching."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        available = ["echo_text", "echo_upper", "read_file", "write_file"]

        # Test close match with longer prefix
        suggestions = invoker._find_similar_tools("echo", available)
        assert "echo_text" in suggestions or "echo_upper" in suggestions

        # Test exact match
        suggestions = invoker._find_similar_tools("echo_text", available)
        assert "echo_text" in suggestions

        # Test no match
        suggestions = invoker._find_similar_tools("xyz", available)
        assert len(suggestions) == 0

        # Test typo
        suggestions = invoker._find_similar_tools("rea_file", available)
        assert "read_file" in suggestions

    def test_find_similar_tools_cutoff(self):
        """Test fuzzy matching uses cutoff."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        available = ["echo_text", "read_file"]

        # Very different name - should not match
        suggestions = invoker._find_similar_tools("xyz", available)
        assert len(suggestions) == 0

    def test_find_similar_tools_limit(self):
        """Test fuzzy matching limits results."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        # Many similar tools
        available = [
            "echo_1",
            "echo_2",
            "echo_3",
            "echo_4",
            "echo_5",
            "echo_6",
            "echo_7",
        ]

        suggestions = invoker._find_similar_tools("echo", available)
        # Should limit to 5
        assert len(suggestions) <= 5

    @pytest.mark.asyncio
    async def test_close_cleanup(self):
        """Test close cleans up resources."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        # Create temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)
            invoker._temp_config_file = temp_path

        # Mock stream manager
        mock_stream_manager = Mock()
        mock_stream_manager.cleanup = AsyncMock()
        invoker._stream_manager = mock_stream_manager

        # Close
        await invoker.close()

        # Verify cleanup was called
        mock_stream_manager.cleanup.assert_called_once()

        # Verify temp file was deleted
        assert not temp_path.exists()

        # Verify initialized flag was reset
        assert invoker._initialized is False

    @pytest.mark.asyncio
    async def test_close_without_stream_manager(self):
        """Test close handles missing stream manager."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        # No stream manager
        invoker._stream_manager = None

        # Should not raise
        await invoker.close()

    @pytest.mark.asyncio
    async def test_close_without_temp_file(self):
        """Test close handles missing temp file."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)

        # No temp file
        invoker._temp_config_file = None

        # Should not raise
        await invoker.close()

    @pytest.mark.asyncio
    async def test_call_import_error_toolcall(self):
        """Test call raises ImportError when ToolCall not available."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)
        invoker._initialized = True  # Skip initialization

        # Mock import to fail
        with patch.dict("sys.modules", {"chuk_tool_processor.models.tool_call": None}):
            with pytest.raises(ImportError, match="chuk-tool-processor"):
                await invoker.call("test_tool")

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.models.tool_call.ToolCall")
    @patch("chuk_tool_processor.registry.ToolRegistryProvider")
    async def test_call_no_results_fallback_error(
        self, mock_registry_provider, mock_tool_call_class, mock_setup
    ):
        """Test call with no results when listing also fails."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock processor returning empty results
        mock_processor = Mock()
        mock_processor.execute = AsyncMock(return_value=[])

        # Mock registry to fail
        mock_registry_provider.get_registry.side_effect = Exception("Registry error")

        mock_setup.return_value = (mock_processor, Mock())

        # Execute call - should raise RuntimeError as fallback
        with pytest.raises(RuntimeError, match="No response from tool"):
            await invoker.call("missing_tool", arg="value")

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    async def test_list_tools_import_error(self):
        """Test list_tools raises ImportError when registry not available."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)
        invoker._initialized = True  # Skip initialization

        # Mock import to fail
        with patch.dict("sys.modules", {"chuk_tool_processor.registry": None}):
            with pytest.raises(ImportError, match="chuk-tool-processor"):
                await invoker.list_tools()

    @pytest.mark.asyncio
    @patch("chuk_tool_processor.mcp.setup_mcp_stdio")
    @patch("chuk_tool_processor.registry.ToolRegistryProvider")
    async def test_list_with_no_description(self, mock_registry_provider, mock_setup):
        """Test list handles tools without description."""
        config = MCPConfig(namespace="mcp")
        invoker = ToolInvoker(mcp_config=config)

        # Mock registry
        mock_registry = Mock()

        # Create a simple object without description attribute
        class ToolWithoutDesc:
            pass

        mock_tool = ToolWithoutDesc()

        mock_registry.list_tools.return_value = {
            "mcp.no_desc_tool": mock_tool,
        }
        mock_registry_provider.get_registry.return_value = mock_registry

        mock_setup.return_value = (Mock(), Mock())

        # List tools
        tools = await invoker.list()

        # Should still create Tool object
        assert len(tools) == 1
        assert tools[0].name == "no_desc_tool"
        assert tools[0].description is None

        # Cleanup
        if invoker._temp_config_file:
            invoker._temp_config_file.unlink()

    @pytest.mark.asyncio
    async def test_call_batch_import_error(self):
        """Test call_batch raises ImportError when ToolCall not available."""
        config = MCPConfig()
        invoker = ToolInvoker(mcp_config=config)
        invoker._initialized = True  # Skip initialization

        # Mock import to fail
        with patch.dict("sys.modules", {"chuk_tool_processor.models.tool_call": None}):
            with pytest.raises(ImportError, match="chuk-tool-processor"):
                await invoker.call_batch([("tool1", {}), ("tool2", {})])
