"""
Neon Database Service
Replaces SupabaseService with direct PostgreSQL access via asyncpg.
"""

import os
import secrets
import hashlib
import bcrypt
import asyncpg
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger


class NeonService:
    """Service for Neon PostgreSQL database operations."""

    def __init__(self):
        """Initialize Neon connection pool."""
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            logger.warning("DATABASE_URL not found - database features disabled")
            self.enabled = False
            self.pool = None
        else:
            self.enabled = True
            self.pool = None  # Created on first use
            logger.info("Neon service initialized")

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=2,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("✅ Neon connection pool created successfully")
            except Exception as e:
                logger.error(f"❌ Failed to create Neon connection pool: {e}")
                raise
        return self.pool

    def is_enabled(self) -> bool:
        """Check if database is configured."""
        return self.enabled

    # ==========================================
    # User Management
    # ==========================================

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user with password."""
        if not self.is_enabled():
            raise Exception("Database not configured")

        pool = await self.get_pool()

        # Hash password
        if isinstance(password, str):
            password = password.encode('utf-8')
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                INSERT INTO users (email, password_hash, full_name, tier)
                VALUES ($1, $2, $3, 'none')
                RETURNING id, email, full_name, tier, created_at
                """,
                email, password_hash, full_name
            )

            # Generate API key
            api_key = self.generate_api_key()
            await self.create_api_key(str(user['id']), api_key, "Default API Key")

            logger.info(f"Created user: {email}")

            return {
                "user_id": str(user['id']),
                "email": user['email'],
                "full_name": user['full_name'],
                "tier": user['tier'],
                "api_key": api_key,
                "created_at": user['created_at'].isoformat()
            }

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user with email/password."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )

            if not user or not user['password_hash']:
                return None

            # Verify password
            if isinstance(password, str):
                password = password.encode('utf-8')

            if bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
                return dict(user)

            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            return dict(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )
            return dict(user) if user else None

    async def get_user_by_subscription(
        self,
        subscription_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user by Polar subscription ID."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE polar_subscription_id = $1",
                subscription_id
            )
            return dict(user) if user else None

    async def create_user_from_subscription(
        self,
        email: str,
        polar_customer_id: str,
        polar_subscription_id: str,
        tier: str
    ) -> Dict[str, Any]:
        """Create user from Polar subscription (no password needed)."""
        if not self.is_enabled():
            raise Exception("Database not configured")

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                INSERT INTO users (
                    email,
                    tier,
                    polar_customer_id,
                    polar_subscription_id,
                    subscription_status
                )
                VALUES ($1, $2, $3, $4, 'active')
                RETURNING id, email, tier, created_at
                """,
                email, tier, polar_customer_id, polar_subscription_id
            )

            logger.info(f"Created user from subscription: {email}")

            return dict(user)

    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update user fields."""
        if not self.is_enabled():
            return False

        pool = await self.get_pool()

        # Build SET clause dynamically
        set_parts = []
        values = []
        idx = 1

        for key, value in updates.items():
            set_parts.append(f"{key} = ${idx}")
            values.append(value)
            idx += 1

        values.append(user_id)

        query = f"""
            UPDATE users
            SET {', '.join(set_parts)}
            WHERE id = ${idx}
        """

        async with pool.acquire() as conn:
            result = await conn.execute(query, *values)
            return result == "UPDATE 1"

    async def initialize_usage_tracking(
        self,
        user_id: str,
        tier: str
    ):
        """Initialize usage tracking for new user."""
        # Get tier limits
        from ..services.polar_service import polar_service
        limits = polar_service.get_tier_limits(tier)

        await self.update_user(
            user_id,
            {
                "requests_per_hour": limits.get("api_requests_per_hour", 0),
                "scans_per_month": limits.get("scans_per_month", 0)
            }
        )

    async def increment_user_scans(self, user_id: str):
        """Increment user scan count."""
        if not self.is_enabled():
            return

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users
                SET scans_per_month = scans_per_month + 1
                WHERE id = $1
                """,
                user_id
            )

    # ==========================================
    # API Key Management
    # ==========================================

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return f"alprina_sk_{secrets.token_urlsafe(32)}"

    async def create_api_key(
        self,
        user_id: str,
        api_key: str,
        name: str,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a new API key."""
        if not self.is_enabled():
            raise Exception("Database not configured")

        pool = await self.get_pool()

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_prefix = api_key[:16]  # First 16 chars for display

        async with pool.acquire() as conn:
            key = await conn.fetchrow(
                """
                INSERT INTO api_keys (user_id, key_hash, key_prefix, name, expires_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, name, key_prefix, created_at
                """,
                user_id, key_hash, key_prefix, name, expires_at
            )

            return {
                "id": str(key['id']),
                "name": key['name'],
                "key_prefix": key['key_prefix'],
                "created_at": key['created_at'].isoformat()
            }

    async def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return user."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT u.*, k.id as key_id
                FROM users u
                JOIN api_keys k ON k.user_id = u.id
                WHERE k.key_hash = $1
                  AND k.is_active = true
                  AND (k.expires_at IS NULL OR k.expires_at > NOW())
                """,
                key_hash
            )

            if result:
                # Update last_used_at
                await conn.execute(
                    "UPDATE api_keys SET last_used_at = NOW() WHERE id = $1",
                    result['key_id']
                )

                return dict(result)

            return None

    async def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List user API keys."""
        if not self.is_enabled():
            return []

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            keys = await conn.fetch(
                """
                SELECT id, name, key_prefix, is_active, created_at, last_used_at, expires_at
                FROM api_keys
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                user_id
            )

            return [dict(key) for key in keys]

    async def deactivate_api_key(self, key_id: str, user_id: str) -> bool:
        """Deactivate an API key."""
        if not self.is_enabled():
            return False

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE api_keys
                SET is_active = false
                WHERE id = $1 AND user_id = $2
                """,
                key_id, user_id
            )

            return result == "UPDATE 1"

    # ==========================================
    # Scan Management
    # ==========================================

    async def create_scan(
        self,
        user_id: str,
        scan_type: str,
        workflow_mode: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a new scan."""
        if not self.is_enabled():
            raise Exception("Database not configured")

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            scan = await conn.fetchrow(
                """
                INSERT INTO scans (user_id, scan_type, workflow_mode, metadata)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user_id, scan_type, workflow_mode, metadata or {}
            )

            return str(scan['id'])

    async def save_scan(
        self,
        scan_id: str,
        status: str,
        findings: Optional[Dict] = None,
        findings_count: int = 0,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update scan with results."""
        if not self.is_enabled():
            return False

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE scans
                SET status = $1,
                    findings = $2,
                    findings_count = $3,
                    metadata = $4,
                    completed_at = NOW()
                WHERE id = $5
                """,
                status, findings or {}, findings_count, metadata or {}, scan_id
            )

            return result == "UPDATE 1"

    async def get_scan(
        self,
        scan_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get scan by ID."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            if user_id:
                scan = await conn.fetchrow(
                    "SELECT * FROM scans WHERE id = $1 AND user_id = $2",
                    scan_id, user_id
                )
            else:
                scan = await conn.fetchrow(
                    "SELECT * FROM scans WHERE id = $1",
                    scan_id
                )

            return dict(scan) if scan else None

    async def list_scans(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        scan_type: Optional[str] = None,
        workflow_mode: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List user scans with pagination."""
        if not self.is_enabled():
            return []

        pool = await self.get_pool()

        query = "SELECT * FROM scans WHERE user_id = $1"
        params = [user_id]
        idx = 2

        if scan_type:
            query += f" AND scan_type = ${idx}"
            params.append(scan_type)
            idx += 1

        if workflow_mode:
            query += f" AND workflow_mode = ${idx}"
            params.append(workflow_mode)
            idx += 1

        query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx+1}"
        params.extend([limit, offset])

        async with pool.acquire() as conn:
            scans = await conn.fetch(query, *params)
            return [dict(scan) for scan in scans]

    # ==========================================
    # Rate Limiting & Usage Tracking
    # ==========================================

    async def check_rate_limit(self, user_id: str) -> Dict[str, Any]:
        """Check if user is within rate limits."""
        if not self.is_enabled():
            return {"allowed": True, "remaining": 0}

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            # Get user tier limits
            user = await conn.fetchrow(
                "SELECT tier, requests_per_hour FROM users WHERE id = $1",
                user_id
            )

            if not user:
                return {"allowed": False, "remaining": 0}

            # Count requests in last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM usage_logs
                WHERE user_id = $1 AND created_at > $2
                """,
                user_id, one_hour_ago
            )

            limit = user['requests_per_hour']
            remaining = max(0, limit - count)
            allowed = count < limit

            return {
                "allowed": allowed,
                "remaining": remaining,
                "limit": limit,
                "used": count
            }

    async def log_request(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float
    ):
        """Log API request."""
        if not self.is_enabled():
            return

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO usage_logs (user_id, endpoint, method, status_code, duration_ms)
                VALUES ($1, $2, $3, $4, $5)
                """,
                user_id, endpoint, method, status_code, duration_ms
            )

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        if not self.is_enabled():
            return {}

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )

            if not user:
                return {}

            # Count scans this month
            first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            scans_count = await conn.fetchval(
                "SELECT COUNT(*) FROM scans WHERE user_id = $1 AND created_at >= $2",
                user_id, first_day
            )

            # Count total scans
            total_scans = await conn.fetchval(
                "SELECT COUNT(*) FROM scans WHERE user_id = $1",
                user_id
            )

            # Count vulnerabilities found
            vulns = await conn.fetchval(
                "SELECT COALESCE(SUM(findings_count), 0) FROM scans WHERE user_id = $1",
                user_id
            )

            return {
                "tier": user['tier'],
                "scans_this_month": scans_count,
                "total_scans": total_scans,
                "vulnerabilities_found": vulns,
                "scans_limit": user['scans_per_month'],
                "requests_limit": user['requests_per_hour']
            }

    # ==========================================
    # Webhook Event Logging
    # ==========================================

    async def log_webhook_event(
        self,
        event_type: str,
        event_id: str,
        payload: Dict[str, Any]
    ):
        """Log webhook event."""
        if not self.is_enabled():
            return

        pool = await self.get_pool()

        import json
        payload_json = json.dumps(payload)

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO webhook_events (event_type, event_id, payload)
                VALUES ($1, $2, $3::jsonb)
                ON CONFLICT (event_id) DO NOTHING
                """,
                event_type, event_id, payload_json
            )

    async def mark_webhook_processed(self, event_id: str):
        """Mark webhook as processed."""
        if not self.is_enabled():
            return

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE webhook_events
                SET processed = true, processed_at = NOW()
                WHERE event_id = $1
                """,
                event_id
            )

    async def mark_webhook_error(self, event_id: str, error: str):
        """Mark webhook as errored."""
        if not self.is_enabled():
            return

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE webhook_events
                SET error = $1
                WHERE event_id = $2
                """,
                error, event_id
            )

    # ==========================================
    # Device Authorization (CLI OAuth)
    # ==========================================

    def generate_device_codes(self) -> tuple[str, str]:
        """Generate device and user codes."""
        device_code = secrets.token_urlsafe(32)
        # User code: 4 digits (like GitHub CLI) - easy to type
        user_code = ''.join(secrets.choice('0123456789') for _ in range(4))
        return device_code, user_code

    async def create_device_authorization(self) -> Dict[str, Any]:
        """Create device authorization for CLI."""
        if not self.is_enabled():
            raise Exception("Database not configured")

        pool = await self.get_pool()

        device_code, user_code = self.generate_device_codes()
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        async with pool.acquire() as conn:
            auth = await conn.fetchrow(
                """
                INSERT INTO device_codes (device_code, user_code, expires_at)
                VALUES ($1, $2, $3)
                RETURNING device_code, user_code, expires_at
                """,
                device_code, user_code, expires_at
            )

            return {
                "device_code": auth['device_code'],
                "user_code": auth['user_code'],
                "verification_uri": "https://www.alprina.com/device",
                "expires_in": 900  # 15 minutes
            }

    async def check_device_authorization(
        self,
        device_code: str
    ) -> Optional[Dict[str, Any]]:
        """Check if device has been authorized."""
        if not self.is_enabled():
            return None

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            auth = await conn.fetchrow(
                """
                SELECT * FROM device_codes
                WHERE device_code = $1
                """,
                device_code
            )

            if not auth:
                return None

            # Check if expired
            if auth['expires_at'] < datetime.utcnow():
                return {"status": "expired"}

            # Check if authorized
            if auth['authorized'] and auth['user_id']:
                return {
                    "status": "authorized",
                    "user_id": str(auth['user_id']),
                    "user_code": auth['user_code']
                }

            # Still pending
            return {"status": "pending"}

    async def authorize_device(self, user_code: str, user_id: str) -> bool:
        """Authorize a device."""
        if not self.is_enabled():
            return False

        pool = await self.get_pool()

        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE device_codes
                SET user_id = $1, authorized = true
                WHERE user_code = $2
                  AND expires_at > NOW()
                  AND authorized = false
                """,
                user_id, user_code
            )

            return result == "UPDATE 1"

    # ==========================================
    # Cleanup
    # ==========================================

    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Neon connection pool closed")


# Create singleton instance
neon_service = NeonService()
