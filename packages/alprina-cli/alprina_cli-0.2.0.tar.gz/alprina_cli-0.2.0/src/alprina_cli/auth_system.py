"""
Authentication & Authorization System

Provides:
- User authentication (API key based)
- Role-Based Access Control (RBAC)
- Audit logging for security operations
- Session management

Context Engineering:
- Lightweight auth that doesn't inflate context
- Fast permission checks (< 1ms)
- Audit logs for compliance
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
from pydantic import BaseModel, Field
from loguru import logger


class Role(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"  # Full access to all operations
    SECURITY_ANALYST = "security_analyst"  # Can run all security tools
    PENTESTER = "pentester"  # Can run offensive tools (red team, exploit)
    DEFENDER = "defender"  # Can run defensive tools (blue team, DFIR)
    AUDITOR = "auditor"  # Read-only access, can view reports
    USER = "user"  # Basic access to scan and recon


class Permission(str, Enum):
    """Fine-grained permissions"""
    # Tool permissions
    SCAN = "scan"
    RECON = "recon"
    VULN_SCAN = "vuln_scan"
    EXPLOIT = "exploit"
    RED_TEAM = "red_team"
    BLUE_TEAM = "blue_team"
    DFIR = "dfir"
    ANDROID_SAST = "android_sast"

    # Administrative permissions
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_ROLES = "manage_roles"

    # Report permissions
    GENERATE_REPORTS = "generate_reports"
    VIEW_REPORTS = "view_reports"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: list(Permission),  # All permissions
    Role.SECURITY_ANALYST: [
        Permission.SCAN,
        Permission.RECON,
        Permission.VULN_SCAN,
        Permission.BLUE_TEAM,
        Permission.DFIR,
        Permission.ANDROID_SAST,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_AUDIT_LOGS,
    ],
    Role.PENTESTER: [
        Permission.SCAN,
        Permission.RECON,
        Permission.VULN_SCAN,
        Permission.EXPLOIT,
        Permission.RED_TEAM,
        Permission.VIEW_REPORTS,
    ],
    Role.DEFENDER: [
        Permission.SCAN,
        Permission.RECON,
        Permission.BLUE_TEAM,
        Permission.DFIR,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_REPORTS,
    ],
    Role.AUDITOR: [
        Permission.VIEW_REPORTS,
        Permission.VIEW_AUDIT_LOGS,
    ],
    Role.USER: [
        Permission.SCAN,
        Permission.RECON,
        Permission.VIEW_REPORTS,
    ],
}


class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    email: str
    role: Role
    api_key_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True


class AuditLogEntry(BaseModel):
    """Audit log entry for security operations"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    username: str
    operation: str
    tool_name: str
    target: Optional[str] = None
    success: bool
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


class AuthenticationService:
    """
    Authentication service for API key management.

    Context: Fast, stateless authentication using API keys.
    """

    def __init__(self):
        # In-memory storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"alprina_{secrets.token_urlsafe(32)}"

    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def create_user(
        self,
        username: str,
        email: str,
        role: Role = Role.USER
    ) -> tuple[User, str]:
        """
        Create a new user and return user object + API key.

        Args:
            username: Username
            email: Email address
            role: User role (default: USER)

        Returns:
            Tuple of (User, api_key)
        """
        user_id = f"user_{secrets.token_hex(8)}"
        api_key = self.generate_api_key()
        api_key_hash = self.hash_api_key(api_key)

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            api_key_hash=api_key_hash
        )

        self.users[user_id] = user
        self.api_keys[api_key] = user_id

        logger.info(f"Created user {username} ({user_id}) with role {role}")

        return user, api_key

    def authenticate(self, api_key: str) -> Optional[User]:
        """
        Authenticate user by API key.

        Args:
            api_key: API key to authenticate

        Returns:
            User object if authenticated, None otherwise
        """
        user_id = self.api_keys.get(api_key)
        if not user_id:
            logger.warning("Authentication failed: Invalid API key")
            return None

        user = self.users.get(user_id)
        if not user or not user.is_active:
            logger.warning(f"Authentication failed: User {user_id} not found or inactive")
            return None

        # Update last login
        user.last_login = datetime.utcnow()

        logger.debug(f"Authenticated user {user.username} ({user_id})")
        return user

    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.

        Args:
            api_key: API key to revoke

        Returns:
            True if revoked, False if not found
        """
        if api_key in self.api_keys:
            user_id = self.api_keys[api_key]
            del self.api_keys[api_key]
            logger.info(f"Revoked API key for user {user_id}")
            return True
        return False

    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id: User ID to deactivate

        Returns:
            True if deactivated, False if not found
        """
        user = self.users.get(user_id)
        if user:
            user.is_active = False
            logger.info(f"Deactivated user {user.username} ({user_id})")
            return True
        return False


