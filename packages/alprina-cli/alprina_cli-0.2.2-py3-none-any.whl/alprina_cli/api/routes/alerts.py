"""
Alerts API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from ...services.alert_service import AlertService
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])
alert_service = AlertService()


class AlertResponse(BaseModel):
    """Alert response model"""
    id: str
    user_id: str
    scan_id: Optional[str]
    alert_type: str
    severity: str
    title: str
    message: str
    metadata: dict
    is_read: bool
    read_at: Optional[str]
    email_sent: bool
    email_sent_at: Optional[str]
    action_url: Optional[str]
    created_at: str
    updated_at: str


class UnreadCountResponse(BaseModel):
    """Unread alert count response"""
    count: int


class MarkReadRequest(BaseModel):
    """Mark alert as read request"""
    alert_id: str


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = 50,
    unread_only: bool = False,
    user: dict = Depends(get_current_user)
):
    """
    Get alerts for the authenticated user

    - **limit**: Maximum number of alerts to return (default: 50)
    - **unread_only**: Only return unread alerts (default: false)
    """
    try:
        alerts = alert_service.get_user_alerts(
            user_id=user['id'],
            limit=limit,
            unread_only=unread_only
        )
        return alerts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(user: dict = Depends(get_current_user)):
    """
    Get count of unread alerts for the authenticated user
    """
    try:
        count = alert_service.get_unread_count(user_id=user['id'])
        return {"count": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching unread count: {str(e)}")


@router.post("/mark-read")
async def mark_alert_read(
    request: MarkReadRequest,
    user: dict = Depends(get_current_user)
):
    """
    Mark a specific alert as read
    """
    try:
        success = alert_service.mark_alert_read(alert_id=request.alert_id)

        if success:
            return {"message": "Alert marked as read", "alert_id": request.alert_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark alert as read")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking alert as read: {str(e)}")


@router.post("/mark-all-read")
async def mark_all_alerts_read(user: dict = Depends(get_current_user)):
    """
    Mark all alerts as read for the authenticated user
    """
    try:
        success = alert_service.mark_all_alerts_read(user_id=user['id'])

        if success:
            return {"message": "All alerts marked as read"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark all alerts as read")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking alerts as read: {str(e)}")


@router.get("/preferences")
async def get_notification_preferences(user: dict = Depends(get_current_user)):
    """
    Get notification preferences for the authenticated user
    """
    try:
        from ...database.neon_service import NeonService
        db = NeonService()

        query = """
            SELECT * FROM user_notification_preferences
            WHERE user_id = %s
        """
        result = db.execute_query(query, (user['id'],))

        if result and len(result) > 0:
            return result[0]
        else:
            # Return default preferences
            return {
                "email_critical_findings": True,
                "email_high_findings": True,
                "email_scan_complete": False,
                "email_scan_failed": True,
                "email_subscription_expiring": True,
                "inapp_critical_findings": True,
                "inapp_high_findings": True,
                "inapp_scan_complete": True,
                "inapp_scan_failed": True,
                "daily_digest_enabled": False,
                "weekly_digest_enabled": True
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")


class UpdatePreferencesRequest(BaseModel):
    """Update notification preferences request"""
    email_critical_findings: Optional[bool] = None
    email_high_findings: Optional[bool] = None
    email_scan_complete: Optional[bool] = None
    email_scan_failed: Optional[bool] = None
    email_subscription_expiring: Optional[bool] = None
    inapp_critical_findings: Optional[bool] = None
    inapp_high_findings: Optional[bool] = None
    inapp_scan_complete: Optional[bool] = None
    inapp_scan_failed: Optional[bool] = None
    daily_digest_enabled: Optional[bool] = None
    weekly_digest_enabled: Optional[bool] = None


@router.put("/preferences")
async def update_notification_preferences(
    request: UpdatePreferencesRequest,
    user: dict = Depends(get_current_user)
):
    """
    Update notification preferences for the authenticated user
    """
    try:
        from ...database.neon_service import NeonService
        db = NeonService()

        # Build update query dynamically based on provided fields
        updates = []
        values = []

        for field, value in request.dict(exclude_none=True).items():
            updates.append(f"{field} = %s")
            values.append(value)

        if not updates:
            raise HTTPException(status_code=400, detail="No preferences to update")

        values.append(user['id'])

        query = f"""
            UPDATE user_notification_preferences
            SET {', '.join(updates)}, updated_at = NOW()
            WHERE user_id = %s
            RETURNING *
        """

        result = db.execute_query(query, tuple(values))

        if result and len(result) > 0:
            return {"message": "Preferences updated successfully", "preferences": result[0]}
        else:
            raise HTTPException(status_code=404, detail="Preferences not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")
