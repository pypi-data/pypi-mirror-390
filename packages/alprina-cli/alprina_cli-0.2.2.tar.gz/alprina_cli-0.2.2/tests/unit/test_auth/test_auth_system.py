"""
Tests for Authentication & Authorization System

Context: Validates auth, RBAC, and audit logging functionality.
"""

import pytest
from datetime import datetime, timedelta
from alprina_cli.auth_system import (
    AuthenticationService,
    AuthorizationService,
    AuditLogger,
    Role,
    Permission,
    User,
    ROLE_PERMISSIONS,
    get_auth_service,
    get_authz_service,
    get_audit_logger
)


class TestAuthenticationService:
    """Tests for authentication service"""

    def test_generate_api_key(self):
        """Test API key generation"""
        auth = AuthenticationService()

        api_key = auth.generate_api_key()

        assert api_key.startswith("alprina_")
        assert len(api_key) > 20

    def test_hash_api_key(self):
        """Test API key hashing"""
        auth = AuthenticationService()

        api_key = "test_key"
        hash1 = auth.hash_api_key(api_key)
        hash2 = auth.hash_api_key(api_key)

        assert hash1 == hash2  # Deterministic
        assert hash1 != api_key  # Different from original

    def test_create_user(self):
        """Test user creation"""
        auth = AuthenticationService()

        user, api_key = auth.create_user(
            username="testuser",
            email="test@example.com",
            role=Role.USER
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == Role.USER
        assert user.is_active is True
        assert api_key.startswith("alprina_")
        assert user.user_id in auth.users

    def test_authenticate_valid_key(self):
        """Test authentication with valid API key"""
        auth = AuthenticationService()

        user, api_key = auth.create_user("testuser", "test@example.com")

        authenticated_user = auth.authenticate(api_key)

        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"
        assert authenticated_user.last_login is not None

    def test_authenticate_invalid_key(self):
        """Test authentication with invalid API key"""
        auth = AuthenticationService()

        authenticated_user = auth.authenticate("invalid_key")

        assert authenticated_user is None

    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user"""
        auth = AuthenticationService()

        user, api_key = auth.create_user("testuser", "test@example.com")
        auth.deactivate_user(user.user_id)

        authenticated_user = auth.authenticate(api_key)

        assert authenticated_user is None

    def test_revoke_api_key(self):
        """Test API key revocation"""
        auth = AuthenticationService()

        user, api_key = auth.create_user("testuser", "test@example.com")

        # Should work before revocation
        assert auth.authenticate(api_key) is not None

        # Revoke
        success = auth.revoke_api_key(api_key)
        assert success is True

        # Should not work after revocation
        assert auth.authenticate(api_key) is None

    def test_deactivate_user(self):
        """Test user deactivation"""
        auth = AuthenticationService()

        user, api_key = auth.create_user("testuser", "test@example.com")

        success = auth.deactivate_user(user.user_id)

        assert success is True
        assert not auth.users[user.user_id].is_active


class TestAuthorizationService:
    """Tests for authorization service"""

    def test_admin_has_all_permissions(self):
        """Test that admin role has all permissions"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="admin",
            email="admin@example.com",
            role=Role.ADMIN
        )

        for permission in Permission:
            assert authz.has_permission(user, permission)

    def test_user_has_limited_permissions(self):
        """Test that user role has limited permissions"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="user",
            email="user@example.com",
            role=Role.USER
        )

        # Should have basic permissions
        assert authz.has_permission(user, Permission.SCAN)
        assert authz.has_permission(user, Permission.RECON)

        # Should NOT have admin permissions
        assert not authz.has_permission(user, Permission.EXPLOIT)
        assert not authz.has_permission(user, Permission.RED_TEAM)
        assert not authz.has_permission(user, Permission.MANAGE_USERS)

    def test_pentester_can_exploit(self):
        """Test that pentester role can use exploit tools"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="pentester",
            email="pentester@example.com",
            role=Role.PENTESTER
        )

        assert authz.has_permission(user, Permission.EXPLOIT)
        assert authz.has_permission(user, Permission.RED_TEAM)

    def test_defender_cannot_exploit(self):
        """Test that defender role cannot use exploit tools"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="defender",
            email="defender@example.com",
            role=Role.DEFENDER
        )

        assert not authz.has_permission(user, Permission.EXPLOIT)
        assert not authz.has_permission(user, Permission.RED_TEAM)
        assert authz.has_permission(user, Permission.BLUE_TEAM)
        assert authz.has_permission(user, Permission.DFIR)

    def test_auditor_readonly_access(self):
        """Test that auditor has read-only access"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="auditor",
            email="auditor@example.com",
            role=Role.AUDITOR
        )

        # Can view
        assert authz.has_permission(user, Permission.VIEW_REPORTS)
        assert authz.has_permission(user, Permission.VIEW_AUDIT_LOGS)

        # Cannot execute
        assert not authz.has_permission(user, Permission.SCAN)
        assert not authz.has_permission(user, Permission.EXPLOIT)

    def test_require_permission_success(self):
        """Test require_permission with valid permission"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="admin",
            email="admin@example.com",
            role=Role.ADMIN
        )

        # Should not raise
        authz.require_permission(user, Permission.SCAN)

    def test_require_permission_failure(self):
        """Test require_permission with invalid permission"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="user",
            email="user@example.com",
            role=Role.USER
        )

        # Should raise PermissionError
        with pytest.raises(PermissionError):
            authz.require_permission(user, Permission.EXPLOIT)

    def test_get_user_permissions(self):
        """Test getting all user permissions"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="pentester",
            email="pentester@example.com",
            role=Role.PENTESTER
        )

        permissions = authz.get_user_permissions(user)

        assert Permission.EXPLOIT in permissions
        assert Permission.RED_TEAM in permissions
        assert len(permissions) > 0

    def test_can_use_tool_scan(self):
        """Test tool access check for scan tool"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="user",
            email="user@example.com",
            role=Role.USER
        )

        assert authz.can_use_tool(user, "ScanTool")

    def test_can_use_tool_exploit_denied(self):
        """Test tool access denied for exploit tool"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="user",
            email="user@example.com",
            role=Role.USER
        )

        assert not authz.can_use_tool(user, "ExploitTool")

    def test_can_use_tool_exploit_allowed(self):
        """Test tool access allowed for exploit tool (pentester)"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="pentester",
            email="pentester@example.com",
            role=Role.PENTESTER
        )

        assert authz.can_use_tool(user, "ExploitTool")

    def test_can_use_unknown_tool(self):
        """Test tool access check for unknown tool"""
        authz = AuthorizationService()
        user = User(
            user_id="test",
            username="admin",
            email="admin@example.com",
            role=Role.ADMIN
        )

        # Unknown tools should be denied by default
        assert not authz.can_use_tool(user, "UnknownTool")


