"""
Integration tests for all security tools

Context: Verify all tools are properly registered and functional.
"""

import pytest
from alprina_cli.tools import ALL_TOOLS, get_tool_by_name


def test_all_tools_registered():
    """Test that all expected tools are registered"""
    expected_tools = [
        "NetworkAnalyzer",
        "Scan",
        "Recon",
        "VulnScan",
        "Exploit",
        "RedTeam",
        "BlueTeam",
        "DFIR",
        "AndroidSAST",
        "Glob",
        "Grep",
        "ReadFile"
    ]

    registered_names = [tool.name for tool in ALL_TOOLS]

    for expected in expected_tools:
        assert expected in registered_names, f"Tool {expected} not registered"


def test_get_tool_by_name():
    """Test tool lookup by name"""
    # Test core security tools
    assert get_tool_by_name("NetworkAnalyzer").name == "NetworkAnalyzer"
    assert get_tool_by_name("Scan").name == "Scan"
    assert get_tool_by_name("Recon").name == "Recon"
    assert get_tool_by_name("VulnScan").name == "VulnScan"
    assert get_tool_by_name("Exploit").name == "Exploit"

    # Test specialized tools
    assert get_tool_by_name("RedTeam").name == "RedTeam"
    assert get_tool_by_name("BlueTeam").name == "BlueTeam"
    assert get_tool_by_name("DFIR").name == "DFIR"
    assert get_tool_by_name("AndroidSAST").name == "AndroidSAST"

    # Test file tools
    assert get_tool_by_name("Glob").name == "Glob"
    assert get_tool_by_name("Grep").name == "Grep"
    assert get_tool_by_name("ReadFile").name == "ReadFile"


def test_tool_not_found():
    """Test error handling for non-existent tool"""
    with pytest.raises(ValueError, match="Tool not found"):
        get_tool_by_name("NonExistentTool")


def test_all_tools_have_required_attributes():
    """Test that all tools have required attributes"""
    for tool in ALL_TOOLS:
        assert hasattr(tool, 'name'), f"Tool missing 'name' attribute"
        assert hasattr(tool, 'description'), f"{tool.name} missing 'description'"
        assert hasattr(tool, 'params'), f"{tool.name} missing 'params'"
        assert hasattr(tool, 'execute'), f"{tool.name} missing 'execute' method"


def test_all_tools_have_memory_support():
    """Test that all tools support memory service"""
    for tool in ALL_TOOLS:
        assert hasattr(tool, 'memory_service'), f"{tool.name} missing 'memory_service' attribute"


def test_tool_count():
    """Test expected number of tools"""
    # 5 core + 4 specialized + 3 file = 12 tools
    assert len(ALL_TOOLS) == 12, f"Expected 12 tools, got {len(ALL_TOOLS)}"


def test_tool_categories():
    """Test tools are properly categorized"""
    security_tools = [
        "NetworkAnalyzer", "Scan", "Recon", "VulnScan", "Exploit",
        "RedTeam", "BlueTeam", "DFIR", "AndroidSAST"
    ]
    file_tools = ["Glob", "Grep", "ReadFile"]

    for tool in ALL_TOOLS:
        if tool.name in security_tools:
            # Security tools should be in security module
            assert "security" in tool.__module__
        elif tool.name in file_tools:
            # File tools should be in file module
            assert "file" in tool.__module__
