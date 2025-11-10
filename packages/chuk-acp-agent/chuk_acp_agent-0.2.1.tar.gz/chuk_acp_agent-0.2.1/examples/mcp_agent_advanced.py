#!/usr/bin/env python3
"""
Advanced MCP agent - showcases all DX improvements.

Demonstrates:
- Tool discovery with ctx.tools.list()
- Better error messages with suggestions
- Batch tool calls
- Clean result access with ToolResult
"""

from chuk_acp_agent import Agent, Context


class AdvancedMCPAgent(Agent):
    """Agent showcasing advanced MCP features."""

    def __init__(self):
        """Initialize agent with MCP servers."""
        super().__init__()

        # Simple configuration using helper method
        self.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")

    async def on_new_session(self, ctx: Context) -> None:
        """Initialize session and discover tools."""
        await ctx.emit("Advanced MCP Agent\n")
        await ctx.emit("===================\n\n")

        # Discover available tools
        try:
            tools = await ctx.tools.list()
            await ctx.emit(f"Available tools ({len(tools)}):\n")
            for tool in tools[:5]:  # Show first 5
                desc = f" - {tool.description}" if tool.description else ""
                await ctx.emit(f"  • {tool.name}{desc}\n")
            if len(tools) > 5:
                await ctx.emit(f"  ... and {len(tools) - 5} more\n")
            await ctx.emit("\n")
        except Exception as e:
            await ctx.emit(f"Tool discovery failed: {e}\n\n")

        await ctx.emit("Commands:\n")
        await ctx.emit("  list - List all tools\n")
        await ctx.emit("  echo <msg> - Echo a message\n")
        await ctx.emit("  batch - Demo batch execution\n")
        await ctx.emit("  error - Demo error handling\n\n")

    async def on_prompt(self, ctx: Context, prompt: str):
        """Handle user prompts."""
        parts = prompt.strip().split(maxsplit=1)

        if not parts:
            yield "Usage: list | echo <msg> | batch | error\n"
            return

        command = parts[0].lower()

        try:
            if command == "list":
                await self._list_tools(ctx)
            elif command == "echo":
                if len(parts) < 2:
                    yield "Usage: echo <message>\n"
                    return
                await self._echo_message(ctx, parts[1])
            elif command == "batch":
                await self._demo_batch(ctx)
            elif command == "error":
                await self._demo_error_handling(ctx)
            else:
                yield f"Unknown command: {command}\n"
                yield "Try: list, echo, batch, error\n"
        except Exception as e:
            yield f"Error: {e}\n"

        yield ""  # Signal completion

    async def _list_tools(self, ctx: Context):
        """List all available tools."""
        await ctx.emit("Discovering tools...\n\n")

        tools = await ctx.tools.list()
        await ctx.emit(f"Found {len(tools)} tools:\n\n")

        for tool in tools:
            desc = f" - {tool.description}" if tool.description else ""
            await ctx.emit(f"  • {tool.name}{desc}\n")

        await ctx.emit("\n")

    async def _echo_message(self, ctx: Context, message: str):
        """Echo a message."""
        await ctx.emit(f"Echoing: {message}\n\n")

        # Clean API with ToolResult
        result = await ctx.tools.call("echo_text", message=message)

        # Access text directly!
        await ctx.emit(f"Result: {result.text}\n")
        await ctx.emit(f"Is error: {result.is_error}\n")

    async def _demo_batch(self, ctx: Context):
        """Demonstrate batch tool execution."""
        await ctx.emit("Executing batch of 3 tools in parallel...\n\n")

        # Batch execution - all run in parallel!
        results = await ctx.tools.call_batch(
            [
                ("echo_text", {"message": "First message"}),
                ("echo_text", {"message": "Second message"}),
                ("echo_text", {"message": "Third message"}),
            ]
        )

        await ctx.emit("Batch results:\n")
        for i, result in enumerate(results, 1):
            status = "✓" if not result.is_error else "✗"
            await ctx.emit(f"  {status} {i}. {result.text}\n")
        await ctx.emit("\n")

    async def _demo_error_handling(self, ctx: Context):
        """Demonstrate improved error messages."""
        await ctx.emit("Testing error handling with typo...\n\n")

        try:
            # Intentional typo: "ech" instead of "echo_text"
            await ctx.tools.call("ech", message="test")
        except Exception as e:
            # This will show suggestions!
            await ctx.emit(f"Caught error:\n{e}\n")


if __name__ == "__main__":
    agent = AdvancedMCPAgent()
    agent.run()
