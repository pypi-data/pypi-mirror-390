# Example Agents

This directory contains example agents demonstrating various features of `chuk-acp-agent`.

## Quick Start

**Interactive client with MCP tools (Kimi-style):**
```bash
chuk-acp-agent client --mcp-config-file examples/mcp_config.json
```

**Simplest possible agent:**
```bash
uv run examples/echo_agent.py
```

**MCP integration (recommended):**
```bash
uv run examples/mcp_agent_simple.py
```

## Core Examples

### 1. Echo Agent (`echo_agent.py`)

**Best for:** Learning the basics

Minimal agent that echoes back user input with session memory.

**Demonstrates:**
- Basic agent structure (20 lines!)
- Session memory
- Streaming responses

**Run:**
```bash
uvx chuk-acp client uv run examples/echo_agent.py --prompt "Hello!"
```

**Output:**
```
Message #1
You said: Hello!
Session: session_abc123
CWD: /path/to/project
```

### 2. File Agent (`file_agent.py`)

**Best for:** File system operations

Read and analyze files in the workspace.

**Demonstrates:**
- File operations
- Command parsing
- Error handling

**Run:**
```bash
uvx chuk-acp client uv run examples/file_agent.py --prompt "read pyproject.toml"
```

### 3. Plan Agent (`plan_agent.py`)

**Best for:** Multi-step tasks

Task execution with progress tracking.

**Demonstrates:**
- Plan/task lists
- Progress updates
- Async operations

**Run:**
```bash
uvx chuk-acp client uv run examples/plan_agent.py --prompt "analyze this project"
```

## Interactive Client

The CLI provides an interactive client that can load MCP tools from a config file:

```bash
# Run with MCP config (Kimi-compatible format)
chuk-acp-agent client --mcp-config-file examples/mcp_config.json
```

Once running, you can:
```
> list                                    # List all available MCP tools
> call echo_text {"message": "hello"}    # Call a tool with JSON arguments
> help                                    # Show help
```

This is compatible with the Kimi CLI config format, so you can use the same `mcp_config.json` file:

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

## MCP Integration Examples

### Simple MCP Agent (`mcp_agent_simple.py`) ⭐ **Recommended**

**Best for:** Getting started with MCP

Clean, minimal MCP integration example.

**Features:**
- Simple configuration (`add_mcp_server()`)
- Clean result access (`.text`)
- ~20 lines of code

**Run:**
```bash
uvx chuk-acp client uv run examples/mcp_agent_simple.py --prompt "echo Hello!"
```

**Output:**
```
Simple MCP Agent Ready!

Try: echo <message>

Echo: Hello!
```

**Code:**
```python
class SimpleMCPAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")

    async def on_prompt(self, ctx: Context, prompt: str):
        result = await ctx.tools.call("echo_text", message=prompt)
        yield f"Echo: {result.text}\n"
```

### Advanced MCP Agent (`mcp_agent_advanced.py`)

**Best for:** Learning all MCP features

Showcases all advanced MCP capabilities.

**Features:**
- Tool discovery (`ctx.tools.list()`)
- Batch execution (`call_batch()`)
- Error handling with suggestions
- Clean abstractions

**Run:**
```bash
# Discover tools
uvx chuk-acp client uv run examples/mcp_agent_advanced.py --prompt "list"

# Batch execution
uvx chuk-acp client uv run examples/mcp_agent_advanced.py --prompt "batch"

# Error handling demo
uvx chuk-acp client uv run examples/mcp_agent_advanced.py --prompt "error"
```

### Original MCP Agent (`mcp_agent.py`)

**Best for:** Reference implementation

Full-featured MCP example with both echo and filesystem servers.

**Features:**
- Multiple MCP servers
- Comprehensive error handling
- File operations in /tmp

**Run:**
```bash
# Echo test
uvx chuk-acp client uv run examples/mcp_agent.py --prompt "echo Hello!"

# File operations
echo "test" > /tmp/test.txt
uvx chuk-acp client uv run examples/mcp_agent.py --prompt "read test.txt"
uvx chuk-acp client uv run examples/mcp_agent.py --prompt "write hello.txt Hello World"
```

## Editor Integration

### Zed

Add to `~/.config/zed/settings.json`:

**Using uv (recommended for development):**

```json
{
  "agent_servers": {
    "Echo Agent": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/chuk-acp-agent/examples/echo_agent.py"]
    },
    "File Agent": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/chuk-acp-agent/examples/file_agent.py"]
    },
    "Plan Agent": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/chuk-acp-agent/examples/plan_agent.py"]
    }
  }
}
```

**Or if installed globally:**

```json
{
  "agent_servers": {
    "Echo Agent": {
      "command": "python",
      "args": ["/absolute/path/to/chuk-acp-agent/examples/echo_agent.py"]
    },
    "File Agent": {
      "command": "python",
      "args": ["/absolute/path/to/chuk-acp-agent/examples/file_agent.py"]
    },
    "Plan Agent": {
      "command": "python",
      "args": ["/absolute/path/to/chuk-acp-agent/examples/plan_agent.py"]
    }
  }
}
```

Then use `Cmd+Shift+P` → "Agent" to interact.

## Next Steps

1. **Customize:** Copy an example and modify it for your use case
2. **Add LLM:** Integrate with OpenAI, Anthropic, or local models in `on_prompt()`
3. **Add Tools:** Use `ctx.tools` to call MCP tools (requires `chuk-tool-processor`)
4. **Add Middleware:** Add tracing, rate limiting, etc.

## Tips

- **Always use absolute paths** for file operations
- **Stream responses** using `yield` for better UX
- **Update plans** to show progress in real-time
- **Use session memory** (`ctx.memory`) for state between prompts
- **Handle errors gracefully** and provide clear feedback
