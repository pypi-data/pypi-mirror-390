"""
Tests for Guardrails Integration in Tools

Context: Validates that all tools properly use input validation and output sanitization.
"""

import pytest
from pydantic import BaseModel, Field
from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError
from alprina_cli.guardrails import (
    InputGuardrail,
    OutputGuardrail,
    GuardrailResult,
    SanitizationResult,
    SQLInjectionGuardrail,
    PIIScrubber
)


class TestParams(BaseModel):
    """Test parameters for tool testing"""
    target: str = Field(description="Target value")
    count: int = Field(default=10, description="Count value")


class TestTool(AlprinaToolBase[TestParams]):
    """Simple test tool for guardrail testing"""
    name: str = "TestTool"
    description: str = "A test tool"
    params: type[TestParams] = TestParams

    async def execute(self, params: TestParams) -> ToolOk | ToolError:
        return ToolOk(
            content=f"Processed: {params.target}",
            output=f"Processed: {params.target}"
        )


class EchoTool(AlprinaToolBase[TestParams]):
    """Tool that echoes back sensitive data (for sanitization testing)"""
    name: str = "EchoTool"
    description: str = "Echoes back input"
    params: type[TestParams] = TestParams

    async def execute(self, params: TestParams) -> ToolOk | ToolError:
        # Return data with potential PII/credentials
        return ToolOk(
            content={
                "target": params.target,
                "message": f"Email: test@example.com, API Key: api_key=sk_test_1234567890abcdefghij"
            }
        )


class TestToolGuardrailsIntegration:
    """Tests for guardrails integration in AlprinaToolBase"""

    @pytest.mark.asyncio
    async def test_tool_initializes_with_default_guardrails(self):
        """Test that tools initialize with default guardrails"""
        tool = TestTool()

        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0
        assert len(tool.output_guardrails) > 0

    @pytest.mark.asyncio
    async def test_tool_can_disable_guardrails(self):
        """Test that guardrails can be disabled"""
        tool = TestTool(enable_guardrails=False)

        assert tool.enable_guardrails is False

    @pytest.mark.asyncio
    async def test_tool_blocks_sql_injection(self):
        """Test that SQL injection attempts are blocked"""
        tool = TestTool()

        params = TestParams(target="' OR 1=1--", count=5)
        result = await tool(params)

        assert isinstance(result, ToolError)
        assert "Security violation" in result.message
        assert "SQL injection" in result.message

    @pytest.mark.asyncio
    async def test_tool_blocks_command_injection(self):
        """Test that command injection attempts are blocked"""
        tool = TestTool()

        params = TestParams(target="test; rm -rf /", count=5)
        result = await tool(params)

        assert isinstance(result, ToolError)
        assert "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_tool_blocks_path_traversal(self):
        """Test that path traversal attempts are blocked"""
        tool = TestTool()

        params = TestParams(target="../../../etc/passwd", count=5)
        result = await tool(params)

        assert isinstance(result, ToolError)
        assert "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_tool_allows_clean_input(self):
        """Test that clean input passes through"""
        tool = TestTool()

        params = TestParams(target="example.com", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)
        assert "Processed: example.com" in result.output

    @pytest.mark.asyncio
    async def test_tool_sanitizes_pii_in_output(self):
        """Test that PII is sanitized from outputs"""
        tool = EchoTool()

        params = TestParams(target="test", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)
        # Check that email was redacted
        assert "[EMAIL_REDACTED]" in result.content["message"]
        assert "test@example.com" not in result.content["message"]

    @pytest.mark.asyncio
    async def test_tool_sanitizes_credentials_in_output(self):
        """Test that credentials are sanitized from outputs"""
        tool = EchoTool()

        params = TestParams(target="test", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)
        # Check that API key was redacted
        assert "[API_KEY_REDACTED]" in result.content["message"]

    @pytest.mark.asyncio
    async def test_tool_with_custom_input_guardrails(self):
        """Test tool with custom input guardrails"""

        class StrictGuardrail(InputGuardrail):
            """Block everything except 'safe'"""
            name = "StrictGuardrail"

            def check(self, value, param_name=""):
                if isinstance(value, str) and value != "safe":
                    return GuardrailResult(
                        passed=False,
                        tripwire_triggered=True,
                        reason="Only 'safe' is allowed",
                        severity="HIGH"
                    )
                return GuardrailResult(passed=True)

        tool = TestTool(enable_guardrails=True)
        tool.input_guardrails = [StrictGuardrail()]

        # Should block
        params = TestParams(target="test", count=5)
        result = await tool(params)
        assert isinstance(result, ToolError)

        # Should pass
        params = TestParams(target="safe", count=5)
        result = await tool(params)
        assert isinstance(result, ToolOk)

    @pytest.mark.asyncio
    async def test_tool_with_custom_output_guardrails(self):
        """Test tool with custom output guardrails"""

        class SecretScrubber(OutputGuardrail):
            """Scrub the word 'secret'"""
            name = "SecretScrubber"

            def sanitize(self, value):
                if isinstance(value, str):
                    sanitized = value.replace("secret", "[REDACTED]")
                    redactions = value.count("secret")
                    return SanitizationResult(
                        sanitized_value=sanitized,
                        redactions_made=redactions,
                        redaction_types=["secret"] if redactions > 0 else []
                    )
                return SanitizationResult(sanitized_value=value, redactions_made=0)

        class SecretTool(AlprinaToolBase[TestParams]):
            name = "SecretTool"
            description = "Returns secrets"
            params = TestParams

            async def execute(self, params: TestParams):
                return ToolOk(content="The secret code is secret123")

        tool = SecretTool(enable_guardrails=True)
        tool.output_guardrails = [SecretScrubber()]

        params = TestParams(target="test", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)
        assert "[REDACTED]" in result.content
        assert "secret" not in result.content

    @pytest.mark.asyncio
    async def test_tool_handles_guardrail_errors_gracefully(self):
        """Test that guardrail errors don't crash tools"""

        class BrokenGuardrail(InputGuardrail):
            """Guardrail that raises an error"""
            name = "BrokenGuardrail"

            def check(self, value, param_name=""):
                raise RuntimeError("Guardrail broke!")

        tool = TestTool(enable_guardrails=True)
        tool.input_guardrails = [BrokenGuardrail()]

        params = TestParams(target="test", count=5)
        # Should not crash, should execute normally
        result = await tool(params)
        assert isinstance(result, ToolOk)

    @pytest.mark.asyncio
    async def test_disabled_guardrails_allow_all(self):
        """Test that disabled guardrails allow everything through"""
        tool = TestTool(enable_guardrails=False)

        # Try SQL injection (should pass through when guardrails disabled)
        params = TestParams(target="' OR 1=1--", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)
        assert "' OR 1=1--" in result.output

    @pytest.mark.asyncio
    async def test_tool_sanitizes_nested_dict_output(self):
        """Test that nested dictionaries are sanitized"""

        class NestedTool(AlprinaToolBase[TestParams]):
            name = "NestedTool"
            description = "Returns nested data"
            params = TestParams

            async def execute(self, params: TestParams):
                return ToolOk(content={
                    "user": {
                        "name": "John",
                        "email": "john@example.com",
                        "phone": "555-123-4567"
                    },
                    "server": {
                        "ip": "10.0.0.5"
                    }
                })

        tool = NestedTool()
        params = TestParams(target="test", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)
        # Check that PII was redacted in nested structure
        assert "[EMAIL_REDACTED]" in str(result.content)
        assert "[PHONE_REDACTED]" in str(result.content)
        assert "[IP_REDACTED]" in str(result.content)

    @pytest.mark.asyncio
    async def test_tool_with_memory_and_guardrails(self):
        """Test that memory service and guardrails work together"""
        # Mock memory service
        class MockMemory:
            def is_enabled(self):
                return True

            def add_scan_results(self, tool_name, target, results):
                pass

        memory = MockMemory()
        tool = TestTool(memory_service=memory, enable_guardrails=True)

        assert tool.memory_service is not None
        assert tool.enable_guardrails is True

        params = TestParams(target="example.com", count=5)
        result = await tool(params)

        assert isinstance(result, ToolOk)


