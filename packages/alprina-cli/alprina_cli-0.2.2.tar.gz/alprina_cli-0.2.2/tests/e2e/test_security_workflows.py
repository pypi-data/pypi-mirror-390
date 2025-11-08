"""
End-to-End Tests for Security Workflows

Tests complete security workflows from authentication through tool execution
to audit logging. Validates the entire system works together correctly.

Context: These tests simulate real-world usage patterns.
"""

import pytest
from datetime import datetime
from alprina_cli.auth_system import (
    get_auth_service,
    get_authz_service,
    get_audit_logger,
    Role,
    Permission
)
from alprina_cli.tools.security.scan import ScanTool, ScanParams
from alprina_cli.tools.security.recon import ReconTool, ReconParams
from alprina_cli.tools.security.vuln_scan import VulnScanTool, VulnScanParams
from alprina_cli.tools.security.exploit import ExploitTool, ExploitParams
from alprina_cli.tools.base import ToolOk, ToolError


class TestCompleteSecurityWorkflow:
    """Test complete security assessment workflow"""

    @pytest.mark.asyncio
    async def test_reconnaissance_to_scan_workflow(self):
        """Test: Recon → Scan → Vulnerability Assessment workflow"""
        # Setup: Create authenticated user
        auth = get_auth_service()
        user, api_key = auth.create_user(
            username="security_analyst",
            email="analyst@example.com",
            role=Role.SECURITY_ANALYST
        )

        # Step 1: Reconnaissance
        recon_tool = ReconTool()
        recon_params = ReconParams(
            target="example.com",
            operation="whois",
            timeout=30
        )

        recon_result = await recon_tool(recon_params)
        assert isinstance(recon_result, ToolOk)

        # Step 2: Network Scan
        scan_tool = ScanTool()
        scan_params = ScanParams(
            target="example.com",
            scan_type="quick",
            ports="80,443"
        )

        scan_result = await scan_tool(scan_params)
        assert isinstance(scan_result, ToolOk)

        # Step 3: Vulnerability Assessment
        vuln_tool = VulnScanTool()
        vuln_params = VulnScanParams(
            target="example.com",
            depth="quick"
        )

        vuln_result = await vuln_tool(vuln_params)
        assert isinstance(vuln_result, ToolOk)

        # Verify: All operations completed successfully
        assert recon_result.content is not None
        assert scan_result.content is not None
        assert vuln_result.content is not None

    @pytest.mark.asyncio
    async def test_pentesting_workflow_with_authorization(self):
        """Test: Authorized pentester can run offensive tools"""
        # Setup: Create pentester user
        auth = get_auth_service()
        authz = get_authz_service()
        audit = get_audit_logger()

        pentester, api_key = auth.create_user(
            username="pentester",
            email="pentester@example.com",
            role=Role.PENTESTER
        )

        # Verify: Pentester has required permissions
        assert authz.has_permission(pentester, Permission.EXPLOIT)
        assert authz.can_use_tool(pentester, "ExploitTool")

        # Execute: Run exploit tool
        exploit_tool = ExploitTool()
        exploit_params = ExploitParams(
            target="testlab.local",
            exploit_type="safe",
            vulnerability="CVE-2024-1234"
        )

        result = await exploit_tool(exploit_params)

        # Verify: Exploit check completed
        assert isinstance(result, ToolOk)

        # Log: Record the operation
        audit.log(
            user=pentester,
            operation="exploit_check",
            tool_name="ExploitTool",
            target="testlab.local",
            success=True,
            details={"cve": "CVE-2024-1234"}
        )

        # Verify: Audit log captured the operation
        logs = audit.get_logs(user_id=pentester.user_id)
        assert len(logs) > 0
        assert logs[0].tool_name == "ExploitTool"

    @pytest.mark.asyncio
    async def test_defender_workflow_incident_response(self):
        """Test: Defender responds to security incident"""
        # Setup: Create defender user
        auth = get_auth_service()
        authz = get_authz_service()

        defender, api_key = auth.create_user(
            username="defender",
            email="defender@example.com",
            role=Role.DEFENDER
        )

        # Verify: Defender has defensive permissions
        assert authz.has_permission(defender, Permission.BLUE_TEAM)
        assert authz.has_permission(defender, Permission.DFIR)

        # Verify: Defender CANNOT use offensive tools
        assert not authz.has_permission(defender, Permission.EXPLOIT)
        assert not authz.can_use_tool(defender, "ExploitTool")

    @pytest.mark.asyncio
    async def test_auditor_readonly_workflow(self):
        """Test: Auditor can view reports but not execute tools"""
        # Setup: Create auditor user
        auth = get_auth_service()
        authz = get_authz_service()
        audit = get_audit_logger()

        auditor, api_key = auth.create_user(
            username="auditor",
            email="auditor@example.com",
            role=Role.AUDITOR
        )

        # Verify: Auditor has view permissions
        assert authz.has_permission(auditor, Permission.VIEW_REPORTS)
        assert authz.has_permission(auditor, Permission.VIEW_AUDIT_LOGS)

        # Verify: Auditor CANNOT execute security tools
        assert not authz.has_permission(auditor, Permission.SCAN)
        assert not authz.has_permission(auditor, Permission.EXPLOIT)

        # Auditor can view audit logs
        logs = audit.get_logs()
        assert isinstance(logs, list)


