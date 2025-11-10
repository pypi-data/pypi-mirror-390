"""
chuk-acp-agent: Opinionated agent kit for building sophisticated ACP agents.

Build powerful editor agents with minimal boilerplate on top of chuk-acp.
"""

from chuk_acp_agent.agent.base import Agent
from chuk_acp_agent.agent.context import Context
from chuk_acp_agent.agent.interactive import InteractiveAgent
from chuk_acp_agent.models import MCPConfig, MCPServerConfig

__version__ = "0.2.1"

__all__ = [
    "Agent",
    "Context",
    "InteractiveAgent",
    "MCPConfig",
    "MCPServerConfig",
]
