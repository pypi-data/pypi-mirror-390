"""
Authentication middleware for Alprina API.
Handles API key verification and user authentication.
"""

from fastapi import Header, HTTPException, Depends
from typing import Optional, Dict, Any
from loguru import logger

from ..services.neon_service import neon_service


async def verify_api_key(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Verify authentication from Authorization header.

    Supports both:
    - JWT tokens (web/mobile users)
    - API keys (CLI users)

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        User dict if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_authorization",
                "message": "Authorization header is required",
                "hint": "Include header: Authorization: Bearer <token>"
            }
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_authorization_format",
                "message": "Authorization header must be: Bearer <token>"
            }
        )

    token = parts[1]

    # NOTE: For Stack Auth JWT tokens, we don't verify them here because:
    # 1. Stack Auth handles JWT verification on the frontend
    # 2. Users are synced to Neon DB via /v1/auth/sync-stack-user endpoint
    # 3. The frontend should use API keys (not JWT) for backend API calls
    #
    # Only API keys (starting with alprina_sk_) are supported for backend authentication

    # Try API key (CLI users and web dashboard)
    if token.startswith("alprina_sk_"):
        user = await neon_service.verify_api_key(token)

        if user:
            # Check rate limits
            rate_limit = await neon_service.check_rate_limit(user["id"])

            if not rate_limit["allowed"]:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": rate_limit.get("reason", "Rate limit exceeded"),
                        "limit": rate_limit.get("limit"),
                        "used": rate_limit.get("used"),
                        "hint": "Upgrade to Pro for higher limits"
                    }
                )

            user["auth_type"] = "api_key"
            logger.info(f"User authenticated via API key: {user['email']} (ID: {user['id']})")
            return user
        else:
            logger.warning(f"Invalid API key attempted: {token[:20]}...")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_api_key",
                    "message": "API key is invalid or has been revoked",
                    "hint": "Check your API key at /v1/auth/api-keys"
                }
            )

    # Neither JWT nor API key worked
    raise HTTPException(
        status_code=401,
        detail={
            "error": "invalid_credentials",
            "message": "Invalid authentication token",
            "hint": "Use a valid JWT token or API key"
        }
    )


async def get_current_user(user: Dict[str, Any] = Depends(verify_api_key)) -> Dict[str, Any]:
    """
    Get current authenticated user.
    Convenience dependency that wraps verify_api_key.
    """
    return user


# Optional: Public endpoint (no auth required)
async def optional_auth(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Optional authentication.
    Returns user if authenticated, None if not.
    Used for endpoints that work with or without auth.
    """
    if not authorization:
        return None

    try:
        return await verify_api_key(authorization)
    except HTTPException:
        return None
