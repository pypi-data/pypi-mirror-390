"""
Interactive agent with MCP tool support.

Provides a REPL-like interface for interacting with MCP tools.
Can be launched from CLI with --mcp-config-file option.
"""

from collections.abc import AsyncIterator

from chuk_acp_agent.agent.base import Agent
from chuk_acp_agent.agent.context import Context


class InteractiveAgent(Agent):
    """
    Generic interactive agent with MCP tool support.

    Features:
    - Automatic tool discovery from MCP config
    - Interactive command interface
    - List, describe, and call tools
    """

    async def on_new_session(self, ctx: Context) -> None:
        """Initialize session with welcome message."""
        await ctx.emit("Interactive Agent Ready!\n\n")

        # List available tools if MCP config is present
        if self._mcp_config and self._mcp_config.mcpServers:
            try:
                tools = await ctx.tools.list()
                if tools:
                    await ctx.emit(f"Loaded {len(tools)} MCP tools from ")
                    await ctx.emit(f"{len(self._mcp_config.mcpServers)} servers\n\n")
                    await ctx.emit("Commands:\n")
                    await ctx.emit("  list - List all available tools\n")
                    await ctx.emit("  call <tool> <json_args> - Call a tool with JSON arguments\n")
                    await ctx.emit("  help - Show this help message\n\n")
                else:
                    await ctx.emit("No tools available. Check your MCP config.\n\n")
            except Exception as e:
                await ctx.emit(f"Warning: Could not initialize MCP tools: {e}\n\n")
        else:
            await ctx.emit("No MCP servers configured.\n")
            await ctx.emit("Use --mcp-config-file to load MCP servers.\n\n")

    async def on_prompt(self, ctx: Context, prompt: str) -> AsyncIterator[str]:
        """Handle user prompts with tool support."""
        parts = prompt.strip().split(maxsplit=1)

        if not parts:
            yield "Usage: list | call <tool> <json_args> | help\n"
            return

        command = parts[0].lower()

        try:
            if command == "list":
                await self._list_tools(ctx)
            elif command == "call":
                if len(parts) < 2:
                    yield "Usage: call <tool_name> <json_args>\n"
                    yield 'Example: call echo_text {"message": "hello"}\n'
                    return
                await self._call_tool(ctx, parts[1])
            elif command == "help":
                await self._show_help(ctx)
            else:
                # Treat unknown input as a direct message/question
                await ctx.emit(f"You said: {prompt}\n\n")
                await ctx.emit("Available commands: list, call, help\n")
        except Exception as e:
            yield f"Error: {e}\n"

        # Signal completion
        yield ""

    async def _list_tools(self, ctx: Context) -> None:
        """List available MCP tools."""
        try:
            tools = await ctx.tools.list()

            if not tools:
                await ctx.emit("No tools available.\n")
                return

            await ctx.emit(f"Available tools ({len(tools)}):\n\n")

            for tool in tools:
                desc = f" - {tool.description}" if tool.description else ""
                await ctx.emit(f"  • {tool.name}{desc}\n")

            await ctx.emit("\n")
        except Exception as e:
            await ctx.emit(f"Error listing tools: {e}\n")

    async def _call_tool(self, ctx: Context, args: str) -> None:
        """
        Call an MCP tool.

        Args:
            ctx: Agent context
            args: String containing tool name and JSON arguments
        """
        import json

        # Parse tool name and arguments
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            await ctx.emit("Usage: call <tool_name> <json_args>\n")
            await ctx.emit('Example: call echo_text {"message": "hello"}\n')
            return

        tool_name = parts[0]
        try:
            tool_args = json.loads(parts[1])
        except json.JSONDecodeError as e:
            await ctx.emit(f"Invalid JSON arguments: {e}\n")
            await ctx.emit('Example: call echo_text {"message": "hello"}\n')
            return

        # Call the tool
        try:
            await ctx.emit(f"Calling {tool_name}...\n\n")
            result = await ctx.tools.call(tool_name, **tool_args)

            await ctx.emit("--- Tool Result ---\n")
            await ctx.emit(result.text)
            await ctx.emit("\n--- End ---\n")
        except Exception as e:
            await ctx.emit(f"Error calling tool: {e}\n")

    async def _show_help(self, ctx: Context) -> None:
        """Show help message."""
        await ctx.emit("Interactive Agent Commands:\n\n")
        await ctx.emit("  list\n")
        await ctx.emit("    List all available MCP tools\n\n")
        await ctx.emit("  call <tool_name> <json_args>\n")
        await ctx.emit("    Call a tool with JSON arguments\n")
        await ctx.emit('    Example: call echo_text {"message": "hello"}\n\n')
        await ctx.emit("  help\n")
        await ctx.emit("    Show this help message\n\n")
