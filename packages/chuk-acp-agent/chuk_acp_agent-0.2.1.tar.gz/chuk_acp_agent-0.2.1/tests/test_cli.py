"""Tests for CLI module."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from chuk_acp_agent import cli


class TestCLI:
    """Test CLI functionality."""

    def test_print_version(self, capsys):
        """Test print_version outputs version."""
        cli.print_version()
        captured = capsys.readouterr()
        assert "chuk-acp-agent" in captured.out
        # Should have some version number
        assert len(captured.out.strip()) > len("chuk-acp-agent")

    def test_main_no_args(self, capsys):
        """Test main with no arguments."""
        with patch.object(sys, "argv", ["chuk-acp-agent"]):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_main_version_command(self, capsys):
        """Test main with version command."""
        with patch.object(sys, "argv", ["chuk-acp-agent", "version"]):
            cli.main()

        captured = capsys.readouterr()
        assert "chuk-acp-agent" in captured.out

    def test_main_help_command(self, capsys):
        """Test main with help command."""
        with patch.object(sys, "argv", ["chuk-acp-agent", "help"]):
            cli.main()

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_client_command_no_config(self, capsys):
        """Test client command without MCP config file."""
        mock_agent = MagicMock()

        with patch.object(sys, "argv", ["chuk-acp-agent", "client"]):
            with patch(
                "chuk_acp_agent.agent.interactive.InteractiveAgent", return_value=mock_agent
            ):
                cli.main()

        # Should create agent and run without config
        mock_agent.run.assert_called_once()

    def test_client_command_with_config(self, capsys):
        """Test client command with MCP config file."""
        # Create temp config file
        config_data = {
            "mcpServers": {
                "echo": {"command": "uvx", "args": ["chuk-mcp-echo", "stdio"], "env": {}}
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            mock_agent = MagicMock()

            with patch.object(
                sys, "argv", ["chuk-acp-agent", "client", "--mcp-config-file", temp_path]
            ):
                with patch(
                    "chuk_acp_agent.agent.interactive.InteractiveAgent", return_value=mock_agent
                ):
                    cli.main()

            # Should load config and run
            mock_agent.load_mcp_config.assert_called_once()
            mock_agent.run.assert_called_once()

            captured = capsys.readouterr()
            assert "Loaded MCP config from:" in captured.out
        finally:
            Path(temp_path).unlink()

    def test_client_command_config_not_found(self, capsys):
        """Test client command with non-existent config file."""
        with patch.object(
            sys,
            "argv",
            ["chuk-acp-agent", "client", "--mcp-config-file", "/nonexistent/config.json"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error: MCP config file not found" in captured.err

    def test_client_command_invalid_config(self, capsys):
        """Test client command with invalid JSON config."""
        # Create temp file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            with patch.object(
                sys, "argv", ["chuk-acp-agent", "client", "--mcp-config-file", temp_path]
            ):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()
                assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Error loading MCP config:" in captured.err
        finally:
            Path(temp_path).unlink()

    def test_run_client_keyboard_interrupt(self, capsys):
        """Test run_client handles keyboard interrupt gracefully."""
        mock_agent = MagicMock()
        mock_agent.run.side_effect = KeyboardInterrupt()

        with patch.object(sys, "argv", ["chuk-acp-agent", "client"]):
            with patch(
                "chuk_acp_agent.agent.interactive.InteractiveAgent", return_value=mock_agent
            ):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()
                assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "Shutting down..." in captured.out
