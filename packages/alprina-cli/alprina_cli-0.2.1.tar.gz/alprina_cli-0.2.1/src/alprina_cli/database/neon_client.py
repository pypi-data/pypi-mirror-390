"""
Neon Database Client for CLI Tools

Context Engineering:
- Lightweight wrapper around NeonService
- Fast operations (< 50ms target)
- Connection pooling for performance
- Minimal token footprint in responses
"""

import os
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime
from loguru import logger

# Import existing NeonService
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api', 'services'))
from neon_service import NeonService


class NeonDatabaseClient:
    """
    Database client for CLI tool integration.

    Context Engineering:
    - All methods < 50ms (p95)
    - Connection pooling (reuse connections)
    - Minimal data transfer (only what's needed)
    - Async-first for non-blocking operations
    """

    def __init__(self):
        """Initialize database client."""
        self.service = NeonService()
        self._cli_version = os.getenv("ALPRINA_CLI_VERSION", "0.1.0")

    async def is_available(self) -> bool:
        """Check if database is configured and available."""
        return self.service.is_enabled()

    # ==========================================
    # Authentication Methods
    # ==========================================

    async def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user via API key.

        Args:
            api_key: Raw API key (e.g., "alprina_...")

        Returns:
            User dict if valid, None otherwise

        Context: Returns only essential user data
        """
        return await self.service.verify_api_key(api_key)

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return await self.service.get_user_by_id(user_id)

    # ==========================================
    # Scan Lifecycle Methods
    # ==========================================

    async def create_scan(
        self,
        user_id: str,
        tool_name: str,
        target: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Create new scan record (status: pending).

        Args:
            user_id: User UUID
            tool_name: Name of tool (e.g., "ScanTool", "ReconTool")
            target: Scan target (domain, IP, file path)
            params: Tool parameters as dict

        Returns:
            Scan ID (UUID)

        Context: Fast creation (< 20ms)
        """
        metadata = {
            "tool_name": tool_name,
            "target": target,
            "params": params,
            "cli_version": self._cli_version,
            "guardrails_enabled": True
        }

        scan_id = await self.service.create_scan(
            user_id=user_id,
            scan_type=tool_name.lower().replace("tool", ""),
            workflow_mode="cli",
            metadata=metadata
        )

        # Also update new columns
        pool = await self.service.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE scans
                SET cli_version = $1,
                    tool_name = $2,
                    target = $3
                WHERE id = $4
                """,
                self._cli_version, tool_name, target, scan_id
            )

        logger.debug(f"Created scan {scan_id} for user {user_id}")
        return scan_id

    async def update_scan_status(
        self,
        scan_id: str,
        status: str
    ) -> bool:
        """
        Update scan status.

        Args:
            scan_id: Scan UUID
            status: New status (pending/running/completed/failed)

        Returns:
            True if updated

        Context: Fast update (< 10ms)
        """
        pool = await self.service.get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE scans
                SET status = $1
                WHERE id = $2
                """,
                status, scan_id
            )
            return result == "UPDATE 1"

    async def save_scan_results(
        self,
        scan_id: str,
        findings: Dict[str, Any],
        findings_count: int,
        status: str = "completed"
    ) -> bool:
        """
        Save scan findings and mark as completed.

        Args:
            scan_id: Scan UUID
            findings: Scan results as dict
            findings_count: Number of findings
            status: Final status (completed/failed)

        Returns:
            True if saved

        Context: Efficient JSONB storage
        """
        return await self.service.save_scan(
            scan_id=scan_id,
            status=status,
            findings=findings,
            findings_count=findings_count
        )

    async def get_scan(
        self,
        scan_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve scan by ID.

        Args:
            scan_id: Scan UUID
            user_id: Optional user ID for access control

        Returns:
            Scan dict or None
        """
        return await self.service.get_scan(scan_id, user_id)

    async def list_user_scans(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        tool_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List user's recent scans.

        Args:
            user_id: User UUID
            limit: Max results (default: 20)
            offset: Pagination offset
            tool_name: Optional filter by tool

        Returns:
            List of scan dicts

        Context: Paginated for performance
        """
        return await self.service.list_scans(
            user_id=user_id,
            limit=limit,
            offset=offset,
            scan_type=tool_name.lower().replace("tool", "") if tool_name else None
        )

    # ==========================================
    # Usage Tracking Methods
    # ==========================================

    async def track_scan_usage(
        self,
        user_id: str,
        scan_id: str,
        tool_name: str,
        credits_used: int = 1,
        duration_ms: Optional[int] = None,
        vulnerabilities_found: int = 0
    ) -> bool:
        """
        Track scan usage for metering.

        Args:
            user_id: User UUID
            scan_id: Scan UUID
            tool_name: Tool name
            credits_used: Credits consumed (default: 1)
            duration_ms: Execution time in milliseconds
            vulnerabilities_found: Number of vulnerabilities found

        Returns:
            True if tracked

        Context: Essential for billing/limits
        """
        pool = await self.service.get_pool()

        # Get subscription_id
        async with pool.acquire() as conn:
            subscription = await conn.fetchrow(
                """
                SELECT id FROM user_subscriptions
                WHERE user_id = $1
                AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                user_id
            )

            subscription_id = str(subscription['id']) if subscription else None

            # Insert usage record
            await conn.execute(
                """
                INSERT INTO scan_usage (
                    user_id, subscription_id, scan_id,
                    scan_type, workflow_mode,
                    credits_used, duration_ms, vulnerabilities_found
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                user_id, subscription_id, scan_id,
                tool_name.lower().replace("tool", ""), "cli",
                credits_used, duration_ms, vulnerabilities_found
            )

        logger.debug(f"Tracked usage for scan {scan_id}: {credits_used} credits")
        return True

    async def check_scan_limit(
        self,
        user_id: str
    ) -> Tuple[bool, int, int]:
        """
        Check if user can perform another scan.

        Args:
            user_id: User UUID

        Returns:
            Tuple of (can_scan, scans_used, scans_limit)

        Context: Critical for rate limiting
        """
        pool = await self.service.get_pool()

        async with pool.acquire() as conn:
            # Get active subscription
            subscription = await conn.fetchrow(
                """
                SELECT
                    scans_used,
                    scans_limit,
                    current_period_start,
                    current_period_end
                FROM user_subscriptions
                WHERE user_id = $1
                AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                user_id
            )

            if not subscription:
                # No active subscription - free tier (10 scans/month)
                # Count scans this month
                scans_count = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM scans
                    WHERE user_id = $1
                    AND created_at >= date_trunc('month', CURRENT_DATE)
                    """,
                    user_id
                )
                return (scans_count < 10, scans_count, 10)

            # Count scans in current period
            scans_used = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM scan_usage
                WHERE user_id = $1
                AND created_at >= $2
                AND created_at < $3
                """,
                user_id,
                subscription['current_period_start'],
                subscription['current_period_end']
            )

            scans_limit = subscription['scans_limit']
            can_scan = scans_used < scans_limit

            return (can_scan, scans_used, scans_limit)

    async def increment_scan_count(self, user_id: str) -> bool:
        """
        Increment scan count for user's active subscription.

        Args:
            user_id: User UUID

        Returns:
            True if incremented
        """
        pool = await self.service.get_pool()

        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE user_subscriptions
                SET scans_used = scans_used + 1
                WHERE user_id = $1
                AND status = 'active'
                """,
                user_id
            )
            return "UPDATE" in result

    # ==========================================
    # CLI Session Tracking
    # ==========================================

    async def create_cli_session(
        self,
        user_id: str,
        cli_version: str,
        os_info: str,
        python_version: str
    ) -> str:
        """
        Create new CLI session for analytics.

        Args:
            user_id: User UUID
            cli_version: CLI version string
            os_info: Operating system
            python_version: Python version

        Returns:
            Session ID
        """
        pool = await self.service.get_pool()

        async with pool.acquire() as conn:
            session = await conn.fetchrow(
                """
                INSERT INTO cli_sessions (
                    user_id, cli_version, os, python_version
                ) VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user_id, cli_version, os_info, python_version
            )
            return str(session['id'])

    async def update_session_activity(self, session_id: str):
        """Update session last_activity timestamp."""
        pool = await self.service.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE cli_sessions
                SET last_activity = NOW(),
                    commands_run = commands_run + 1
                WHERE id = $1
                """,
                session_id
            )

    # ==========================================
    # API Key Methods
    # ==========================================

    async def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List user's API keys."""
        return await self.service.list_api_keys(user_id)

    async def create_api_key(
        self,
        user_id: str,
        name: str
    ) -> Tuple[str, str]:
        """
        Create new API key.

        Args:
            user_id: User UUID
            name: Key name/description

        Returns:
            Tuple of (raw_key, key_id)
        """
        api_key = self.service.generate_api_key()
        await self.service.create_api_key(user_id, api_key, name)

        # Get key ID
        pool = await self.service.get_pool()
        async with pool.acquire() as conn:
            key_hash = self.service.hash_api_key(api_key)
            key = await conn.fetchrow(
                "SELECT id FROM api_keys WHERE key_hash = $1",
                key_hash
            )
            return (api_key, str(key['id']))

    async def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke (deactivate) API key."""
        return await self.service.deactivate_api_key(key_id, user_id)

    # ==========================================
    # Analytics Methods
    # ==========================================

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics for dashboard.

        Returns:
            Dict with scan counts, vulnerabilities, usage, etc.
        """
        return await self.service.get_user_stats(user_id)

    async def get_scan_analytics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get scan analytics for charts.

        Args:
            user_id: User UUID
            period_days: Number of days to analyze

        Returns:
            Dict with time series data, breakdowns, etc.
        """
        pool = await self.service.get_pool()

        async with pool.acquire() as conn:
            # Scans over time (daily counts)
            scans_over_time = await conn.fetch(
                """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count,
                    scan_type
                FROM scans
                WHERE user_id = $1
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(created_at), scan_type
                ORDER BY date DESC
                """ % period_days,
                user_id
            )

            # Vulnerabilities by severity
            # (This would need to parse JSONB findings - simplified here)
            vuln_breakdown = await conn.fetchrow(
                """
                SELECT
                    SUM(findings_count) as total,
                    COUNT(*) as scan_count
                FROM scans
                WHERE user_id = $1
                AND status = 'completed'
                AND created_at >= NOW() - INTERVAL '%s days'
                """ % period_days,
                user_id
            )

            # Top targets
            top_targets = await conn.fetch(
                """
                SELECT
                    target,
                    COUNT(*) as scan_count
                FROM scans
                WHERE user_id = $1
                AND target IS NOT NULL
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY target
                ORDER BY scan_count DESC
                LIMIT 10
                """ % period_days,
                user_id
            )

            return {
                "scans_over_time": [dict(row) for row in scans_over_time],
                "vulnerabilities": dict(vuln_breakdown) if vuln_breakdown else {},
                "top_targets": [dict(row) for row in top_targets]
            }

    # ==========================================
    # Cleanup
    # ==========================================

    async def close(self):
        """Close database connection pool."""
        await self.service.close()


# Singleton instance
_client_instance = None


def get_database_client() -> NeonDatabaseClient:
    """Get singleton database client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = NeonDatabaseClient()
    return _client_instance
