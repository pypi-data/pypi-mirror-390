"""Tests for filesystem capability."""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from chuk_acp_agent.capabilities.filesystem import FileSystem


class TestFileSystem:
    """Test FileSystem capability."""

    def test_initialization(self):
        """Test filesystem initialization."""
        transport = Mock()
        fs = FileSystem(transport)
        assert fs._transport == transport

    @pytest.mark.asyncio
    async def test_read_text(self):
        """Test reading text file."""
        from unittest.mock import patch

        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        fs = FileSystem(transport)

        # Use platform-independent absolute path
        test_path = str(Path.cwd() / "file.txt")

        # Mock the send_fs_read_text_file function
        with patch("chuk_acp_agent.capabilities.filesystem.send_fs_read_text_file") as mock_read:
            mock_read.return_value = "file contents"

            result = await fs.read_text(test_path)
            assert result == "file contents"

    def test_validate_absolute_path_rejects_relative(self):
        """Test that relative paths are rejected."""
        transport = Mock()
        fs = FileSystem(transport)

        with pytest.raises(ValueError, match="Path must be absolute"):
            fs._validate_absolute_path("relative/path.txt")

    def test_validate_absolute_path_accepts_absolute(self):
        """Test that absolute paths are accepted."""
        transport = Mock()
        fs = FileSystem(transport)

        # Use platform-independent absolute path
        test_path = str(Path.cwd() / "path.txt")

        # Should not raise
        fs._validate_absolute_path(test_path)

    @pytest.mark.asyncio
    async def test_read_text_validates_path(self):
        """Test read_text validates path."""
        transport = Mock()
        fs = FileSystem(transport)

        with pytest.raises(ValueError, match="Path must be absolute"):
            await fs.read_text("relative/path.txt")

    @pytest.mark.asyncio
    async def test_write_text_validates_path(self):
        """Test write_text validates path."""
        transport = Mock()
        fs = FileSystem(transport)

        with pytest.raises(ValueError, match="Path must be absolute"):
            await fs.write_text("relative/path.txt", "contents")

    @pytest.mark.asyncio
    async def test_read_text_with_permission(self):
        """Test reading text file with permission check."""
        from unittest.mock import patch

        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        fs = FileSystem(transport)

        # Use platform-independent absolute path
        test_path = str(Path.cwd() / "file.txt")

        # Mock the send_fs_read_text_file function
        with patch("chuk_acp_agent.capabilities.filesystem.send_fs_read_text_file") as mock_read:
            mock_read.return_value = "file contents"

            result = await fs.read_text(test_path, require_permission=True)
            assert result == "file contents"

    @pytest.mark.asyncio
    async def test_write_text(self):
        """Test writing text file."""
        from unittest.mock import patch

        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        fs = FileSystem(transport)

        # Use platform-independent absolute path
        test_path = str(Path.cwd() / "file.txt")

        # Mock the send_fs_write_text_file function
        with patch("chuk_acp_agent.capabilities.filesystem.send_fs_write_text_file") as mock_write:
            mock_write.return_value = None

            await fs.write_text(test_path, "new contents")
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_text_with_permission(self):
        """Test writing text file with permission check."""
        from unittest.mock import patch

        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        fs = FileSystem(transport)

        # Use platform-independent absolute path
        test_path = str(Path.cwd() / "file.txt")

        # Mock the send_fs_write_text_file function
        with patch("chuk_acp_agent.capabilities.filesystem.send_fs_write_text_file") as mock_write:
            mock_write.return_value = None

            await fs.write_text(test_path, "new contents", require_permission=True)
            mock_write.assert_called_once()
