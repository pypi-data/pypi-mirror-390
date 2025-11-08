"""
Tests for MemoryService

Context: Validates memory persistence and retrieval.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from alprina_cli.memory_service import (
    MemoryService,
    MemoryConfig,
    get_memory_service,
    init_memory_service
)


def test_memory_config_creation():
    """Test creating memory configuration"""
    config = MemoryConfig(
        api_key="test-key",
        enabled=True,
        user_id="test-user"
    )

    assert config.api_key == "test-key"
    assert config.enabled is True
    assert config.user_id == "test-user"


def test_memory_service_disabled_without_api_key():
    """Test memory service is disabled without API key"""
    service = MemoryService(api_key=None, user_id="test")

    assert service.enabled is False
    assert service.is_enabled() is False


@patch('alprina_cli.memory_service.MemoryClient')
def test_memory_service_initialization(mock_client):
    """Test memory service initialization with API key"""
    service = MemoryService(api_key="test-key", user_id="test-user")

    assert service.api_key == "test-key"
    assert service.user_id == "test-user"
    assert service.enabled is True
    mock_client.assert_called_once_with(api_key="test-key")


@patch('alprina_cli.memory_service.MemoryClient')
def test_add_finding(mock_client):
    """Test adding security finding to memory"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    finding = {
        "tool": "VulnScan",
        "target": "/app/login.py",
        "vulnerability": "SQL injection",
        "severity": "HIGH",
        "description": "Unsafe SQL query"
    }

    result = service.add_finding(finding)

    assert result is True
    mock_instance.add.assert_called_once()

    # Check the call arguments
    call_args = mock_instance.add.call_args
    messages = call_args[0][0]

    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    assert "VulnScan" in messages[0]["content"]
    assert "SQL injection" in messages[0]["content"]


@patch('alprina_cli.memory_service.MemoryClient')
def test_add_scan_results(mock_client):
    """Test adding scan results to memory"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    results = {
        "summary": {"total_findings": 5},
        "findings": [
            {"severity": "HIGH", "title": "SQL Injection"},
            {"severity": "MEDIUM", "title": "XSS"}
        ]
    }

    result = service.add_scan_results(
        tool_name="VulnScan",
        target="/app",
        results=results
    )

    assert result is True
    mock_instance.add.assert_called_once()

    call_args = mock_instance.add.call_args
    messages = call_args[0][0]

    assert "VulnScan" in messages[0]["content"]
    assert "/app" in messages[0]["content"]


@patch('alprina_cli.memory_service.MemoryClient')
def test_add_context(mock_client):
    """Test adding arbitrary context to memory"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    result = service.add_context(
        role="user",
        content="I prefer deep scans for Python files",
        metadata={"preference": "scan_depth"}
    )

    assert result is True
    mock_instance.add.assert_called_once()


@patch('alprina_cli.memory_service.MemoryClient')
def test_search_memory(mock_client):
    """Test searching memory"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    # Mock search results
    mock_instance.search.return_value = [
        {
            "id": "mem1",
            "memory": "Found SQL injection in login.py",
            "metadata": {"severity": "HIGH"}
        }
    ]

    service = MemoryService(api_key="test-key", user_id="test-user")

    results = service.search("SQL injection vulnerabilities", limit=5)

    assert len(results) == 1
    assert results[0]["memory"] == "Found SQL injection in login.py"

    # Verify search was called with correct filters
    mock_instance.search.assert_called_once()
    call_kwargs = mock_instance.search.call_args[1]
    assert call_kwargs["version"] == "v2"
    assert "filters" in call_kwargs


@patch('alprina_cli.memory_service.MemoryClient')
def test_get_relevant_findings(mock_client):
    """Test getting relevant past findings"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance
    mock_instance.search.return_value = []

    service = MemoryService(api_key="test-key", user_id="test-user")

    results = service.get_relevant_findings("/app/login.py")

    assert isinstance(results, list)
    mock_instance.search.assert_called_once()


