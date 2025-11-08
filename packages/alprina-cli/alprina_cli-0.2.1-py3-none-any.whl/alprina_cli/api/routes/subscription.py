"""
Subscription Management - /v1/billing/
Handles subscription operations (cancel, update, etc.)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from ..services.polar_service import polar_service
from ..services.neon_service import neon_service

router = APIRouter()


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel a subscription."""
    subscription_id: str


class CancelSubscriptionResponse(BaseModel):
    """Response after canceling subscription."""
    status: str
    message: str
    subscription_id: str
    ends_at: Optional[str] = None


@router.post("/billing/cancel-subscription", response_model=CancelSubscriptionResponse)
async def cancel_subscription(request: CancelSubscriptionRequest):
    """
    Cancel a user's subscription.

    The subscription will remain active until the end of the current billing period.

    **Request Body:**
    ```json
    {
      "subscription_id": "sub_123..."
    }
    ```

    **Response:**
    ```json
    {
      "status": "canceled",
      "message": "Subscription will end on 2025-11-12",
      "subscription_id": "sub_123...",
      "ends_at": "2025-11-12T13:15:54Z"
    }
    ```
    """
    subscription_id = request.subscription_id

    if not subscription_id:
        raise HTTPException(
            status_code=400,
            detail="Subscription ID is required"
        )

    logger.info(f"Canceling subscription: {subscription_id}")

    try:
        # Cancel via Polar API
        result = await polar_service.cancel_subscription(subscription_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Subscription not found"
            )

        # Get updated subscription info
        subscription = result.get("subscription", {})
        ends_at = subscription.get("current_period_end")

        logger.info(f"Successfully canceled subscription {subscription_id}")

        return CancelSubscriptionResponse(
            status="canceled",
            message=f"Subscription will remain active until {ends_at}",
            subscription_id=subscription_id,
            ends_at=ends_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/billing/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    """
    Get subscription details.

    Returns current subscription status, billing period, and usage info.
    """
    try:
        subscription = await polar_service.get_subscription(subscription_id)

        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="Subscription not found"
            )

        return {
            "status": "success",
            "subscription": subscription
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch subscription: {str(e)}"
        )
