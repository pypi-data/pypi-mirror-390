"""
Usage Tracking Service

Manages user usage tracking, limits, and enforcement.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from fastapi import HTTPException

from .polar_service import polar_service


class UsageService:
    """Service for tracking and enforcing usage limits."""

    def __init__(self):
        self.polar = polar_service

    def get_current_month(self) -> str:
        """Get current month in YYYY-MM format."""
        return datetime.utcnow().strftime("%Y-%m")

    async def get_or_create_usage_record(
        self,
        user_id: str,
        tier: str,
        db_service
    ) -> Dict[str, Any]:
        """
        Get or create usage record for current month.

        Args:
            user_id: User ID
            tier: User tier
            db_service: Database service instance

        Returns:
            Usage record
        """
        current_month = self.get_current_month()

        # Try to get existing record
        usage = await db_service.get_usage_record(user_id, current_month)

        if usage:
            return usage

        # Create new record with tier limits
        limits = self.polar.get_tier_limits(tier)

        usage = await db_service.create_usage_record(
            user_id=user_id,
            month=current_month,
            scans_limit=limits["scans_per_month"],
            api_calls_limit=limits["api_requests_per_hour"]
        )

        logger.info(f"Created usage record for user {user_id}, month {current_month}")
        return usage

    async def check_scan_limit(
        self,
        user_id: str,
        tier: str,
        db_service
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Check if user can perform a scan.

        Args:
            user_id: User ID
            tier: User tier
            db_service: Database service

        Returns:
            Tuple of (can_scan, error_message, usage_info)
        """
        usage = await self.get_or_create_usage_record(user_id, tier, db_service)

        scans_count = usage.get("scans_count", 0)
        scans_limit = usage.get("scans_limit")

        # No limit (Pro/Enterprise)
        if scans_limit is None:
            # Soft limit check for Pro (warn at 1000)
            if tier == "pro" and scans_count >= 1000:
                logger.warning(f"User {user_id} exceeded 1000 scans (soft limit)")
                # Allow but log

            return True, None, {
                "scans_used": scans_count,
                "scans_limit": "unlimited",
                "scans_remaining": "unlimited"
            }

        # Hard limit check
        if scans_count >= scans_limit:
            return False, (
                f"Monthly scan limit reached ({scans_limit} scans). "
                f"Upgrade to Pro for unlimited scans."
            ), {
                "scans_used": scans_count,
                "scans_limit": scans_limit,
                "scans_remaining": 0
            }

        # Approaching limit warning (90%)
        if scans_count >= scans_limit * 0.9:
            logger.warning(
                f"User {user_id} approaching scan limit: "
                f"{scans_count}/{scans_limit}"
            )

        return True, None, {
            "scans_used": scans_count,
            "scans_limit": scans_limit,
            "scans_remaining": scans_limit - scans_count
        }

    async def check_workflow_access(
        self,
        tier: str,
        workflow_mode: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user tier has access to workflow mode.

        Args:
            tier: User tier
            workflow_mode: Workflow mode (parallel, sequential, coordinated)

        Returns:
            Tuple of (has_access, error_message)
        """
        limits = self.polar.get_tier_limits(tier)

        # Free and Developer: only single agent scans
        if workflow_mode == "parallel":
            if not limits["parallel_scans"]:
                return False, "Parallel scans require Pro tier or higher"

        elif workflow_mode == "sequential":
            if not limits["sequential_scans"]:
                return False, "Sequential workflows require Pro tier or higher"

        elif workflow_mode == "coordinated":
            if not limits["coordinated_chains"]:
                return False, "Coordinated agent chains require Pro tier or higher"

        return True, None

    async def check_file_limit(
        self,
        tier: str,
        file_count: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if file count is within tier limits.

        Args:
            tier: User tier
            file_count: Number of files to scan

        Returns:
            Tuple of (within_limit, error_message)
        """
        limits = self.polar.get_tier_limits(tier)
        files_per_scan = limits["files_per_scan"]

        # No limit
        if files_per_scan is None:
            return True, None

        if file_count > files_per_scan:
            return False, (
                f"File count ({file_count}) exceeds tier limit "
                f"({files_per_scan} files per scan). "
                f"Upgrade to Pro for higher limits."
            )

        return True, None

    async def increment_scan_count(
        self,
        user_id: str,
        tier: str,
        workflow_mode: str,
        file_count: int,
        db_service
    ) -> Dict[str, Any]:
        """
        Increment scan count after successful scan.

        Args:
            user_id: User ID
            tier: User tier
            workflow_mode: Workflow mode used
            file_count: Files scanned
            db_service: Database service

        Returns:
            Updated usage record
        """
        usage = await self.get_or_create_usage_record(user_id, tier, db_service)

        updates = {
            "scans_count": usage["scans_count"] + 1,
            "files_scanned_total": usage.get("files_scanned_total", 0) + file_count
        }

        # Track workflow mode usage
        if workflow_mode == "parallel":
            updates["parallel_scans_count"] = usage.get("parallel_scans_count", 0) + 1
        elif workflow_mode == "sequential":
            updates["sequential_scans_count"] = usage.get("sequential_scans_count", 0) + 1
        elif workflow_mode == "coordinated":
            updates["coordinated_chains_count"] = usage.get("coordinated_chains_count", 0) + 1

        usage = await db_service.update_usage_record(
            user_id,
            self.get_current_month(),
            updates
        )

        logger.info(
            f"Incremented scan count for user {user_id}: "
            f"{updates['scans_count']} scans"
        )

        return usage

    async def record_scan(
        self,
        user_id: str,
        scan_data: Dict[str, Any],
        db_service
    ) -> Dict[str, Any]:
        """
        Record a scan in history.

        Args:
            user_id: User ID
            scan_data: Scan details
            db_service: Database service

        Returns:
            Scan history record
        """
        record = await db_service.create_scan_history(
            user_id=user_id,
            scan_type=scan_data.get("scan_type", "code"),
            agent_used=scan_data.get("agent", "unknown"),
            target=scan_data.get("target", ""),
            files_count=scan_data.get("files_count", 0),
            findings_count=scan_data.get("findings_count", 0),
            critical_findings=scan_data.get("critical_findings", 0),
            high_findings=scan_data.get("high_findings", 0),
            medium_findings=scan_data.get("medium_findings", 0),
            low_findings=scan_data.get("low_findings", 0),
            workflow_mode=scan_data.get("workflow_mode", "single"),
            duration_seconds=scan_data.get("duration", 0),
            status=scan_data.get("status", "completed")
        )

        return record

    async def get_usage_stats(
        self,
        user_id: str,
        tier: str,
        db_service
    ) -> Dict[str, Any]:
        """
        Get usage statistics for user.

        Args:
            user_id: User ID
            tier: User tier
            db_service: Database service

        Returns:
            Usage statistics
        """
        usage = await self.get_or_create_usage_record(user_id, tier, db_service)
        limits = self.polar.get_tier_limits(tier)

        # Get scan history summary
        current_month = self.get_current_month()
        scan_history = await db_service.get_user_scan_history(user_id, limit=10)

        # Calculate percentage used
        scans_limit = usage.get("scans_limit")
        if scans_limit:
            usage_percentage = (usage["scans_count"] / scans_limit) * 100
        else:
            usage_percentage = 0

        return {
            "current_period": {
                "month": current_month,
                "scans_used": usage["scans_count"],
                "scans_limit": scans_limit or "unlimited",
                "scans_remaining": (scans_limit - usage["scans_count"]) if scans_limit else "unlimited",
                "usage_percentage": round(usage_percentage, 1),
                "files_scanned": usage.get("files_scanned_total", 0),
                "reports_generated": usage.get("reports_generated", 0)
            },
            "workflows": {
                "parallel_scans": usage.get("parallel_scans_count", 0),
                "sequential_scans": usage.get("sequential_scans_count", 0),
                "coordinated_chains": usage.get("coordinated_chains_count", 0)
            },
            "tier_limits": limits,
            "recent_scans": scan_history,
            "reset_date": self._get_next_reset_date()
        }

    def _get_next_reset_date(self) -> str:
        """Get next monthly reset date."""
        now = datetime.utcnow()
        next_month = now.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        return next_month.strftime("%Y-%m-%d")

    async def enforce_rate_limit(
        self,
        user_id: str,
        tier: str,
        db_service
    ) -> Tuple[bool, Optional[str]]:
        """
        Check API rate limit.

        Args:
            user_id: User ID
            tier: User tier
            db_service: Database service

        Returns:
            Tuple of (within_limit, error_message)
        """
        # Simple hourly rate limit check
        # In production, use Redis for better rate limiting
        limits = self.polar.get_tier_limits(tier)
        api_limit = limits["api_requests_per_hour"]

        if api_limit is None:
            return True, None  # No limit

        # Get API calls in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        api_calls = await db_service.count_api_calls_since(user_id, one_hour_ago)

        if api_calls >= api_limit:
            return False, (
                f"API rate limit exceeded ({api_limit} requests/hour). "
                f"Please try again later or upgrade to Pro for higher limits."
            )

        return True, None


# Create singleton instance
usage_service = UsageService()
