"""Tests for MCP configuration models."""

from chuk_acp_agent.models.mcp import MCPConfig, MCPServerConfig


class TestMCPServerConfig:
    """Test MCPServerConfig model."""

    def test_creation_minimal(self):
        """Test creating with minimal fields."""
        config = MCPServerConfig(command="uvx", args=["chuk-mcp-echo"])
        assert config.command == "uvx"
        assert config.args == ["chuk-mcp-echo"]
        assert config.env == {}

    def test_creation_with_env(self):
        """Test creating with environment variables."""
        config = MCPServerConfig(command="node", args=["server.js"], env={"NODE_ENV": "production"})
        assert config.command == "node"
        assert config.args == ["server.js"]
        assert config.env == {"NODE_ENV": "production"}

    def test_default_env_is_empty_dict(self):
        """Test that env defaults to empty dict."""
        config = MCPServerConfig(command="test", args=[])
        assert config.env == {}
        assert isinstance(config.env, dict)

    def test_model_dump(self):
        """Test Pydantic model_dump."""
        config = MCPServerConfig(command="test", args=["arg1"])
        data = config.model_dump()
        assert "command" in data
        assert "args" in data
        assert "env" in data


class TestMCPConfig:
    """Test MCPConfig model."""

    def test_creation_minimal(self):
        """Test creating with minimal fields."""
        config = MCPConfig()
        assert config.mcpServers == {}
        assert config.namespace == "mcp"
        assert config.enable_caching is True
        assert config.cache_ttl == 300
        assert config.default_timeout == 10.0
        assert config.max_retries == 3

    def test_creation_with_servers(self):
        """Test creating with MCP servers."""
        servers = {"echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo"])}
        config = MCPConfig(mcpServers=servers)
        assert "echo" in config.mcpServers
        assert config.mcpServers["echo"].command == "uvx"

    def test_custom_namespace(self):
        """Test custom namespace."""
        config = MCPConfig(namespace="tools")
        assert config.namespace == "tools"

    def test_disable_caching(self):
        """Test disabling cache."""
        config = MCPConfig(enable_caching=False)
        assert config.enable_caching is False

    def test_custom_timeouts(self):
        """Test custom timeout values."""
        config = MCPConfig(cache_ttl=600, default_timeout=60, max_retries=5)
        assert config.cache_ttl == 600
        assert config.default_timeout == 60
        assert config.max_retries == 5

    def test_to_dict(self):
        """Test converting to dictionary."""
        servers = {"echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo"])}
        config = MCPConfig(mcpServers=servers, namespace="mcp", enable_caching=True)
        data = config.to_dict()
        assert "mcpServers" in data
        assert "echo" in data["mcpServers"]
        assert data["mcpServers"]["echo"]["command"] == "uvx"

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "mcpServers": {
                "echo": {"command": "uvx", "args": ["chuk-mcp-echo", "stdio"], "env": {}}
            },
            "namespace": "mcp",
            "enable_caching": True,
            "cache_ttl": 300,
            "default_timeout": 10.0,
            "max_retries": 3,
        }
        config = MCPConfig.from_dict(data)
        assert "echo" in config.mcpServers
        assert config.mcpServers["echo"].command == "uvx"
        assert config.namespace == "mcp"
        assert config.enable_caching is True

    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        data = {"mcpServers": {}}
        config = MCPConfig.from_dict(data)
        assert config.mcpServers == {}
        # Should use defaults
        assert config.namespace == "mcp"
        assert config.enable_caching is True

    def test_round_trip(self):
        """Test to_dict -> from_dict round trip."""
        original = MCPConfig(
            mcpServers={
                "echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo"], env={"DEBUG": "1"})
            },
            namespace="test",
            enable_caching=False,
            cache_ttl=600,
        )
        data = original.to_dict()
        restored = MCPConfig.from_dict(data)

        assert restored.namespace == original.namespace
        assert restored.enable_caching == original.enable_caching
        assert restored.cache_ttl == original.cache_ttl
        assert "echo" in restored.mcpServers

    def test_multiple_servers(self):
        """Test configuration with multiple servers."""
        servers = {
            "echo": MCPServerConfig(command="uvx", args=["chuk-mcp-echo"]),
            "fs": MCPServerConfig(command="npx", args=["@modelcontextprotocol/server-filesystem"]),
        }
        config = MCPConfig(mcpServers=servers)
        assert len(config.mcpServers) == 2
        assert "echo" in config.mcpServers
        assert "fs" in config.mcpServers

    def test_model_dump(self):
        """Test Pydantic model_dump."""
        config = MCPConfig(namespace="test")
        data = config.model_dump()
        assert "mcpServers" in data
        assert "namespace" in data
        assert data["namespace"] == "test"

    def test_defaults(self):
        """Test all default values."""
        config = MCPConfig()
        assert config.mcpServers == {}
        assert config.namespace == "mcp"
        assert config.enable_caching is True
        assert config.cache_ttl == 300
        assert config.default_timeout == 10.0
        assert config.max_retries == 3
