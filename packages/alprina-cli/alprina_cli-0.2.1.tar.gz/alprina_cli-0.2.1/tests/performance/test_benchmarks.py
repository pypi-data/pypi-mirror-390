"""
Performance Tests - Benchmarking

Benchmarks tool execution performance, guardrail overhead, and system scalability.
Ensures the system meets performance requirements for production use.

Context: Performance is a feature - fast security tools = better UX.
"""

import pytest
import time
import asyncio
from statistics import mean, stdev
from alprina_cli.tools.security.scan import ScanTool, ScanParams
from alprina_cli.tools.security.recon import ReconTool, ReconParams
from alprina_cli.tools.security.vuln_scan import VulnScanTool, VulnScanParams
from alprina_cli.guardrails import validate_input, sanitize_output
from alprina_cli.auth_system import get_auth_service, Role


class TestGuardrailPerformance:
    """Benchmark guardrail performance"""

    def test_input_validation_performance(self):
        """Test: Input validation completes in < 5ms"""
        test_inputs = [
            "example.com",
            "192.168.1.1",
            "test-server-01",
            "https://example.com/path/to/resource",
            "user@example.com"
        ]

        times = []
        iterations = 1000

        for _ in range(iterations):
            start = time.perf_counter()
            for test_input in test_inputs:
                validate_input(test_input, "target")
            end = time.perf_counter()
            times.append((end - start) / len(test_inputs) * 1000)  # ms per validation

        avg_time = mean(times)
        std_dev = stdev(times)

        print(f"\nInput Validation: {avg_time:.3f}ms ± {std_dev:.3f}ms per validation")
        assert avg_time < 5.0, f"Input validation too slow: {avg_time:.3f}ms (max 5ms)"

    def test_output_sanitization_performance(self):
        """Test: Output sanitization completes in < 10ms"""
        test_output = """
        Scan Results:
        Target: example.com
        Admin Email: admin@example.com
        API Key: sk_test_1234567890abcdefghijklmnop
        Server: 10.0.0.5
        Path: /home/admin/config.txt
        """

        times = []
        iterations = 1000

        for _ in range(iterations):
            start = time.perf_counter()
            sanitize_output(test_output)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms

        avg_time = mean(times)
        std_dev = stdev(times)

        print(f"\nOutput Sanitization: {avg_time:.3f}ms ± {std_dev:.3f}ms")
        assert avg_time < 10.0, f"Output sanitization too slow: {avg_time:.3f}ms (max 10ms)"

    def test_malicious_pattern_detection_performance(self):
        """Test: Malicious pattern detection is fast"""
        malicious_inputs = [
            "' OR 1=1--",
            "'; DROP TABLE users--",
            "../../../etc/passwd",
            "test; rm -rf /",
            "<!ENTITY xxe SYSTEM 'file:///etc/passwd'>",
        ]

        times = []
        iterations = 1000

        for _ in range(iterations):
            start = time.perf_counter()
            for malicious in malicious_inputs:
                validate_input(malicious, "target")
            end = time.perf_counter()
            times.append((end - start) / len(malicious_inputs) * 1000)  # ms per check

        avg_time = mean(times)
        std_dev = stdev(times)

        print(f"\nMalicious Pattern Detection: {avg_time:.3f}ms ± {std_dev:.3f}ms")
        assert avg_time < 10.0, f"Pattern detection too slow: {avg_time:.3f}ms (max 10ms)"


