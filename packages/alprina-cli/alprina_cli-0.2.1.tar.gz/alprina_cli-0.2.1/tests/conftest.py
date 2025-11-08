"""
Pytest configuration and shared fixtures.

Context: Provides reusable test infrastructure without bloating individual tests.
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create event loop for async tests.

    Context: Ensures async tests have proper event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_scan_results():
    """
    Provide high-signal mock scan data.

    Context: Compressed mock data (not verbose logs) for testing.
    """
    return {
        "target": "example.com",
        "vulnerabilities": [
            {
                "id": "vuln-001",
                "severity": "high",
                "type": "sqli",
                "description": "SQL injection in login form"
            },
            {
                "id": "vuln-002",
                "severity": "medium",
                "type": "xss",
                "description": "Reflected XSS in search"
            }
        ],
        "summary": "Found 2 vulnerabilities (1 high, 1 medium)",
        "timestamp": "2025-11-06T10:00:00Z"
    }


@pytest.fixture
def mock_recon_results():
    """Provide mock reconnaissance data"""
    return {
        "target": "example.com",
        "services": [
            {"port": 80, "service": "http", "version": "nginx/1.18.0"},
            {"port": 443, "service": "https", "version": "nginx/1.18.0"}
        ],
        "technologies": ["nginx", "php", "mysql"],
        "summary": "Found 2 open ports, 3 technologies identified"
    }


# Future fixtures will be added here as we implement more features:
# - mock_memory_manager
# - mock_guardrail_results
# - mock_api_client
# etc.