class AuthorizationService:
    """
    Authorization service for RBAC.

    Context: Fast permission checks without context overhead.
    """

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def has_permission(self, user: User, permission: Permission) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user: User to check
            permission: Permission to check

        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = self.role_permissions.get(user.role, [])
        has_perm = permission in user_permissions

        if not has_perm:
            logger.warning(
                f"Permission denied: User {user.username} ({user.role}) "
                f"does not have {permission} permission"
            )

        return has_perm

    def require_permission(self, user: User, permission: Permission) -> None:
        """
        Require a permission, raise exception if not granted.

        Args:
            user: User to check
            permission: Required permission

        Raises:
            PermissionError: If user doesn't have permission
        """
        if not self.has_permission(user, permission):
            raise PermissionError(
                f"User {user.username} does not have {permission} permission"
            )

    def get_user_permissions(self, user: User) -> List[Permission]:
        """Get all permissions for a user"""
        return self.role_permissions.get(user.role, [])

    def can_use_tool(self, user: User, tool_name: str) -> bool:
        """
        Check if user can use a specific tool.

        Args:
            user: User to check
            tool_name: Name of tool to check

        Returns:
            True if user can use tool, False otherwise
        """
        # Map tool names to permissions
        tool_permission_map = {
            "ScanTool": Permission.SCAN,
            "ReconTool": Permission.RECON,
            "VulnScanTool": Permission.VULN_SCAN,
            "ExploitTool": Permission.EXPLOIT,
            "RedTeamTool": Permission.RED_TEAM,
            "BlueTeamTool": Permission.BLUE_TEAM,
            "DFIRTool": Permission.DFIR,
            "AndroidSASTTool": Permission.ANDROID_SAST,
        }

        permission = tool_permission_map.get(tool_name)
        if not permission:
            # Unknown tool - deny by default
            logger.warning(f"Unknown tool: {tool_name}")
            return False

        return self.has_permission(user, permission)


class AuditLogger:
    """
    Audit logger for security operations.

    Context: Compliance-ready audit logging.
    """

    def __init__(self, max_entries: int = 10000):
        # In-memory storage (replace with database in production)
        self.audit_log: List[AuditLogEntry] = []
        self.max_entries = max_entries

    def log(
        self,
        user: User,
        operation: str,
        tool_name: str,
        target: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log a security operation.

        Args:
            user: User performing operation
            operation: Operation name (e.g., "scan", "exploit")
            tool_name: Name of tool used
            target: Target of operation (e.g., IP, domain)
            success: Whether operation succeeded
            details: Additional details
            ip_address: IP address of user
        """
        entry = AuditLogEntry(
            user_id=user.user_id,
            username=user.username,
            operation=operation,
            tool_name=tool_name,
            target=target,
            success=success,
            details=details or {},
            ip_address=ip_address
        )

        self.audit_log.append(entry)

        # Trim log if it gets too large
        if len(self.audit_log) > self.max_entries:
            self.audit_log = self.audit_log[-self.max_entries:]

        logger.info(
            f"AUDIT: {user.username} {operation} {tool_name} "
            f"target={target} success={success}"
        )

    def get_logs(
        self,
        user_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """
        Query audit logs with filters.

        Args:
            user_id: Filter by user ID
            tool_name: Filter by tool name
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results

        Returns:
            List of matching audit log entries
        """
        results = self.audit_log

        if user_id:
            results = [e for e in results if e.user_id == user_id]

        if tool_name:
            results = [e for e in results if e.tool_name == tool_name]

        if start_time:
            results = [e for e in results if e.timestamp >= start_time]

        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        # Return most recent first
        results = sorted(results, key=lambda e: e.timestamp, reverse=True)

        return results[:limit]

    def get_user_activity(self, user_id: str, days: int = 7) -> List[AuditLogEntry]:
        """Get user activity for the past N days"""
        start_time = datetime.utcnow() - timedelta(days=days)
        return self.get_logs(user_id=user_id, start_time=start_time)


# Global instances (singleton pattern)
_auth_service: Optional[AuthenticationService] = None
_authz_service: Optional[AuthorizationService] = None
_audit_logger: Optional[AuditLogger] = None


def get_auth_service() -> AuthenticationService:
    """Get global authentication service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service


def get_authz_service() -> AuthorizationService:
    """Get global authorization service instance"""
    global _authz_service
    if _authz_service is None:
        _authz_service = AuthorizationService()
    return _authz_service


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
