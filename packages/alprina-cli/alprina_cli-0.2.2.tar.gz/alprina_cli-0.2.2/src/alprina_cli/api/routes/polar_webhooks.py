"""
Polar Webhooks - /v1/webhooks/polar

Handles Polar.sh webhook events for subscription management.
"""

from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..services.polar_service import polar_service
from ..services.neon_service import neon_service

router = APIRouter()


class WebhookResponse(BaseModel):
    """Webhook response model."""
    status: str
    event_type: str
    event_id: str
    processed: bool
    message: str


@router.post("/webhooks/polar", response_model=WebhookResponse)
async def handle_polar_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    polar_signature: Optional[str] = Header(None, alias="Polar-Signature")
):
    """
    Handle Polar.sh webhook events.

    Processes subscription creation, updates, cancellations, and payments.

    **Webhook Events:**
    - `subscription.created` - New subscription created
    - `subscription.updated` - Subscription modified
    - `subscription.cancelled` - Subscription cancelled
    - `payment.succeeded` - Payment successful
    - `payment.failed` - Payment failed

    **Example webhook payload:**
    ```json
    {
      "type": "subscription.created",
      "id": "evt_123...",
      "data": {
        "id": "sub_123...",
        "customer_id": "cus_123...",
        "product_id": "prod_123...",
        "status": "active"
      }
    }
    ```
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    if polar_signature:
        is_valid = polar_service.verify_webhook_signature(
            body,
            polar_signature
        )

        if not is_valid:
            logger.error("Invalid Polar webhook signature")
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )

    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )

    event_type = payload.get("type")
    # Polar sends subscription ID in data.id, not at root level
    event_id = payload.get("id") or payload.get("data", {}).get("id")

    if not event_type:
        raise HTTPException(
            status_code=400,
            detail="Missing event type"
        )

    if not event_id:
        # Use timestamp as fallback ID if no ID provided
        event_id = f"{event_type}_{payload.get('timestamp', datetime.utcnow().isoformat())}"

    logger.info(f"Received Polar webhook: {event_type} ({event_id})")

    # Log webhook event
    if neon_service.is_enabled():
        await neon_service.log_webhook_event(
            event_type=event_type,
            event_id=event_id,
            payload=payload
        )

    # Process webhook in background
    background_tasks.add_task(
        process_webhook_background,
        event_type,
        event_id,
        payload
    )

    return WebhookResponse(
        status="received",
        event_type=event_type,
        event_id=event_id,
        processed=False,
        message="Webhook received and queued for processing"
    )


async def process_webhook_background(
    event_type: str,
    event_id: str,
    payload: Dict[str, Any]
):
    """
    Process webhook event in background.

    Args:
        event_type: Type of webhook event
        event_id: Unique event ID
        payload: Full webhook payload
    """
    try:
        logger.info(f"Processing Polar webhook: {event_type}")

        if event_type == "checkout.completed":
            await handle_checkout_completed(payload)
        elif event_type == "checkout.updated":
            await handle_checkout_updated(payload)
        elif event_type == "subscription.created":
            await handle_subscription_created(payload)
        elif event_type == "subscription.updated":
            await handle_subscription_updated(payload)
        elif event_type in ["subscription.cancelled", "subscription.canceled"]:
            await handle_subscription_cancelled(payload)
        elif event_type == "benefit_grant.revoked":
            await handle_benefit_grant_revoked(payload)
        elif event_type == "benefit_grant.granted":
            await handle_benefit_grant_granted(payload)
        elif event_type == "payment.succeeded":
            await handle_payment_succeeded(payload)
        elif event_type == "payment.failed":
            await handle_payment_failed(payload)
        else:
            logger.warning(f"Unhandled webhook event: {event_type}")

        # Mark as processed
        if neon_service.is_enabled():
            await neon_service.mark_webhook_processed(event_id)

        logger.info(f"Successfully processed webhook: {event_type}")

    except Exception as e:
        logger.error(f"Failed to process webhook {event_type}: {e}")

        # Log error
        if neon_service.is_enabled():
            await neon_service.mark_webhook_error(event_id, str(e))


async def handle_checkout_completed(payload: Dict[str, Any]):
    """
    Handle checkout.completed event.

    This is fired when a checkout is completed, before subscription.created.
    We can log it but the main work happens in subscription.created.
    """
    data = payload.get("data", {})

    customer_email = data.get("customer_email")
    product_name = data.get("product", {}).get("name", "Unknown")

    logger.info(
        f"Checkout completed for {customer_email} - {product_name}"
    )

    # Just log for now - the subscription.created event will do the actual work
    # This prevents 500 errors when checkout.completed is received


async def handle_subscription_created(payload: Dict[str, Any]):
    """
    Handle subscription.created event.

    Creates or updates user with subscription info.
    """
    data = payload.get("data", {})

    subscription_id = data.get("id")
    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    status = data.get("status")

    # Extract customer email from nested customer object
    customer = data.get("customer", {})
    customer_email = customer.get("email")

    if not customer_email:
        logger.error("No customer email in webhook payload!")
        return

    logger.info(
        f"New subscription created: {subscription_id} "
        f"for customer {customer_id} ({customer_email}) "
        f"product: {product_id}"
    )

    # Get tier from product_id (fast, reliable)
    tier = polar_service.get_tier_from_product_id(product_id)

    if tier == "none":
        # Fallback: Use product name from webhook payload (NOT API call)
        product = data.get("product", {})
        product_name = product.get("name", "")

        if product_name:
            tier = polar_service.get_tier_from_product(product_name)
            logger.info(f"Determined tier from product name: {tier} (from '{product_name}')")
        else:
            logger.error(f"Could not determine tier for product_id: {product_id}")
            tier = "developer"  # Safe default

        # Log warning if product_id not in map
        logger.warning(
            f"⚠️ Product ID {product_id} not in PRODUCT_ID_MAP! "
            f"Please add it to polar_service.py. Using tier: {tier}"
        )
    else:
        logger.info(f"Determined tier from product_id: {tier}")

    # Get or create user
    if neon_service.is_enabled():
        user = await neon_service.get_user_by_email(customer_email)

        if user:
            # Update existing user (already signed up with Stack Auth)
            logger.info(f"Found existing user {user['id']} for {customer_email}")

            # Check if this is a Stack Auth user
            has_stack_id = user.get('stack_user_id') is not None
            if has_stack_id:
                logger.info(f"✅ Linking Polar subscription to Stack Auth user: {user['stack_user_id']}")
            else:
                logger.info(f"⚠️ User {user['id']} has no stack_user_id - may be legacy user")

            logger.info(f"Updating user with tier={tier}, status={status}")

            await neon_service.update_user(
                user["id"],
                {
                    "tier": tier,
                    "polar_customer_id": customer_id,
                    "polar_subscription_id": subscription_id,
                    "subscription_status": status,
                    "subscription_started_at": datetime.utcnow().isoformat()
                }
            )
            logger.info(f"✅ Successfully updated user {user['id']} with tier={tier}")

        else:
            # Create new user (purchased without signing up first)
            # This shouldn't normally happen, but handle gracefully
            logger.warning(f"⚠️ No user found for {customer_email} - creating new user from Polar subscription")
            user = await neon_service.create_user_from_subscription(
                email=customer_email,
                polar_customer_id=customer_id,
                polar_subscription_id=subscription_id,
                tier=tier
            )
            logger.info(f"Created new user {user['id']} from Polar subscription (no Stack Auth link)")

        # Initialize usage tracking
        await neon_service.initialize_usage_tracking(
            user["id"],
            tier
        )


async def handle_subscription_updated(payload: Dict[str, Any]):
    """
    Handle subscription.updated event.

    Updates user tier or subscription status.
    """
    data = payload.get("data", {})

    subscription_id = data.get("id")
    status = data.get("status")
    customer = data.get("customer", {})
    customer_email = customer.get("email")
    product_id = data.get("product_id")

    logger.info(f"Subscription updated: {subscription_id}, status: {status}, email: {customer_email}")

    if neon_service.is_enabled() and customer_email:
        # Try to find user by email first (more reliable than subscription ID)
        user = await neon_service.get_user_by_email(customer_email)

        if not user:
            # Fallback: try by subscription ID
            user = await neon_service.get_user_by_subscription(subscription_id)

        if user:
            # Determine tier from product_id
            tier = polar_service.get_tier_from_product_id(product_id)

            await neon_service.update_user(
                user["id"],
                {
                    "tier": tier,
                    "subscription_status": status,
                    "polar_subscription_id": subscription_id,
                    "polar_customer_id": data.get("customer_id")
                }
            )
            logger.info(f"Updated user {user['id']} - tier: {tier}, status: {status}")
        else:
            logger.warning(f"User not found for email: {customer_email}")


async def handle_subscription_cancelled(payload: Dict[str, Any]):
    """
    Handle subscription.cancelled/canceled event.

    Downgrades user to none tier (no free tier).
    """
    data = payload.get("data", {})

    subscription_id = data.get("id")
    cancelled_at = data.get("cancelled_at") or data.get("canceled_at")
    customer = data.get("customer", {})
    customer_email = customer.get("email")

    logger.info(f"Subscription cancelled: {subscription_id}, email: {customer_email}")

    if neon_service.is_enabled() and customer_email:
        # Try to find user by email first
        user = await neon_service.get_user_by_email(customer_email)

        if not user:
            # Fallback to subscription ID
            user = await neon_service.get_user_by_subscription(subscription_id)

        if user:
            await neon_service.update_user(
                user["id"],
                {
                    "tier": "none",  # Changed from "free" to "none"
                    "subscription_status": "canceled",  # Use American spelling
                    "subscription_ends_at": cancelled_at,
                    "scans_per_month": 0,  # Reset limits
                    "requests_per_hour": 0
                }
            )
            logger.info(f"Downgraded user {user['id']} to none tier (subscription canceled)")
        else:
            logger.warning(f"User not found for canceled subscription: {customer_email}")


async def handle_payment_succeeded(payload: Dict[str, Any]):
    """
    Handle payment.succeeded event.

    Ensures subscription is active.
    """
    data = payload.get("data", {})

    subscription_id = data.get("subscription_id")
    amount = data.get("amount")

    logger.info(
        f"Payment succeeded for subscription {subscription_id}: "
        f"${amount/100:.2f}"
    )

    if neon_service.is_enabled():
        user = await neon_service.get_user_by_subscription(subscription_id)

        if user:
            await neon_service.update_user(
                user["id"],
                {
                    "subscription_status": "active"
                }
            )


async def handle_payment_failed(payload: Dict[str, Any]):
    """
    Handle payment.failed event.

    Marks subscription as past_due.
    """
    data = payload.get("data", {})

    subscription_id = data.get("subscription_id")
    error_message = data.get("error", {}).get("message", "Unknown error")

    logger.warning(
        f"Payment failed for subscription {subscription_id}: "
        f"{error_message}"
    )

    if neon_service.is_enabled():
        user = await neon_service.get_user_by_subscription(subscription_id)

        if user:
            await neon_service.update_user(
                user["id"],
                {
                    "subscription_status": "past_due"
                }
            )
            logger.info(f"Marked user {user['id']} subscription as past_due")


async def handle_checkout_updated(payload: Dict[str, Any]):
    """
    Handle checkout.updated event.

    Fired when checkout session is updated (e.g., payment method added).
    We just log it - no action needed.
    """
    data = payload.get("data", {})
    checkout_id = data.get("id")
    status = data.get("status")

    logger.info(f"Checkout updated: {checkout_id} - status: {status}")


async def handle_benefit_grant_granted(payload: Dict[str, Any]):
    """
    Handle benefit_grant.granted event.

    Fired when a benefit (like credits) is granted to a customer.
    We can log it or track credits if needed.
    """
    data = payload.get("data", {})
    customer_email = data.get("customer", {}).get("email")
    benefit_desc = data.get("benefit", {}).get("description")

    logger.info(f"Benefit granted to {customer_email}: {benefit_desc}")


async def handle_benefit_grant_revoked(payload: Dict[str, Any]):
    """
    Handle benefit_grant.revoked event.

    Fired when a benefit is revoked (e.g., subscription cancelled).
    We just log it - the subscription.cancelled event handles the main work.
    """
    data = payload.get("data", {})
    customer_email = data.get("customer", {}).get("email")
    benefit_desc = data.get("benefit", {}).get("description")

    logger.info(f"Benefit revoked from {customer_email}: {benefit_desc}")


@router.post("/webhooks/polar/fix-user-tier")
async def fix_user_tier(email: str, tier: str):
    """
    Manual endpoint to fix user tier in database.

    USE THIS if webhook didn't update tier correctly.

    Args:
        email: User email
        tier: Tier to set (developer, pro, team)

    Example:
        POST /v1/webhooks/polar/fix-user-tier?email=malte@joshwagenbach.com&tier=developer
    """
    if neon_service.is_enabled():
        user = await neon_service.get_user_by_email(email)

        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {email}")

        await neon_service.update_user(
            user["id"],
            {"tier": tier}
        )

        logger.info(f"✅ Manually fixed tier for {email}: {tier}")

        return {
            "status": "success",
            "message": f"Updated {email} to tier={tier}",
            "user_id": user["id"],
            "tier": tier
        }
    else:
        raise HTTPException(status_code=503, detail="Database not configured")


@router.get("/webhooks/polar/test")
async def test_webhook():
    """
    Test endpoint to verify webhook configuration.

    Returns:
        Simple success message
    """
    return {
        "status": "ok",
        "message": "Polar webhook endpoint is configured correctly",
        "endpoint": "/v1/webhooks/polar"
    }
