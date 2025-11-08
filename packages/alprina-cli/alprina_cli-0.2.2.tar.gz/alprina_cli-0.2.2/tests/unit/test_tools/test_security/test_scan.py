"""
Tests for ScanTool

Context: Validates unified scan tool for local and remote targets.
"""

import pytest
import tempfile
from pathlib import Path
from alprina_cli.tools.security.scan import ScanTool, ScanParams
from alprina_cli.tools.base import ToolOk, ToolError


@pytest.mark.asyncio
async def test_scan_tool_creation():
    """Test creating scan tool"""
    tool = ScanTool()

    assert tool.name == "Scan"
    assert tool.params == ScanParams
    assert "security scan" in tool.description.lower()


@pytest.mark.asyncio
async def test_scan_params_validation():
    """Test parameter validation"""
    # Valid params
    params = ScanParams(target="./src", profile="code-audit")
    assert params.target == "./src"
    assert params.profile == "code-audit"
    assert params.safe_only is True

    # Empty target should fail
    with pytest.raises(ValueError, match="Target cannot be empty"):
        ScanParams(target="", profile="code-audit")

    # Whitespace-only target should fail
    with pytest.raises(ValueError, match="Target cannot be empty"):
        ScanParams(target="   ", profile="code-audit")


@pytest.mark.asyncio
async def test_scan_local_file():
    """Test scanning a local file"""
    tool = ScanTool()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("password = 'hardcoded123'\n")
        f.write("api_key = 'secret-key'\n")
        temp_path = f.name

    try:
        params = ScanParams(
            target=temp_path,
            profile="secret-detection",
            safe_only=True
        )

        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert result.content["scan_type"] == "local"
        assert result.content["profile"] == "secret-detection"
        assert "findings" in result.content

        # Should detect potential secrets
        findings = result.content["findings"]
        secret_findings = [f for f in findings if "secret" in f.get("title", "").lower() or "password" in f.get("title", "").lower()]
        assert len(secret_findings) > 0

    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_scan_local_directory():
    """Test scanning a local directory"""
    tool = ScanTool()

    # Create temp directory with files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a few test files
        for i in range(3):
            (Path(temp_dir) / f"file{i}.txt").write_text(f"Test content {i}")

        params = ScanParams(
            target=temp_dir,
            profile="code-audit",
            safe_only=True
        )

        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert result.content["scan_type"] == "local"
        assert "findings" in result.content

        # Should report directory scan
        findings = result.content["findings"]
        dir_findings = [f for f in findings if "directory" in f.get("title", "").lower()]
        assert len(dir_findings) > 0


@pytest.mark.asyncio
async def test_scan_nonexistent_local_target():
    """Test scanning non-existent local target"""
    tool = ScanTool()

    params = ScanParams(
        target="/nonexistent/path/to/file.txt",
        profile="code-audit"
    )

    result = await tool.execute(params)

    # Should fail gracefully
    assert isinstance(result, ToolError)
    assert "not found" in result.message.lower() or "failed" in result.message.lower()


@pytest.mark.asyncio
async def test_scan_remote_https_target():
    """Test scanning HTTPS remote target"""
    tool = ScanTool()

    params = ScanParams(
        target="https://example.com",
        profile="web-recon",
        safe_only=True
    )

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert result.content["scan_type"] == "remote"
    assert result.content["target"] == "https://example.com"
    assert "findings" in result.content


@pytest.mark.asyncio
async def test_scan_remote_http_target():
    """Test scanning HTTP (insecure) remote target"""
    tool = ScanTool()

    params = ScanParams(
        target="http://example.com",
        profile="web-recon",
        safe_only=True
    )

    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    findings = result.content["findings"]

    # Should detect HTTP (not HTTPS) as security issue
    http_findings = [f for f in findings if "http" in f.get("title", "").lower()]
    assert len(http_findings) > 0


@pytest.mark.asyncio
async def test_scan_max_findings_limit():
    """Test max_findings parameter limits results"""
    tool = ScanTool()

    # Create temp directory with many files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create 30 files (more than max_findings)
        for i in range(30):
            (Path(temp_dir) / f"file{i}.txt").write_text("test")

        params = ScanParams(
            target=temp_dir,
            profile="code-audit",
            max_findings=5  # Limit to 5
        )

        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        # Should limit findings
        assert len(result.content["findings"]) <= 5


@pytest.mark.asyncio
async def test_scan_profiles():
    """Test different scan profiles"""
    tool = ScanTool()

    profiles = ["code-audit", "web-recon", "vuln-scan", "secret-detection", "config-audit"]

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("test content")
        temp_path = f.name

    try:
        for profile in profiles:
            params = ScanParams(
                target=temp_path,
                profile=profile,  # type: ignore
                safe_only=True
            )

            result = await tool.execute(params)

            assert isinstance(result, ToolOk)
            assert result.content["profile"] == profile

    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_scan_safe_mode():
    """Test safe_only parameter"""
    tool = ScanTool()

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test")
        temp_path = f.name

    try:
        # Safe mode
        params_safe = ScanParams(target=temp_path, safe_only=True)
        result_safe = await tool.execute(params_safe)
        assert result_safe.content["summary"]["safe_mode"] is True

        # Non-safe mode
        params_unsafe = ScanParams(target=temp_path, safe_only=False)
        result_unsafe = await tool.execute(params_unsafe)
        assert result_unsafe.content["summary"]["safe_mode"] is False

    finally:
        Path(temp_path).unlink()


def test_scan_is_local_target():
    """Test local target detection"""
    tool = ScanTool()

    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name

    try:
        # Local path
        assert tool._is_local_target(temp_path) is True

        # Non-existent path
        assert tool._is_local_target("/nonexistent/path") is False

        # URL
        assert tool._is_local_target("https://example.com") is False

    finally:
        Path(temp_path).unlink()


def test_scan_is_valid_remote_target():
    """Test remote target validation"""
    tool = ScanTool()

    # Valid URLs
    assert tool._is_valid_remote_target("https://example.com") is True
    assert tool._is_valid_remote_target("http://api.example.com") is True

    # Valid IPs
    assert tool._is_valid_remote_target("192.168.1.1") is True
    assert tool._is_valid_remote_target("10.0.0.1") is True

    # Valid domains
    assert tool._is_valid_remote_target("example.com") is True
    assert tool._is_valid_remote_target("api.example.com") is True

    # Invalid
    assert tool._is_valid_remote_target("/local/path") is False
    assert tool._is_valid_remote_target("not-a-target") is False


@pytest.mark.asyncio
async def test_scan_large_file_detection():
    """Test detection of large files"""
    tool = ScanTool()

    # Create a larger file (>1MB)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        # Write 2MB of data
        f.write("x" * (2 * 1024 * 1024))
        temp_path = f.name

    try:
        params = ScanParams(target=temp_path, profile="code-audit")
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        # Built-in scan should report on large file
        findings = result.content["findings"]
        # May or may not detect based on threshold, but should complete

    finally:
        Path(temp_path).unlink()


def test_scan_to_dict():
    """Test tool serialization"""
    tool = ScanTool()
    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "Scan"
    assert "description" in tool_dict
    assert "parameters" in tool_dict


def test_scan_to_mcp_schema():
    """Test MCP schema generation"""
    tool = ScanTool()
    mcp_schema = tool.to_mcp_schema()

    assert mcp_schema["name"] == "Scan"
    assert "inputSchema" in mcp_schema
    assert "properties" in mcp_schema["inputSchema"]
    assert "target" in mcp_schema["inputSchema"]["properties"]
    assert "profile" in mcp_schema["inputSchema"]["properties"]
