"""Tests for Tool and ToolParameter models."""

import pytest

from chuk_acp_agent.models.tool import Tool, ToolParameter


class TestToolParameter:
    """Test ToolParameter model."""

    def test_creation_minimal(self):
        """Test creating parameter with minimal fields."""
        param = ToolParameter(name="count", type="integer")
        assert param.name == "count"
        assert param.type == "integer"
        assert param.description is None
        assert param.required is False

    def test_creation_full(self):
        """Test creating parameter with all fields."""
        param = ToolParameter(
            name="query", type="string", description="Search query", required=True
        )
        assert param.name == "query"
        assert param.type == "string"
        assert param.description == "Search query"
        assert param.required is True

    def test_default_required_is_false(self):
        """Test that required defaults to False."""
        param = ToolParameter(name="opt", type="string")
        assert param.required is False

    def test_pydantic_validation(self):
        """Test Pydantic validation."""
        # Missing required field should raise
        with pytest.raises(Exception):  # Pydantic ValidationError
            ToolParameter(name="test")  # Missing type

    def test_model_dump(self):
        """Test converting to dict."""
        param = ToolParameter(
            name="limit", type="integer", description="Max results", required=True
        )
        data = param.model_dump()
        assert data["name"] == "limit"
        assert data["type"] == "integer"
        assert data["description"] == "Max results"
        assert data["required"] is True


class TestTool:
    """Test Tool model."""

    def test_creation_minimal(self):
        """Test creating tool with minimal fields."""
        tool = Tool(name="echo_text")
        assert tool.name == "echo_text"
        assert tool.description is None
        assert tool.parameters is None

    def test_creation_with_description(self):
        """Test creating tool with description."""
        tool = Tool(name="search", description="Search for items")
        assert tool.name == "search"
        assert tool.description == "Search for items"

    def test_creation_with_parameters(self):
        """Test creating tool with parameters."""
        params = [
            ToolParameter(name="query", type="string", required=True),
            ToolParameter(name="limit", type="integer", required=False),
        ]
        tool = Tool(name="search", description="Search tool", parameters=params)
        assert tool.name == "search"
        assert len(tool.parameters) == 2
        assert tool.parameters[0].name == "query"
        assert tool.parameters[1].name == "limit"

    def test_parameters_none_by_default(self):
        """Test that parameters defaults to None."""
        tool = Tool(name="test")
        assert tool.parameters is None

    def test_pydantic_validation(self):
        """Test Pydantic validation."""
        # Missing required field
        with pytest.raises(Exception):  # Pydantic ValidationError
            Tool()  # Missing name

    def test_model_dump(self):
        """Test converting to dict."""
        tool = Tool(name="echo", description="Echo text")
        data = tool.model_dump()
        assert data["name"] == "echo"
        assert data["description"] == "Echo text"
        assert data["parameters"] is None

    def test_model_dump_with_parameters(self):
        """Test converting to dict with parameters."""
        params = [ToolParameter(name="msg", type="string")]
        tool = Tool(name="echo", parameters=params)
        data = tool.model_dump()
        assert "parameters" in data
        assert len(data["parameters"]) == 1
        assert data["parameters"][0]["name"] == "msg"

    def test_sorting_by_name(self):
        """Test tools can be sorted by name."""
        tools = [Tool(name="zebra"), Tool(name="alpha"), Tool(name="beta")]
        sorted_tools = sorted(tools, key=lambda t: t.name)
        assert sorted_tools[0].name == "alpha"
        assert sorted_tools[1].name == "beta"
        assert sorted_tools[2].name == "zebra"

    def test_equality(self):
        """Test tool equality."""
        tool1 = Tool(name="test", description="A test")
        tool2 = Tool(name="test", description="A test")
        # Pydantic models should be equal if fields match
        assert tool1.name == tool2.name
        assert tool1.description == tool2.description

    def test_str_with_description(self):
        """Test string representation with description."""
        tool = Tool(name="echo", description="Echo text")
        assert str(tool) == "echo - Echo text"

    def test_str_without_description(self):
        """Test string representation without description."""
        tool = Tool(name="echo")
        assert str(tool) == "echo"

    def test_repr(self):
        """Test detailed representation."""
        tool = Tool(name="echo", description="Echo text")
        repr_str = repr(tool)
        assert "Tool(name='echo'" in repr_str
        assert "description='Echo text'" in repr_str

    def test_parameter_names_with_parameters(self):
        """Test parameter_names property."""
        params = [
            ToolParameter(name="message", type="string"),
            ToolParameter(name="count", type="integer"),
        ]
        tool = Tool(name="echo", parameters=params)
        assert tool.parameter_names == ["message", "count"]

    def test_parameter_names_without_parameters(self):
        """Test parameter_names when no parameters."""
        tool = Tool(name="echo")
        assert tool.parameter_names == []

    def test_required_parameters(self):
        """Test required_parameters property."""
        params = [
            ToolParameter(name="message", type="string", required=True),
            ToolParameter(name="count", type="integer", required=False),
            ToolParameter(name="format", type="string", required=True),
        ]
        tool = Tool(name="echo", parameters=params)
        assert tool.required_parameters == ["message", "format"]

    def test_required_parameters_none(self):
        """Test required_parameters when no required params."""
        params = [
            ToolParameter(name="message", type="string", required=False),
            ToolParameter(name="count", type="integer", required=False),
        ]
        tool = Tool(name="echo", parameters=params)
        assert tool.required_parameters == []

    def test_required_parameters_no_params(self):
        """Test required_parameters when no parameters."""
        tool = Tool(name="echo")
        assert tool.required_parameters == []

    def test_get_parameter_found(self):
        """Test get_parameter when parameter exists."""
        params = [
            ToolParameter(name="message", type="string"),
            ToolParameter(name="count", type="integer"),
        ]
        tool = Tool(name="echo", parameters=params)
        param = tool.get_parameter("count")
        assert param is not None
        assert param.name == "count"
        assert param.type == "integer"

    def test_get_parameter_not_found(self):
        """Test get_parameter when parameter doesn't exist."""
        params = [ToolParameter(name="message", type="string")]
        tool = Tool(name="echo", parameters=params)
        param = tool.get_parameter("nonexistent")
        assert param is None

    def test_get_parameter_no_params(self):
        """Test get_parameter when tool has no parameters."""
        tool = Tool(name="echo")
        param = tool.get_parameter("anything")
        assert param is None

    def test_tool_parameter_with_default(self):
        """Test ToolParameter with default value."""
        param = ToolParameter(name="count", type="integer", default=5)
        assert param.default == 5
