"""
Authentication endpoints - /v1/auth/*

Active endpoints for Stack Auth + Neon DB integration.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any
from loguru import logger

from ..services.neon_service import neon_service
from ..middleware.auth import get_current_user

router = APIRouter()


# Request/Response Models
class CreateAPIKeyRequest(BaseModel):
    name: str = Field(default="API Key", description="Name for the API key")
    expires_days: int | None = Field(default=None, description="Expiration in days (optional)")


@router.get("/auth/me")
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information.

    Requires authentication via API key.

    **Example:**
    ```bash
    curl https://api.alprina.com/v1/auth/me \\
      -H "Authorization: Bearer alprina_sk_..."
    ```
    """
    # Get usage stats
    stats = await neon_service.get_user_stats(user["id"])

    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "tier": user["tier"],
            "created_at": user["created_at"]
        },
        "usage": stats
    }


@router.get("/auth/api-keys")
async def list_api_keys(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all API keys for current user.

    **Example:**
    ```bash
    curl https://api.alprina.com/v1/auth/api-keys \\
      -H "Authorization: Bearer alprina_sk_..."
    ```
    """
    api_keys = await neon_service.list_api_keys(user["id"])

    return {
        "api_keys": api_keys,
        "total": len(api_keys)
    }


@router.post("/auth/api-keys", status_code=201)
async def create_api_key(
    request: CreateAPIKeyRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new API key.

    **Example:**
    ```bash
    curl -X POST https://api.alprina.com/v1/auth/api-keys \\
      -H "Authorization: Bearer alprina_sk_..." \\
      -H "Content-Type: application/json" \\
      -d '{"name": "Production API Key", "expires_days": 365}'
    ```

    **Response:**
    - Returns the NEW API key
    - Save it - it won't be shown again!
    """
    # Generate new key
    api_key = neon_service.generate_api_key()

    # Store in database
    key_data = await neon_service.create_api_key(
        user_id=user["id"],
        api_key=api_key,
        name=request.name,
        expires_days=request.expires_days
    )

    return {
        "api_key": api_key,
        "key_info": {
            "id": key_data["id"],
            "name": key_data["name"],
            "key_prefix": key_data["key_prefix"],
            "created_at": key_data["created_at"],
            "expires_at": key_data["expires_at"]
        },
        "message": "API key created successfully. Save it securely - it won't be shown again!"
    }


@router.delete("/auth/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Revoke (deactivate) an API key.

    **Example:**
    ```bash
    curl -X DELETE https://api.alprina.com/v1/auth/api-keys/{key_id} \\
      -H "Authorization: Bearer alprina_sk_..."
    ```
    """
    success = await neon_service.deactivate_api_key(key_id, user["id"])

    if not success:
        raise HTTPException(404, "API key not found")

    return {
        "message": "API key revoked successfully",
        "key_id": key_id
    }


# ============================================
# OAuth User Sync (GitHub, Google, etc.)
# ============================================

class SyncOAuthUserRequest(BaseModel):
    """Request to sync an OAuth user to backend database."""
    user_id: str = Field(..., description="OAuth provider user ID")
    email: EmailStr
    full_name: str | None = None
    provider: str = Field(default="github", description="OAuth provider (github, google, etc.)")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "provider": "github"
            }
        }


@router.post("/auth/sync-oauth-user", status_code=201)
async def sync_oauth_user(request: SyncOAuthUserRequest):
    """
    Sync an OAuth user to Neon database.

    This endpoint is called after a user signs up via GitHub/Google OAuth
    to create their profile in the backend database and generate an API key.

    **Flow:**
    1. User signs in with GitHub OAuth → Creates user record
    2. Frontend calls this endpoint to sync to Neon DB
    3. Backend creates API key for the user
    4. User can now use the platform

    **Example:**
    ```bash
    curl -X POST https://api.alprina.com/v1/auth/sync-oauth-user \\
      -H "Content-Type: application/json" \\
      -d '{
        "user_id": "oauth-user-uuid",
        "email": "user@example.com",
        "full_name": "John Doe",
        "provider": "github"
      }'
    ```

    **Response:**
    - Returns user info and API key
    - If user already exists, returns existing data
    """
    if not neon_service.is_enabled():
        raise HTTPException(503, "Database not configured")

    try:
        # Check if user already exists in public.users
        existing_user = await neon_service.get_user_by_id(request.user_id)

        if existing_user:
            # User already synced, just get their API keys
            api_keys = await neon_service.list_api_keys(request.user_id)

            # Get or create a session key
            if not api_keys:
                session_key = neon_service.generate_api_key()
                await neon_service.create_api_key(
                    user_id=request.user_id,
                    api_key=session_key,
                    name="OAuth Session"
                )
            else:
                session_key = None  # We don't store full keys, only prefixes

            return {
                "user_id": existing_user["id"],
                "email": existing_user["email"],
                "full_name": existing_user.get("full_name"),
                "tier": existing_user.get("tier", "free"),
                "api_key": session_key,  # Will be None if keys already exist
                "message": "User already exists",
                "is_new": False
            }

        # Create new user in public.users
        # NOTE: No free tier - user must choose a plan
        user_data = {
            "id": request.user_id,  # Use same ID as OAuth provider
            "email": request.email,
            "full_name": request.full_name,
            "tier": "none",            # No plan selected yet
            "requests_per_hour": 0,    # Must subscribe to use
            "scans_per_month": 0       # Must subscribe to use
        }

        response = neon_service.client.table("users").insert(user_data).execute()
        user = response.data[0] if response.data else user_data

        # Generate API key for CLI/API use
        api_key = neon_service.generate_api_key()
        await neon_service.create_api_key(
            user_id=request.user_id,
            api_key=api_key,
            name=f"{request.provider.title()} OAuth"
        )

        logger.info(f"Synced OAuth user to backend: {request.email} (provider: {request.provider})")

        return {
            "user_id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "tier": user.get("tier", "free"),
            "api_key": api_key,
            "message": "OAuth user synced successfully",
            "is_new": True
        }

    except Exception as e:
        logger.error(f"Failed to sync OAuth user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync OAuth user: {str(e)}"
        )


# ============================================
# Stack Auth User Sync
# ============================================

class SyncStackUserRequest(BaseModel):
    """Request to sync a Stack Auth user to backend database."""
    stack_user_id: str = Field(..., description="Stack Auth user ID")
    email: EmailStr
    full_name: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "stack_user_id": "stack_user_123abc",
                "email": "user@example.com",
                "full_name": "John Doe"
            }
        }


@router.post("/auth/sync-stack-user", status_code=201)
async def sync_stack_user(request: SyncStackUserRequest):
    """
    Sync a Stack Auth user to Neon database.

    This endpoint is called after a user signs in via Stack Auth
    to create their profile in the backend database and generate an API key.

    **Flow:**
    1. User signs in with Stack Auth → Stack creates user record
    2. Frontend calls this endpoint to sync to Neon DB
    3. Backend creates/updates user and API key
    4. User can now use the platform

    **Example:**
    ```bash
    curl -X POST https://api.alprina.com/v1/auth/sync-stack-user \\
      -H "Content-Type: application/json" \\
      -d '{
        "stack_user_id": "stack_user_123abc",
        "email": "user@example.com",
        "full_name": "John Doe"
      }'
    ```

    **Response:**
    - Returns user info and API key
    - If user already exists, returns existing data
    """
    if not neon_service.is_enabled():
        raise HTTPException(503, "Database not configured")

    try:
        # Check if user already exists by stack_user_id
        pool = await neon_service.get_pool()
        async with pool.acquire() as conn:
            existing_user = await conn.fetchrow(
                "SELECT * FROM users WHERE stack_user_id = $1",
                request.stack_user_id
            )

            if existing_user:
                # User already synced - check if they have an active session key
                existing_keys = await conn.fetch(
                    """
                    SELECT key_hash, key_prefix FROM api_keys
                    WHERE user_id = $1
                      AND is_active = true
                      AND name = 'Stack Auth Web Session'
                      AND (expires_at IS NULL OR expires_at > NOW())
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    existing_user['id']
                )

                # If they have an active session key, don't return it (we can't retrieve the full key)
                # Frontend should use the key already in localStorage
                # Only create a new key if they have no active session keys at all
                if existing_keys:
                    logger.info(f"Stack user already exists with active session: {request.email}")
                    return {
                        "user_id": str(existing_user["id"]),
                        "email": existing_user["email"],
                        "full_name": existing_user.get("full_name"),
                        "tier": existing_user.get("tier", "none"),
                        "api_key": None,  # Don't create new key - use existing from localStorage
                        "message": "User already has active session",
                        "is_new": False
                    }
                else:
                    # No active session key - create one (first login or all keys revoked)
                    session_key = neon_service.generate_api_key()
                    await neon_service.create_api_key(
                        user_id=str(existing_user['id']),
                        api_key=session_key,
                        name="Stack Auth Web Session"
                    )

                    logger.info(f"Created new session key for existing user: {request.email}")

                    return {
                        "user_id": str(existing_user["id"]),
                        "email": existing_user["email"],
                        "full_name": existing_user.get("full_name"),
                        "tier": existing_user.get("tier", "none"),
                        "api_key": session_key,
                        "message": "New session created",
                        "is_new": False
                    }

            # Check if user exists by email (migration case)
            existing_by_email = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                request.email
            )

            if existing_by_email:
                # Update existing user with stack_user_id
                await conn.execute(
                    "UPDATE users SET stack_user_id = $1 WHERE email = $2",
                    request.stack_user_id,
                    request.email
                )

                # Create a fresh session key for web use
                session_key = neon_service.generate_api_key()
                await neon_service.create_api_key(
                    user_id=str(existing_by_email['id']),
                    api_key=session_key,
                    name="Stack Auth Web Session"
                )

                logger.info(f"Linked existing user to Stack Auth: {request.email}")

                return {
                    "user_id": str(existing_by_email["id"]),
                    "email": existing_by_email["email"],
                    "full_name": existing_by_email.get("full_name"),
                    "tier": existing_by_email.get("tier", "none"),
                    "api_key": session_key,
                    "message": "Existing user linked to Stack Auth",
                    "is_new": False
                }

            # Create new user in Neon DB
            new_user = await conn.fetchrow(
                """
                INSERT INTO users (email, full_name, stack_user_id, tier)
                VALUES ($1, $2, $3, 'none')
                RETURNING id, email, full_name, tier, created_at
                """,
                request.email,
                request.full_name,
                request.stack_user_id
            )

            # Generate API key for CLI/API use
            api_key = neon_service.generate_api_key()
            await neon_service.create_api_key(
                user_id=str(new_user['id']),
                api_key=api_key,
                name="Stack Auth"
            )

            logger.info(f"Created new Stack Auth user: {request.email}")

            return {
                "user_id": str(new_user["id"]),
                "email": new_user["email"],
                "full_name": new_user.get("full_name"),
                "tier": new_user.get("tier", "none"),
                "api_key": api_key,
                "message": "Stack Auth user synced successfully",
                "is_new": True
            }

    except Exception as e:
        logger.error(f"Failed to sync Stack Auth user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync Stack Auth user: {str(e)}"
        )
