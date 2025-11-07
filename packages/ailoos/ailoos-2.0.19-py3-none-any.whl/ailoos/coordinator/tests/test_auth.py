"""
Tests for authentication and authorization system.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from ..auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    refresh_access_token,
    revoke_token,
    revoke_all_node_tokens,
    create_node_token
)
from ..auth.permissions import Role, RolePermissions, PermissionChecker
from ..auth.node_auth import NodeAuthService
from ..models.base import Node, RevokedToken, RefreshToken
from ..config.settings import settings


class TestJWTAuthentication:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test access token creation."""
        subject = "node123"
        token = create_access_token(subject, "node", "validator")

        assert token is not None
        assert isinstance(token, str)

        # Verify token
        payload = verify_token(token)
        assert payload.sub == subject
        assert payload.type == "node"
        assert payload.role == "validator"
        assert payload.permissions is not None

    def test_create_refresh_token(self, db_session: Session):
        """Test refresh token creation."""
        subject = "node123"
        token, jti = create_refresh_token(subject, "node", db=db_session)

        assert token is not None
        assert jti is not None

        # Check database storage
        stored_token = db_session.query(RefreshToken).filter(
            RefreshToken.token_jti == jti
        ).first()
        assert stored_token is not None
        assert stored_token.node_id == subject
        assert not stored_token.is_revoked

    def test_refresh_access_token(self, db_session: Session):
        """Test token refresh functionality."""
        subject = "node123"

        # Create refresh token
        refresh_token, jti = create_refresh_token(subject, "node", db=db_session)

        # Refresh access token
        new_access, new_refresh = refresh_access_token(refresh_token, db_session)

        assert new_access is not None
        assert new_refresh is not None

        # Verify new access token
        payload = verify_token(new_access, db_session)
        assert payload.sub == subject
        assert payload.type == "node"

    def test_token_revocation(self, db_session: Session):
        """Test token revocation."""
        subject = "node123"
        access_token = create_access_token(subject, "node")

        # Verify token works initially
        payload = verify_token(access_token, db_session)
        assert payload.sub == subject

        # Revoke token
        revoke_token(payload.jti, "access", db=db_session)

        # Verify token is now invalid
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token(access_token, db_session)

    def test_expired_token(self):
        """Test expired token handling."""
        # Create token that expires immediately
        subject = "node123"
        token = create_access_token(
            subject, "node",
            expires_delta=timedelta(seconds=-1)
        )

        # Should raise expired exception
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token(token)


class TestPermissions:
    """Test permission system."""

    def test_role_permissions(self):
        """Test role-based permissions."""
        # Node permissions
        node_perms = RolePermissions.get_inherited_permissions(Role.NODE)
        assert "node:read" in node_perms
        assert "node:contribute" in node_perms
        assert "admin:read" not in node_perms

        # Validator permissions (inherits from node)
        validator_perms = RolePermissions.get_inherited_permissions(Role.VALIDATOR)
        assert "node:read" in validator_perms
        assert "contribution:validate" in validator_perms
        assert "admin:read" not in validator_perms

        # Admin permissions (inherits from validator)
        admin_perms = RolePermissions.get_inherited_permissions(Role.ADMIN)
        assert "node:read" in admin_perms
        assert "contribution:validate" in admin_perms
        assert "admin:read" in admin_perms

    def test_permission_checker(self):
        """Test permission checking utility."""
        user_permissions = ["node:read", "node:contribute", "session:join"]
        checker = PermissionChecker(user_permissions)

        assert checker.has_permission("node:read")
        assert checker.has_any_permission(["node:read", "admin:read"])
        assert checker.has_all_permissions(["node:read", "session:join"])
        assert not checker.has_permission("admin:read")
        assert not checker.has_all_permissions(["node:read", "admin:read"])

    def test_role_hierarchy(self):
        """Test role hierarchy validation."""
        hierarchy = RolePermissions.get_role_hierarchy()

        assert Role.NODE in hierarchy
        assert Role.VALIDATOR in hierarchy[Role.ADMIN]
        assert Role.NODE in hierarchy[Role.VALIDATOR]


