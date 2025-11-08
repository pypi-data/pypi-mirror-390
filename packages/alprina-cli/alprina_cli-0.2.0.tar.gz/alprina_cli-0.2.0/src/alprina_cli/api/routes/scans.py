"""
Scan management endpoints - /v1/scans/*
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..services.neon_service import neon_service
from ..middleware.auth import get_current_user

router = APIRouter()


# Request/Response Models
class CreateScanRequest(BaseModel):
    target: str = Field(..., description="Scan target (path, URL, etc.)")
    scan_type: str = Field(..., description="'local' or 'remote'")
    profile: str = Field(default="default", description="Scan profile name")

    class Config:
        schema_extra = {
            "example": {
                "target": "./src",
                "scan_type": "local",
                "profile": "code-audit"
            }
        }


class UpdateScanRequest(BaseModel):
    results: Dict[str, Any] = Field(..., description="Scan results data")

    class Config:
        schema_extra = {
            "example": {
                "results": {
                    "findings": [
                        {
                            "severity": "HIGH",
                            "title": "SQL Injection vulnerability",
                            "description": "User input not sanitized"
                        }
                    ],
                    "summary": {
                        "critical": 0,
                        "high": 1,
                        "medium": 2,
                        "low": 3,
                        "info": 0
                    }
                }
            }
        }


@router.post("/scans", status_code=201)
async def create_scan(
    request: CreateScanRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new scan entry (before execution).

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/v1/scans \\
      -H "Authorization: Bearer alprina_sk_live_..." \\
      -H "Content-Type: application/json" \\
      -d '{
        "target": "./src",
        "scan_type": "local",
        "profile": "code-audit"
      }'
    ```

    **Response:**
    ```json
    {
      "scan_id": "uuid-here",
      "status": "running",
      "created_at": "2025-11-03T18:00:00Z"
    }
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        scan = await neon_service.create_scan(
            user_id=user["id"],
            target=request.target,
            scan_type=request.scan_type,
            profile=request.profile
        )

        return {
            "scan_id": scan["id"],
            "status": scan["status"],
            "created_at": scan["created_at"],
            "message": "Scan created successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create scan: {str(e)}"
        )


@router.patch("/scans/{scan_id}")
async def update_scan(
    scan_id: str,
    request: UpdateScanRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update scan with results after completion.

    **Example:**
    ```bash
    curl -X PATCH http://localhost:8000/v1/scans/{scan_id} \\
      -H "Authorization: Bearer alprina_sk_live_..." \\
      -H "Content-Type: application/json" \\
      -d '{
        "results": {
          "findings": [...],
          "summary": {...}
        }
      }'
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    # Verify scan belongs to user
    existing_scan = await neon_service.get_scan(scan_id, user["id"])
    if not existing_scan:
        raise HTTPException(404, "Scan not found")

    try:
        updated_scan = await neon_service.save_scan(
            scan_id=scan_id,
            results=request.results
        )

        return {
            "scan_id": scan_id,
            "status": updated_scan.get("status", "completed"),
            "findings_count": updated_scan.get("findings_count", 0),
            "message": "Scan updated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update scan: {str(e)}"
        )


@router.get("/scans")
async def list_scans(
    user: Dict[str, Any] = Depends(get_current_user),
    page: int = 1,
    limit: int = 20,
    severity: Optional[str] = None
):
    """
    List all scans for current user with pagination.

    **Example:**
    ```bash
    curl http://localhost:8000/v1/scans?page=1&limit=20 \\
      -H "Authorization: Bearer alprina_sk_live_..."
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    try:
        result = await neon_service.list_scans(
            user_id=user["id"],
            page=page,
            limit=limit,
            severity=severity
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list scans: {str(e)}"
        )


@router.get("/scans/{scan_id}")
async def get_scan(
    scan_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed scan results by ID.

    **Example:**
    ```bash
    curl http://localhost:8000/v1/scans/{scan_id} \\
      -H "Authorization: Bearer alprina_sk_live_..."
    ```
    """
    if not neon_service.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )

    scan = await neon_service.get_scan(scan_id, user["id"])

    if not scan:
        raise HTTPException(404, "Scan not found")

    return scan
