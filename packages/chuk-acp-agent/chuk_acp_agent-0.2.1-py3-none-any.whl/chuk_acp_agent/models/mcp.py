"""
Pydantic models for MCP configuration.
"""

from typing import Any

from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    command: str = Field(..., description="Command to execute (e.g., 'npx', 'uvx', 'python')")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")


class MCPConfig(BaseModel):
    """MCP configuration matching the JSON config file format."""

    mcpServers: dict[str, MCPServerConfig] = Field(  # noqa: N815
        default_factory=dict, description="Map of server name to server configuration"
    )
    namespace: str = Field(default="mcp", description="Tool namespace prefix")
    enable_caching: bool = Field(default=True, description="Enable tool result caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    default_timeout: float = Field(default=10.0, description="Default timeout for tool calls")
    max_retries: int = Field(default=3, description="Maximum retries for failed calls")

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "MCPConfig":
        """
        Create MCPConfig from dictionary (e.g., loaded from JSON).

        Args:
            config: Configuration dictionary

        Returns:
            MCPConfig instance
        """
        # Convert nested server configs to MCPServerConfig objects
        servers = {}
        for name, server_data in config.get("mcpServers", {}).items():
            if isinstance(server_data, dict):
                servers[name] = MCPServerConfig(**server_data)
            else:
                servers[name] = server_data

        return cls(
            mcpServers=servers,
            namespace=config.get("namespace", "mcp"),
            enable_caching=config.get("enable_caching", True),
            cache_ttl=config.get("cache_ttl", 300),
            default_timeout=config.get("default_timeout", 10.0),
            max_retries=config.get("max_retries", 3),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Configuration as dictionary
        """
        return {
            "mcpServers": {
                name: {
                    "command": server.command,
                    "args": server.args,
                    "env": server.env,
                }
                for name, server in self.mcpServers.items()
            },
            "namespace": self.namespace,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
        }
