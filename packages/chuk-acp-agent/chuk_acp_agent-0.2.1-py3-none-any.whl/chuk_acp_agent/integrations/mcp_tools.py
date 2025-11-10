"""
MCP tool integration via chuk-tool-processor.
"""

import difflib
import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chuk_acp_agent.models.mcp import MCPConfig

import builtins

from chuk_acp_agent.exceptions import ToolExecutionError, ToolNotFoundError
from chuk_acp_agent.models.tool import Tool
from chuk_acp_agent.models.tool_result import ToolResult


class ToolInvoker:
    """
    MCP tool invoker using chuk-tool-processor.

    Manages MCP server lifecycle and tool invocation.
    """

    def __init__(
        self,
        mcp_config: "MCPConfig",
    ) -> None:
        """
        Initialize tool invoker.

        Args:
            mcp_config: MCP configuration (Pydantic model)
        """
        self._mcp_config = mcp_config
        self._processor: Any | None = None
        self._stream_manager: Any | None = None
        self._initialized = False
        self._temp_config_file: Path | None = None

    async def _ensure_initialized(self) -> None:
        """Initialize chuk-tool-processor if not already done."""
        if self._initialized:
            return

        try:
            # Import here to avoid hard dependency
            from chuk_tool_processor.mcp import setup_mcp_stdio
        except ImportError as e:
            raise ImportError(
                "MCP support requires chuk-tool-processor. "
                "Install with: pip install chuk-tool-processor"
            ) from e

        # Create temporary config file from Pydantic model
        config_dict = self._mcp_config.to_dict()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_dict, f, indent=2)
            self._temp_config_file = Path(f.name)

        # Use setup_mcp_stdio to initialize MCP servers
        server_names = list(self._mcp_config.mcpServers.keys())

        self._processor, self._stream_manager = await setup_mcp_stdio(
            config_file=str(self._temp_config_file),
            servers=server_names,
            namespace=self._mcp_config.namespace,
            default_timeout=self._mcp_config.default_timeout,
            enable_caching=self._mcp_config.enable_caching,
            cache_ttl=self._mcp_config.cache_ttl,
            max_retries=self._mcp_config.max_retries,
        )

        self._initialized = True

    async def call(
        self,
        tool_name: str,
        **arguments: Any,
    ) -> ToolResult:
        """
        Call an MCP tool.

        Args:
            tool_name: Tool name (without namespace prefix)
            **arguments: Tool arguments

        Returns:
            ToolResult wrapper with convenient accessors

        Raises:
            ImportError: If chuk-tool-processor not installed
            RuntimeError: If tool call fails
        """
        await self._ensure_initialized()

        try:
            from chuk_tool_processor.models.tool_call import ToolCall
        except ImportError as e:
            raise ImportError(
                "MCP support requires chuk-tool-processor. "
                "Install with: pip install chuk-tool-processor"
            ) from e

        # Create tool call using Pydantic model
        # Tool name should be namespaced (e.g., "mcp.echo_text")
        full_tool_name = f"{self._mcp_config.namespace}.{tool_name}"

        tool_call = ToolCall(
            tool=full_tool_name,
            arguments=arguments,
        )

        # Execute the tool call (use execute, not process)
        assert self._processor is not None, "Processor not initialized"
        results = await self._processor.execute([tool_call])

        # Check results
        if not results or len(results) == 0:
            # Get available tools for better error message
            try:
                raw_tools = await self.list_tools()
                available = [
                    name[len(f"{self._mcp_config.namespace}.") :]
                    if name.startswith(f"{self._mcp_config.namespace}.")
                    else name
                    for name in raw_tools.keys()
                ]
                suggestions = self._find_similar_tools(tool_name, available)
                raise ToolNotFoundError(tool_name, suggestions, available)
            except ToolNotFoundError:
                raise
            except Exception:
                # Fallback to simple error if listing fails
                raise RuntimeError(f"No response from tool '{full_tool_name}'")

        result = results[0]

        # Check if result has an error
        if hasattr(result, "error") and result.error:
            raise ToolExecutionError(full_tool_name, result.error)

        # Wrap in ToolResult for convenient access
        return ToolResult(result)

    async def list_tools(self) -> dict[str, Any]:
        """
        List available tools (low-level registry format).

        For clean tool discovery, use list() instead.

        Returns:
            Dictionary mapping tool names to tool definitions
        """
        await self._ensure_initialized()

        try:
            from chuk_tool_processor.registry import ToolRegistryProvider
        except ImportError as e:
            raise ImportError(
                "MCP support requires chuk-tool-processor. "
                "Install with: pip install chuk-tool-processor"
            ) from e

        # Get registry (singleton, not a coroutine)
        registry = ToolRegistryProvider.get_registry()
        tools: dict[str, Any] = registry.list_tools()
        return tools

    async def list(self) -> list[Tool]:
        """
        List available tools in clean format.

        Returns:
            List of Tool objects with name, description, parameters

        Example:
            tools = await ctx.tools.list()
            for tool in tools:
                print(f"{tool.name}: {tool.description}")
        """
        try:
            raw_tools = await self.list_tools()
        except (AttributeError, TypeError):
            # Fallback: If registry access fails, return empty list
            # This is a known issue with chuk-tool-processor registry API
            return []

        tools = []
        namespace_prefix = f"{self._mcp_config.namespace}."

        for tool_name, tool_def in raw_tools.items():
            # Remove namespace prefix for clean names
            clean_name = tool_name
            if tool_name.startswith(namespace_prefix):
                clean_name = tool_name[len(namespace_prefix) :]

            # Extract description
            description = None
            if hasattr(tool_def, "description"):
                description = tool_def.description
            elif hasattr(tool_def, "__doc__"):
                description = tool_def.__doc__

            # Create Tool object
            tools.append(
                Tool(
                    name=clean_name,
                    description=description,
                    parameters=None,  # TODO: Extract from tool schema
                )
            )

        return sorted(tools, key=lambda t: t.name)

    async def call_batch(
        self,
        calls: builtins.list[tuple[str, dict[str, Any]]],
    ) -> builtins.list[ToolResult]:
        """
        Execute multiple tool calls in parallel.

        Args:
            calls: List of (tool_name, arguments) tuples

        Returns:
            List of ToolResult objects

        Example:
            results = await ctx.tools.call_batch([
                ("echo_text", {"message": "one"}),
                ("echo_uppercase", {"message": "two"}),
            ])
        """
        await self._ensure_initialized()

        try:
            from chuk_tool_processor.models.tool_call import ToolCall
        except ImportError as e:
            raise ImportError(
                "MCP support requires chuk-tool-processor. "
                "Install with: pip install chuk-tool-processor"
            ) from e

        # Create tool calls
        tool_calls = []
        for tool_name, arguments in calls:
            full_tool_name = f"{self._mcp_config.namespace}.{tool_name}"
            tool_calls.append(
                ToolCall(
                    tool=full_tool_name,
                    arguments=arguments,
                )
            )

        # Execute batch
        assert self._processor is not None, "Processor not initialized"
        results = await self._processor.execute(tool_calls)

        # Wrap all results
        return [ToolResult(result) for result in results]

    def _find_similar_tools(
        self, tool_name: str, available_tools: builtins.list[str]
    ) -> builtins.list[str]:
        """
        Find similar tool names using fuzzy matching.

        Args:
            tool_name: Tool name to match
            available_tools: List of available tool names

        Returns:
            List of similar tool names
        """
        # Use difflib for fuzzy matching
        matches = difflib.get_close_matches(
            tool_name,
            available_tools,
            n=5,
            cutoff=0.6,
        )
        return matches

    async def close(self) -> None:
        """Shutdown MCP servers and cleanup."""
        if self._stream_manager:
            await self._stream_manager.cleanup()

        # Clean up temporary config file
        if self._temp_config_file and self._temp_config_file.exists():
            self._temp_config_file.unlink()

        self._initialized = False
