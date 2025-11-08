"""
Insights API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from ...services.insights_service import InsightsService
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/insights", tags=["insights"])
insights_service = InsightsService()


class WeeklySummaryResponse(BaseModel):
    """Weekly summary response model"""
    critical_findings: int
    high_findings: int
    total_scans: int
    total_vulnerabilities: int
    period: str


class MostScannedTargetResponse(BaseModel):
    """Most scanned target response model"""
    target: Optional[str]
    scan_count: Optional[int]


class SecurityTrendResponse(BaseModel):
    """Security trend response model"""
    trend: str  # improving, declining, stable
    direction: str  # up, down, none
    change_percentage: int
    message: str
    current_score: Optional[int] = None
    previous_score: Optional[int] = None


class RecommendationResponse(BaseModel):
    """Recommendation response model"""
    priority: str  # critical, high, medium, low, info
    title: str
    description: str
    action: str
    action_url: str


class VulnerableTargetResponse(BaseModel):
    """Vulnerable target response model"""
    target: str
    critical: int
    high: int
    medium: int
    low: int
    total_vulnerabilities: int
    scan_count: int
    last_scan: Optional[str]


@router.get("/summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(user: dict = Depends(get_current_user)):
    """
    Get weekly security summary for the authenticated user

    Returns statistics for the last 7 days including:
    - Critical findings count
    - High severity findings count
    - Total scans performed
    - Total vulnerabilities found
    """
    try:
        summary = insights_service.get_weekly_summary(user_id=user['id'])
        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weekly summary: {str(e)}")


@router.get("/most-scanned", response_model=MostScannedTargetResponse)
async def get_most_scanned_target(
    days: int = 30,
    user: dict = Depends(get_current_user)
):
    """
    Get the most frequently scanned target

    - **days**: Number of days to look back (default: 30)
    """
    try:
        result = insights_service.get_most_scanned_target(user_id=user['id'], days=days)

        if result is None:
            return {"target": None, "scan_count": None}

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching most scanned target: {str(e)}")


@router.get("/trend", response_model=SecurityTrendResponse)
async def get_security_trend(user: dict = Depends(get_current_user)):
    """
    Get security trend analysis

    Compares current week vs previous week to determine if security posture
    is improving, declining, or stable.
    """
    try:
        trend = insights_service.get_security_trend(user_id=user['id'])
        return trend

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating security trend: {str(e)}")


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(user: dict = Depends(get_current_user)):
    """
    Get personalized security recommendations

    Returns actionable recommendations based on scan history,
    vulnerability patterns, and security posture.
    """
    try:
        recommendations = insights_service.get_recommendations(user_id=user['id'])
        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.get("/vulnerable-targets", response_model=List[VulnerableTargetResponse])
async def get_vulnerable_targets(
    limit: int = 5,
    user: dict = Depends(get_current_user)
):
    """
    Get targets with the most vulnerabilities

    - **limit**: Number of targets to return (default: 5)

    Returns targets sorted by severity-weighted vulnerability count.
    """
    try:
        targets = insights_service.get_top_vulnerable_targets(user_id=user['id'], limit=limit)
        return targets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vulnerable targets: {str(e)}")
