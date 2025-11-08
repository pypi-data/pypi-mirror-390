"""
Tests for base tool classes.

Context: Validates tool infrastructure before building specific tools.
"""

import pytest
from pydantic import BaseModel, Field

from alprina_cli.tools.base import (
    AlprinaToolBase,
    SyncToolBase,
    ToolOk,
    ToolError
)


# Test fixtures
class TestParams(BaseModel):
    """Test parameter model"""
    value: str = Field(description="Test value")
    count: int = Field(default=1, description="Test count")


class TestTool(AlprinaToolBase[TestParams]):
    """Test tool implementation"""
    name: str = "TestTool"
    description: str = "A tool for testing"
    params: type[TestParams] = TestParams

    async def execute(self, params: TestParams):
        return ToolOk(content=f"Executed with {params.value} x {params.count}")


class FailingTool(AlprinaToolBase[TestParams]):
    """Tool that fails for testing error handling"""
    name: str = "FailingTool"
    description: str = "A tool that fails"
    params: type[TestParams] = TestParams

    async def execute(self, params: TestParams):
        return ToolError(
            message=f"Failed to process {params.value}",
            brief="Processing failed"
        )


# Tests
@pytest.mark.asyncio
async def test_tool_creation():
    """Test creating a basic tool"""
    tool = TestTool()

    assert tool.name == "TestTool"
    assert tool.description == "A tool for testing"
    assert tool.params == TestParams


@pytest.mark.asyncio
async def test_tool_execution_success():
    """Test successful tool execution"""
    tool = TestTool()
    params = TestParams(value="test", count=3)

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert "test" in str(result.content)
    assert "3" in str(result.content)


@pytest.mark.asyncio
async def test_tool_execution_failure():
    """Test failed tool execution"""
    tool = FailingTool()
    params = TestParams(value="error_case")

    result = await tool.execute(params)

    assert isinstance(result, ToolError)
    assert result.message == "Failed to process error_case"
    assert result.brief == "Processing failed"


@pytest.mark.asyncio
async def test_tool_call_interface():
    """Test calling tool via __call__ interface"""
    tool = TestTool()
    params = TestParams(value="callable", count=5)

    result = await tool(params)

    assert isinstance(result, ToolOk)
    assert "callable" in str(result.content)


def test_tool_to_dict():
    """Test tool serialization to dict"""
    tool = TestTool()
    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "TestTool"
    assert tool_dict["description"] == "A tool for testing"
    assert "parameters" in tool_dict
    assert "properties" in tool_dict["parameters"]


def test_tool_to_mcp_schema():
    """Test tool conversion to MCP schema"""
    tool = TestTool()
    mcp_schema = tool.to_mcp_schema()

    assert mcp_schema["name"] == "TestTool"
    assert mcp_schema["description"] == "A tool for testing"
    assert "inputSchema" in mcp_schema
    assert "properties" in mcp_schema["inputSchema"]


def test_tool_repr():
    """Test tool string representation"""
    tool = TestTool()
    repr_str = repr(tool)

    assert "TestTool" in repr_str
    assert "name='TestTool'" in repr_str


# Sync tool tests
class SyncTestTool(SyncToolBase[TestParams]):
    """Synchronous test tool"""
    name: str = "SyncTestTool"
    description: str = "Sync test tool"
    params: type[TestParams] = TestParams

    def execute(self, params: TestParams):
        return ToolOk(content=f"Sync: {params.value}")


def test_sync_tool_execution():
    """Test synchronous tool execution"""
    tool = SyncTestTool()
    params = TestParams(value="sync_test")

    result = tool.execute(params)

    assert isinstance(result, ToolOk)
    assert "sync_test" in str(result.content)


def test_sync_tool_call():
    """Test synchronous tool via __call__"""
    tool = SyncTestTool()
    params = TestParams(value="sync_call")

    result = tool(params)

    assert isinstance(result, ToolOk)
    assert "sync_call" in str(result.content)


# Parameter validation tests
@pytest.mark.asyncio
async def test_parameter_validation():
    """Test Pydantic parameter validation"""
    tool = TestTool()

    # Valid parameters
    valid_params = TestParams(value="valid", count=10)
    result = await tool.execute(valid_params)
    assert isinstance(result, ToolOk)

    # Test that invalid parameters raise Pydantic error
    with pytest.raises(Exception):  # Pydantic ValidationError
        TestParams(value="test", count="not_a_number")  # type: ignore


# Registry tests (will be used when we have multiple tools)
def test_tool_initialization_with_kwargs():
    """Test tool initialization with keyword arguments"""
    tool = TestTool(custom_attr="custom_value")

    assert hasattr(tool, "custom_attr")
    assert tool.custom_attr == "custom_value"
