#!/usr/bin/env python3
"""
Plan demo agent - demonstrates plan/task list functionality.

This agent shows how to create and update plans during execution.

Usage:
    python examples/plan_agent.py
"""

import asyncio

from chuk_acp import AgentInfo

from chuk_acp_agent import Agent, Context


class PlanAgent(Agent):
    """Agent that demonstrates plan/task management."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent metadata using Pydantic type."""
        return AgentInfo(
            name="plan-agent",
            version="1.0.0",
            title="Plan Agent - Task Tracking Demo",
        )

    async def on_prompt(self, ctx: Context, prompt: str):
        """Execute a multi-step task with plan tracking."""
        # Create initial plan
        await ctx.send_plan(
            [
                {"content": "Parse user request", "status": "pending"},
                {"content": "Analyze requirements", "status": "pending"},
                {"content": "Execute task", "status": "pending"},
                {"content": "Summarize results", "status": "pending"},
            ]
        )

        # Step 1: Parse
        await ctx.update_plan(0, status="in_progress")
        yield "Parsing your request...\n"
        await asyncio.sleep(0.5)  # Simulate work
        await ctx.update_plan(0, status="completed")

        # Step 2: Analyze
        await ctx.update_plan(1, status="in_progress")
        yield "Analyzing requirements...\n"
        await asyncio.sleep(0.5)
        await ctx.update_plan(1, status="completed")

        # Step 3: Execute
        await ctx.update_plan(2, status="in_progress")
        yield f"Executing task: {prompt}\n"
        await asyncio.sleep(0.5)

        # Handle different prompts
        if "error" in prompt.lower():
            # Demonstrate error handling with plan update
            await ctx.update_plan(2, content="Execute task (encountered issue)", status="completed")
            yield "Encountered an error during execution\n"
        else:
            await ctx.update_plan(2, status="completed")
            yield "Task completed successfully\n"

        # Step 4: Summarize
        await ctx.update_plan(3, status="in_progress")
        yield "\n--- Summary ---\n"
        yield f"Request: {prompt}\n"
        yield f"Session: {ctx.session_id}\n"
        yield "Status: Done\n"
        await ctx.update_plan(3, status="completed")


if __name__ == "__main__":
    agent = PlanAgent()
    agent.run()
