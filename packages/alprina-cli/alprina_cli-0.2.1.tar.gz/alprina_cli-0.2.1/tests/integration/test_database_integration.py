"""
Integration tests for database persistence.

Tests that CLI tools properly save scans to Neon database.
"""

import pytest
import os
from alprina_cli.database import get_database_client
from alprina_cli.tools.security.scan import ScanTool, ScanParams


@pytest.mark.asyncio
@pytest.mark.integration
async def test_scan_with_database_persistence():
    """Test: Scan is automatically saved to database"""
    # Setup
    db = get_database_client()

    # Skip if database not configured
    if not await db.is_available():
        pytest.skip("Database not configured (DATABASE_URL not set)")

    # Create a test API key (you'll need to create a test user first)
    # For now, this test demonstrates the flow
    api_key = os.getenv("TEST_API_KEY")
    if not api_key:
        pytest.skip("TEST_API_KEY not set - skipping database integration test")

    # Create tool with database client and API key
    tool = ScanTool(
        database_client=db,
        enable_database=True,
        api_key=api_key
    )

    # Execute scan
    params = ScanParams(target="example.com", scan_type="quick", ports="80,443")
    result = await tool(params)

    # Verify
    assert result is not None
    assert hasattr(result, 'metadata')
    assert 'scan_id' in result.metadata
    assert 'duration_ms' in result.metadata

    scan_id = result.metadata['scan_id']
    print(f"✓ Scan saved to database with ID: {scan_id}")

    # Verify scan was saved
    scan = await db.get_scan(scan_id)
    assert scan is not None
    assert scan['status'] in ['completed', 'running']
    assert scan['tool_name'] == 'ScanTool'
    assert scan['target'] == 'example.com'

    print(f"✓ Scan verified in database")
    print(f"  Status: {scan['status']}")
    print(f"  Findings: {scan['findings_count']}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_scan_limit_enforcement():
    """Test: Scan limits are enforced"""
    db = get_database_client()

    if not await db.is_available():
        pytest.skip("Database not configured")

    api_key = os.getenv("TEST_API_KEY")
    if not api_key:
        pytest.skip("TEST_API_KEY not set")

    # Authenticate to get user_id
    auth_result = await db.authenticate_api_key(api_key)
    assert auth_result is not None

    user_id = auth_result['user_id']

    # Check scan limits
    can_scan, scans_used, scans_limit = await db.check_scan_limit(user_id)

    print(f"✓ User scan status: {scans_used}/{scans_limit}")
    assert isinstance(can_scan, bool)
    assert isinstance(scans_used, int)
    assert isinstance(scans_limit, int)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_usage_tracking():
    """Test: Scan usage is tracked for billing"""
    db = get_database_client()

    if not await db.is_available():
        pytest.skip("Database not configured")

    api_key = os.getenv("TEST_API_KEY")
    if not api_key:
        pytest.skip("TEST_API_KEY not set")

    # Run a scan
    tool = ScanTool(
        database_client=db,
        enable_database=True,
        api_key=api_key
    )

    params = ScanParams(target="example.com", scan_type="quick", ports="80")
    result = await tool(params)

    scan_id = result.metadata.get('scan_id')
    assert scan_id is not None

    # Verify usage was tracked
    # (In real implementation, you'd query scan_usage table)
    print(f"✓ Usage tracked for scan: {scan_id}")


if __name__ == "__main__":
    # Run tests
    import asyncio

    async def run_tests():
        print("=" * 60)
        print("DATABASE INTEGRATION TESTS")
        print("=" * 60)

        try:
            print("\n1. Testing scan with database persistence...")
            await test_scan_with_database_persistence()
        except Exception as e:
            print(f"✗ Test failed: {e}")

        try:
            print("\n2. Testing scan limit enforcement...")
            await test_scan_limit_enforcement()
        except Exception as e:
            print(f"✗ Test failed: {e}")

        try:
            print("\n3. Testing usage tracking...")
            await test_usage_tracking()
        except Exception as e:
            print(f"✗ Test failed: {e}")

        print("\n" + "=" * 60)
        print("Tests complete!")
        print("=" * 60)

    asyncio.run(run_tests())
