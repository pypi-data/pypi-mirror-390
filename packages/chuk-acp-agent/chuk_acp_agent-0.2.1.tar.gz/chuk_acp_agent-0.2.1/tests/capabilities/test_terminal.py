"""Tests for terminal capability."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from chuk_acp_agent.capabilities.terminal import CommandResult, Terminal


class TestCommandResult:
    """Test CommandResult dataclass."""

    def test_creation(self):
        """Test CommandResult creation."""
        result = CommandResult(exit_code=0, stdout="output", stderr="")
        assert result.exit_code == 0
        assert result.stdout == "output"
        assert result.stderr == ""


class TestTerminal:
    """Test Terminal capability."""

    def test_initialization(self):
        """Test terminal initialization."""
        transport = Mock()
        terminal = Terminal(transport)
        assert terminal._transport == transport

    @pytest.mark.asyncio
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_create")
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_wait_for_exit")
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_release")
    async def test_run(self, mock_release, mock_wait, mock_create):
        """Test running a command."""
        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        terminal = Terminal(transport)

        # Mock responses
        mock_create_result = Mock()
        mock_create_result.id = "term-123"
        mock_create.return_value = mock_create_result

        mock_exit_result = Mock()
        mock_exit_result.exitCode = 0
        mock_wait.return_value = mock_exit_result

        mock_release.return_value = None

        # Run command
        result = await terminal.run("ls", "-la", cwd="/tmp")

        # Verify calls
        mock_create.assert_called_once()
        mock_wait.assert_called_once()
        mock_release.assert_called_once()

        # Verify result
        assert isinstance(result, CommandResult)
        assert result.exit_code == 0

    @pytest.mark.asyncio
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_create")
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_wait_for_exit")
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_release")
    async def test_run_with_error_still_releases(self, mock_release, mock_wait, mock_create):
        """Test that terminal is released even if wait fails."""
        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        terminal = Terminal(transport)

        # Mock responses
        mock_create_result = Mock()
        mock_create_result.id = "term-123"
        mock_create.return_value = mock_create_result

        # Make wait fail
        mock_wait.side_effect = RuntimeError("Wait failed")

        # Run command - should raise but still release
        with pytest.raises(RuntimeError, match="Wait failed"):
            await terminal.run("ls")

        # Verify release was still called
        mock_release.assert_called_once()

    @pytest.mark.asyncio
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_create")
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_wait_for_exit")
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_release")
    async def test_run_streaming(self, mock_release, mock_wait, mock_create):
        """Test streaming command execution."""
        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        terminal = Terminal(transport)

        # Mock responses
        mock_create_result = Mock()
        mock_create_result.id = "term-456"
        mock_create.return_value = mock_create_result

        mock_exit_result = Mock()
        mock_exit_result.exitCode = 0
        mock_wait.return_value = mock_exit_result

        # Collect streamed output
        outputs = []
        async for output in terminal.run_streaming("echo", "hello"):
            outputs.append(output)

        # Verify output
        assert len(outputs) > 0
        assert "exited with code 0" in outputs[0]

        # Verify cleanup
        mock_release.assert_called_once()

    @pytest.mark.asyncio
    @patch("chuk_acp_agent.capabilities.terminal.send_terminal_kill")
    async def test_kill(self, mock_kill):
        """Test killing a terminal."""
        transport = Mock()
        mock_read_stream = Mock()
        mock_write_stream = Mock()
        transport.get_streams = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        terminal = Terminal(transport)

        await terminal.kill("term-789")

        mock_kill.assert_called_once()