@patch('alprina_cli.memory_service.MemoryClient')
def test_get_tool_context(mock_client):
    """Test getting tool usage context"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance
    mock_instance.search.return_value = []

    service = MemoryService(api_key="test-key", user_id="test-user")

    results = service.get_tool_context("VulnScan")

    assert isinstance(results, list)
    mock_instance.search.assert_called_once()


def test_memory_service_disabled_operations():
    """Test operations when memory service is disabled"""
    service = MemoryService(api_key=None)

    # All operations should return False or empty results
    assert service.add_finding({"test": "data"}) is False
    assert service.add_scan_results("Tool", "target", {}) is False
    assert service.add_context("user", "content") is False
    assert service.search("query") == []
    assert service.get_relevant_findings("target") == []
    assert service.get_tool_context("tool") == []


@patch('alprina_cli.memory_service.MemoryClient')
def test_format_finding(mock_client):
    """Test finding formatting"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    finding = {
        "tool": "VulnScan",
        "target": "/app/login.py",
        "vulnerability": "SQL injection",
        "severity": "HIGH",
        "description": "Unsafe query",
        "file": "/app/login.py",
        "line_number": 42
    }

    formatted = service._format_finding(finding)

    assert "Tool: VulnScan" in formatted
    assert "Target: /app/login.py" in formatted
    assert "Vulnerability: SQL injection" in formatted
    assert "Severity: HIGH" in formatted
    assert "File: /app/login.py" in formatted
    assert "Line: 42" in formatted


@patch('alprina_cli.memory_service.MemoryClient')
def test_error_handling_in_add_finding(mock_client):
    """Test error handling when adding finding fails"""
    mock_instance = MagicMock()
    mock_instance.add.side_effect = Exception("API error")
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    result = service.add_finding({"test": "data"})

    assert result is False


@patch('alprina_cli.memory_service.MemoryClient')
def test_error_handling_in_search(mock_client):
    """Test error handling when search fails"""
    mock_instance = MagicMock()
    mock_instance.search.side_effect = Exception("Search error")
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    results = service.search("test query")

    assert results == []


@patch('alprina_cli.memory_service.MemoryClient')
def test_get_memory_service_singleton(mock_client):
    """Test global memory service singleton"""
    # Reset global state
    import alprina_cli.memory_service as mem_module
    mem_module._memory_service = None

    service1 = get_memory_service(api_key="test-key")
    service2 = get_memory_service()

    assert service1 is service2


@patch('alprina_cli.memory_service.MemoryClient')
def test_init_memory_service(mock_client):
    """Test initializing global memory service"""
    import alprina_cli.memory_service as mem_module
    mem_module._memory_service = None

    service = init_memory_service(api_key="test-key", user_id="test-user")

    assert service.api_key == "test-key"
    assert service.user_id == "test-user"
    assert mem_module._memory_service is service


@patch('alprina_cli.memory_service.MemoryClient')
def test_memory_service_with_env_var(mock_client, monkeypatch):
    """Test memory service uses environment variable"""
    monkeypatch.setenv("MEM0_API_KEY", "env-key")

    service = MemoryService()

    assert service.api_key == "env-key"
    assert service.enabled is True


@patch('alprina_cli.memory_service.MemoryClient')
def test_clear_user_memory(mock_client):
    """Test clearing user memory"""
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance

    service = MemoryService(api_key="test-key", user_id="test-user")

    result = service.clear_user_memory()

    # Currently just logs, so should return True
    assert result is True


@patch('alprina_cli.memory_service.MemoryClient')
def test_memory_client_initialization_failure(mock_client):
    """Test handling of memory client initialization failure"""
    mock_client.side_effect = Exception("Connection error")

    service = MemoryService(api_key="test-key", user_id="test-user")

    # Should be disabled due to initialization failure
    assert service.enabled is False
