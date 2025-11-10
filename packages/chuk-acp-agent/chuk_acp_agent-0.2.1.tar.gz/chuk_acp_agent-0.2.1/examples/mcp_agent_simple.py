#!/usr/bin/env python3
"""
Simple MCP agent - demonstrates improved DX with helper methods.

This is the same as mcp_agent.py but with simpler configuration using
the add_mcp_server() helper method instead of Pydantic models.
"""

from chuk_acp_agent import Agent, Context


class SimpleMCPAgent(Agent):
    """Agent with MCP - using simple configuration helpers."""

    def __init__(self):
        """Initialize agent with MCP servers."""
        super().__init__()

        # Simple string-based configuration!
        self.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")
        self.add_mcp_server("filesystem", "npx -y @modelcontextprotocol/server-filesystem /tmp")

    async def on_new_session(self, ctx: Context) -> None:
        """Initialize session."""
        await ctx.emit("Simple MCP Agent Ready!\n\n")
        await ctx.emit("Try: echo <message>\n\n")

    async def on_prompt(self, ctx: Context, prompt: str):
        """Handle user prompts."""
        parts = prompt.strip().split(maxsplit=1)

        if not parts:
            yield "Usage: echo <message>\n"
            return

        command = parts[0].lower()

        if command == "echo":
            if len(parts) < 2:
                yield "Usage: echo <message>\n"
                return

            # Simple tool call with clean result!
            result = await ctx.tools.call("echo_text", message=parts[1])
            yield f"Echo: {result.text}\n"  # Clean text extraction!
        else:
            yield f"Unknown command: {command}\n"

        yield ""  # Signal completion


if __name__ == "__main__":
    agent = SimpleMCPAgent()
    agent.run()
