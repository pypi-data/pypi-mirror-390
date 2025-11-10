"""
Custom exceptions for better error messages.
"""


class ToolError(Exception):
    """Base exception for tool-related errors."""

    pass


class ToolNotFoundError(ToolError):
    """Raised when a tool is not found."""

    def __init__(
        self,
        tool_name: str,
        suggestions: list[str] | None = None,
        available_tools: list[str] | None = None,
    ):
        """
        Initialize error.

        Args:
            tool_name: Name of tool that wasn't found
            suggestions: List of suggested tool names
            available_tools: List of all available tool names
        """
        self.tool_name = tool_name
        self.suggestions = suggestions or []
        self.available_tools = available_tools or []

        # Build helpful error message
        message = f"Tool '{tool_name}' not found."

        if self.suggestions:
            message += "\n\nDid you mean one of these?"
            for suggestion in self.suggestions[:3]:  # Show top 3
                message += f"\n  - {suggestion}"

        if self.available_tools:
            message += f"\n\nAvailable tools ({len(self.available_tools)}):"
            # Show first 10 tools
            for tool in self.available_tools[:10]:
                message += f"\n  - {tool}"
            if len(self.available_tools) > 10:
                message += f"\n  ... and {len(self.available_tools) - 10} more"

        message += "\n\nUse ctx.tools.list() to see all available tools."

        super().__init__(message)


class ToolParameterError(ToolError):
    """Raised when tool parameters are invalid."""

    def __init__(
        self,
        tool_name: str,
        parameter: str,
        issue: str,
        expected: str | None = None,
    ):
        """
        Initialize error.

        Args:
            tool_name: Name of the tool
            parameter: Parameter name with issue
            issue: Description of the issue
            expected: Expected format/type
        """
        self.tool_name = tool_name
        self.parameter = parameter
        self.issue = issue
        self.expected = expected

        message = f"Invalid parameter '{parameter}' for tool '{tool_name}': {issue}"
        if expected:
            message += f"\nExpected: {expected}"

        super().__init__(message)


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""

    def __init__(self, tool_name: str, error_message: str):
        """
        Initialize error.

        Args:
            tool_name: Name of the tool
            error_message: Error message from tool execution
        """
        self.tool_name = tool_name
        self.error_message = error_message

        message = f"Tool '{tool_name}' execution failed: {error_message}"
        super().__init__(message)
