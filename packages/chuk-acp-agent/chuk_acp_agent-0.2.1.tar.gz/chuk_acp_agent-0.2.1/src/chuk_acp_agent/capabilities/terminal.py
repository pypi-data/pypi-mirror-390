"""
Terminal capability wrapper for command execution.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass

from chuk_acp.protocol.messages.terminal import (
    send_terminal_create,
    send_terminal_kill,
    send_terminal_release,
    send_terminal_wait_for_exit,
)
from chuk_acp.transport.base import Transport


@dataclass
class CommandResult:
    """Result of command execution."""

    exit_code: int
    stdout: str
    stderr: str


class Terminal:
    """
    Terminal operations for command execution.

    Provides both blocking and streaming execution modes.
    """

    def __init__(self, transport: Transport) -> None:
        """
        Initialize terminal capability.

        Args:
            transport: ACP transport for communication
        """
        self._transport = transport

    async def run(
        self,
        command: str,
        *args: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> CommandResult:
        """
        Execute command and wait for completion.

        Args:
            command: Command to execute
            args: Command arguments
            cwd: Working directory (absolute path)
            env: Environment variables

        Returns:
            CommandResult with exit code and output

        Raises:
            RuntimeError: If command execution fails
        """
        # Get streams from transport
        read_stream, write_stream = await self._transport.get_streams()

        # Create terminal
        create_result = await send_terminal_create(
            read_stream,
            write_stream,
            command=command,
            args=list(args),
            cwd=cwd,
            env=env,
        )

        terminal_id = create_result.id

        try:
            # Wait for exit
            exit_result = await send_terminal_wait_for_exit(
                read_stream,
                write_stream,
                terminal_id=terminal_id,
            )

            # TODO: Capture stdout/stderr
            # For now, return basic result
            return CommandResult(
                exit_code=exit_result.exitCode,
                stdout="",  # TODO: capture output
                stderr="",
            )

        finally:
            # Always release terminal
            await send_terminal_release(
                read_stream,
                write_stream,
                terminal_id=terminal_id,
            )

    async def run_streaming(
        self,
        command: str,
        *args: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> AsyncIterator[str]:
        """
        Execute command and stream output line-by-line.

        Args:
            command: Command to execute
            args: Command arguments
            cwd: Working directory (absolute path)
            env: Environment variables

        Yields:
            Output lines as they arrive

        Note:
            This is a simplified streaming implementation.
            Full streaming requires output capture and notification handling.
        """
        # Get streams from transport
        read_stream, write_stream = await self._transport.get_streams()

        # Create terminal
        create_result = await send_terminal_create(
            read_stream,
            write_stream,
            command=command,
            args=list(args),
            cwd=cwd,
            env=env,
        )

        terminal_id = create_result.id

        try:
            # TODO: Implement actual streaming via output notifications
            # For now, just wait and yield final result
            exit_result = await send_terminal_wait_for_exit(
                read_stream,
                write_stream,
                terminal_id=terminal_id,
            )

            yield f"Command exited with code {exit_result.exitCode}\n"

        finally:
            await send_terminal_release(
                read_stream,
                write_stream,
                terminal_id=terminal_id,
            )

    async def kill(self, terminal_id: str) -> None:
        """
        Kill a running terminal process.

        Args:
            terminal_id: Terminal identifier

        Raises:
            RuntimeError: If kill fails
        """
        read_stream, write_stream = await self._transport.get_streams()
        await send_terminal_kill(
            read_stream,
            write_stream,
            terminal_id=terminal_id,
        )
