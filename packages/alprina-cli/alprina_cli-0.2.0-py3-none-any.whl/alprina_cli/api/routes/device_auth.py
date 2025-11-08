"""
Device Authorization Flow - OAuth for CLI
Similar to GitHub CLI, Vercel CLI, etc.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..services.neon_service import neon_service
from ..middleware.auth import get_current_user

router = APIRouter()


class DeviceAuthResponse(BaseModel):
    device_code: str
    user_code: str
    verification_url: str
    expires_in: int = 900  # 15 minutes
    interval: int = 5  # Poll every 5 seconds


class DeviceTokenRequest(BaseModel):
    device_code: str


class AuthorizeDeviceRequest(BaseModel):
    user_code: str
    stack_user_id: str | None = None
    email: str | None = None
    full_name: str | None = None


class CLICodeRequest(BaseModel):
    cli_code: str


class DeviceInfo(BaseModel):
    id: str
    name: str
    created_at: datetime
    last_used: Optional[datetime]
    status: str  # active, revoked


@router.post("/auth/device", response_model=DeviceAuthResponse)
async def request_device_authorization():
    """
    Step 1: CLI requests device authorization.

    Returns device_code and user_code.
    CLI will poll /auth/device/token with device_code.
    User will visit verification_url and enter user_code.

    **Example (CLI):**
    ```bash
    curl -X POST http://localhost:8000/v1/auth/device
    ```

    **Response:**
    ```json
    {
      "device_code": "abc123...",
      "user_code": "ABC-DEF",
      "verification_url": "https://www.alprina.com/authorize",
      "expires_in": 900,
      "interval": 5
    }
    ```

    **CLI Flow:**
    1. GET device_code and user_code
    2. Open browser to verification_url
    3. Poll /auth/device/token every 5 seconds
    4. Receive API key when user authorizes
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        auth = await neon_service.create_device_authorization()

        return DeviceAuthResponse(
            device_code=auth["device_code"],
            user_code=auth["user_code"],
            verification_url="https://www.alprina.com/authorize",
            expires_in=900,
            interval=5
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create device authorization: {str(e)}"
        )