class TestToolExecutionPerformance:
    """Benchmark individual tool execution performance"""

    @pytest.mark.asyncio
    async def test_scan_tool_with_guardrails_overhead(self):
        """Test: Guardrails add < 10ms overhead to scan tool"""
        # Tool with guardrails
        tool_with_guardrails = ScanTool(enable_guardrails=True)

        # Tool without guardrails
        tool_without_guardrails = ScanTool(enable_guardrails=False)

        params = ScanParams(target="example.com", scan_type="quick", ports="80")

        # Measure with guardrails
        times_with = []
        for _ in range(10):
            start = time.perf_counter()
            await tool_with_guardrails(params)
            end = time.perf_counter()
            times_with.append((end - start) * 1000)  # ms

        # Measure without guardrails
        times_without = []
        for _ in range(10):
            start = time.perf_counter()
            await tool_without_guardrails(params)
            end = time.perf_counter()
            times_without.append((end - start) * 1000)  # ms

        avg_with = mean(times_with)
        avg_without = mean(times_without)
        overhead = avg_with - avg_without

        print(f"\nScan Tool Performance:")
        print(f"  With guardrails:    {avg_with:.3f}ms")
        print(f"  Without guardrails: {avg_without:.3f}ms")
        print(f"  Overhead:           {overhead:.3f}ms")

        assert overhead < 10.0, f"Guardrail overhead too high: {overhead:.3f}ms (max 10ms)"

    @pytest.mark.asyncio
    async def test_multiple_tool_execution_performance(self):
        """Test: Execute multiple tools efficiently"""
        scan_tool = ScanTool()
        recon_tool = ReconTool()
        vuln_tool = VulnScanTool()

        scan_params = ScanParams(target="example.com", scan_type="quick", ports="80")
        recon_params = ReconParams(target="example.com", operation="whois", timeout=30)
        vuln_params = VulnScanParams(target="example.com", depth="quick")

        # Measure sequential execution
        start = time.perf_counter()
        await scan_tool(scan_params)
        await recon_tool(recon_params)
        await vuln_tool(vuln_params)
        sequential_time = (time.perf_counter() - start) * 1000  # ms

        # Measure parallel execution
        start = time.perf_counter()
        await asyncio.gather(
            scan_tool(scan_params),
            recon_tool(recon_params),
            vuln_tool(vuln_params)
        )
        parallel_time = (time.perf_counter() - start) * 1000  # ms

        speedup = sequential_time / parallel_time

        print(f"\nMulti-Tool Execution:")
        print(f"  Sequential: {sequential_time:.3f}ms")
        print(f"  Parallel:   {parallel_time:.3f}ms")
        print(f"  Speedup:    {speedup:.2f}x")

        # Parallel should be faster (at least 1.5x speedup)
        assert speedup >= 1.5, f"Parallel execution not efficient enough: {speedup:.2f}x"


class TestAuthenticationPerformance:
    """Benchmark authentication system performance"""

    def test_authentication_performance(self):
        """Test: Authentication completes in < 1ms"""
        auth = get_auth_service()

        # Create test user
        user, api_key = auth.create_user("test_user", "test@example.com", Role.USER)

        times = []
        iterations = 1000

        for _ in range(iterations):
            start = time.perf_counter()
            auth.authenticate(api_key)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms

        avg_time = mean(times)
        std_dev = stdev(times)

        print(f"\nAuthentication: {avg_time:.3f}ms ± {std_dev:.3f}ms")
        assert avg_time < 1.0, f"Authentication too slow: {avg_time:.3f}ms (max 1ms)"

    def test_authorization_check_performance(self):
        """Test: Authorization check completes in < 0.5ms"""
        from alprina_cli.auth_system import get_authz_service, User, Permission

        authz = get_authz_service()
        user = User(
            user_id="test",
            username="test_user",
            email="test@example.com",
            role=Role.SECURITY_ANALYST
        )

        times = []
        iterations = 10000

        for _ in range(iterations):
            start = time.perf_counter()
            authz.has_permission(user, Permission.SCAN)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms

        avg_time = mean(times)
        std_dev = stdev(times)

        print(f"\nAuthorization Check: {avg_time:.3f}ms ± {std_dev:.3f}ms")
        assert avg_time < 0.5, f"Authorization check too slow: {avg_time:.3f}ms (max 0.5ms)"


