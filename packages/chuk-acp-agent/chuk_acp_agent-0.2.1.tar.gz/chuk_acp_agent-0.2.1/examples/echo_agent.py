#!/usr/bin/env python3
"""
Minimal echo agent - demonstrates basic agent structure.

Usage:
    python examples/echo_agent.py

Then configure in Zed:
    {
      "agent_servers": {
        "Echo Agent": {
          "command": "python",
          "args": ["/absolute/path/to/examples/echo_agent.py"]
        }
      }
    }
"""

from chuk_acp import AgentInfo

from chuk_acp_agent import Agent, Context


class EchoAgent(Agent):
    """Simple agent that echoes back user input."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent metadata using Pydantic type."""
        return AgentInfo(
            name="echo-agent",
            version="1.0.0",
            title="Echo Agent - Simple Testing Agent",
        )

    async def on_new_session(self, ctx: Context) -> None:
        """Initialize session state."""
        ctx.memory.set("message_count", 0)

    async def on_prompt(self, ctx: Context, prompt: str):
        """Echo back the user's prompt."""
        # Increment message counter
        count = ctx.memory.get("message_count", 0)
        ctx.memory.set("message_count", count + 1)

        # Stream response
        yield f"Message #{count + 1}\n"
        yield f"You said: {prompt}\n"
        yield f"Session: {ctx.session_id}\n"
        yield f"CWD: {ctx.cwd}\n"


if __name__ == "__main__":
    agent = EchoAgent()
    agent.run()
