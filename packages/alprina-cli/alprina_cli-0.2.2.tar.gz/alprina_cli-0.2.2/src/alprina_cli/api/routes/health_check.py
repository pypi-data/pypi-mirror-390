"""
Health check and diagnostics endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any
from loguru import logger

from ..services.neon_service import neon_service

router = APIRouter()


@app.get("/v1/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with database connection status.
    """
    health = {
        "api": "healthy",
        "database": {
            "enabled": False,
            "connected": False,
            "pool_initialized": False,
            "error": None
        }
    }

    # Check Neon service
    if neon_service.is_enabled():
        health["database"]["enabled"] = True

        try:
            pool = await neon_service.get_pool()
            health["database"]["pool_initialized"] = True

            # Test query
            async with pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                health["database"]["connected"] = True
                health["database"]["version"] = version[:50]  # First 50 chars

                # Count tables
                table_count = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = 'public'
                    """
                )
                health["database"]["tables_count"] = table_count

                # Count rows in key tables
                health["database"]["row_counts"] = {
                    "users": await conn.fetchval("SELECT COUNT(*) FROM users"),
                    "webhook_events": await conn.fetchval("SELECT COUNT(*) FROM webhook_events"),
                    "api_keys": await conn.fetchval("SELECT COUNT(*) FROM api_keys"),
                    "scans": await conn.fetchval("SELECT COUNT(*) FROM scans")
                }

        except Exception as e:
            health["database"]["error"] = str(e)
            logger.error(f"Health check database error: {e}")

    return health


@app.get("/v1/health/database-test")
async def database_test() -> Dict[str, Any]:
    """
    Test database write capability.
    """
    if not neon_service.is_enabled():
        return {"error": "Database not enabled"}

    try:
        pool = await neon_service.get_pool()

        async with pool.acquire() as conn:
            # Try to insert a test webhook event
            await conn.execute(
                """
                INSERT INTO webhook_events (event_type, event_id, payload)
                VALUES ($1, $2, $3)
                ON CONFLICT (event_id) DO NOTHING
                """,
                "test.health_check",
                f"test_health_{datetime.utcnow().timestamp()}",
                {"test": True}
            )

            # Count webhooks
            count = await conn.fetchval("SELECT COUNT(*) FROM webhook_events")

            return {
                "status": "success",
                "message": "Database write test passed",
                "webhook_events_count": count
            }

    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
