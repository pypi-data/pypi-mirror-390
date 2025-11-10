"""
Tool result wrapper for clean, ergonomic access to MCP tool results.
"""

from typing import Any


class ToolResult:
    """
    Wrapper for MCP tool results with convenient accessors.

    Provides clean access to tool result data without needing to know
    the underlying MCP content format.
    """

    def __init__(self, raw_result: Any):
        """
        Initialize tool result wrapper.

        Args:
            raw_result: Raw result from tool processor
        """
        self._raw = raw_result

    @property
    def text(self) -> str:
        """
        Extract text content from result.

        Returns:
            Text content as string
        """
        # Get the result object
        result_obj = self._raw
        if hasattr(self._raw, "result") and self._raw.result:
            result_obj = self._raw.result

        # Handle MCP content format: content=[{'type': 'text', 'text': '...'}]
        if hasattr(result_obj, "content") and result_obj.content:
            if isinstance(result_obj.content, list) and len(result_obj.content) > 0:
                first_item = result_obj.content[0]
                if isinstance(first_item, dict):
                    return str(first_item.get("text", str(self._raw)))
                return str(first_item)
            return str(result_obj.content)

        # Fallback to string representation
        return str(self._raw)

    @property
    def is_error(self) -> bool:
        """
        Check if result represents an error.

        Returns:
            True if error, False otherwise
        """
        # Check the tool processor result first
        if hasattr(self._raw, "error") and self._raw.error:
            return True
        if hasattr(self._raw, "is_success"):
            return not bool(self._raw.is_success)

        # Check the inner result object
        if hasattr(self._raw, "result") and self._raw.result:
            result_obj = self._raw.result
            if hasattr(result_obj, "isError"):
                return bool(result_obj.isError)
            if hasattr(result_obj, "is_error"):
                return bool(result_obj.is_error)

        return False

    @property
    def error(self) -> str | None:
        """
        Get error message if result is an error.

        Returns:
            Error message or None
        """
        if hasattr(self._raw, "error"):
            error_value = self._raw.error
            return str(error_value) if error_value is not None else None
        return None

    @property
    def metadata(self) -> dict[str, Any]:
        """
        Get result metadata (timing, etc.).

        Returns:
            Metadata dictionary
        """
        meta = {}

        if hasattr(self._raw, "meta") and self._raw.meta:
            meta.update(self._raw.meta)

        if hasattr(self._raw, "start_time"):
            meta["start_time"] = self._raw.start_time
        if hasattr(self._raw, "end_time"):
            meta["end_time"] = self._raw.end_time
        if hasattr(self._raw, "duration"):
            meta["duration"] = self._raw.duration

        return meta

    @property
    def raw(self) -> Any:
        """
        Get raw underlying result object.

        Returns:
            Raw result from tool processor
        """
        return self._raw

    def json(self) -> dict[str, Any]:
        """
        Convert result to JSON-serializable dict.

        Returns:
            Dictionary representation
        """
        return {
            "text": self.text,
            "is_error": self.is_error,
            "error": self.error,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """String representation returns text content."""
        return self.text

    def __repr__(self) -> str:
        """Detailed representation."""
        if self.is_error:
            return f"ToolResult(error={self.error!r})"
        return f"ToolResult(text={self.text!r})"
