"""
Usage Check Middleware

Enforces usage limits for scans and API requests.
"""

from fastapi import Request, HTTPException, Depends
from typing import Dict, Any, Optional
from loguru import logger

from ..middleware.auth import get_current_user
from ..services.usage_service import usage_service
from ..services.neon_service import neon_service


async def check_usage_limits(
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check if user is within usage limits.

    Args:
        request: FastAPI request object
        user: Current authenticated user

    Returns:
        User object with usage info

    Raises:
        HTTPException: If usage limits exceeded
    """
    user_id = user["id"]
    tier = user["tier"]

    # Check API rate limit
    within_limit, error = await usage_service.enforce_rate_limit(
        user_id,
        tier,
        neon_service
    )

    if not within_limit:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": error,
                "tier": tier,
                "upgrade_url": "https://platform.alprina.ai/upgrade"
            }
        )

    # Add usage info to user object
    user["usage_checked"] = True
    return user


async def check_scan_permission(
    workflow_mode: str = "single",
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check if user has permission to perform scan.

    Args:
        workflow_mode: Workflow mode (single, parallel, sequential, coordinated)
        user: Current authenticated user

    Returns:
        User object

    Raises:
        HTTPException: If scan not permitted
    """
    user_id = user["id"]
    tier = user["tier"]

    # Check scan limit
    can_scan, error, usage_info = await usage_service.check_scan_limit(
        user_id,
        tier,
        neon_service
    )

    if not can_scan:
        logger.warning(f"Scan limit exceeded for user {user_id}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "scan_limit_exceeded",
                "message": error,
                "usage": usage_info,
                "tier": tier,
                "upgrade_url": "https://platform.alprina.ai/upgrade"
            }
        )

    # Check workflow access
    has_access, error = await usage_service.check_workflow_access(tier, workflow_mode)

    if not has_access:
        logger.warning(
            f"User {user_id} attempted {workflow_mode} workflow "
            f"without access (tier: {tier})"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "workflow_not_available",
                "message": error,
                "tier": tier,
                "required_tier": "pro",
                "upgrade_url": "https://platform.alprina.ai/upgrade"
            }
        )

    # Add usage info to user
    user["usage_info"] = usage_info
    return user


async def record_scan_usage(
    user_id: str,
    tier: str,
    workflow_mode: str,
    file_count: int,
    scan_data: Dict[str, Any]
):
    """
    Record scan usage after successful scan.

    Args:
        user_id: User ID
        tier: User tier
        workflow_mode: Workflow mode used
        file_count: Number of files scanned
        scan_data: Full scan data
    """
    try:
        # Increment scan count
        await usage_service.increment_scan_count(
            user_id,
            tier,
            workflow_mode,
            file_count,
            neon_service
        )

        # Record in history
        await usage_service.record_scan(
            user_id,
            scan_data,
            neon_service
        )

        logger.info(f"Recorded scan usage for user {user_id}")

    except Exception as e:
        logger.error(f"Failed to record scan usage: {e}")
        # Don't fail the scan if usage recording fails