class TestNodeAuth:
    """Test node authentication service."""

    @patch('src.ailoos.coordinator.auth.node_auth.NodeVerifier')
    async def test_node_login_success(self, mock_verifier_class, db_session: Session):
        """Test successful node login."""
        # Mock node verifier
        mock_verifier = Mock()
        mock_verifier.verify_node_identity.return_value = True
        mock_verifier.is_node_eligible.return_value = (True, "Eligible")
        mock_verifier.update_node_reputation.return_value = None
        mock_verifier_class.return_value = mock_verifier

        # Create test node
        node = Node(
            id="test_node",
            public_key="test_key",
            is_verified=True
        )
        db_session.add(node)
        db_session.commit()

        auth_service = NodeAuthService()

        result = await auth_service.authenticate_node(
            node_id="test_node",
            signature="test_signature",
            db=db_session
        )

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["node_info"]["node_id"] == "test_node"

    @patch('src.ailoos.coordinator.auth.node_auth.NodeVerifier')
    async def test_node_login_unverified(self, mock_verifier_class, db_session: Session):
        """Test login with unverified node."""
        # Create unverified node
        node = Node(
            id="test_node",
            public_key="test_key",
            is_verified=False
        )
        db_session.add(node)
        db_session.commit()

        auth_service = NodeAuthService()

        with pytest.raises(Exception):  # Should raise HTTPException
            await auth_service.authenticate_node(
                node_id="test_node",
                signature="test_signature",
                db=db_session
            )

    @patch('src.ailoos.coordinator.auth.node_auth.NodeVerifier')
    async def test_node_login_ineligible(self, mock_verifier_class, db_session: Session):
        """Test login with ineligible node."""
        # Mock verifier to return ineligible
        mock_verifier = Mock()
        mock_verifier.verify_node_identity.return_value = True
        mock_verifier.is_node_eligible.return_value = (False, "Low reputation")
        mock_verifier_class.return_value = mock_verifier

        # Create verified node
        node = Node(
            id="test_node",
            public_key="test_key",
            is_verified=True
        )
        db_session.add(node)
        db_session.commit()

        auth_service = NodeAuthService()

        with pytest.raises(Exception):  # Should raise HTTPException
            await auth_service.authenticate_node(
                node_id="test_node",
                signature="test_signature",
                db=db_session
            )


class TestSecurityMiddleware:
    """Test security middleware functionality."""

    def test_rate_limiting_logic(self):
        """Test rate limiting logic (without actual middleware)."""
        # This would test the rate limiting logic from middleware.py
        # For now, just ensure the logic is sound
        assert True  # Placeholder

    def test_audit_logging(self):
        """Test audit logging functionality."""
        # This would test the audit logging from middleware.py
        assert True  # Placeholder


class TestIntegration:
    """Integration tests for the auth system."""

    def test_complete_auth_flow(self, db_session: Session):
        """Test complete authentication flow."""
        # Create node
        node = Node(
            id="integration_node",
            public_key="test_public_key",
            is_verified=True
        )
        db_session.add(node)
        db_session.commit()

        # Create tokens
        access_token, refresh_token = create_node_token("integration_node", db_session)

        # Verify access token
        payload = verify_token(access_token, db_session)
        assert payload.sub == "integration_node"
        assert payload.type == "node"

        # Refresh token
        new_access, new_refresh = refresh_access_token(refresh_token, db_session)
        assert new_access != access_token  # Should be different token

        # Verify new token
        new_payload = verify_token(new_access, db_session)
        assert new_payload.sub == "integration_node"

        # Revoke all tokens for node
        revoke_all_node_tokens("integration_node", "test", db_session)

        # Old tokens should be invalid
        with pytest.raises(Exception):
            verify_token(access_token, db_session)

        with pytest.raises(Exception):
            verify_token(new_access, db_session)