class TestConcurrentOperations:
    """Test performance under concurrent load"""

    @pytest.mark.asyncio
    async def test_concurrent_scan_performance(self):
        """Test: Handle 10 concurrent scans efficiently"""
        tool = ScanTool()

        num_concurrent = 10
        params_list = [
            ScanParams(target=f"target{i}.example.com", scan_type="quick", ports="80")
            for i in range(num_concurrent)
        ]

        start = time.perf_counter()

        # Execute concurrently
        results = await asyncio.gather(*[tool(params) for params in params_list])

        elapsed = (time.perf_counter() - start) * 1000  # ms
        avg_per_scan = elapsed / num_concurrent

        print(f"\nConcurrent Scans ({num_concurrent}):")
        print(f"  Total time:     {elapsed:.3f}ms")
        print(f"  Per scan (avg): {avg_per_scan:.3f}ms")

        # Should complete all scans in reasonable time
        assert elapsed < 2000, f"Concurrent scans too slow: {elapsed:.3f}ms"
        assert len(results) == num_concurrent

    @pytest.mark.asyncio
    async def test_concurrent_guardrail_validation(self):
        """Test: Guardrails scale with concurrent requests"""
        tool = ScanTool()

        num_concurrent = 50
        params_list = [
            ScanParams(target="example.com", scan_type="quick", ports="80")
            for _ in range(num_concurrent)
        ]

        start = time.perf_counter()

        # Execute concurrently with guardrails
        results = await asyncio.gather(*[tool(params) for params in params_list])

        elapsed = (time.perf_counter() - start) * 1000  # ms
        avg_per_request = elapsed / num_concurrent

        print(f"\nConcurrent Guardrail Validation ({num_concurrent}):")
        print(f"  Total time:        {elapsed:.3f}ms")
        print(f"  Per request (avg): {avg_per_request:.3f}ms")

        # Should scale well
        assert avg_per_request < 100, f"Per-request time too high: {avg_per_request:.3f}ms"

    @pytest.mark.asyncio
    async def test_sustained_load_performance(self):
        """Test: Maintain performance under sustained load"""
        tool = ScanTool()
        params = ScanParams(target="example.com", scan_type="quick", ports="80")

        num_iterations = 100
        execution_times = []

        for _ in range(num_iterations):
            start = time.perf_counter()
            await tool(params)
            end = time.perf_counter()
            execution_times.append((end - start) * 1000)  # ms

        avg_time = mean(execution_times)
        std_dev = stdev(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)

        print(f"\nSustained Load ({num_iterations} iterations):")
        print(f"  Average:  {avg_time:.3f}ms")
        print(f"  Std Dev:  {std_dev:.3f}ms")
        print(f"  Min:      {min_time:.3f}ms")
        print(f"  Max:      {max_time:.3f}ms")

        # Performance should be consistent (low std dev)
        # Std dev should be < 20% of mean
        assert std_dev < (avg_time * 0.2), f"Performance too inconsistent: {std_dev:.3f}ms"


