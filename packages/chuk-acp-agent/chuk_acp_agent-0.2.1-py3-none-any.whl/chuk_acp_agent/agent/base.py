"""
Base agent class that extends chuk-acp's ACPAgent with opinionated defaults.
"""

import json
from abc import abstractmethod
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from chuk_acp.agent import ACPAgent as BaseACPAgent
from chuk_acp.agent.models import AgentSession
from chuk_acp.protocol.types import AgentCapabilities, AgentInfo

from chuk_acp_agent.agent.context import Context
from chuk_acp_agent.models.mcp import MCPConfig, MCPServerConfig


class Agent(BaseACPAgent):
    """
    High-level agent base class with opinionated defaults.

    Subclass and implement:
    - on_prompt(ctx, prompt) - Required: handle user prompts
    - on_new_session(ctx) - Optional: session setup
    """

    def __init__(self) -> None:
        """Initialize agent with default configuration."""
        super().__init__()
        self._mcp_config: MCPConfig | None = None
        self._middlewares: list[Any] = []
        self._agent_name = self.__class__.__name__
        self._agent_version = "0.1.0"
        self._contexts: dict[str, Context] = {}

    # Public API for configuration

    def add_mcp_server(
        self,
        name: str,
        command: str | list[str],
        env: dict[str, str] | None = None,
    ) -> None:
        """
        Add an MCP server using simple command string or list.

        Args:
            name: Server identifier
            command: Command as string ("uvx chuk-mcp-echo stdio") or list
                ["uvx", "chuk-mcp-echo", "stdio"]
            env: Optional environment variables

        Examples:
            # String format (auto-parsed)
            agent.add_mcp_server("echo", "uvx chuk-mcp-echo stdio")

            # List format
            agent.add_mcp_server(
                "filesystem",
                ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            )
        """
        # Parse command if string
        if isinstance(command, str):
            parts = command.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []
        else:
            cmd = command[0]
            args = command[1:] if len(command) > 1 else []

        # Create or update config
        if self._mcp_config is None:
            self._mcp_config = MCPConfig()

        # Add server
        self._mcp_config.mcpServers[name] = MCPServerConfig(
            command=cmd,
            args=args,
            env=env or {},
        )

    def load_mcp_config(self, file_path: str | Path) -> None:
        """
        Load MCP configuration from JSON file.

        Args:
            file_path: Path to mcp_config.json file

        Example:
            agent.load_mcp_config("mcp_config.json")
        """
        path = Path(file_path)
        with open(path) as f:
            config_dict = json.load(f)

        self._mcp_config = MCPConfig.from_dict(config_dict)

    def add_middleware(self, middleware: Any) -> None:
        """
        Add middleware for cross-cutting concerns.

        Middleware can intercept and modify agent behavior.
        """
        self._middlewares.append(middleware)

    # Implement ACPAgent abstract methods

    def get_agent_info(self) -> AgentInfo:
        """Return agent metadata."""
        return AgentInfo(
            name=self._agent_name,
            version=self._agent_version,
            title=f"{self._agent_name} Agent",
        )

    def get_agent_capabilities(self) -> AgentCapabilities:
        """Return agent capabilities (default: basic support)."""
        return AgentCapabilities(
            loadSession=False,  # TODO: support session loading
            modes=["ask", "code"],  # Support ask and code modes
            prompts=None,  # Default text prompts only
            mcpServers=None,  # TODO: advertise MCP support based on registered servers
        )

    async def handle_prompt(self, session: AgentSession, prompt: list) -> str:
        """
        Handle prompt by delegating to on_prompt and streaming response.

        Args:
            session: Current session
            prompt: List of Content objects from the protocol

        Returns:
            Empty string (response is streamed via send_message)
        """
        # Get or create context for this session
        ctx = self._get_or_create_context(session)

        # Call on_new_session if this is the first prompt
        if session.session_id not in self._contexts:
            await self.on_new_session(ctx)
            self._contexts[session.session_id] = ctx

        # Extract text from Content list
        prompt_text = self._extract_text_from_content(prompt)

        # Stream response from agent
        try:
            async for chunk in self.on_prompt(ctx, prompt_text):
                self.send_message(chunk, session.session_id)
        except Exception as e:
            # Stream error back to user
            self.send_message(f"\nError: {str(e)}\n", session.session_id)
            raise

        # Return empty string since we stream via send_message
        return ""

    def _extract_text_from_content(self, content_list: list) -> str:
        """
        Extract text from list of Content objects.

        Args:
            content_list: List of Content objects (dicts with 'type' and content)

        Returns:
            Concatenated text from all text content items
        """
        if not content_list:
            return ""

        texts = []
        for item in content_list:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))

        return " ".join(texts)

    # Lifecycle hooks (override in subclass)

    async def on_new_session(self, ctx: Context) -> None:
        """
        Called when a new session starts.

        Override to initialize session state, load context, etc.

        Args:
            ctx: Agent context for this session
        """
        pass

    @abstractmethod
    async def on_prompt(self, ctx: Context, prompt: str) -> AsyncIterator[str]:
        """
        Handle user prompt - REQUIRED override.

        Yield strings to stream back to the user.

        Args:
            ctx: Agent context
            prompt: User's prompt text

        Yields:
            Response tokens/chunks to stream back
        """
        raise NotImplementedError("Agents must implement on_prompt")
        yield  # Make this a generator for type checking

    # Internal helpers

    def _get_or_create_context(self, session: AgentSession) -> Context:
        """Get existing context or create new one for session."""
        if session.session_id in self._contexts:
            return self._contexts[session.session_id]

        # Create new context
        return Context(
            session_id=session.session_id,
            cwd=session.cwd or "/",  # Default to root if no cwd provided
            agent=self,
            mcp_config=self._mcp_config,
        )
