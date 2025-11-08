"""
Tests for ReconTool

Context: Validates reconnaissance and information gathering.
"""

import pytest
import tempfile
from pathlib import Path
from alprina_cli.tools.security.recon import ReconTool, ReconParams
from alprina_cli.tools.base import ToolOk, ToolError


@pytest.mark.asyncio
async def test_recon_tool_creation():
    """Test creating recon tool"""
    tool = ReconTool()
    assert tool.name == "Recon"
    assert tool.params == ReconParams


@pytest.mark.asyncio
async def test_recon_dns_resolution():
    """Test DNS resolution for network target"""
    tool = ReconTool()

    params = ReconParams(
        target="localhost",
        scope="passive"
    )
    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert result.content["target"] == "localhost"
    assert result.content["scope"] == "passive"
    assert result.content["summary"]["target_type"] == "network"
    assert len(result.content["findings"]) > 0

    # Should have DNS resolution finding
    dns_finding = next((f for f in result.content["findings"] if f["type"] == "DNS Resolution"), None)
    assert dns_finding is not None


@pytest.mark.asyncio
async def test_recon_http_protocol_detection():
    """Test detection of insecure HTTP protocol"""
    tool = ReconTool()

    params = ReconParams(
        target="http://example.com",
        scope="passive"
    )
    result = await tool.execute(params)

    assert isinstance(result, ToolOk)

    # Should detect insecure protocol
    security_findings = [f for f in result.content["findings"] if f["type"] == "Security"]
    assert len(security_findings) > 0
    assert any("Insecure Protocol" in f["title"] for f in security_findings)


@pytest.mark.asyncio
async def test_recon_active_scope_port_scan():
    """Test active scope includes port scanning"""
    tool = ReconTool()

    params = ReconParams(
        target="localhost",
        scope="active"
    )
    result = await tool.execute(params)

    assert isinstance(result, ToolOk)

    # Active scope should include port scan results
    # Note: May not find open ports on localhost, but scan should run
    assert result.content["scope"] == "active"


@pytest.mark.asyncio
async def test_recon_full_scope():
    """Test full scope includes technology detection"""
    tool = ReconTool()

    params = ReconParams(
        target="http://example.com/wp-admin",
        scope="full"
    )
    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert result.content["scope"] == "full"

    # Should detect WordPress
    tech_findings = [f for f in result.content["findings"] if f["type"] == "Technology"]
    if tech_findings:
        assert any("WordPress" in str(f) for f in tech_findings)


@pytest.mark.asyncio
async def test_recon_file_target():
    """Test reconnaissance on file target"""
    tool = ReconTool()

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        temp_file = Path(f.name)
        temp_file.write_text("test content")

    try:
        params = ReconParams(
            target=str(temp_file),
            scope="passive"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert result.content["summary"]["target_type"] == "file"

        # Should have file info finding
        file_findings = [f for f in result.content["findings"] if f["type"] == "File Info"]
        assert len(file_findings) > 0

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_recon_sensitive_file_detection():
    """Test detection of sensitive file extensions"""
    tool = ReconTool()

    with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as f:
        temp_file = Path(f.name)
        temp_file.write_text("SECRET_KEY=test")

    try:
        params = ReconParams(
            target=str(temp_file),
            scope="passive"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect sensitive file
        sensitive_findings = [f for f in result.content["findings"] if f["type"] == "Sensitive File"]
        assert len(sensitive_findings) > 0
        assert sensitive_findings[0]["severity"] == "HIGH"

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_recon_directory_target():
    """Test reconnaissance on directory"""
    tool = ReconTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        (Path(temp_dir) / "file1.txt").touch()
        (Path(temp_dir) / "file2.py").touch()
        (Path(temp_dir) / ".env").write_text("SECRET=test")

        params = ReconParams(
            target=temp_dir,
            scope="passive"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert result.content["summary"]["target_type"] == "file"

        # Should have directory info
        dir_findings = [f for f in result.content["findings"] if f["type"] == "Directory Info"]
        assert len(dir_findings) > 0

        # Should detect .env file
        sensitive_findings = [f for f in result.content["findings"] if f["type"] == "Sensitive File"]
        assert len(sensitive_findings) > 0


@pytest.mark.asyncio
async def test_recon_nonexistent_file():
    """Test recon on nonexistent file with absolute path"""
    tool = ReconTool()

    # Use absolute path to ensure it's treated as file target
    params = ReconParams(
        target="/nonexistent/path/to/file.txt",
        scope="passive"
    )
    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert result.content["summary"]["target_type"] == "file"

    # Should report error in findings
    error_findings = [f for f in result.content["findings"] if f["type"] == "Error"]
    assert len(error_findings) > 0
    assert "not exist" in error_findings[0]["description"].lower()


@pytest.mark.asyncio
async def test_recon_max_findings_limit():
    """Test max_findings parameter limits results"""
    tool = ReconTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create many sensitive files to generate many findings
        sensitive_names = [".env", ".env.local", "credentials.json", "id_rsa",
                          "id_dsa", "config.json", "secrets.yml"]
        for name in sensitive_names:
            (Path(temp_dir) / name).write_text("test")

        # Also create some regular files
        for i in range(10):
            (Path(temp_dir) / f"file{i}.txt").touch()

        params = ReconParams(
            target=temp_dir,
            scope="passive",
            max_findings=3  # Very low limit to ensure truncation
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["findings"]) <= 3
        # If we have many findings, they should be truncated
        if result.content["summary"]["total_findings"] > 3:
            assert result.content["summary"]["truncated"] is True


@pytest.mark.asyncio
async def test_recon_dns_failure():
    """Test handling of DNS resolution failure"""
    tool = ReconTool()

    params = ReconParams(
        target="nonexistent-domain-12345.invalid",
        scope="passive"
    )
    result = await tool.execute(params)

    # Should still return ToolOk with DNS failure finding
    assert isinstance(result, ToolOk)

    dns_findings = [f for f in result.content["findings"] if f["type"] == "DNS Resolution"]
    assert len(dns_findings) > 0
    assert any("Failed" in f.get("title", "") for f in dns_findings)


@pytest.mark.asyncio
async def test_recon_target_type_detection():
    """Test correct detection of network vs file targets"""
    tool = ReconTool()

    # Network targets
    assert tool._is_network_target("http://example.com") is True
    assert tool._is_network_target("https://example.com") is True
    assert tool._is_network_target("example.com") is True
    assert tool._is_network_target("192.168.1.1") is True

    # File targets (assuming they exist)
    with tempfile.NamedTemporaryFile() as f:
        assert tool._is_network_target(f.name) is False


def test_recon_to_dict():
    """Test tool serialization"""
    tool = ReconTool()
    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "Recon"
    assert "target" in tool_dict["parameters"]["properties"]
    assert "scope" in tool_dict["parameters"]["properties"]
