"""Tests for ToolResult wrapper."""

from unittest.mock import Mock

from chuk_acp_agent.models.tool_result import ToolResult


class TestToolResult:
    """Test ToolResult functionality."""

    def test_text_from_nested_result(self):
        """Test extracting text when result is nested."""
        # Create mock with proper structure
        inner_result = Mock()
        inner_result.content = [{"type": "text", "text": "Nested"}]

        result = Mock()
        result.result = inner_result
        result.error = None

        tool_result = ToolResult(result)
        assert tool_result.text == "Nested"

    def test_text_from_direct_content(self):
        """Test extracting text from direct content list."""
        # Mock needs to NOT have result attribute but have content
        result = Mock(spec=["content", "error"])
        result.content = [{"type": "text", "text": "Direct"}]
        result.error = None

        tool_result = ToolResult(result)
        assert tool_result.text == "Direct"

    def test_text_fallback_to_str(self):
        """Test fallback to string representation."""

        # Create a simple object that has no result or content attributes
        class SimpleResult:
            pass

        result = SimpleResult()

        tool_result = ToolResult(result)
        # Should fallback to str representation which includes the class name
        assert "SimpleResult" in tool_result.text

    def test_text_with_non_dict_content(self):
        """Test handling non-dict content items."""
        inner_result = Mock()
        inner_result.content = ["simple string"]

        result = Mock()
        result.result = inner_result
        result.error = None

        tool_result = ToolResult(result)
        assert tool_result.text == "simple string"

    def test_is_error_true_from_error_attr(self):
        """Test is_error when error attribute present."""
        result = Mock()
        result.error = "Something failed"

        tool_result = ToolResult(result)
        assert tool_result.is_error is True

    def test_is_error_false_when_no_error(self):
        """Test is_error when no error."""
        result = Mock()
        result.error = None

        tool_result = ToolResult(result)
        assert tool_result.is_error is False

    def test_is_error_from_nested_is_error(self):
        """Test is_error from inner result.isError."""

        # Create objects with actual attributes, not Mocks
        class InnerResult:
            def __init__(self):
                self.isError = True

        class OuterResult:
            def __init__(self):
                self.error = None
                self.result = InnerResult()

        result = OuterResult()

        tool_result = ToolResult(result)
        assert tool_result.is_error is True

    def test_metadata_with_meta(self):
        """Test metadata extraction from meta attribute."""
        result = Mock()
        result.meta = {"duration": 0.5, "source": "test"}
        # Mock doesn't have timing attributes
        result.start_time = Mock()
        result.start_time.__bool__ = Mock(return_value=False)  # Make it falsy
        delattr(result, "end_time")
        delattr(result, "duration")

        tool_result = ToolResult(result)
        meta = tool_result.metadata
        assert meta["duration"] == 0.5
        assert meta["source"] == "test"

    def test_metadata_with_timing_attrs(self):
        """Test metadata includes timing attributes."""
        result = Mock()
        result.meta = None
        result.start_time = 100
        result.end_time = 150
        result.duration = 50

        tool_result = ToolResult(result)
        meta = tool_result.metadata
        assert meta["start_time"] == 100
        assert meta["end_time"] == 150
        assert meta["duration"] == 50

    def test_metadata_empty_when_none(self):
        """Test metadata returns empty dict when not present."""
        result = Mock(spec=[])

        tool_result = ToolResult(result)
        assert tool_result.metadata == {}

    def test_raw_result_accessible(self):
        """Test that raw result is accessible."""
        result = Mock()

        tool_result = ToolResult(result)
        assert tool_result.raw == result

    def test_json_serialization(self):
        """Test JSON serialization."""
        inner_result = Mock()
        inner_result.content = [{"type": "text", "text": "Test"}]

        result = Mock()
        result.result = inner_result
        result.error = None
        result.meta = None  # Set to None to avoid Mock.keys() issue

        tool_result = ToolResult(result)
        json_data = tool_result.json()

        assert "text" in json_data
        assert "is_error" in json_data
        assert "error" in json_data
        assert "metadata" in json_data
        assert json_data["text"] == "Test"
        assert json_data["is_error"] is False

    def test_str_representation(self):
        """Test string representation returns text."""
        inner_result = Mock()
        inner_result.content = [{"type": "text", "text": "Test"}]

        result = Mock()
        result.result = inner_result

        tool_result = ToolResult(result)
        assert str(tool_result) == "Test"

    def test_repr_normal(self):
        """Test repr for normal result."""
        inner_result = Mock()
        inner_result.content = [{"type": "text", "text": "Test"}]

        result = Mock()
        result.result = inner_result
        result.error = None

        tool_result = ToolResult(result)
        repr_str = repr(tool_result)
        assert "ToolResult" in repr_str
        assert "Test" in repr_str

    def test_repr_error(self):
        """Test repr for error result."""
        result = Mock()
        result.error = "Failed"

        tool_result = ToolResult(result)
        repr_str = repr(tool_result)
        assert "ToolResult" in repr_str
        assert "error" in repr_str

    def test_error_property(self):
        """Test error property."""
        result = Mock()
        result.error = "Something failed"

        tool_result = ToolResult(result)
        assert tool_result.error == "Something failed"

    def test_error_property_none(self):
        """Test error property when no error."""
        result = Mock(spec=[])

        tool_result = ToolResult(result)
        assert tool_result.error is None

    def test_text_with_string_content(self):
        """Test handling string content."""
        inner_result = Mock()
        inner_result.content = "plain string"

        result = Mock()
        result.result = inner_result

        tool_result = ToolResult(result)
        assert tool_result.text == "plain string"

    def test_text_with_empty_content_list(self):
        """Test handling empty content list."""
        inner_result = Mock()
        inner_result.content = []

        result = Mock()
        result.result = inner_result

        tool_result = ToolResult(result)
        # Should fallback to str representation
        assert "Mock" in tool_result.text or tool_result.text == ""
