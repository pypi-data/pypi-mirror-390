#!/usr/bin/env python3
"""
File helper agent - demonstrates file system operations.

This agent can read and analyze files in the workspace.

Usage:
    python examples/file_agent.py
"""

from chuk_acp import AgentInfo

from chuk_acp_agent import Agent, Context


class FileAgent(Agent):
    """Agent that helps with file operations."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent metadata using Pydantic type."""
        return AgentInfo(
            name="file-agent",
            version="1.0.0",
            title="File Agent - File Analysis and Operations",
        )

    async def on_new_session(self, ctx: Context) -> None:
        """Set up session."""
        await ctx.emit("File Agent ready! Try:\n")
        await ctx.emit("- 'read <file>' to read a file\n")
        await ctx.emit("- 'analyze <file>' to get statistics\n")

    async def on_prompt(self, ctx: Context, prompt: str):
        """Handle file operations based on prompt."""
        parts = prompt.strip().split(maxsplit=1)

        if len(parts) < 2:
            yield "Usage: <command> <file>\n"
            yield "Commands: read, analyze\n"
            return

        command, arg = parts

        if command == "read":
            await self._read_file(ctx, arg)
        elif command == "analyze":
            await self._analyze_file(ctx, arg)
        else:
            yield f"Unknown command: {command}\n"

    async def _read_file(self, ctx: Context, file_path: str):
        """Read and display file contents."""
        try:
            # Make path absolute if relative
            import os

            if not os.path.isabs(file_path):
                file_path = os.path.join(ctx.cwd, file_path)

            await ctx.emit(f"Reading {file_path}...\n\n")

            # Use standard Python file operations
            with open(file_path) as f:
                content = f.read()

            await ctx.emit("--- File Contents ---\n")
            await ctx.emit(content)
            await ctx.emit("\n--- End ---\n")

        except Exception as e:
            await ctx.emit(f"Error reading file: {e}\n")

    async def _analyze_file(self, ctx: Context, file_path: str):
        """Analyze file and show statistics."""
        try:
            # Make path absolute if relative
            import os

            if not os.path.isabs(file_path):
                file_path = os.path.join(ctx.cwd, file_path)

            await ctx.emit(f"Analyzing {file_path}...\n\n")

            # Use standard Python file operations
            with open(file_path) as f:
                content = f.read()

            # Calculate stats
            lines = content.split("\n")
            words = content.split()
            chars = len(content)

            await ctx.emit(f"File: {file_path}\n")
            await ctx.emit(f"Lines: {len(lines)}\n")
            await ctx.emit(f"Words: {len(words)}\n")
            await ctx.emit(f"Characters: {chars}\n")

            # Count non-empty lines
            non_empty = sum(1 for line in lines if line.strip())
            await ctx.emit(f"Non-empty lines: {non_empty}\n")

        except Exception as e:
            await ctx.emit(f"Error analyzing file: {e}\n")


if __name__ == "__main__":
    agent = FileAgent()
    agent.run()