class TestAuditLogger:
    """Tests for audit logger"""

    def test_log_operation(self):
        """Test logging an operation"""
        audit = AuditLogger()
        user = User(
            user_id="test",
            username="testuser",
            email="test@example.com",
            role=Role.USER
        )

        audit.log(
            user=user,
            operation="scan",
            tool_name="ScanTool",
            target="example.com",
            success=True
        )

        assert len(audit.audit_log) == 1
        entry = audit.audit_log[0]
        assert entry.user_id == "test"
        assert entry.operation == "scan"
        assert entry.tool_name == "ScanTool"
        assert entry.target == "example.com"
        assert entry.success is True

    def test_log_with_details(self):
        """Test logging with additional details"""
        audit = AuditLogger()
        user = User(
            user_id="test",
            username="testuser",
            email="test@example.com",
            role=Role.USER
        )

        details = {"findings": 5, "severity": "HIGH"}

        audit.log(
            user=user,
            operation="vuln_scan",
            tool_name="VulnScanTool",
            target="example.com",
            success=True,
            details=details
        )

        entry = audit.audit_log[0]
        assert entry.details["findings"] == 5
        assert entry.details["severity"] == "HIGH"

    def test_get_logs_no_filter(self):
        """Test retrieving logs without filters"""
        audit = AuditLogger()
        user = User(
            user_id="test",
            username="testuser",
            email="test@example.com",
            role=Role.USER
        )

        # Log multiple operations
        for i in range(5):
            audit.log(user, "scan", "ScanTool", f"target{i}.com", True)

        logs = audit.get_logs()

        assert len(logs) == 5

    def test_get_logs_filter_by_user(self):
        """Test retrieving logs filtered by user"""
        audit = AuditLogger()
        user1 = User(user_id="user1", username="user1", email="user1@example.com", role=Role.USER)
        user2 = User(user_id="user2", username="user2", email="user2@example.com", role=Role.USER)

        audit.log(user1, "scan", "ScanTool", "example.com", True)
        audit.log(user2, "scan", "ScanTool", "example.com", True)
        audit.log(user1, "recon", "ReconTool", "example.com", True)

        logs = audit.get_logs(user_id="user1")

        assert len(logs) == 2
        assert all(e.user_id == "user1" for e in logs)

    def test_get_logs_filter_by_tool(self):
        """Test retrieving logs filtered by tool"""
        audit = AuditLogger()
        user = User(user_id="test", username="test", email="test@example.com", role=Role.USER)

        audit.log(user, "scan", "ScanTool", "example.com", True)
        audit.log(user, "recon", "ReconTool", "example.com", True)
        audit.log(user, "scan", "ScanTool", "example2.com", True)

        logs = audit.get_logs(tool_name="ScanTool")

        assert len(logs) == 2
        assert all(e.tool_name == "ScanTool" for e in logs)

    def test_get_logs_filter_by_time(self):
        """Test retrieving logs filtered by time"""
        audit = AuditLogger()
        user = User(user_id="test", username="test", email="test@example.com", role=Role.USER)

        # Log operation
        audit.log(user, "scan", "ScanTool", "example.com", True)

        # Filter by time range
        now = datetime.utcnow()
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)

        # Should find the log
        logs = audit.get_logs(start_time=past, end_time=future)
        assert len(logs) == 1

        # Should not find the log (too far in past)
        logs = audit.get_logs(start_time=now + timedelta(hours=2))
        assert len(logs) == 0

    def test_get_logs_limit(self):
        """Test retrieving logs with limit"""
        audit = AuditLogger()
        user = User(user_id="test", username="test", email="test@example.com", role=Role.USER)

        # Log 10 operations
        for i in range(10):
            audit.log(user, "scan", "ScanTool", f"target{i}.com", True)

        logs = audit.get_logs(limit=5)

        assert len(logs) == 5

    def test_get_user_activity(self):
        """Test getting user activity"""
        audit = AuditLogger()
        user = User(user_id="test", username="test", email="test@example.com", role=Role.USER)

        # Log operations
        for i in range(3):
            audit.log(user, "scan", "ScanTool", f"target{i}.com", True)

        activity = audit.get_user_activity("test", days=7)

        assert len(activity) == 3
        assert all(e.user_id == "test" for e in activity)

    def test_log_trimming(self):
        """Test that audit log is trimmed when it exceeds max size"""
        audit = AuditLogger(max_entries=10)
        user = User(user_id="test", username="test", email="test@example.com", role=Role.USER)

        # Log more than max_entries
        for i in range(15):
            audit.log(user, "scan", "ScanTool", f"target{i}.com", True)

        # Should be trimmed to max_entries
        assert len(audit.audit_log) == 10


