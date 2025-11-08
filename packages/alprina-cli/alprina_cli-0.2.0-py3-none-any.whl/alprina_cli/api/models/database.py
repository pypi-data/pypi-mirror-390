"""
Database Models for Alprina
SQLAlchemy models for users, usage tracking, and billing.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    password_hash = Column(String, nullable=False)

    # Billing info
    tier = Column(String, default="free", nullable=False)  # free, developer, pro, enterprise
    polar_customer_id = Column(String, unique=True, index=True)
    polar_subscription_id = Column(String, unique=True, index=True)
    subscription_status = Column(String, default="inactive")  # active, inactive, cancelled, past_due
    subscription_started_at = Column(DateTime)
    subscription_ends_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    usage_records = relationship("UsageTracking", back_populates="user")
    scan_history = relationship("ScanHistory", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class UsageTracking(Base):
    """Monthly usage tracking per user."""
    __tablename__ = "usage_tracking"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    month = Column(String, nullable=False, index=True)  # Format: 'YYYY-MM'

    # Scan usage
    scans_count = Column(Integer, default=0, nullable=False)
    scans_limit = Column(Integer)  # NULL for unlimited
    files_scanned_total = Column(Integer, default=0)
    reports_generated = Column(Integer, default=0)

    # API usage
    api_calls_count = Column(Integer, default=0, nullable=False)
    api_calls_limit = Column(Integer)  # NULL for unlimited

    # Workflow usage
    parallel_scans_count = Column(Integer, default=0)
    sequential_scans_count = Column(Integer, default=0)
    coordinated_chains_count = Column(Integer, default=0)

    # Reset tracking
    last_reset_at = Column(DateTime, default=datetime.utcnow)
    next_reset_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_records")


class ScanHistory(Base):
    """Individual scan records."""
    __tablename__ = "scan_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Scan details
    scan_type = Column(String, nullable=False)  # code, web, network, etc.
    agent_used = Column(String, nullable=False)
    target = Column(Text)

    # Results
    files_count = Column(Integer, default=0)
    findings_count = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)

    # Execution details
    workflow_mode = Column(String)  # single, parallel, sequential, coordinated
    duration_seconds = Column(Float)
    status = Column(String, default="completed")  # completed, failed, timeout

    # Report info
    report_path = Column(Text)
    report_format = Column(String)  # html, pdf, markdown

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="scan_history")


class APIKey(Base):
    """API keys for user authentication."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Key details
    name = Column(String, default="API Key")
    key_hash = Column(String, nullable=False, unique=True, index=True)
    key_prefix = Column(String, nullable=False)  # First 12 chars for display

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime)

    # Expiration
    expires_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class PolarWebhook(Base):
    """Polar webhook event log."""
    __tablename__ = "polar_webhooks"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Event details
    event_type = Column(String, nullable=False, index=True)
    polar_event_id = Column(String, unique=True, index=True)

    # Payload
    payload = Column(JSON, nullable=False)

    # Processing
    processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime)
    error_message = Column(Text)

    # Customer info
    polar_customer_id = Column(String, index=True)
    polar_subscription_id = Column(String, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<PolarWebhook {self.event_type} {self.polar_event_id}>"
