"""
Polar Webhook Handler
Processes subscription lifecycle events from Polar
"""
import os
import hmac
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
import logging
from alprina_cli.api.services.neon_service import NeonService

logger = logging.getLogger(__name__)

class PolarWebhookHandler:
    """Handle Polar webhook events for subscription management"""

    WEBHOOK_SECRET = os.getenv("POLAR_WEBHOOK_SECRET")

    # Polar Product IDs (from your configuration)
    # NOTE: No free plan - all plans include 7-day trial
    PRODUCT_IDS = {
        "developer": "68443920-6061-434f-880d-83d4efd50fde",
        "pro": "fa25e85e-5295-4dd5-bdd9-5cb5cac15a0b",
        "team": "41768ba5-f37d-417d-a10e-fb240b702cb6"
    }

    # Tier configuration (all with 7-day trial)
    TIER_CONFIG = {
        "developer": {"scan_limit": 100, "seats": 1, "price": 29},
        "pro": {"scan_limit": 500, "seats": 1, "price": 49},
        "team": {"scan_limit": 2000, "seats": 5, "price": 99}
    }

    def __init__(self):
        self.neon = NeonService()
        logger.info("Webhook handler initialized with Neon database")

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Polar.

        Args:
            payload: Raw request body
            signature: Signature from X-Polar-Signature header

        Returns:
            True if signature is valid
        """
        if not self.WEBHOOK_SECRET:
            logger.warning("POLAR_WEBHOOK_SECRET not set - skipping verification")
            return True

        expected_signature = hmac.new(
            self.WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def get_tier_from_product_id(self, product_id: str) -> Optional[str]:
        """Get tier name from Polar product ID"""
        for tier, pid in self.PRODUCT_IDS.items():
            if pid == product_id:
                return tier
        return None

    async def log_webhook_event(self, event_type: str, payload: Dict[str, Any], error: Optional[str] = None) -> None:
        """Log webhook event to database"""
        try:
            pool = await self.neon.get_pool()
            event_id = payload.get('id', 'unknown')

            await pool.execute(
                """
                INSERT INTO webhook_events (event_id, event_type, payload, processed, error, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                event_id,
                event_type,
                payload,
                error is None,
                error,
                datetime.utcnow()
            )
            logger.info(f"✅ Logged webhook event: {event_type}")
        except Exception as e:
            logger.error(f"❌ Failed to log webhook event: {str(e)}")

    async def handle_subscription_created(self, data: Dict[str, Any]) -> None:
        """
        Handle subscription.created event.
        Create new subscription record in database.
        """
        pool = await self.neon.get_pool()

        subscription = data.get('data', {})
        product_id = subscription.get('product_id')
        user_email = subscription.get('customer_email') or subscription.get('customer', {}).get('email')
        polar_subscription_id = subscription.get('id')

        if not user_email:
            raise Exception("No customer email in subscription data")

        tier = self.get_tier_from_product_id(product_id)
        if not tier:
            raise Exception(f"Unknown product ID: {product_id}")

        config = self.TIER_CONFIG[tier]

        # Check if subscription already exists
        existing = await pool.fetchrow(
            "SELECT id FROM user_subscriptions WHERE polar_subscription_id = $1",
            polar_subscription_id
        )

        if existing:
            logger.info(f"Subscription {polar_subscription_id} already exists")
            return

        # Find or create user by email
        user = await pool.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            user_email
        )

        if not user:
            # Create user if doesn't exist (from Polar checkout)
            user_id = await pool.fetchval(
                """
                INSERT INTO users (email, tier, scans_per_month, requests_per_hour, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                user_email,
                tier,
                config['scan_limit'],
                100 if tier == 'developer' else 200,
                datetime.utcnow(),
                datetime.utcnow()
            )
            logger.info(f"✅ Created new user {user_email}")
        else:
            user_id = user['id']

            # Update existing user's tier and limits
            await pool.execute(
                """
                UPDATE users
                SET tier = $1, scans_per_month = $2, requests_per_hour = $3, updated_at = $4
                WHERE id = $5
                """,
                tier,
                config['scan_limit'],
                100 if tier == 'developer' else 200,
                datetime.utcnow(),
                user_id
            )
            logger.info(f"✅ Updated user {user_email} to {tier} tier")

        # Create new subscription
        await pool.execute(
            """
            INSERT INTO user_subscriptions (
                user_id, email, polar_subscription_id, polar_product_id,
                tier, status, scan_limit, scans_used, seats_limit, seats_used,
                price_amount, price_currency, current_period_start, current_period_end,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """,
            user_id,
            user_email,
            polar_subscription_id,
            product_id,
            tier,
            'active',
            config['scan_limit'],
            0,  # scans_used
            config['seats'],
            1,  # seats_used
            config['price'],
            'EUR',
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=30),
            datetime.utcnow(),
            datetime.utcnow()
        )

        logger.info(f"✅ Created subscription for {user_email} - {tier} tier")

    async def handle_subscription_updated(self, data: Dict[str, Any]) -> None:
        """
        Handle subscription.updated event.
        Update subscription details (plan changes, etc).
        """
        pool = await self.neon.get_pool()

        subscription = data.get('data', {})
        polar_subscription_id = subscription.get('id')
        product_id = subscription.get('product_id')
        status = subscription.get('status', 'active')

        tier = self.get_tier_from_product_id(product_id)
        if not tier:
            raise Exception(f"Unknown product ID: {product_id}")

        config = self.TIER_CONFIG[tier]

        # Update subscription
        await pool.execute(
            """
            UPDATE user_subscriptions
            SET polar_product_id = $1, tier = $2, status = $3,
                scan_limit = $4, seats_limit = $5, price_amount = $6, updated_at = $7
            WHERE polar_subscription_id = $8
            """,
            product_id,
            tier,
            status,
            config['scan_limit'],
            config['seats'],
            config['price'],
            datetime.utcnow(),
            polar_subscription_id
        )

        logger.info(f"✅ Updated subscription {polar_subscription_id} to {tier} tier")

    async def handle_subscription_canceled(self, data: Dict[str, Any]) -> None:
        """
        Handle subscription.canceled event.
        Mark subscription as canceled.
        """
        pool = await self.neon.get_pool()

        subscription = data.get('data', {})
        polar_subscription_id = subscription.get('id')

        # Update subscription status
        await pool.execute(
            """
            UPDATE user_subscriptions
            SET status = $1, canceled_at = $2, updated_at = $3
            WHERE polar_subscription_id = $4
            """,
            'canceled',
            datetime.utcnow(),
            datetime.utcnow(),
            polar_subscription_id
        )

        logger.info(f"✅ Canceled subscription {polar_subscription_id}")

    async def handle_subscription_revoked(self, data: Dict[str, Any]) -> None:
        """
        Handle subscription.revoked event.
        Revoke access immediately (payment failed, etc).
        """
        pool = await self.neon.get_pool()

        subscription = data.get('data', {})
        polar_subscription_id = subscription.get('id')

        # Update subscription status
        await pool.execute(
            """
            UPDATE user_subscriptions
            SET status = $1, revoked_at = $2, updated_at = $3
            WHERE polar_subscription_id = $4
            """,
            'revoked',
            datetime.utcnow(),
            datetime.utcnow(),
            polar_subscription_id
        )

        logger.info(f"✅ Revoked subscription {polar_subscription_id}")

    async def handle_subscription_renewed(self, data: Dict[str, Any]) -> None:
        """
        Handle subscription billing period renewal.
        Reset usage counters for new billing period.
        """
        pool = await self.neon.get_pool()

        subscription = data.get('data', {})
        polar_subscription_id = subscription.get('id')

        # Reset usage and update period
        await pool.execute(
            """
            UPDATE user_subscriptions
            SET scans_used = $1, current_period_start = $2, current_period_end = $3, updated_at = $4
            WHERE polar_subscription_id = $5
            """,
            0,
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=30),
            datetime.utcnow(),
            polar_subscription_id
        )

        logger.info(f"✅ Renewed subscription {polar_subscription_id} - reset usage counters")

    async def process_webhook(self, request: Request) -> Dict[str, Any]:
        """
        Main webhook processor.

        Args:
            request: FastAPI request object

        Returns:
            Response data

        Raises:
            HTTPException: If signature invalid or processing fails
        """
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get('X-Polar-Signature', '')

        # Verify signature
        if not self.verify_signature(body, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        # Parse JSON
        import json
        payload = json.loads(body)

        event_type = payload.get('type')
        logger.info(f"📥 Received webhook: {event_type}")

        try:
            # Route to appropriate handler
            if event_type == 'subscription.created':
                await self.handle_subscription_created(payload)
            elif event_type == 'subscription.updated':
                await self.handle_subscription_updated(payload)
            elif event_type == 'subscription.canceled':
                await self.handle_subscription_canceled(payload)
            elif event_type == 'subscription.revoked':
                await self.handle_subscription_revoked(payload)
            elif event_type == 'subscription.renewed':
                await self.handle_subscription_renewed(payload)
            else:
                logger.warning(f"Unhandled event type: {event_type}")

            # Log successful processing
            await self.log_webhook_event(event_type, payload)

            return {"status": "success", "event": event_type}

        except Exception as e:
            logger.error(f"Failed to process webhook: {str(e)}")
            await self.log_webhook_event(event_type, payload, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
