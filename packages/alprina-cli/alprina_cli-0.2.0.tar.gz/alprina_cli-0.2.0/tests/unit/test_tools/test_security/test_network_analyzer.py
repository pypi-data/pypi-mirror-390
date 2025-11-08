"""
Tests for NetworkAnalyzerTool

Context: Validates tool conversion from agent pattern to tool pattern.
"""

import pytest
from alprina_cli.tools.security.network_analyzer import (
    NetworkAnalyzerTool,
    NetworkAnalyzerParams
)
from alprina_cli.tools.base import ToolOk, ToolError


@pytest.mark.asyncio
async def test_network_analyzer_creation():
    """Test creating network analyzer tool"""
    tool = NetworkAnalyzerTool()

    assert tool.name == "NetworkAnalyzer"
    assert tool.params == NetworkAnalyzerParams
    assert "network traffic" in tool.description.lower()


@pytest.mark.asyncio
async def test_network_analyzer_ip_target():
    """Test analyzing IP address target"""
    tool = NetworkAnalyzerTool()
    params = NetworkAnalyzerParams(target="192.168.1.1", safe_only=True)

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert "target" in result.content
    assert result.content["target"] == "192.168.1.1"
    assert "findings" in result.content
    assert "summary" in result.content


@pytest.mark.asyncio
async def test_network_analyzer_domain_target():
    """Test analyzing domain name target"""
    tool = NetworkAnalyzerTool()
    params = NetworkAnalyzerParams(target="example.com", safe_only=True)

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert result.content["target"] == "example.com"
    assert len(result.content["findings"]) >= 0


@pytest.mark.asyncio
async def test_network_analyzer_port_detection():
    """Test detection of sensitive ports"""
    tool = NetworkAnalyzerTool()
    params = NetworkAnalyzerParams(target="192.168.1.1:22", safe_only=True)

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    findings = result.content["findings"]

    # Should detect port 22 (SSH) as sensitive
    port_findings = [f for f in findings if "port" in f.get("title", "").lower()]
    assert len(port_findings) > 0


@pytest.mark.asyncio
async def test_network_analyzer_max_findings():
    """Test max_findings parameter limits results"""
    tool = NetworkAnalyzerTool()
    params = NetworkAnalyzerParams(
        target="192.168.1.1",
        safe_only=True,
        max_findings=2
    )

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    # Should limit findings even if more were found
    assert len(result.content["findings"]) <= 2


@pytest.mark.asyncio
async def test_network_analyzer_safe_mode():
    """Test safe_only parameter"""
    tool = NetworkAnalyzerTool()

    # Safe mode
    params_safe = NetworkAnalyzerParams(target="example.com", safe_only=True)
    result_safe = await tool.execute(params_safe)
    assert result_safe.content["summary"]["safe_mode"] is True

    # Non-safe mode
    params_unsafe = NetworkAnalyzerParams(target="example.com", safe_only=False)
    result_unsafe = await tool.execute(params_unsafe)
    assert result_unsafe.content["summary"]["safe_mode"] is False


@pytest.mark.asyncio
async def test_network_analyzer_ip_validation():
    """Test IP address validation helper"""
    tool = NetworkAnalyzerTool()

    # Valid IPs
    assert tool._is_ip_address("192.168.1.1") is True
    assert tool._is_ip_address("10.0.0.1") is True
    assert tool._is_ip_address("255.255.255.255") is True

    # Invalid IPs
    assert tool._is_ip_address("256.1.1.1") is False
    assert tool._is_ip_address("example.com") is False
    assert tool._is_ip_address("192.168.1") is False


@pytest.mark.asyncio
async def test_network_analyzer_builtin_analysis():
    """Test built-in analysis (when CAI unavailable)"""
    tool = NetworkAnalyzerTool()
    params = NetworkAnalyzerParams(target="10.0.0.1", safe_only=True)

    result = await tool._analyze_builtin(params)

    assert "target" in result
    assert "findings" in result
    assert "summary" in result
    assert result["summary"]["powered_by"] == "built-in"


@pytest.mark.asyncio
async def test_network_analyzer_parse_cai_response():
    """Test parsing CAI response into findings"""
    tool = NetworkAnalyzerTool()

    # Mock CAI response
    response = """
CRITICAL: SQL Injection vulnerability detected in login form

HIGH: Insecure password storage using MD5

MEDIUM: Missing security headers
"""

    findings = tool._parse_cai_response(response, "example.com")

    assert len(findings) >= 2  # Should find critical and high severity items
    severities = [f["severity"] for f in findings]
    assert "CRITICAL" in severities
    assert "HIGH" in severities


@pytest.mark.asyncio
async def test_network_analyzer_call_interface():
    """Test calling tool via __call__ interface"""
    tool = NetworkAnalyzerTool()
    params = NetworkAnalyzerParams(target="192.168.1.100")

    result = await tool(params)

    assert isinstance(result, (ToolOk, ToolError))
    if isinstance(result, ToolOk):
        assert "findings" in result.content


def test_network_analyzer_to_dict():
    """Test tool serialization"""
    tool = NetworkAnalyzerTool()
    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "NetworkAnalyzer"
    assert "description" in tool_dict
    assert "parameters" in tool_dict


def test_network_analyzer_to_mcp_schema():
    """Test MCP schema generation"""
    tool = NetworkAnalyzerTool()
    mcp_schema = tool.to_mcp_schema()

    assert mcp_schema["name"] == "NetworkAnalyzer"
    assert "inputSchema" in mcp_schema
    assert "properties" in mcp_schema["inputSchema"]
    assert "target" in mcp_schema["inputSchema"]["properties"]


# Parameter validation tests
def test_network_analyzer_params_validation():
    """Test parameter validation"""
    # Valid params
    params = NetworkAnalyzerParams(target="192.168.1.1")
    assert params.target == "192.168.1.1"
    assert params.safe_only is True  # Default
    assert params.max_findings == 10  # Default

    # Custom params
    params2 = NetworkAnalyzerParams(
        target="example.com",
        safe_only=False,
        max_findings=5
    )
    assert params2.safe_only is False
    assert params2.max_findings == 5
