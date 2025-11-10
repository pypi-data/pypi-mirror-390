#!/usr/bin/env python3
"""Test ToolResult wrapper."""

import asyncio
import json
import tempfile
from pathlib import Path


async def main():
    """Test ToolResult extraction."""
    from chuk_tool_processor.mcp import setup_mcp_stdio
    from chuk_tool_processor.models.tool_call import ToolCall

    from chuk_acp_agent.models.tool_result import ToolResult

    # Setup MCP
    config = {"mcpServers": {"echo": {"command": "uvx", "args": ["chuk-mcp-echo", "stdio"]}}}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f, indent=2)
        config_file = f.name

    try:
        processor, _ = await setup_mcp_stdio(
            config_file=config_file,
            servers=["echo"],
            namespace="mcp",
        )

        # Make tool call
        tool_call = ToolCall(tool="mcp.echo_text", arguments={"message": "Test message"})

        results = await processor.execute([tool_call])
        raw_result = results[0]

        print(f"Raw result type: {type(raw_result)}")
        print(f"Raw result: {raw_result}")
        print()

        # Check all attributes
        print("All attributes:")
        for attr in dir(raw_result):
            if not attr.startswith("_"):
                value = getattr(raw_result, attr)
                if not callable(value):
                    print(f"  {attr}: {value}")
        print()

        # Test ToolResult wrapper
        wrapped = ToolResult(raw_result)
        print(f"ToolResult.text: {wrapped.text}")
        print(f"ToolResult.is_error: {wrapped.is_error}")
        print(f"ToolResult.__str__(): {str(wrapped)}")

    finally:
        Path(config_file).unlink()


if __name__ == "__main__":
    asyncio.run(main())
