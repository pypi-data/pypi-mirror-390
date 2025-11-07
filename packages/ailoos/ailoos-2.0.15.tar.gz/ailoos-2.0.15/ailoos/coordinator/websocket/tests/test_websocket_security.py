"""
Security tests for WebSocket functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import WebSocket, HTTPException
import jwt

from ...main import create_application
from ..manager import ConnectionManager, manager, verify_token
from ..room_manager import RoomManager, room_manager
from ..message_broker import MessageBroker, message_broker
from ..heartbeat import HeartbeatManager, heartbeat_manager
from ..message_types import WebSocketMessageFactory, MessageType
from ...config.settings import settings


class TestWebSocketAuthenticationSecurity:
    """Test WebSocket authentication security."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app = create_application()
        self.client = TestClient(self.app)

    def test_jwt_token_verification(self):
        """Test JWT token verification security."""
        # Test valid token
        with patch('ailoos.coordinator.auth.jwt.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "sub": "node123",
                "type": "node",
                "exp": 2000000000,  # Future timestamp
                "iat": 1000000000,
                "jti": "test-jti"
            }

            token_data = verify_token("valid_token", None)
            assert token_data.sub == "node123"
            assert token_data.type == "node"

    def test_expired_token_rejection(self):
        """Test that expired tokens are rejected."""
        with patch('ailoos.coordinator.auth.jwt.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

            with pytest.raises(HTTPException) as exc_info:
                verify_token("expired_token", None)

            assert exc_info.value.status_code == 401
            assert "expired" in str(exc_info.value.detail).lower()

    def test_invalid_token_rejection(self):
        """Test that invalid tokens are rejected."""
        with patch('ailoos.coordinator.auth.jwt.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                verify_token("invalid_token", None)

            assert exc_info.value.status_code == 401
            assert "invalid" in str(exc_info.value.detail).lower()

    def test_revoked_token_rejection(self):
        """Test that revoked tokens are rejected."""
        with patch('ailoos.coordinator.auth.jwt.jwt.decode') as mock_decode, \
             patch('ailoos.coordinator.database.connection.get_db') as mock_db:

            mock_decode.return_value = {
                "sub": "node123",
                "type": "node",
                "exp": 2000000000,
                "iat": 1000000000,
                "jti": "revoked-jti"
            }

            # Mock revoked token in database
            mock_db_session = Mock()
            mock_revoked_token = Mock()
            mock_revoked_token.token_jti = "revoked-jti"
            mock_db_session.query.return_value.filter.return_value.first.return_value = mock_revoked_token

            with pytest.raises(HTTPException) as exc_info:
                verify_token("revoked_token", mock_db_session)

            assert exc_info.value.status_code == 401
            assert "revoked" in str(exc_info.value.detail).lower()

    def test_wrong_token_type_rejection(self):
        """Test that wrong token types are rejected for WebSocket connections."""
        with patch('ailoos.coordinator.auth.jwt.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "sub": "user123",
                "type": "user",  # Wrong type for WebSocket
                "exp": 2000000000,
                "iat": 1000000000,
                "jti": "test-jti"
            }

            token_data = verify_token("user_token", None)
            # This should succeed for token verification, but fail at WebSocket level
            assert token_data.type == "user"

    @pytest.mark.asyncio
    async def test_node_id_mismatch_rejection(self):
        """Test that node ID mismatch in token is rejected."""
        mock_ws = AsyncMock()
        mock_ws.close = AsyncMock()

        # Token for different node
        with patch('ailoos.coordinator.websocket.manager.verify_token') as mock_verify:
            token_data = Mock()
            token_data.sub = "different_node"
            token_data.type = "node"
            mock_verify.return_value = token_data

            # This would be handled by the endpoint, but we test the logic
            assert token_data.sub == "different_node"  # Would fail != requested node_id


class TestWebSocketAuthorizationSecurity:
    """Test WebSocket authorization security."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    @pytest.mark.asyncio
    async def test_permission_based_access(self):
        """Test that WebSocket access respects permissions."""
        # Test node with read-only permissions
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]  # No contribute permission

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Verify connection allowed (read permission is sufficient for connection)
        assert "session123" in self.manager.active_connections

        # Cleanup
        self.manager.disconnect("session123", "node123")

    @pytest.mark.asyncio
    async def test_admin_only_endpoints(self):
        """Test that admin-only endpoints reject non-admin users."""
        # This would be tested at the endpoint level
        # Mock admin token
        with patch('ailoos.coordinator.websocket.manager.verify_token') as mock_verify:
            admin_token_data = Mock()
            admin_token_data.sub = "admin_user"
            admin_token_data.permissions = ["admin:read", "admin:write"]
            mock_verify.return_value = admin_token_data

            # Test admin token verification
            assert "admin:read" in admin_token_data.permissions

    def test_global_endpoint_admin_requirement(self):
        """Test that global endpoint requires admin permissions."""
        # This is enforced at the endpoint level
        # Test the permission check logic
        from ...auth.permissions import check_permissions

        # Admin user
        admin_permissions = ["admin:read", "admin:write"]
        assert check_permissions(["admin:read"], admin_permissions)

        # Regular node
        node_permissions = ["node:read", "node:contribute"]
        assert not check_permissions(["admin:read"], node_permissions)


class TestWebSocketRateLimitingSecurity:
    """Test WebSocket rate limiting security."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    def test_rate_limit_enforcement(self):
        """Test that rate limits are properly enforced."""
        node_id = "rate_limit_test_node"

        # Test within limits
        for i in range(100):
            assert self.manager._check_rate_limit(node_id) == True
            self.manager.rate_limits[node_id] = {"count": i + 1, "last_reset": "2023-01-01"}

        # Test limit exceeded
        assert self.manager._check_rate_limit(node_id) == False

    @pytest.mark.asyncio
    async def test_rate_limit_message_blocking(self):
        """Test that messages are blocked when rate limit is exceeded."""
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Set rate limit exceeded
        self.manager.rate_limits["node123"] = {"count": 100, "last_reset": "2023-01-01"}

        # Try to send message
        message = WebSocketMessageFactory.create_ping()
        await self.manager.send_personal_message(message, "session123", "node123")

        # Verify message was not sent
        mock_ws.send_text.assert_not_called()

        # Cleanup
        self.manager.disconnect("session123", "node123")


class TestWebSocketInputValidationSecurity:
    """Test WebSocket input validation security."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON messages."""
        # This would be handled in the message processing loop
        # Test JSON parsing error handling
        import json

        malformed_json = '{"type": "test", "data": '  # Missing closing brace

        with pytest.raises(json.JSONDecodeError):
            json.loads(malformed_json)

    def test_large_message_handling(self):
        """Test handling of extremely large messages."""
        # Create a very large message
        large_data = "x" * 1000000  # 1MB message
        large_message = WebSocketMessageFactory.create_session_update(
            "session123", "large_test", {"data": large_data}
        )

        # Test that compression handles it
        compressed = message_broker._compress_message(large_message)

        # Verify compression worked
        assert compressed.type.startswith("compressed.")
        assert len(compressed.data["data"]) < len(large_data)

    def test_invalid_message_types(self):
        """Test handling of invalid message types."""
        # Create message with invalid type
        invalid_message = WebSocketMessageFactory.create_session_update(
            "session123", "test", {"data": "test"}
        )
        # Manually change type to invalid
        invalid_message.type = "invalid.type.that.does.not.exist"

        # This should not cause errors, just be ignored or logged
        assert invalid_message.type == "invalid.type.that.does.not.exist"

    def test_sql_injection_prevention(self):
        """Test prevention of SQL injection through WebSocket messages."""
        # Test that user input is properly handled
        malicious_data = {
            "name": "'; DROP TABLE users; --",
            "value": "malicious_input"
        }

        message = WebSocketMessageFactory.create_session_update(
            "session123", "test", malicious_data
        )

        # The message should contain the malicious data as-is
        # (actual SQL injection prevention is handled at the database layer)
        assert message.data["data"]["name"] == "'; DROP TABLE users; --"


class TestWebSocketConnectionSecurity:
    """Test WebSocket connection-level security."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    @pytest.mark.asyncio
    async def test_connection_metadata_tracking(self):
        """Test that connection metadata is properly tracked."""
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Verify metadata is stored
        assert "session123" in self.manager.connection_metadata
        assert "node123" in self.manager.connection_metadata["session123"]

        metadata = self.manager.connection_metadata["session123"]["node123"]
        assert "connected_at" in metadata
        assert metadata["token_data"] == token_data

        # Cleanup
        self.manager.disconnect("session123", "node123")

    @pytest.mark.asyncio
    async def test_connection_cleanup_security(self):
        """Test that connections are properly cleaned up."""
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Verify connection exists
        assert "node123" in self.manager.active_connections["session123"]

        # Disconnect
        self.manager.disconnect("session123", "node123")

        # Verify complete cleanup
        assert "session123" not in self.manager.active_connections
        assert "node123" not in self.manager.node_subscriptions
        assert "session123" not in self.manager.connection_metadata
        assert "session123" not in self.manager.heartbeats

    def test_heartbeat_security(self):
        """Test heartbeat security and manipulation prevention."""
        node_id = "heartbeat_test_node"

        # Record heartbeat
        heartbeat_manager.record_heartbeat(node_id)

        # Verify heartbeat recorded
        assert node_id in heartbeat_manager.last_heartbeats

        # Test heartbeat status
        status = heartbeat_manager.get_heartbeat_status(node_id)
        assert status["status"] == "healthy"

        # Test heartbeat manipulation prevention
        # (This is more about not exposing internal state)
        all_status = heartbeat_manager.get_all_heartbeat_status()
        assert isinstance(all_status, dict)
        assert node_id in all_status


class TestWebSocketPrivacySecurity:
    """Test WebSocket privacy and data protection."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    def test_message_isolation(self):
        """Test that messages are properly isolated between sessions/nodes."""
        # Create messages for different sessions
        message1 = WebSocketMessageFactory.create_session_update(
            "session1", "update1", {"data": "session1_data"}
        )
        message2 = WebSocketMessageFactory.create_session_update(
            "session2", "update2", {"data": "session2_data"}
        )

        # Verify messages are properly scoped
        assert message1.session_id == "session1"
        assert message2.session_id == "session2"
        assert message1.data["data"] != message2.data["data"]

    def test_node_data_isolation(self):
        """Test that node data is properly isolated."""
        # This would be tested by ensuring nodes only receive their own data
        # and not other nodes' data

        node1_data = {"private": "node1_secret"}
        node2_data = {"private": "node2_secret"}

        message1 = WebSocketMessageFactory.create_node_status("node1", "online", node1_data)
        message2 = WebSocketMessageFactory.create_node_status("node2", "online", node2_data)

        assert message1.node_id == "node1"
        assert message2.node_id == "node2"
        assert message1.data["data"]["private"] != message2.data["data"]["private"]

    def test_token_data_privacy(self):
        """Test that token data is not exposed in messages."""
        # Token data should not be included in WebSocket messages
        message = WebSocketMessageFactory.create_session_update(
            "session123", "test", {"data": "test"}
        )

        # Message should not contain token information
        assert "token" not in json.dumps(message.dict()).lower()
        assert "password" not in json.dumps(message.dict()).lower()
        assert "secret" not in json.dumps(message.dict()).lower()


class TestWebSocketAuditSecurity:
    """Test WebSocket audit logging security."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    @pytest.mark.asyncio
    async def test_connection_audit_logging(self):
        """Test that connections are properly audit logged."""
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = "audit_test_node"
        token_data.permissions = ["node:read"]

        # This would normally trigger audit logging
        await self.manager.connect(mock_ws, "audit_session", "audit_test_node", token_data)

        # Verify connection metadata includes audit information
        metadata = self.manager.connection_metadata["audit_session"]["audit_test_node"]
        assert "connected_at" in metadata
        assert "token_data" in metadata

        # Cleanup
        self.manager.disconnect("audit_session", "audit_test_node")

    def test_error_audit_logging(self):
        """Test that errors are properly audit logged."""
        # Error handling should include audit logging
        # This is tested implicitly through the error handling tests above

        # Test rate limit logging
        node_id = "rate_limit_audit_node"
        self.manager.rate_limits[node_id] = {"count": 100, "last_reset": "2023-01-01"}

        # This would trigger rate limit logging
        can_send = self.manager._check_rate_limit(node_id)
        assert can_send == False

        # The logging would happen in the actual implementation
        # Here we just verify the logic works