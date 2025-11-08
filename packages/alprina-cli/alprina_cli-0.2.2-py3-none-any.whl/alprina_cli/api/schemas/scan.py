"""
Scan-related request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CodeScanRequest(BaseModel):
    """Request schema for code scanning."""

    code: str = Field(..., description="Source code to scan", min_length=1)
    language: str = Field(default="python", description="Programming language")
    profile: str = Field(
        default="code-audit",
        description="Scan profile to use",
        pattern="^(code-audit|secret-detection|config-audit|web-recon)$"
    )
    safe_only: bool = Field(default=True, description="Only run safe, non-intrusive checks")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    class Config:
        schema_extra = {
            "example": {
                "code": "def login(user, pwd):\\n    query = f\\\"SELECT * FROM users WHERE user='{user}'\\\"",
                "language": "python",
                "profile": "code-audit",
                "safe_only": True
            }
        }


class Finding(BaseModel):
    """Individual security finding."""

    id: Optional[str] = Field(None, description="Finding ID")
    severity: str = Field(..., description="Severity level")
    type: str = Field(..., description="Vulnerability type")
    title: str = Field(..., description="Finding title")
    description: str = Field(..., description="Detailed description")
    location: Optional[str] = Field(None, description="Location in code")
    line: Optional[int] = Field(None, description="Line number")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")


class ScanSummary(BaseModel):
    """Summary of scan results."""

    total_findings: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class TargetScanRequest(BaseModel):
    """Generic request schema for target-based scanning (file paths, URLs, systems)."""

    target: str = Field(..., description="Target to scan (file path, URL, IP, etc.)", min_length=1)
    safe_only: bool = Field(default=True, description="Only run safe, non-intrusive checks")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    class Config:
        schema_extra = {
            "example": {
                "target": "/path/to/app",
                "safe_only": True,
                "metadata": {"depth": "comprehensive"}
            }
        }


class ScanResponse(BaseModel):
    """Response schema for scan results."""

    scan_id: str = Field(..., description="Unique scan identifier")
    status: str = Field(..., description="Scan status")
    scanned_by: str = Field(default="Alprina Security Engine")
    alprina_engine: str = Field(..., description="Engine status (active/fallback)")
    findings: List[Finding] = Field(default=[], description="List of findings")
    summary: ScanSummary = Field(..., description="Scan summary")
    duration_ms: Optional[int] = Field(None, description="Scan duration in milliseconds")

    class Config:
        schema_extra = {
            "example": {
                "scan_id": "scan_abc123",
                "status": "completed",
                "scanned_by": "Alprina Security Engine",
                "alprina_engine": "active",
                "findings": [
                    {
                        "id": "finding_1",
                        "severity": "HIGH",
                        "type": "SQL Injection",
                        "title": "SQL injection vulnerability detected",
                        "description": "User input directly interpolated into SQL query",
                        "location": "login.py:5",
                        "line": 5,
                        "confidence": 0.95
                    }
                ],
                "summary": {
                    "total_findings": 1,
                    "high": 1,
                    "medium": 0,
                    "low": 0
                }
            }
        }
