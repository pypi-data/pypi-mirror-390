"""
File system capability wrapper with permission policies.
"""

from pathlib import Path

from chuk_acp.protocol.messages.filesystem import (
    send_fs_read_text_file,
    send_fs_write_text_file,
)
from chuk_acp.transport.base import Transport


class FileSystem:
    """
    File system operations with optional permission checks.

    All paths must be absolute.
    """

    def __init__(self, transport: Transport) -> None:
        """
        Initialize file system capability.

        Args:
            transport: ACP transport for communication
        """
        self._transport = transport

    async def read_text(
        self,
        path: str,
        *,
        require_permission: bool = False,
    ) -> str:
        """
        Read text file contents.

        Args:
            path: Absolute file path
            require_permission: If True, request user permission before reading

        Returns:
            File contents as string

        Raises:
            ValueError: If path is not absolute
            FileNotFoundError: If file doesn't exist (via ACP error)
        """
        self._validate_absolute_path(path)

        # TODO: Implement permission check via send_session_request_permission
        if require_permission:
            # For now, just proceed - permission framework TBD
            pass

        read_stream, write_stream = await self._transport.get_streams()
        result = await send_fs_read_text_file(
            read_stream,
            write_stream,
            path=path,
        )

        return result

    async def write_text(
        self,
        path: str,
        contents: str,
        *,
        require_permission: bool = False,
    ) -> None:
        """
        Write text to file.

        Args:
            path: Absolute file path
            contents: Text to write
            require_permission: If True, request user permission before writing

        Raises:
            ValueError: If path is not absolute
        """
        self._validate_absolute_path(path)

        # TODO: Implement permission check
        if require_permission:
            pass

        read_stream, write_stream = await self._transport.get_streams()
        await send_fs_write_text_file(
            read_stream,
            write_stream,
            path=path,
            contents=contents,
        )

    def _validate_absolute_path(self, path: str) -> None:
        """
        Validate that path is absolute.

        Args:
            path: Path to validate

        Raises:
            ValueError: If path is not absolute
        """
        if not Path(path).is_absolute():
            raise ValueError(f"Path must be absolute, got: {path}")
