# chuk-acp-agent

**Build powerful ACP agents with minimal boilerplate**

A clean, type-safe framework for building editor agents. Features one-line MCP setup, direct result access, and zero legacy code.

```python
# That's it - a complete working agent!
from chuk_acp_agent import Agent, Context

class MyAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")  # One line!

    async def on_prompt(self, ctx: Context, prompt: str):
        result = await ctx.tools.call("echo_text", message=prompt)
        yield f"Echo: {result.text}\n"  # Direct access!
```

## Features

- **High-level abstractions**: Rich `Context` API with memory, streaming, and tool integration
- **MCP integration**: Built-in support for Model Context Protocol via `chuk-tool-processor`
  - **Simple config**: One-line MCP server setup with `add_mcp_server()`
  - **Clean results**: Direct `.text` access, no manual extraction
  - **Tool discovery**: List available tools with `ctx.tools.list()`
  - **Batch execution**: Parallel tool calls with `call_batch()`
  - **Load from file**: `load_mcp_config("config.json")` for file-based configuration
- **Session memory**: Key-value storage scoped to session lifecycle
- **Streaming responses**: Async generator pattern with `yield` for real-time output
- **Plan tracking**: Create and update task plans with `send_plan()` and `update_plan()`
- **Type-safe**: Pydantic models throughout (AgentInfo, ToolResult, etc.)

## Installation

```bash
pip install chuk-acp-agent
```

## CLI Usage

The `chuk-acp-agent` CLI provides commands for running agents interactively:

### Interactive Client with MCP Tools

Run an interactive agent with MCP tools loaded from a config file:

```bash
# Run with MCP config file (Kimi-style)
chuk-acp-agent client --mcp-config-file mcp_config.json

# Or using uvx
uvx chuk-acp-agent client --mcp-config-file mcp_config.json
```

The MCP config file follows the standard convention (compatible with Kimi CLI):

```json
{
  "mcpServers": {
    "echo": {
      "command": "uvx",
      "args": ["chuk-mcp-echo", "stdio"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "env": {}
    }
  }
}
```

**Note:** This config format is compatible with Kimi CLI and other tools following the MCP config convention. You can use the same config file with both `chuk-acp-agent client --mcp-config-file` and `kimi --mcp-config-file`.

Once running, you can interact with the agent:

```
> list                                    # List available tools
> call echo_text {"message": "hello"}    # Call a tool
> help                                    # Show help
```

### Comparison with Kimi CLI

| Feature | chuk-acp-agent | Kimi CLI |
|---------|----------------|----------|
| `--mcp-config-file` option | ✅ Yes | ✅ Yes |
| Standard `mcpServers` config | ✅ Yes | ✅ Yes |
| Local MCP servers (stdio) | ✅ Yes | ✅ Yes |
| Remote MCP servers (HTTP) | ❌ No | ✅ Yes |
| Interactive REPL | ✅ Yes | ✅ Yes |
| Custom agent development | ✅ Yes | ❌ No |
| Editor integration (Zed, VS Code) | ✅ Yes | ❌ No |

**Key differences:**
- chuk-acp-agent focuses on **agent development** with editor integration
- Kimi CLI focuses on **interactive use** with remote MCP servers
- Both support the same config format for local MCP servers

### Other Commands

```bash
chuk-acp-agent version   # Show version
chuk-acp-agent help      # Show help
```

## Quick Start

### Minimal Agent

```python
from chuk_acp_agent import Agent, Context

class MyAgent(Agent):
    async def on_prompt(self, ctx: Context, prompt: str):
        """Handle user prompts - yield strings to stream back."""
        # Increment message counter
        count = ctx.memory.get("count", 0) + 1
        ctx.memory.set("count", count)

        yield f"Message #{count}\n"
        yield f"You said: {prompt}\n"
        yield f"Session: {ctx.session_id}\n"

if __name__ == "__main__":
    MyAgent().run()
```

Run it:

```bash
# If installed in current environment
python my_agent.py

# Or use uv (recommended for development)
uv run my_agent.py
```

Test it with the chuk-acp client:

```bash
# Using uv (recommended)
uvx chuk-acp client uv run my_agent.py --prompt "Hello!"

# Or if chuk-acp-agent is installed globally
uvx chuk-acp client python my_agent.py --prompt "Hello!"
```

### Using MCP Tools

**Simple configuration and clean result access:**

```python
from chuk_acp_agent import Agent, Context

class MCPAgent(Agent):
    def __init__(self):
        super().__init__()
        # Simple one-line configuration!
        self.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")
        self.add_mcp_server("filesystem", "npx -y @modelcontextprotocol/server-filesystem /tmp")

    async def on_prompt(self, ctx: Context, prompt: str):
        # Call MCP tool - returns clean ToolResult
        result = await ctx.tools.call("echo_text", message=prompt)

        # Access text directly - no manual extraction!
        yield f"Echo: {result.text}\n"

        # List available tools
        tools = await ctx.tools.list()
        yield f"Available: {', '.join(t.name for t in tools)}\n"

        # Batch execution (runs in parallel)
        results = await ctx.tools.call_batch([
            ("echo_text", {"message": "First"}),
            ("echo_text", {"message": "Second"}),
        ])
        for r in results:
            yield f"- {r.text}\n"
```

