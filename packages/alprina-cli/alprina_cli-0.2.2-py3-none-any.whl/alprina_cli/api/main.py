"""
Alprina API - Main Application
FastAPI-based REST API for security scanning.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os
from pathlib import Path

# Add parent directory to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..security_engine import run_agent, run_local_scan, AGENTS_AVAILABLE
from ..agent_bridge import SecurityAgentBridge

# Initialize FastAPI app
app = FastAPI(
    title="Alprina API",
    description="AI-powered security scanning and vulnerability detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - allow all origins in development, specific origins in production
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS == "*":
    origins = ["*"]
else:
    # Split comma-separated origins
    origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import route modules
from .routes import scan, agents, auth, scans, device_auth, polar_webhooks, billing, subscription, alerts, insights

# Import services for startup/shutdown
from .services.neon_service import neon_service

# Include routers
app.include_router(scan.router, prefix="/v1", tags=["Scanning"])
app.include_router(agents.router, prefix="/v1", tags=["Agents"])
app.include_router(auth.router, prefix="/v1", tags=["Authentication"])
app.include_router(scans.router, prefix="/v1", tags=["Scan Management"])
app.include_router(device_auth.router, prefix="/v1", tags=["Device Authorization"])
app.include_router(polar_webhooks.router, prefix="/v1", tags=["Billing & Webhooks"])
app.include_router(billing.router, tags=["Billing"])
app.include_router(subscription.router, prefix="/v1", tags=["Subscription Management"])
app.include_router(alerts.router, prefix="/v1", tags=["Alerts & Notifications"])
app.include_router(insights.router, prefix="/v1", tags=["Security Insights"])


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    from loguru import logger
    logger.info("🚀 Starting Alprina API...")

    # Initialize Neon connection pool
    if neon_service.is_enabled():
        try:
            await neon_service.get_pool()
            logger.info("✅ Neon connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Neon connection pool: {e}")
    else:
        logger.warning("⚠️ Neon service not enabled (DATABASE_URL not set)")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    from loguru import logger
    logger.info("🛑 Shutting down Alprina API...")

    # Close Neon connection pool
    if neon_service.is_enabled():
        await neon_service.close()
        logger.info("✅ Neon connection pool closed")


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Alprina API",
        "version": "1.0.0",
        "description": "AI-powered security scanning",
        "docs": "/docs",
        "security_engine": "active" if AGENTS_AVAILABLE else "fallback",
        "endpoints": {
            "scan_code": "POST /v1/scan/code",
            "list_agents": "GET /v1/agents",
            "register": "POST /v1/auth/register",
            "login": "POST /v1/auth/login",
            "documentation": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "security_engine": "active" if AGENTS_AVAILABLE else "fallback",
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "documentation_url": "https://docs.alprina.com/errors"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "server_error",
                "message": "An internal server error occurred",
                "documentation_url": "https://docs.alprina.com/errors/server_error"
            }
        }
    )


# Production server configuration
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "alprina_cli.api.main:app",
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=600,  # 10 minutes for long-running AI scans
        timeout_notify=570,       # Notify client at 9.5 minutes
        reload=False,             # Disable reload in production
    )