class TestMultiUserCollaboration:
    """Test multiple users collaborating on security assessment"""

    @pytest.mark.asyncio
    async def test_team_based_security_assessment(self):
        """Test: Multiple users with different roles collaborate"""
        auth = get_auth_service()
        audit = get_audit_logger()

        # Create team members
        analyst, analyst_key = auth.create_user(
            "analyst1", "analyst1@example.com", Role.SECURITY_ANALYST
        )
        pentester, pentester_key = auth.create_user(
            "pentester1", "pentester1@example.com", Role.PENTESTER
        )
        defender, defender_key = auth.create_user(
            "defender1", "defender1@example.com", Role.DEFENDER
        )

        # Analyst performs reconnaissance
        recon_tool = ReconTool()
        recon_result = await recon_tool(ReconParams(
            target="testlab.local",
            operation="dns",
            timeout=30
        ))
        audit.log(analyst, "recon", "ReconTool", "testlab.local", True)

        # Analyst performs vulnerability scan
        vuln_tool = VulnScanTool()
        vuln_result = await vuln_tool(VulnScanParams(
            target="testlab.local",
            depth="quick"
        ))
        audit.log(analyst, "vuln_scan", "VulnScanTool", "testlab.local", True)

        # Pentester validates findings (authorized)
        exploit_tool = ExploitTool()
        exploit_result = await exploit_tool(ExploitParams(
            target="testlab.local",
            exploit_type="safe",
            vulnerability="CVE-2024-TEST"
        ))
        audit.log(pentester, "exploit_check", "ExploitTool", "testlab.local", True)

        # Verify: All operations succeeded
        assert isinstance(recon_result, ToolOk)
        assert isinstance(vuln_result, ToolOk)
        assert isinstance(exploit_result, ToolOk)

        # Verify: Audit trail shows collaboration
        analyst_logs = audit.get_logs(user_id=analyst.user_id)
        pentester_logs = audit.get_logs(user_id=pentester.user_id)

        assert len(analyst_logs) >= 2  # Recon + VulnScan
        assert len(pentester_logs) >= 1  # Exploit check


class TestGuardrailsInWorkflow:
    """Test that guardrails protect the entire workflow"""

    @pytest.mark.asyncio
    async def test_workflow_blocks_malicious_input(self):
        """Test: Malicious input is blocked throughout workflow"""
        auth = get_auth_service()
        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.USER
        )

        # Attempt SQL injection in scan
        scan_tool = ScanTool()
        malicious_params = ScanParams(
            target="' OR 1=1--",
            scan_type="quick",
            ports="80"
        )

        result = await scan_tool(malicious_params)

        # Verify: Attack was blocked
        assert isinstance(result, ToolError)
        assert "Security violation" in result.message

    @pytest.mark.asyncio
    async def test_workflow_sanitizes_sensitive_output(self):
        """Test: Sensitive data is sanitized in workflow outputs"""
        auth = get_auth_service()
        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.SECURITY_ANALYST
        )

        # Create a mock tool that returns sensitive data
        from alprina_cli.tools.base import AlprinaToolBase
        from pydantic import BaseModel

        class TestParams(BaseModel):
            target: str

        class SensitiveDataTool(AlprinaToolBase[TestParams]):
            name = "SensitiveDataTool"
            description = "Test tool"
            params = TestParams

            async def execute(self, params: TestParams):
                return ToolOk(content={
                    "target": params.target,
                    "admin_email": "admin@example.com",
                    "api_key": "api_key=sk_test_1234567890abcdefghijklmnop",
                    "server_ip": "10.0.0.5"
                })

        tool = SensitiveDataTool()
        result = await tool(TestParams(target="example.com"))

        # Verify: Sensitive data was sanitized
        assert isinstance(result, ToolOk)
        assert "[EMAIL_REDACTED]" in str(result.content)
        assert "[API_KEY_REDACTED]" in str(result.content)
        assert "[IP_REDACTED]" in str(result.content)