class TestAllToolsHaveGuardrails:
    """Verify all tools in the system have guardrails enabled"""

    @pytest.mark.asyncio
    async def test_scan_tool_has_guardrails(self):
        """Test that ScanTool has guardrails"""
        from alprina_cli.tools.security.scan import ScanTool

        tool = ScanTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_recon_tool_has_guardrails(self):
        """Test that ReconTool has guardrails"""
        from alprina_cli.tools.security.recon import ReconTool

        tool = ReconTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_vuln_scan_tool_has_guardrails(self):
        """Test that VulnScanTool has guardrails"""
        from alprina_cli.tools.security.vuln_scan import VulnScanTool

        tool = VulnScanTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_exploit_tool_has_guardrails(self):
        """Test that ExploitTool has guardrails"""
        from alprina_cli.tools.security.exploit import ExploitTool

        tool = ExploitTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_red_team_tool_has_guardrails(self):
        """Test that RedTeamTool has guardrails"""
        from alprina_cli.tools.security.red_team import RedTeamTool

        tool = RedTeamTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_blue_team_tool_has_guardrails(self):
        """Test that BlueTeamTool has guardrails"""
        from alprina_cli.tools.security.blue_team import BlueTeamTool

        tool = BlueTeamTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_dfir_tool_has_guardrails(self):
        """Test that DFIRTool has guardrails"""
        from alprina_cli.tools.security.dfir import DFIRTool

        tool = DFIRTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0

    @pytest.mark.asyncio
    async def test_android_sast_tool_has_guardrails(self):
        """Test that AndroidSASTTool has guardrails"""
        from alprina_cli.tools.security.android_sast import AndroidSASTTool

        tool = AndroidSASTTool()
        assert tool.enable_guardrails is True
        assert len(tool.input_guardrails) > 0


class TestGuardrailPerformance:
    """Test that guardrails don't significantly impact performance"""

    @pytest.mark.asyncio
    async def test_guardrails_add_minimal_overhead(self):
        """Test that guardrails add < 10ms overhead"""
        import time

        tool_with_guardrails = TestTool(enable_guardrails=True)
        tool_without_guardrails = TestTool(enable_guardrails=False)

        params = TestParams(target="example.com", count=5)

        # Measure with guardrails
        start = time.time()
        for _ in range(10):
            await tool_with_guardrails(params)
        with_guardrails_time = (time.time() - start) / 10

        # Measure without guardrails
        start = time.time()
        for _ in range(10):
            await tool_without_guardrails(params)
        without_guardrails_time = (time.time() - start) / 10

        overhead = with_guardrails_time - without_guardrails_time

        # Guardrails should add less than 10ms overhead
        assert overhead < 0.010, f"Guardrails added {overhead*1000:.2f}ms overhead (max 10ms)"
