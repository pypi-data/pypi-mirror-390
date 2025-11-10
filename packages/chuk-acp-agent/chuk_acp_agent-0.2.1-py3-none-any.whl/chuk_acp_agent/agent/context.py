"""
Context object that provides access to all agent capabilities.
"""

from typing import TYPE_CHECKING, Any, Optional, cast

from chuk_acp.protocol.types import PlanEntry, PlanEntryPriority, PlanEntryStatus

from chuk_acp_agent.agent.session import SessionMemory

if TYPE_CHECKING:
    from chuk_acp_agent.agent.base import Agent
    from chuk_acp_agent.models.mcp import MCPConfig


class Context:
    """
    Agent context providing access to capabilities and session state.

    Attributes:
        session_id: Unique session identifier
        cwd: Current working directory
        memory: Session-scoped key-value storage
    """

    def __init__(
        self,
        session_id: str,
        cwd: str,
        agent: "Agent",
        mcp_config: Optional["MCPConfig"] = None,
    ) -> None:
        """
        Initialize context.

        Args:
            session_id: Session identifier
            cwd: Working directory
            agent: ACP agent for communication
            mcp_config: Optional MCP configuration (Pydantic model)
        """
        self.session_id = session_id
        self.cwd = cwd
        self._agent = agent
        self._mcp_config = mcp_config

        # Initialize capabilities
        # Note: fs and terminal are temporarily disabled until we have proper transport integration
        # self.fs = FileSystem(transport)
        # self.terminal = Terminal(terminal)
        self.memory = SessionMemory()

        # Tools will be initialized lazily
        self._tools: Any | None = None
        self._plan: list[PlanEntry] = []

    async def emit(self, text: str) -> None:
        """
        Stream text back to the user.

        Args:
            text: Text chunk to stream
        """
        # Use agent's send_message which writes to stdout (not async)
        self._agent.send_message(text, self.session_id)

    async def send_plan(
        self,
        entries: list[dict[str, Any]],
    ) -> None:
        """
        Send plan/task list to the user.

        Args:
            entries: List of plan entries with:
                - content: str (required) - Task description
                - status: str (optional) - pending/in_progress/completed
                - priority: str (optional) - high/medium/low
        """
        # TODO: Implement plan sending via agent
        # For now, just store the plan
        self._plan = [
            PlanEntry(
                content=entry["content"],
                status=entry.get("status", "pending"),  # Just use the string directly
                priority=entry.get("priority", "medium"),  # Just use the string directly
            )
            for entry in entries
        ]

    async def update_plan(
        self,
        index: int,
        *,
        content: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> None:
        """
        Update a specific plan entry.

        Args:
            index: Entry index (0-based)
            content: Optional new content
            status: Optional new status (pending/in_progress/completed)
            priority: Optional new priority (high/medium/low)
        """
        if index < 0 or index >= len(self._plan):
            raise IndexError(f"Plan index {index} out of range (0-{len(self._plan) - 1})")

        entry = self._plan[index]
        if content is not None:
            entry.content = content
        if status is not None:
            entry.status = cast(PlanEntryStatus, status)
        if priority is not None:
            entry.priority = cast(PlanEntryPriority, priority)

        # TODO: Re-send entire plan via agent

    @property
    def tools(self) -> Any:
        """
        Get MCP tool invoker.

        Raises:
            ImportError: If chuk-tool-processor is not installed
            RuntimeError: If no MCP config is set
        """
        if self._tools is None:
            if not self._mcp_config:
                raise RuntimeError("No MCP configuration set. Use agent.add_mcp_server() first.")

            try:
                from chuk_acp_agent.integrations.mcp_tools import ToolInvoker
            except ImportError as e:
                raise ImportError(
                    "MCP support requires chuk-tool-processor. "
                    "Install with: pip install chuk-acp-agent"
                ) from e

            self._tools = ToolInvoker(mcp_config=self._mcp_config)

        return self._tools