@router.post("/auth/device/token")
async def poll_device_authorization(request: DeviceTokenRequest):
    """
    Step 2: CLI polls for authorization status.

    CLI calls this endpoint every 5 seconds with device_code.
    Returns 400 (pending) until user authorizes.
    Returns 200 with API key when authorized.

    **Example (CLI):**
    ```bash
    curl -X POST http://localhost:8000/v1/auth/device/token \\
      -H "Content-Type: application/json" \\
      -d '{"device_code": "abc123..."}'
    ```

    **Response (pending):**
    ```json
    {
      "error": "authorization_pending",
      "message": "User hasn't authorized yet"
    }
    ```

    **Response (authorized):**
    ```json
    {
      "api_key": "alprina_sk_live_...",
      "user": {...}
    }
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        auth = await neon_service.check_device_authorization(request.device_code)

        if not auth:
            raise HTTPException(
                status_code=404,
                detail="Invalid device code"
            )

        if auth["status"] == "expired":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "expired_token",
                    "message": "Device code has expired. Please request a new one."
                }
            )

        if auth["status"] == "pending":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "authorization_pending",
                    "message": "User hasn't authorized yet. Keep polling."
                }
            )

        if auth["status"] == "authorized":
            # Get user and API key
            user_id = auth["user_id"]
            user = await neon_service.get_user_by_id(user_id)

            if not user:
                raise HTTPException(404, "User not found")

            # Always create a new API key for CLI (we can't retrieve existing keys)
            api_key = neon_service.generate_api_key()
            await neon_service.create_api_key(
                user_id=user_id,
                api_key=api_key,
                name="CLI (Device Authorization)",
                expires_days=365  # CLI keys last 1 year
            )

            # Clean up device code (use Neon's pool, not Supabase client)
            pool = await neon_service.get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM device_codes WHERE device_code = $1",
                    request.device_code
                )

            return {
                "api_key": api_key,
                "user": {
                    "id": str(user["id"]),
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "tier": user["tier"]
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check authorization: {str(e)}"
        )


@router.post("/auth/device/authorize")
async def authorize_device(request: AuthorizeDeviceRequest):
    """
    Step 3: User authorizes device from browser.

    User visits /activate page, logs in via Stack Auth, enters user_code.
    This endpoint marks the device as authorized.

    **Two modes:**
    1. With Stack Auth (recommended): Pass stack_user_id, email, full_name
    2. With API key: Use Authorization header (legacy)

    **Example (Stack Auth from web):**
    ```javascript
    fetch('/v1/auth/device/authorize', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        user_code: 'ABCD-1234',
        stack_user_id: 'user_...',
        email: 'user@example.com',
        full_name: 'John Doe'
      })
    })
    ```

    **Response:**
    ```json
    {
      "message": "Device authorized successfully",
      "user_code": "ABCD-1234"
    }
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        # Get or create user from Stack Auth
        if request.stack_user_id:
            # Stack Auth flow
            async with neon_service.pool.acquire() as conn:
                # Check if user exists
                user = await conn.fetchrow(
                    "SELECT id FROM users WHERE stack_user_id = $1",
                    request.stack_user_id
                )

                if not user:
                    # Create new user
                    user = await conn.fetchrow(
                        """
                        INSERT INTO users (stack_user_id, email, full_name, tier)
                        VALUES ($1, $2, $3, 'none')
                        RETURNING id
                        """,
                        request.stack_user_id,
                        request.email,
                        request.full_name
                    )

                user_id = str(user['id'])
        else:
            raise HTTPException(
                status_code=400,
                detail="stack_user_id is required"
            )

        # Authorize the device
        success = await neon_service.authorize_device(
            user_code=request.user_code.upper(),
            user_id=user_id
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Invalid user code or authorization expired"
            )

        return {
            "message": "Device authorized successfully",
            "user_code": request.user_code
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to authorize device: {str(e)}"
        )


@router.post("/auth/dashboard-code")
async def generate_dashboard_code(authorization: str = Header(...)):
    """
    Generate a 6-digit code from the dashboard that users can enter in CLI.

    This is the reverse flow: Dashboard → CLI (instead of CLI → Dashboard).
    Much simpler and more reliable than URL parameters.

    **Example (from dashboard):**
    ```javascript
    fetch('/v1/auth/dashboard-code', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer user_...'
      }
    })
    ```

    **Response:**
    ```json
    {
      "cli_code": "ABC123",
      "expires_in": 900,
      "message": "Enter this code in your CLI: alprina auth login --code ABC123"
    }
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        # Extract Stack user ID from Authorization header
        stack_user_id = authorization.replace("Bearer ", "").strip()

        if not stack_user_id:
            raise HTTPException(
                status_code=401,
                detail="Authorization header required"
            )

        # Get or create user from Stack Auth ID
        async with neon_service.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE stack_user_id = $1",
                stack_user_id
            )

            if not user:
                # Create new user
                user = await conn.fetchrow(
                    """
                    INSERT INTO users (stack_user_id, email, full_name, tier)
                    VALUES ($1, $2, $3, 'none')
                    RETURNING id
                    """,
                    stack_user_id,
                    "dashboard@user.com",  # Placeholder, will be updated
                    "Dashboard User"       # Placeholder, will be updated
                )

            user_id = str(user['id'])

        # Generate a 6-digit alphanumeric code
        import secrets
        import string
        cli_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        # Store the code in device_codes table with special type
        async with neon_service.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO device_codes (device_code, user_code, user_id, status, expires_at, created_at)
                VALUES ($1, $2, $3, 'pending', NOW() + INTERVAL '15 minutes', NOW())
                """,
                f"dashboard_{cli_code}",  # Prefix to identify dashboard codes
                cli_code,
                user_id
            )

        return {
            "cli_code": cli_code,
            "expires_in": 900,  # 15 minutes
            "message": f"Enter this code in your CLI: alprina auth login --code {cli_code}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard code: {str(e)}"
        )


@router.post("/auth/cli-verify")
async def verify_cli_code(request: CLICodeRequest):
    """
    Verify a CLI code entered by the user (reverse flow).

    User gets code from dashboard, enters it in CLI.
    This endpoint verifies the code and returns an API key.

    **Example (CLI):**
    ```bash
    curl -X POST /v1/auth/cli-verify \\
      -H "Content-Type: application/json" \\
      -d '{"cli_code": "ABC123"}'
    ```

    **Response:**
    ```json
    {
      "api_key": "alprina_sk_live_...",
      "user": {
        "id": "123",
        "email": "user@example.com"
      }
    }
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        # Find the dashboard code
        async with neon_service.pool.acquire() as conn:
            code_record = await conn.fetchrow(
                """
                SELECT device_code, user_id, status, expires_at
                FROM device_codes
                WHERE user_code = $1
                AND device_code LIKE 'dashboard_%'
                AND expires_at > NOW()
                """,
                request.cli_code.upper()
            )

            if not code_record:
                raise HTTPException(
                    status_code=404,
                    detail="Invalid or expired CLI code"
                )

            if code_record['status'] == 'used':
                raise HTTPException(
                    status_code=400,
                    detail="CLI code has already been used"
                )

            user_id = code_record['user_id']

            # Mark code as used
            await conn.execute(
                "UPDATE device_codes SET status = 'used' WHERE user_code = $1",
                request.cli_code.upper()
            )

            # Get user details
            user = await conn.fetchrow(
                "SELECT id, email, full_name, tier FROM users WHERE id = $1",
                user_id
            )

            if not user:
                raise HTTPException(404, "User not found")

            # Generate API key
            api_key = neon_service.generate_api_key()
            await neon_service.create_api_key(
                user_id=str(user_id),
                api_key=api_key,
                name="CLI (Dashboard Code)",
                expires_days=365
            )

            return {
                "api_key": api_key,
                "user": {
                    "id": str(user["id"]),
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "tier": user["tier"]
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify CLI code: {str(e)}"
        )


@router.get("/auth/devices", response_model=List[DeviceInfo])
async def list_user_devices(authorization: str = Header(...)):
    """
    List connected CLI devices for the current user.

    Used by the settings dashboard to show authorized devices.
    Expects Stack Auth user ID in Authorization header.

    **Example:**
    ```javascript
    fetch('/v1/auth/devices', {
      headers: {
        'Authorization': 'Bearer user_...'
      }
    })
    ```

    **Response:**
    ```json
    [
      {
        "id": "key_123",
        "name": "CLI (Device Authorization)",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used": "2024-01-01T12:00:00Z",
        "status": "active"
      }
    ]
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        # Extract Stack user ID from Authorization header
        stack_user_id = authorization.replace("Bearer ", "").strip()

        if not stack_user_id:
            raise HTTPException(
                status_code=401,
                detail="Authorization header required"
            )

        # Get user from Stack Auth ID
        async with neon_service.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE stack_user_id = $1",
                stack_user_id
            )

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            user_id = user['id']

            # Get API keys (devices) for this user
            devices = await conn.fetch(
                """
                SELECT id, name, created_at, last_used_at, is_active
                FROM api_keys
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                user_id
            )

            return [
                DeviceInfo(
                    id=str(device['id']),
                    name=device['name'],
                    created_at=device['created_at'],
                    last_used=device['last_used_at'],
                    status="active" if device['is_active'] else "revoked"
                )
                for device in devices
            ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list devices: {str(e)}"
        )