class TestMemoryUsage:
    """Test memory efficiency"""

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test: No memory leaks during repeated execution"""
        import gc
        import sys

        tool = ScanTool()
        params = ScanParams(target="example.com", scan_type="quick", ports="80")

        # Force garbage collection
        gc.collect()

        # Get initial memory usage
        initial_objects = len(gc.get_objects())

        # Execute many times
        for _ in range(100):
            await tool(params)

        # Force garbage collection again
        gc.collect()

        # Check final memory usage
        final_objects = len(gc.get_objects())

        object_growth = final_objects - initial_objects
        growth_rate = (object_growth / initial_objects) * 100

        print(f"\nMemory Usage:")
        print(f"  Initial objects: {initial_objects}")
        print(f"  Final objects:   {final_objects}")
        print(f"  Growth:          {object_growth} ({growth_rate:.2f}%)")

        # Object count should not grow significantly (< 10%)
        assert growth_rate < 10, f"Possible memory leak: {growth_rate:.2f}% growth"


class TestScalabilityLimits:
    """Test system limits and scalability"""

    @pytest.mark.asyncio
    async def test_maximum_concurrent_requests(self):
        """Test: Handle up to 100 concurrent requests"""
        tool = ScanTool()

        max_concurrent = 100
        params_list = [
            ScanParams(target=f"target{i}.example.com", scan_type="quick", ports="80")
            for i in range(max_concurrent)
        ]

        start = time.perf_counter()

        try:
            # Execute concurrently
            results = await asyncio.gather(*[tool(params) for params in params_list])
            elapsed = (time.perf_counter() - start) * 1000  # ms

            print(f"\nMax Concurrent Requests ({max_concurrent}):")
            print(f"  Total time: {elapsed:.3f}ms")
            print(f"  Per request (avg): {elapsed / max_concurrent:.3f}ms")

            # Should complete without crashing
            assert len(results) == max_concurrent

        except Exception as e:
            pytest.fail(f"Failed to handle {max_concurrent} concurrent requests: {e}")

    def test_audit_log_performance_at_scale(self):
        """Test: Audit log maintains performance with many entries"""
        from alprina_cli.auth_system import get_audit_logger, User

        audit = get_audit_logger()
        user = User(
            user_id="test",
            username="test_user",
            email="test@example.com",
            role=Role.USER
        )

        # Add 1000 log entries
        for i in range(1000):
            audit.log(user, "scan", "ScanTool", f"target{i}.com", True)

        # Measure query performance
        times = []
        for _ in range(100):
            start = time.perf_counter()
            logs = audit.get_logs(limit=10)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms

        avg_time = mean(times)

        print(f"\nAudit Log Query (1000 entries):")
        print(f"  Average query time: {avg_time:.3f}ms")

        # Should maintain fast queries even with many entries
        assert avg_time < 5.0, f"Audit log query too slow: {avg_time:.3f}ms"


class TestRealWorldScenarios:
    """Test performance in real-world scenarios"""

    @pytest.mark.asyncio
    async def test_typical_security_assessment_performance(self):
        """Test: Complete security assessment in reasonable time"""
        scan_tool = ScanTool()
        recon_tool = ReconTool()
        vuln_tool = VulnScanTool()

        start = time.perf_counter()

        # Step 1: Reconnaissance
        await recon_tool(ReconParams(
            target="example.com",
            operation="whois",
            timeout=30
        ))

        # Step 2: Network Scan
        await scan_tool(ScanParams(
            target="example.com",
            scan_type="quick",
            ports="80,443"
        ))

        # Step 3: Vulnerability Assessment
        await vuln_tool(VulnScanParams(
            target="example.com",
            depth="quick"
        ))

        elapsed = (time.perf_counter() - start) * 1000  # ms

        print(f"\nComplete Security Assessment:")
        print(f"  Total time: {elapsed:.3f}ms")

        # Should complete in reasonable time (< 5 seconds for basic assessment)
        assert elapsed < 5000, f"Security assessment too slow: {elapsed:.3f}ms"

    @pytest.mark.asyncio
    async def test_rapid_fire_scans_performance(self):
        """Test: Handle rapid successive scans (CI/CD scenario)"""
        tool = ScanTool()

        num_scans = 20
        targets = [f"target{i}.example.com" for i in range(num_scans)]

        start = time.perf_counter()

        for target in targets:
            await tool(ScanParams(target=target, scan_type="quick", ports="80"))

        elapsed = (time.perf_counter() - start) * 1000  # ms
        avg_per_scan = elapsed / num_scans

        print(f"\nRapid Fire Scans ({num_scans}):")
        print(f"  Total time:     {elapsed:.3f}ms")
        print(f"  Per scan (avg): {avg_per_scan:.3f}ms")

        # Should handle rapid scans efficiently
        assert avg_per_scan < 200, f"Rapid scans too slow: {avg_per_scan:.3f}ms per scan"
