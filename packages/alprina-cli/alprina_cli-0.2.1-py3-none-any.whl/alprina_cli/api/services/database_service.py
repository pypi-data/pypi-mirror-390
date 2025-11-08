"""
Database Service for SQLAlchemy Operations
Handles direct database access for usage tracking and Polar integration.
"""

import os
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from loguru import logger

from ..models.database import Base, User, UsageTracking, ScanHistory, APIKey, PolarWebhook


class DatabaseService:
    """Service for SQLAlchemy database operations."""
    
    def __init__(self):
        """Initialize database connection."""
        # Use DATABASE_URL for direct database access
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            logger.warning("DATABASE_URL not set - database operations disabled")
            self.engine = None
            self.SessionLocal = None
            self.enabled = False
            return
        
        try:
            # Create engine with NullPool to avoid connection issues
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,
                echo=False
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            self.enabled = True
            
            logger.info("✅ Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.engine = None
            self.SessionLocal = None
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if database is available."""
        return self.enabled and self.engine is not None
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with automatic cleanup."""
        if not self.is_enabled():
            raise Exception("Database not available")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==========================================
    # Usage Tracking Operations
    # ==========================================
    
    async def get_usage_record(self, user_id: str, month: str) -> Optional[Dict[str, Any]]:
        """Get usage record for specific user and month."""
        if not self.is_enabled():
            return None
        
        with self.get_session() as session:
            record = session.query(UsageTracking).filter(
                UsageTracking.user_id == user_id,
                UsageTracking.month == month
            ).first()
            
            if not record:
                return None
            
            return {
                "id": record.id,
                "user_id": record.user_id,
                "month": record.month,
                "scans_count": record.scans_count,
                "scans_limit": record.scans_limit,
                "files_scanned_total": record.files_scanned_total,
                "api_calls_count": record.api_calls_count,
                "api_calls_limit": record.api_calls_limit,
                "parallel_scans_count": record.parallel_scans_count,
                "sequential_scans_count": record.sequential_scans_count,
                "coordinated_chains_count": record.coordinated_chains_count
            }
    
    async def create_usage_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new usage record."""
        if not self.is_enabled():
            return data
        
        with self.get_session() as session:
            record = UsageTracking(**data)
            session.add(record)
            session.flush()
            
            return {
                "id": record.id,
                "user_id": record.user_id,
                "month": record.month,
                "scans_count": record.scans_count,
                "scans_limit": record.scans_limit
            }
    
    async def update_usage_record(self, user_id: str, month: str, updates: Dict[str, Any]) -> bool:
        """Update usage record."""
        if not self.is_enabled():
            return False
        
        with self.get_session() as session:
            record = session.query(UsageTracking).filter(
                UsageTracking.user_id == user_id,
                UsageTracking.month == month
            ).first()
            
            if not record:
                return False
            
            for key, value in updates.items():
                setattr(record, key, value)
            
            return True
    
    async def increment_scan_count(self, user_id: str, month: str) -> bool:
        """Increment scan count for user."""
        if not self.is_enabled():
            return False
        
        with self.get_session() as session:
            record = session.query(UsageTracking).filter(
                UsageTracking.user_id == user_id,
                UsageTracking.month == month
            ).first()
            
            if not record:
                return False
            
            record.scans_count += 1
            return True
    
    # ==========================================
    # Scan History Operations
    # ==========================================
    
    async def create_scan_history(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create scan history record."""
        if not self.is_enabled():
            return data
        
        with self.get_session() as session:
            scan = ScanHistory(**data)
            session.add(scan)
            session.flush()
            
            return {"id": scan.id, "created_at": scan.created_at}
    
    async def get_scan_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scan history for user."""
        if not self.is_enabled():
            return []
        
        with self.get_session() as session:
            scans = session.query(ScanHistory).filter(
                ScanHistory.user_id == user_id
            ).order_by(ScanHistory.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": scan.id,
                    "scan_type": scan.scan_type,
                    "agent_used": scan.agent_used,
                    "findings_count": scan.findings_count,
                    "critical_findings": scan.critical_findings,
                    "created_at": scan.created_at
                }
                for scan in scans
            ]
    
    # ==========================================
    # Polar Webhook Operations
    # ==========================================
    
    async def log_webhook_event(self, event_type: str, polar_event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Log Polar webhook event."""
        if not self.is_enabled():
            return {}
        
        with self.get_session() as session:
            webhook = PolarWebhook(
                event_type=event_type,
                polar_event_id=polar_event_id,
                payload=payload,
                polar_customer_id=payload.get("data", {}).get("customer_id"),
                polar_subscription_id=payload.get("data", {}).get("subscription_id")
            )
            session.add(webhook)
            session.flush()
            
            return {"id": webhook.id, "created_at": webhook.created_at}
    
    async def mark_webhook_processed(self, polar_event_id: str, error_message: Optional[str] = None) -> bool:
        """Mark webhook as processed."""
        if not self.is_enabled():
            return False
        
        with self.get_session() as session:
            webhook = session.query(PolarWebhook).filter(
                PolarWebhook.polar_event_id == polar_event_id
            ).first()
            
            if not webhook:
                return False
            
            webhook.processed = error_message is None
            webhook.processed_at = os.time()
            if error_message:
                webhook.error_message = error_message
            
            return True
    
    # ==========================================
    # User Operations
    # ==========================================
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user record."""
        if not self.is_enabled():
            return False
        
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            for key, value in updates.items():
                setattr(user, key, value)
            
            return True
    
    async def get_user_by_polar_customer(self, polar_customer_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Polar customer ID."""
        if not self.is_enabled():
            return None
        
        with self.get_session() as session:
            user = session.query(User).filter(
                User.polar_customer_id == polar_customer_id
            ).first()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "tier": user.tier,
                "polar_customer_id": user.polar_customer_id,
                "polar_subscription_id": user.polar_subscription_id,
                "subscription_status": user.subscription_status
            }


# Global instance
database_service = DatabaseService()