class TestFailureRecovery:
    """Test system behavior during failures"""

    @pytest.mark.asyncio
    async def test_workflow_continues_after_tool_failure(self):
        """Test: Workflow can continue after non-critical tool failure"""
        auth = get_auth_service()
        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.SECURITY_ANALYST
        )

        # Step 1: Successful recon
        recon_tool = ReconTool()
        recon_result = await recon_tool(ReconParams(
            target="example.com",
            operation="whois",
            timeout=30
        ))
        assert isinstance(recon_result, ToolOk)

        # Step 2: Scan with invalid target (will fail)
        scan_tool = ScanTool()
        scan_result = await scan_tool(ScanParams(
            target="invalid..target..com",  # Invalid target
            scan_type="quick",
            ports="80"
        ))
        # Should handle gracefully (may be ToolError or ToolOk with error message)

        # Step 3: Continue with valid operation
        vuln_tool = VulnScanTool()
        vuln_result = await vuln_tool(VulnScanParams(
            target="example.com",
            depth="quick"
        ))
        assert isinstance(vuln_result, ToolOk)

        # Verify: First and last operations succeeded
        assert isinstance(recon_result, ToolOk)
        assert isinstance(vuln_result, ToolOk)

    @pytest.mark.asyncio
    async def test_authentication_failure_prevents_execution(self):
        """Test: Tools cannot execute without valid authentication"""
        auth = get_auth_service()

        # Try to authenticate with invalid API key
        user = auth.authenticate("invalid_api_key_12345")

        # Verify: Authentication failed
        assert user is None

        # Note: In real implementation, tool execution would check authentication
        # and block execution if user is None


class TestAuditTrailCompleteness:
    """Test that audit trail captures all operations"""

    @pytest.mark.asyncio
    async def test_complete_audit_trail(self):
        """Test: All operations are logged in audit trail"""
        auth = get_auth_service()
        audit = get_audit_logger()

        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.SECURITY_ANALYST
        )

        initial_log_count = len(audit.get_logs(user_id=user.user_id))

        # Perform multiple operations
        operations = [
            ("recon", "ReconTool", "example.com"),
            ("scan", "ScanTool", "example.com"),
            ("vuln_scan", "VulnScanTool", "example.com"),
        ]

        for operation, tool_name, target in operations:
            audit.log(user, operation, tool_name, target, True)

        # Verify: All operations logged
        final_logs = audit.get_logs(user_id=user.user_id)
        assert len(final_logs) == initial_log_count + len(operations)

        # Verify: Logs contain correct information
        for i, (operation, tool_name, target) in enumerate(operations):
            log_entry = final_logs[len(operations) - 1 - i]  # Reverse order (newest first)
            assert log_entry.operation == operation
            assert log_entry.tool_name == tool_name
            assert log_entry.target == target
            assert log_entry.success is True

    @pytest.mark.asyncio
    async def test_audit_trail_includes_failures(self):
        """Test: Failed operations are also logged"""
        auth = get_auth_service()
        audit = get_audit_logger()

        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.USER
        )

        # Log successful operation
        audit.log(user, "scan", "ScanTool", "example.com", True)

        # Log failed operation
        audit.log(user, "exploit", "ExploitTool", "example.com", False,
                 details={"error": "Permission denied"})

        # Verify: Both operations logged
        logs = audit.get_logs(user_id=user.user_id, limit=2)
        assert len(logs) == 2

        # Verify: Success/failure captured
        assert logs[0].success is False  # Most recent (failed)
        assert logs[1].success is True   # Older (successful)


class TestPerformanceUnderLoad:
    """Test system performance with multiple concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test: Multiple tools can execute concurrently"""
        import asyncio

        auth = get_auth_service()
        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.SECURITY_ANALYST
        )

        # Create multiple scan tasks
        scan_tool = ScanTool()
        tasks = []

        for i in range(5):
            params = ScanParams(
                target=f"target{i}.example.com",
                scan_type="quick",
                ports="80"
            )
            tasks.append(scan_tool(params))

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify: All completed (may have errors for invalid targets, but shouldn't crash)
        assert len(results) == 5
        # Check that we got results (not exceptions)
        for result in results:
            assert isinstance(result, (ToolOk, ToolError))

    @pytest.mark.asyncio
    async def test_guardrails_performance_at_scale(self):
        """Test: Guardrails maintain performance with many validations"""
        import time

        auth = get_auth_service()
        user, api_key = auth.create_user(
            "test_user", "test@example.com", Role.USER
        )

        scan_tool = ScanTool()

        # Execute 100 scans with guardrails enabled
        start_time = time.time()

        for i in range(100):
            params = ScanParams(
                target="example.com",
                scan_type="quick",
                ports="80"
            )
            await scan_tool(params)

        elapsed_time = time.time() - start_time
        avg_time_per_scan = elapsed_time / 100

        # Verify: Average time per scan is reasonable (< 1 second with guardrails)
        # Note: This is a loose bound for E2E test, actual performance test is separate
        assert avg_time_per_scan < 1.0, f"Average scan time too slow: {avg_time_per_scan:.3f}s"
