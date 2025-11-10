"""Capability wrappers for file system, terminal, etc."""

from chuk_acp_agent.capabilities.filesystem import FileSystem
from chuk_acp_agent.capabilities.terminal import CommandResult, Terminal

__all__ = [
    "FileSystem",
    "Terminal",
    "CommandResult",
]
