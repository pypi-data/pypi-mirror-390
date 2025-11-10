"""
Tool metadata models for clean tool discovery.
"""

from typing import Any

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Information about a tool parameter."""

    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (e.g., 'string', 'number')")
    description: str | None = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Any | None = Field(None, description="Default value if not provided")


class Tool(BaseModel):
    """
    Tool metadata for discovery and introspection.

    Provides clean access to tool information without needing to know
    the underlying registry format.
    """

    name: str = Field(..., description="Tool name (without namespace)")
    description: str | None = Field(None, description="Tool description")
    parameters: list[ToolParameter] | None = Field(None, description="Tool parameters")

    def __str__(self) -> str:
        """String representation."""
        desc = f" - {self.description}" if self.description else ""
        return f"{self.name}{desc}"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Tool(name={self.name!r}, description={self.description!r})"

    @property
    def parameter_names(self) -> list[str]:
        """Get list of parameter names."""
        if not self.parameters:
            return []
        return [p.name for p in self.parameters]

    @property
    def required_parameters(self) -> list[str]:
        """Get list of required parameter names."""
        if not self.parameters:
            return []
        return [p.name for p in self.parameters if p.required]

    def get_parameter(self, name: str) -> ToolParameter | None:
        """
        Get parameter by name.

        Args:
            name: Parameter name

        Returns:
            ToolParameter or None if not found
        """
        if not self.parameters:
            return None
        return next((p for p in self.parameters if p.name == name), None)
