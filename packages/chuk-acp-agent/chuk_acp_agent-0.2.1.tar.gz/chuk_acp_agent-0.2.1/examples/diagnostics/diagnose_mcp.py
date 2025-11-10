#!/usr/bin/env python3
"""
Diagnostic script to test MCP integration directly.

This tests chuk-tool-processor setup independently of the agent framework
to identify where the issue is.
"""

import asyncio
import json
import tempfile
from pathlib import Path


async def main():
    """Run MCP diagnostics."""
    print("=== MCP Diagnostic Script ===\n")

    # Step 1: Create MCP config
    print("Step 1: Creating MCP config...")
    config = {"mcpServers": {"echo": {"command": "uvx", "args": ["chuk-mcp-echo", "stdio"]}}}

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f, indent=2)
        config_file = f.name

    print(f"   Config file: {config_file}")
    print(f"   Config: {json.dumps(config, indent=2)}\n")

    try:
        # Step 2: Import chuk-tool-processor
        print("Step 2: Importing chuk-tool-processor...")
        try:
            from chuk_tool_processor.mcp import setup_mcp_stdio
            from chuk_tool_processor.models.tool_call import ToolCall
            from chuk_tool_processor.registry import ToolRegistryProvider

            print("   ✓ Imports successful\n")
        except ImportError as e:
            print(f"   ✗ Import failed: {e}\n")
            return

        # Step 3: Setup MCP
        print("Step 3: Setting up MCP with setup_mcp_stdio...")
        try:
            processor, stream_manager = await setup_mcp_stdio(
                config_file=config_file,
                servers=["echo"],
                namespace="mcp",
            )
            print("   ✓ MCP setup successful\n")
        except Exception as e:
            print(f"   ✗ Setup failed: {e}\n")
            import traceback

            traceback.print_exc()
            return

        # Step 4: List tools
        print("Step 4: Listing available tools...")
        try:
            registry = ToolRegistryProvider.get_registry()
            tools = registry.list_tools()
            print(f"   Found {len(tools)} tools:")
            for tool_name, tool in tools.items():
                print(f"     - {tool_name}")
                if hasattr(tool, "description"):
                    print(f"       {tool.description}")
            print()
        except AttributeError:
            # registry is a coroutine, try awaiting it
            try:
                print("   (Awaiting registry coroutine...)")
                registry = await ToolRegistryProvider.get_registry()
                tools = registry.list_tools()
                print(f"   Found {len(tools)} tools:")
                for tool_name, tool in tools.items():
                    print(f"     - {tool_name}")
                    if hasattr(tool, "description"):
                        print(f"       {tool.description}")
                print()
            except Exception as e:
                print(f"   ✗ Failed to list tools (with await): {e}\n")
                import traceback

                traceback.print_exc()
        except Exception as e:
            print(f"   ✗ Failed to list tools: {e}\n")
            import traceback

            traceback.print_exc()

        # Step 5: Test echo tool call
        print("Step 5: Testing echo tool call...")
        test_message = "Hello from diagnostic!"

        try:
            # Try different tool call formats
            test_calls = [
                ("mcp.echo_text", {"message": test_message}),
                ("mcp.echo_text", {"text": test_message}),
                ("echo_text", {"message": test_message}),
                ("echo_text", {"text": test_message}),
            ]

            for tool_name, args in test_calls:
                print(f"\n   Attempting: tool='{tool_name}', args={args}")
                tool_call = ToolCall(tool=tool_name, arguments=args)
                print(f"   Tool call object: {tool_call}")

                # Use execute() with list, not process()
                results = await processor.execute([tool_call])
                print(f"   Results type: {type(results)}")
                print(f"   Results length: {len(results)}")

                if results and len(results) > 0:
                    result = results[0]
                    print(f"   ✓ Success with '{tool_name}'!")
                    print(f"   Result: {result}")
                    if hasattr(result, "result"):
                        print(f"   Content: {result.result}")
                    if hasattr(result, "error"):
                        print(f"   Error: {result.error}")
                    break
                else:
                    print("   ✗ No results")
            else:
                print("\n   ✗ All tool name variations failed")

        except Exception as e:
            print(f"   ✗ Tool call failed: {e}\n")
            import traceback

            traceback.print_exc()

        # Step 6: Cleanup
        print("\nStep 6: Cleaning up...")
        try:
            await stream_manager.cleanup()
            Path(config_file).unlink()
            print("   ✓ Cleanup successful")
        except Exception as e:
            print(f"   ✗ Cleanup failed: {e}")

    finally:
        # Ensure temp file is deleted
        try:
            Path(config_file).unlink()
        except Exception:
            pass

    print("\n=== Diagnostic Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
