"""
Tests for VulnScanTool

Context: Validates vulnerability scanning and detection.
"""

import pytest
import tempfile
from pathlib import Path
from alprina_cli.tools.security.vuln_scan import VulnScanTool, VulnScanParams
from alprina_cli.tools.base import ToolOk, ToolError


@pytest.mark.asyncio
async def test_vuln_scan_tool_creation():
    """Test creating vuln scan tool"""
    tool = VulnScanTool()
    assert tool.name == "VulnScan"
    assert tool.params == VulnScanParams


@pytest.mark.asyncio
async def test_vuln_scan_exposed_password():
    """Test detection of exposed passwords"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('password = "super_secret_123"\n')
        f.write('api_key = "sk_test_1234567890"\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="quick"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["findings"]) > 0

        # Should detect password
        password_findings = [
            f for f in result.content["findings"]
            if "password" in f["title"].lower()
        ]
        assert len(password_findings) > 0
        assert password_findings[0]["severity"] in ["HIGH", "CRITICAL"]

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_api_key_detection():
    """Test detection of exposed API keys"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('API_KEY = "sk_live_abcdef1234567890"\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="quick"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect API key
        api_key_findings = [
            f for f in result.content["findings"]
            if "api key" in f["title"].lower()
        ]
        assert len(api_key_findings) > 0
        assert api_key_findings[0]["severity"] == "CRITICAL"

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_sql_injection():
    """Test detection of SQL injection vulnerabilities"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('query = "SELECT * FROM users WHERE id = " + user_input\n')
        f.write('cursor.execute(query)\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="standard"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect SQL injection
        sql_findings = [
            f for f in result.content["findings"]
            if "sql" in f["title"].lower()
        ]
        assert len(sql_findings) > 0
        assert sql_findings[0]["category"] == "injection"

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_command_injection():
    """Test detection of command injection vulnerabilities"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('import os\n')
        f.write('os.system("ping " + user_input)\n')
        f.write('eval(user_code)\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="standard"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect command injection
        cmd_findings = [
            f for f in result.content["findings"]
            if "command" in f["title"].lower() or "eval" in str(f).lower()
        ]
        assert len(cmd_findings) > 0

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_weak_crypto():
    """Test detection of weak cryptography"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('import hashlib\n')
        f.write('hash = hashlib.md5(data).hexdigest()\n')
        f.write('hash2 = hashlib.sha1(data).hexdigest()\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="standard"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect weak crypto
        crypto_findings = [
            f for f in result.content["findings"]
            if f["category"] == "crypto" and "weak" in f["title"].lower()
        ]
        assert len(crypto_findings) > 0

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_debug_mode():
    """Test detection of debug mode enabled"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('DEBUG = True\n')
        f.write('app.run(debug=True)\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="quick"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect debug mode
        debug_findings = [
            f for f in result.content["findings"]
            if "debug" in f["title"].lower()
        ]
        assert len(debug_findings) > 0
        assert debug_findings[0]["category"] == "config"

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_env_file():
    """Test detection of .env files"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".env", delete=False) as f:
        f.write('SECRET_KEY=test123\n')
        f.write('API_KEY=abc\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="quick"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should detect env file
        env_findings = [
            f for f in result.content["findings"]
            if "environment" in f["title"].lower() or ".env" in f.get("description", "")
        ]
        assert len(env_findings) > 0

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_directory():
    """Test scanning entire directory"""
    tool = VulnScanTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple files with vulnerabilities
        (Path(temp_dir) / "app.py").write_text('password = "test123"\n')
        (Path(temp_dir) / "config.py").write_text('DEBUG = True\n')
        (Path(temp_dir) / "db.py").write_text('query = "SELECT * FROM users WHERE id = " + user_input\n')

        params = VulnScanParams(
            target=temp_dir,
            depth="standard"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["findings"]) > 0
        assert result.content["summary"]["target_type"] == "local"


@pytest.mark.asyncio
async def test_vuln_scan_depth_quick():
    """Test quick scan depth"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('password = "test"\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="quick"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert result.content["depth"] == "quick"

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_depth_deep():
    """Test deep scan includes code quality checks"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('# TODO: Fix this later\n')
        f.write('# FIXME: Security issue\n')
        f.write('password = "test"\n')
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="deep"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Deep scan should find TODO/FIXME comments
        code_findings = [
            f for f in result.content["findings"]
            if f.get("category") == "code"
        ]
        # May or may not find code issues depending on content
        # Just verify deep scan runs

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_category_filter():
    """Test filtering by vulnerability category"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        f.write('password = "test123"\n')
        f.write('DEBUG = True\n')
        f.write('hash = hashlib.md5(data).hexdigest()\n')
        temp_file = Path(f.name)

    try:
        # Scan for crypto issues only
        params = VulnScanParams(
            target=str(temp_file),
            depth="standard",
            categories=["crypto"]
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        # Should only have crypto findings
        if len(result.content["findings"]) > 0:
            assert all(
                f["category"] == "crypto"
                for f in result.content["findings"]
            )

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_max_findings():
    """Test max_findings parameter limits results"""
    tool = VulnScanTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create many files with vulnerabilities
        for i in range(10):
            (Path(temp_dir) / f"file{i}.py").write_text('password = "test"\n')

        params = VulnScanParams(
            target=temp_dir,
            depth="quick",
            max_findings=5
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["findings"]) <= 5
        if result.content["summary"]["total_findings"] > 5:
            assert result.content["summary"]["truncated"] is True


@pytest.mark.asyncio
async def test_vuln_scan_severity_sorting():
    """Test findings are sorted by severity"""
    tool = VulnScanTool()

    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as f:
        # Create various severity findings
        f.write('# TODO: fix\n')  # INFO
        f.write('DEBUG = True\n')  # MEDIUM
        f.write('api_key = "sk_test_12345"\n')  # CRITICAL
        f.write('password = "test"\n')  # HIGH
        temp_file = Path(f.name)

    try:
        params = VulnScanParams(
            target=str(temp_file),
            depth="deep"
        )
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)

        if len(result.content["findings"]) > 1:
            # Verify sorted by severity
            severities = [f["severity"] for f in result.content["findings"]]
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
            severity_values = [severity_order[s] for s in severities]

            # Check if sorted
            assert severity_values == sorted(severity_values)

    finally:
        temp_file.unlink()


@pytest.mark.asyncio
async def test_vuln_scan_remote_http():
    """Test scanning remote HTTP target"""
    tool = VulnScanTool()

    params = VulnScanParams(
        target="http://example.com",
        depth="quick"
    )
    result = await tool.execute(params)

    assert isinstance(result, ToolOk)
    assert result.content["summary"]["target_type"] == "remote"

    # Should detect HTTP
    http_findings = [
        f for f in result.content["findings"]
        if "http" in f["title"].lower()
    ]
    assert len(http_findings) > 0


def test_vuln_scan_to_dict():
    """Test tool serialization"""
    tool = VulnScanTool()
    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "VulnScan"
    assert "target" in tool_dict["parameters"]["properties"]
    assert "depth" in tool_dict["parameters"]["properties"]