**Clean and simple - that's it!**

### Streaming & Progress

```python
async def on_prompt(self, ctx: Context, prompt: str):
    # Send plan
    await ctx.send_plan([
        {"content": "Analyzing code", "status": "in_progress"},
        {"content": "Applying fixes", "status": "pending"},
    ])

    # Stream tokens
    yield "Analyzing...\n"

    # Update plan
    await ctx.update_plan(0, status="completed")
    await ctx.update_plan(1, status="in_progress")

    # Continue streaming
    yield "Fixed 3 issues\n"
```

## Context API

The `Context` object provides access to all agent capabilities:

### Session Memory

```python
# Store data per session
ctx.memory.set("current_file", "/path/to/file.py")
ctx.memory.set("user_preferences", {"theme": "dark"})

# Retrieve
file = ctx.memory.get("current_file")
prefs = ctx.memory.get("user_preferences", default={})
```

### Tools (MCP)

```python
# Call MCP tools - returns clean ToolResult
result = await ctx.tools.call("tool_name", **kwargs)
text = result.text  # Direct text access
is_error = result.is_error  # Check for errors

# List available tools (returns List[Tool])
tools = await ctx.tools.list()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Batch execution (parallel)
results = await ctx.tools.call_batch([
    ("echo_text", {"message": "one"}),
    ("echo_text", {"message": "two"}),
])
```

### Streaming

```python
# Stream text tokens
await ctx.emit("Processing...\n")

# Stream with flushing
async for token in llm_stream:
    await ctx.emit(token)
```

### Plans & Progress

```python
# Create plan
await ctx.send_plan([
    {"content": "Step 1", "status": "pending"},
    {"content": "Step 2", "status": "pending"},
])

# Update plan
await ctx.update_plan(0, status="in_progress")
await ctx.update_plan(0, status="completed")
```

## Agent Lifecycle

```python
from chuk_acp import AgentInfo
from chuk_acp_agent import Agent, Context

class MyAgent(Agent):
    def get_agent_info(self) -> AgentInfo:
        """Return agent metadata using Pydantic type."""
        return AgentInfo(
            name="my-agent",
            version="1.0.0",
            title="My Agent - Custom Agent",
        )

    async def on_new_session(self, ctx: Context) -> None:
        """Called when a new session starts."""
        ctx.memory.set("session_start", time.time())

    async def on_prompt(self, ctx: Context, prompt: str):
        """Handle user prompt. Yield strings to stream back."""
        yield "Response\n"

    async def on_cancel(self, ctx: Context) -> None:
        """Called when user cancels ongoing prompt."""
        # Cleanup resources
        pass
```

## Middleware

Add cross-cutting behaviors:

```python
from chuk_acp_agent import Agent, Context
from chuk_acp_agent.middlewares import TracingMiddleware, RateLimitMiddleware

class MyAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_middleware(TracingMiddleware())
        self.add_middleware(RateLimitMiddleware(max_tokens_per_minute=100000))
```

## Editor Integration

### Zed

Add to `~/.config/zed/settings.json`:

```json
{
  "agent_servers": {
    "My Agent": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/my_agent.py"],
      "env": {}
    }
  }
}
```

Or if `chuk-acp-agent` is installed globally:

```json
{
  "agent_servers": {
    "My Agent": {
      "command": "python",
      "args": ["/absolute/path/to/my_agent.py"],
      "env": {}
    }
  }
}
```

### VS Code (future)

Coming soon.

## Examples

See the [`examples/`](examples/) directory for complete working examples:

**Core Examples:**
- [`echo_agent.py`](examples/echo_agent.py) - Minimal agent with session memory
- [`file_agent.py`](examples/file_agent.py) - File reading and analysis
- [`plan_agent.py`](examples/plan_agent.py) - Task tracking with plans

**MCP Integration:**
- [`mcp_agent_simple.py`](examples/mcp_agent_simple.py) ⭐ **Recommended** - Minimal MCP example (~20 lines)
- [`mcp_agent_advanced.py`](examples/mcp_agent_advanced.py) - Tool discovery, batch execution, error handling
- [`mcp_agent.py`](examples/mcp_agent.py) - Full-featured multi-server setup

All examples showcase the clean DX improvements!

## Architecture

```
chuk-acp-agent/
├─ agent/                 # Core abstractions
│   ├─ base.py            # Agent base class with add_mcp_server()
│   └─ context.py         # Context with tools, memory, plans
├─ integrations/
│   └─ mcp_tools.py       # MCP tool invoker (ToolResult, call_batch, list)
├─ models/
│   ├─ mcp.py             # MCPConfig, MCPServerConfig (Pydantic)
│   ├─ tool.py            # Tool, ToolParameter (Pydantic)
│   └─ tool_result.py     # ToolResult wrapper
├─ exceptions.py          # ToolNotFoundError, ToolExecutionError
└─ examples/              # Working example agents
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=chuk_acp_agent
```

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT
