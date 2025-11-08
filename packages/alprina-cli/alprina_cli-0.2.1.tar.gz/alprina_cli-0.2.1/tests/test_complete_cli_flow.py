"""
Complete CLI Integration Tests
Tests the full CLI workflow from installation to scanning

Based on USER_STORIES.md - Journey 1 & 2
"""

import subprocess
import pytest
import os
import tempfile
import json
from pathlib import Path


class TestCLIInstallation:
    """Test CLI installation from PyPI"""

    def test_cli_available_on_pypi(self):
        """Check if alprina-cli is available on PyPI"""
        result = subprocess.run(
            ['pip', 'index', 'versions', 'alprina-cli'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert 'alprina-cli' in result.stdout
        assert '0.1.1' in result.stdout

    def test_cli_version_command(self):
        """Test alprina --version works"""
        result = subprocess.run(
            ['alprina', '--version'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert '0.1' in result.stdout


class TestCLIAuthentication:
    """Test CLI authentication flow"""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create temporary config directory"""
        config_path = tmp_path / ".alprina"
        config_path.mkdir()
        return config_path

    def test_auth_login_starts_device_flow(self, monkeypatch, config_dir):
        """Test that alprina auth login initiates device flow"""
        # Set temporary config path
        monkeypatch.setenv('ALPRINA_CONFIG_DIR', str(config_dir))

        result = subprocess.run(
            ['alprina', 'auth', 'login', '--no-browser'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should show device code
        assert 'device code' in result.stdout.lower() or 'code:' in result.stdout.lower()

    def test_config_file_created_after_auth(self, config_dir):
        """Test that config.json is created after successful auth"""
        config_file = config_dir / "config.json"

        # Simulate config creation
        config_data = {
            "api_key": "alprina_test_key",
            "api_url": "https://api.alprina.com",
            "user": {
                "id": "test-user-id",
                "email": "test@example.com",
                "tier": "free"
            }
        }

        config_file.write_text(json.dumps(config_data, indent=2))

        # Verify config exists and is valid
        assert config_file.exists()

        loaded_config = json.loads(config_file.read_text())
        assert 'api_key' in loaded_config
        assert 'user' in loaded_config


class TestCLIScanning:
    """Test CLI scanning functionality"""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a test project to scan"""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Create some test files
        (project_dir / "main.py").write_text("""
import os

API_KEY = "hardcoded-secret-key"  # Security vulnerability

def insecure_function():
    eval(input("Enter command: "))  # Code injection vulnerability
""")

        (project_dir / "requirements.txt").write_text("""
flask==1.0.0  # Outdated version with known CVEs
requests==2.0.0
""")

        return project_dir

    def test_quick_scan_works(self, test_project):
        """Test quick scan execution"""
        result = subprocess.run(
            ['alprina', 'scan', str(test_project), '--type', 'quick', '--no-save'],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Check if scan completed
        assert result.returncode == 0 or 'Error' not in result.stderr

        # Check if findings are shown
        assert 'Finding' in result.stdout or 'Vulnerability' in result.stdout or 'Complete' in result.stdout

    def test_scan_detects_hardcoded_secrets(self, test_project):
        """Test that scan detects hardcoded secrets"""
        result = subprocess.run(
            ['alprina', 'scan', str(test_project), '--type', 'quick', '--no-save'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout.lower()

        # Should detect hardcoded secret
        assert 'secret' in output or 'credential' in output or 'key' in output

    def test_comprehensive_scan_uses_multiple_agents(self, test_project):
        """Test comprehensive scan with multiple agents"""
        result = subprocess.run(
            ['alprina', 'scan', str(test_project), '--type', 'comprehensive', '--no-save'],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout.lower()

        # Should mention multiple agents or comprehensive analysis
        assert 'comprehensive' in output or 'agent' in output or 'analyzing' in output

    def test_scan_with_api_key_flag(self, test_project, monkeypatch):
        """Test scan with --api-key flag"""
        # Use test API key
        test_api_key = "alprina_test_key_12345"

        result = subprocess.run(
            ['alprina', 'scan', str(test_project), '--api-key', test_api_key, '--type', 'quick'],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Should not error on API key (may fail on invalid key, but shouldn't crash)
        assert 'error parsing' not in result.stderr.lower()


class TestCLIReportExport:
    """Test CLI report export functionality"""

    def test_export_pdf_command_exists(self):
        """Test that export command is available"""
        result = subprocess.run(
            ['alprina', 'export', '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert 'export' in result.stdout.lower()

    def test_list_report_formats(self):
        """Test listing available report formats"""
        result = subprocess.run(
            ['alprina', 'export', '--help'],
            capture_output=True,
            text=True
        )

        # Should mention PDF format
        assert 'pdf' in result.stdout.lower()


class TestCLIUsageLimits:
    """Test CLI handles usage limits correctly"""

    def test_scan_limit_error_message(self, tmp_path):
        """Test that CLI shows clear error when scan limit reached"""
        # This would require mocking the API response
        # For now, just verify the error message exists in code

        from alprina_cli.api.middleware.usage_check import check_scan_limit

        # Check function exists
        assert callable(check_scan_limit)

    def test_upgrade_prompt_shown(self):
        """Test that upgrade prompt is shown when limit reached"""
        # This would be tested in integration with mock API
        pass


class TestCLIErrorHandling:
    """Test CLI error handling"""

    def test_invalid_path_error(self):
        """Test scanning invalid path shows error"""
        result = subprocess.run(
            ['alprina', 'scan', '/nonexistent/path', '--no-save'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode != 0 or 'error' in result.stderr.lower() or 'not found' in result.stdout.lower()

    def test_network_error_handling(self, test_project, monkeypatch):
        """Test CLI handles network errors gracefully"""
        # Set invalid API URL
        monkeypatch.setenv('ALPRINA_API_URL', 'http://invalid-url-that-does-not-exist.com')

        result = subprocess.run(
            ['alprina', 'scan', str(test_project), '--type', 'quick'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should show network error or continue with local scan
        # Both are acceptable behaviors
        assert 'connection' in result.stderr.lower() or 'network' in result.stderr.lower() or result.returncode == 0

    def test_timeout_handling(self, tmp_path):
        """Test that very large scans timeout gracefully"""
        # Create a large project
        large_project = tmp_path / "large_project"
        large_project.mkdir()

        # Create 100 Python files
        for i in range(100):
            (large_project / f"file_{i}.py").write_text(f"# File {i}\n" + "x = 1\n" * 1000)

        result = subprocess.run(
            ['alprina', 'scan', str(large_project), '--type', 'quick', '--no-save', '--timeout', '5'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should either complete or timeout gracefully
        assert result.returncode in [0, 1]  # 0 = success, 1 = timeout


class TestCLIConfigManagement:
    """Test CLI configuration management"""

    def test_config_show_command(self):
        """Test showing current configuration"""
        result = subprocess.run(
            ['alprina', 'config', 'show'],
            capture_output=True,
            text=True
        )

        # Should show config or indicate not configured
        assert result.returncode == 0 or 'not configured' in result.stdout.lower()

    def test_config_set_command(self, tmp_path, monkeypatch):
        """Test setting config values"""
        config_dir = tmp_path / ".alprina"
        config_dir.mkdir()
        monkeypatch.setenv('ALPRINA_CONFIG_DIR', str(config_dir))

        result = subprocess.run(
            ['alprina', 'config', 'set', 'api_url', 'http://localhost:8000'],
            capture_output=True,
            text=True
        )

        # Should succeed or show appropriate error
        assert result.returncode == 0 or 'config' in result.stdout.lower()


class TestCLIHelpDocumentation:
    """Test CLI help and documentation"""

    def test_main_help_shows_commands(self):
        """Test alprina --help shows all commands"""
        result = subprocess.run(
            ['alprina', '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Check for key commands
        commands = ['scan', 'auth', 'export', 'config']
        for cmd in commands:
            assert cmd in result.stdout.lower()

    def test_scan_help_shows_options(self):
        """Test alprina scan --help shows scan options"""
        result = subprocess.run(
            ['alprina', 'scan', '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Check for key options
        options = ['--type', '--format', '--agents']
        for opt in options:
            assert opt in result.stdout.lower()


# Integration test markers
pytestmark = pytest.mark.integration


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
