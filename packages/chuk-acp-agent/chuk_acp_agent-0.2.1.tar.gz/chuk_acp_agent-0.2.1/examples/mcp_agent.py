#!/usr/bin/env python3
"""
MCP tool agent - demonstrates MCP integration.

This agent shows how to use MCP (Model Context Protocol) servers
to give your agent access to tools via the Context API.

Demonstrates integration with:
- chuk-mcp-echo: Simple echo server for testing
- @modelcontextprotocol/server-filesystem: File operations in /tmp

Requirements:
    pip install chuk-acp-agent
    # MCP servers are auto-installed via uvx/npx when first used

Usage:
    uv run examples/mcp_agent.py

Then try:
    echo <message> - Echo a message
    read <file> - Read a file from /tmp
    write <file> <content> - Write to /tmp
"""

from chuk_acp_agent import Agent, Context


class MCPAgent(Agent):
    """Agent with MCP tool integration - full example with multiple servers."""

    def __init__(self):
        """Initialize agent with MCP servers."""
        super().__init__()

        # Simple configuration using improved DX!
        self.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")
        self.add_mcp_server("filesystem", "npx -y @modelcontextprotocol/server-filesystem /tmp")

    async def on_new_session(self, ctx: Context) -> None:
        """Initialize session."""
        await ctx.emit("MCP Agent Ready!\n\n")
        await ctx.emit("Commands:\n")
        await ctx.emit("  echo <message> - Echo via MCP\n")
        await ctx.emit("  read <file> - Read file from /tmp\n")
        await ctx.emit("  write <file> <content> - Write to /tmp\n\n")

    async def on_prompt(self, ctx: Context, prompt: str):
        """Handle user prompts with MCP tool support."""
        parts = prompt.strip().split(maxsplit=1)

        if not parts:
            yield "Usage: list | echo <msg> | read <file> | write <file> <content>\n"
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
            elif command == "read":
                if len(parts) < 2:
                    yield "Usage: read <filename>\n"
                    return
                await self._read_file(ctx, parts[1])
            elif command == "write":
                if len(parts) < 2:
                    yield "Usage: write <filename> <content>\n"
                    return
                # Split into filename and content
                file_parts = parts[1].split(maxsplit=1)
                if len(file_parts) < 2:
                    yield "Usage: write <filename> <content>\n"
                    return
                await self._write_file(ctx, file_parts[0], file_parts[1])
            else:
                yield f"Unknown command: {command}\n"
                yield "Try: list, echo, read, write\n"
        except Exception as e:
            yield f"Error: {e}\n"

        # Signal completion
        yield ""

    async def _echo_message(self, ctx: Context, message: str):
        """Echo a message using MCP echo server."""
        await ctx.emit(f"Echoing via MCP: {message}\n\n")

        # Call MCP tool via Context API - returns clean ToolResult
        result = await ctx.tools.call("echo_text", message=message)

        # Access text directly - no manual extraction needed!
        await ctx.emit(f"MCP Echo Response: {result.text}\n")

    async def _list_tools(self, ctx: Context):
        """List available MCP tools."""
        # Use clean list() API instead of list_tools()
        tools = await ctx.tools.list()

        await ctx.emit(f"Available MCP tools ({len(tools)}):\n\n")

        for tool in tools:
            desc = f" - {tool.description}" if tool.description else ""
            await ctx.emit(f"  • {tool.name}{desc}\n")

        await ctx.emit("\n")

    async def _read_file(self, ctx: Context, filename: str):
        """Read a file using MCP filesystem tool."""
        await ctx.emit(f"Reading {filename}...\n\n")

        # Call MCP tool via Context API - returns clean ToolResult
        result = await ctx.tools.call("read_file", path=f"/tmp/{filename}")

        await ctx.emit("--- File Contents ---\n")
        await ctx.emit(result.text)
        await ctx.emit("\n--- End ---\n")

    async def _write_file(self, ctx: Context, filename: str, content: str):
        """Write a file using MCP filesystem tool."""
        await ctx.emit(f"Writing to {filename}...\n")

        # Call MCP tool via Context API
        await ctx.tools.call("write_file", path=f"/tmp/{filename}", content=content)

        await ctx.emit(f"Successfully wrote to /tmp/{filename}\n")


if __name__ == "__main__":
    agent = MCPAgent()
    agent.run()
