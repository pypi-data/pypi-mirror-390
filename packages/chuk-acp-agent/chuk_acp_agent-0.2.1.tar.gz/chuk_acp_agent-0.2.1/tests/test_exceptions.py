"""Tests for custom exceptions."""

import pytest

from chuk_acp_agent.exceptions import (
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolParameterError,
)


class TestToolError:
    """Test base ToolError exception."""

    def test_creation(self):
        """Test basic creation."""
        error = ToolError("Test error")
        assert str(error) == "Test error"

    def test_inheritance(self):
        """Test inherits from Exception."""
        error = ToolError("Test")
        assert isinstance(error, Exception)


class TestToolNotFoundError:
    """Test ToolNotFoundError with suggestions."""

    def test_creation_without_suggestions(self):
        """Test error without suggestions."""
        error = ToolNotFoundError("missing_tool", [], [])
        assert "missing_tool" in str(error)
        assert "not found" in str(error)

    def test_creation_with_suggestions(self):
        """Test error with fuzzy match suggestions."""
        error = ToolNotFoundError(
            "ech",
            suggestions=["echo_text", "echo_upper"],
            available_tools=["echo_text", "echo_upper", "other_tool"],
        )
        error_str = str(error)
        assert "ech" in error_str
        assert "not found" in error_str
        assert "Did you mean" in error_str
        assert "echo_text" in error_str
        assert "echo_upper" in error_str

    def test_creation_with_available_tools_only(self):
        """Test error showing available tools when no suggestions."""
        error = ToolNotFoundError("xyz", suggestions=[], available_tools=["tool1", "tool2"])
        error_str = str(error)
        assert "Available tools (2):" in error_str
        assert "tool1" in error_str
        assert "tool2" in error_str

    def test_inherits_from_tool_error(self):
        """Test inheritance."""
        error = ToolNotFoundError("test", [], [])
        assert isinstance(error, ToolError)

    def test_suggestions_limit(self):
        """Test that suggestions are limited."""
        error = ToolNotFoundError(
            "test", suggestions=["s1", "s2", "s3", "s4", "s5", "s6"], available_tools=[]
        )
        error_str = str(error)
        # Should only show first few suggestions
        assert "s1" in error_str


class TestToolExecutionError:
    """Test ToolExecutionError."""

    def test_creation_with_message(self):
        """Test creation with error message."""
        error = ToolExecutionError("my_tool", "Something went wrong")
        error_str = str(error)
        assert "my_tool" in error_str
        assert "Something went wrong" in error_str

    def test_creation_with_dict_error(self):
        """Test creation with error dict."""
        error_dict = {"code": 500, "message": "Internal error"}
        error = ToolExecutionError("my_tool", error_dict)
        error_str = str(error)
        assert "my_tool" in error_str
        assert "500" in error_str or "Internal error" in error_str

    def test_inherits_from_tool_error(self):
        """Test inheritance."""
        error = ToolExecutionError("test", "error")
        assert isinstance(error, ToolError)


class TestToolParameterError:
    """Test ToolParameterError."""

    def test_creation(self):
        """Test basic creation."""
        error = ToolParameterError(
            tool_name="echo_text", parameter="count", issue="must be positive"
        )
        assert "echo_text" in str(error)
        assert "count" in str(error)
        assert "must be positive" in str(error)

    def test_creation_with_expected(self):
        """Test creation with expected format."""
        error = ToolParameterError(
            tool_name="search", parameter="limit", issue="invalid type", expected="integer"
        )
        assert "search" in str(error)
        assert "limit" in str(error)
        assert "invalid type" in str(error)
        assert "integer" in str(error)

    def test_inherits_from_tool_error(self):
        """Test inheritance."""
        error = ToolParameterError("test_tool", "param", "test issue")
        assert isinstance(error, ToolError)

    def test_can_be_raised_and_caught(self):
        """Test exception can be raised and caught."""
        with pytest.raises(ToolParameterError) as exc_info:
            raise ToolParameterError("my_tool", "my_param", "test param error")

        assert "my_tool" in str(exc_info.value)
        assert "my_param" in str(exc_info.value)
        assert "test param error" in str(exc_info.value)
