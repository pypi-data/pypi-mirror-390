"""
Agent-related request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class AgentInfo(BaseModel):
    """Information about a security agent."""

    name: str = Field(..., description="Agent name/ID")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(default=[], description="Agent capabilities")
    supported_languages: Optional[List[str]] = Field(None, description="Supported programming languages")
    category: str = Field(default="core", description="Agent category (core, offensive, defensive, specialized, utility)")
    icon: Optional[str] = Field(None, description="Agent icon emoji for UI display")


class AgentListResponse(BaseModel):
    """Response schema for agent listing."""

    agents: List[AgentInfo] = Field(..., description="List of available agents")
    total: int = Field(..., description="Total number of agents")
    security_engine: str = Field(..., description="Engine status")

    class Config:
        schema_extra = {
            "example": {
                "agents": [
                    {
                        "name": "codeagent",
                        "display_name": "Code Security Agent",
                        "description": "Analyzes source code for vulnerabilities",
                        "capabilities": ["code-audit", "secret-detection"],
                        "supported_languages": ["python", "javascript", "go", "rust"]
                    }
                ],
                "total": 1,
                "security_engine": "active"
            }
        }