class TestSingletonInstances:
    """Test singleton pattern for global instances"""

    def test_get_auth_service_singleton(self):
        """Test that get_auth_service returns same instance"""
        service1 = get_auth_service()
        service2 = get_auth_service()

        assert service1 is service2

    def test_get_authz_service_singleton(self):
        """Test that get_authz_service returns same instance"""
        service1 = get_authz_service()
        service2 = get_authz_service()

        assert service1 is service2

    def test_get_audit_logger_singleton(self):
        """Test that get_audit_logger returns same instance"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()

        assert logger1 is logger2


class TestRolePermissions:
    """Test role permission mappings"""

    def test_all_roles_have_permissions(self):
        """Test that all roles have defined permissions"""
        for role in Role:
            assert role in ROLE_PERMISSIONS
            assert len(ROLE_PERMISSIONS[role]) > 0

    def test_admin_has_most_permissions(self):
        """Test that admin has the most permissions"""
        admin_perms = len(ROLE_PERMISSIONS[Role.ADMIN])

        for role in Role:
            if role != Role.ADMIN:
                role_perms = len(ROLE_PERMISSIONS[role])
                assert admin_perms >= role_perms

    def test_auditor_has_no_execution_perms(self):
        """Test that auditor cannot execute security tools"""
        auditor_perms = ROLE_PERMISSIONS[Role.AUDITOR]

        execution_perms = [
            Permission.SCAN,
            Permission.EXPLOIT,
            Permission.RED_TEAM,
            Permission.BLUE_TEAM
        ]

        for perm in execution_perms:
            assert perm not in auditor_perms
