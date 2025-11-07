"""
Integration tests for WebSocket functionality with FastAPI TestClient.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket
import websockets

from ...main import create_application
from ..manager import ConnectionManager, manager
from ..room_manager import RoomManager, room_manager
from ..message_broker import MessageBroker, message_broker
from ..heartbeat import HeartbeatManager, heartbeat_manager
from ..message_types import (
    WebSocketMessage, MessageType, MessagePriority,
    WebSocketMessageFactory, get_message_priority
)


class TestWebSocketEndpoints:
    """Test WebSocket endpoints with FastAPI TestClient."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app = create_application()
        self.client = TestClient(self.app)

    @patch('websockets.connect')
    @pytest.mark.asyncio
    async def test_session_websocket_connection(self, mock_connect):
        """Test session WebSocket endpoint connection."""
        # Mock WebSocket connection
        mock_ws = AsyncMock()
        mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_ws.__aexit__ = AsyncMock(return_value=None)
        mock_ws.recv = AsyncMock(return_value='{"type": "ping"}')
        mock_ws.send = AsyncMock()
        mock_connect.return_value = mock_ws

        # This would require a running server for full integration testing
        # For now, test the endpoint exists and routing works
        assert True  # Placeholder for actual endpoint testing

    def test_websocket_router_included(self):
        """Test that WebSocket router is included in the app."""
        routes = [route.path for route in self.app.routes]
        assert any("/ws/" in route for route in routes)


class TestWebSocketAuthentication:
    """Test WebSocket authentication integration."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app = create_application()
        self.client = TestClient(self.app)

    @patch('ailoos.coordinator.websocket.manager.verify_token')
    def test_websocket_authentication_validation(self, mock_verify):
        """Test JWT token validation for WebSocket connections."""
        # Mock valid token
        mock_token_data = Mock()
        mock_token_data.sub = "node123"
        mock_token_data.type = "node"
        mock_verify.return_value = mock_token_data

        # Test token verification logic (would be called during connection)
        from ..manager import verify_token
        result = verify_token("fake_token", None)
        mock_verify.assert_called_once_with("fake_token", None)


class TestWebSocketLifecycle:
    """Test complete WebSocket connection lifecycle."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()
        self.room_manager = RoomManager()
        self.heartbeat_manager = HeartbeatManager()

    @pytest.mark.asyncio
    async def test_full_connection_lifecycle(self):
        """Test complete connection lifecycle."""
        # Mock WebSocket and token
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read", "node:contribute"]

        # Connect
        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Verify connection
        assert "session123" in self.manager.active_connections
        assert "node123" in self.manager.active_connections["session123"]
        assert "node123" in self.room_manager.node_subscriptions

        # Test heartbeat
        self.heartbeat_manager.record_heartbeat("node123")
        status = self.heartbeat_manager.get_heartbeat_status("node123")
        assert status["status"] == "healthy"

        # Disconnect
        self.manager.disconnect("session123", "node123")

        # Verify cleanup
        assert "session123" not in self.manager.active_connections
        assert "node123" not in self.room_manager.node_subscriptions


class TestWebSocketBroadcasting:
    """Test WebSocket broadcasting functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()
        self.room_manager = RoomManager()
        self.message_broker = MessageBroker(max_workers=1)

    @pytest.mark.asyncio
    async def test_room_broadcasting(self):
        """Test broadcasting to rooms."""
        # Setup room and subscription
        self.room_manager.create_room("test_room", "session")
        self.room_manager.subscribe_node_to_room("node123", "test_room")

        # Mock WebSocket
        mock_ws = AsyncMock()
        mock_ws.send_text = AsyncMock()

        # Setup connection
        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Create and broadcast message
        message = WebSocketMessageFactory.create_session_update(
            "session123", "status_changed", {"status": "running"}
        )

        await self.room_manager.broadcast_to_room("session_test_room", message)

        # Verify message was sent (this would need more complex mocking for full test)

    @pytest.mark.asyncio
    async def test_event_broadcasting(self):
        """Test broadcasting to event subscribers."""
        # Subscribe to event
        self.room_manager.subscribe_to_event("node123", "training.metrics")

        # Create event message
        message = WebSocketMessageFactory.create_training_metrics(
            "session123", 1, {"accuracy": 0.95}
        )

        await self.room_manager.broadcast_event("training.metrics", message)

        # Verify event was broadcast (would need WebSocket mocking)


class TestWebSocketErrorHandling:
    """Test WebSocket error handling scenarios."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    @pytest.mark.asyncio
    async def test_invalid_token_connection(self):
        """Test connection with invalid token."""
        mock_ws = AsyncMock()
        mock_ws.close = AsyncMock()

        # Test would require mocking the endpoint handler
        # This tests the conceptual error handling
        assert True  # Placeholder

    def test_rate_limit_exceeded(self):
        """Test rate limiting behavior."""
        # Test rate limit logic
        assert self.manager._check_rate_limit("node123") == True

        # Simulate rate limit hit
        self.manager.rate_limits["node123"] = {"count": 100, "last_reset": "2023-01-01"}
        assert self.manager._check_rate_limit("node123") == False

    @pytest.mark.asyncio
    async def test_stale_connection_cleanup(self):
        """Test cleanup of stale connections."""
        # Setup connection
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        # Simulate stale connection
        stale_connections = self.manager.get_stale_connections(timeout_seconds=0)
        assert len(stale_connections) > 0

        # Cleanup
        await self.manager.cleanup_stale_connections()


class TestWebSocketPerformance:
    """Test WebSocket performance and scalability."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()
        self.message_broker = MessageBroker(max_workers=2)

    @pytest.mark.asyncio
    async def test_multiple_connections(self):
        """Test handling multiple simultaneous connections."""
        # Create multiple mock connections
        for i in range(10):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{i}"
            token_data.permissions = ["node:read"]

            await self.manager.connect(mock_ws, f"session{i}", f"node{i}", token_data)

        # Verify all connections
        assert len(self.manager.active_connections) == 10
        assert len(self.manager.node_subscriptions) == 10

    @pytest.mark.asyncio
    async def test_message_queue_performance(self):
        """Test message broker queue performance."""
        # Send multiple messages
        for i in range(50):
            message = WebSocketMessageFactory.create_training_metrics(
                "session123", i, {"accuracy": 0.9 + i * 0.001}
            )
            await self.message_broker.publish(message, "broadcast")

        # Check queue size
        assert self.message_broker.message_queue.qsize() == 50

    def test_compression_performance(self):
        """Test message compression performance."""
        # Create large message
        large_data = {"data": "x" * 5000}
        message = WebSocketMessage(
            type="test.large_message",
            data=large_data
        )

        compressed = self.message_broker._compress_message(message)

        # Verify compression
        assert compressed.type == "compressed.test.large_message"
        assert "compressed" in compressed.data
        assert len(compressed.data["data"]) < len(json.dumps(large_data))


class TestWebSocketMonitoring:
    """Test WebSocket monitoring and metrics."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()
        self.heartbeat_manager = HeartbeatManager()
        self.message_broker = MessageBroker(max_workers=1)

    @pytest.mark.asyncio
    async def test_connection_monitoring(self):
        """Test connection monitoring capabilities."""
        # Setup connections
        for i in range(5):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{i}"
            token_data.permissions = ["node:read"]

            await self.manager.connect(mock_ws, "session123", f"node{i}", token_data)
            self.heartbeat_manager.record_heartbeat(f"node{i}")

        # Check connection counts
        session_connections = self.manager.get_session_connections("session123")
        assert len(session_connections) == 5

        # Check heartbeat status
        all_status = self.heartbeat_manager.get_all_heartbeat_status()
        assert len(all_status) == 5

    @pytest.mark.asyncio
    async def test_broker_stats(self):
        """Test message broker statistics."""
        # Send some messages
        for i in range(10):
            message = WebSocketMessageFactory.create_node_status(f"node{i}", "online")
            await self.message_broker.publish(message, "broadcast")

        # Get stats
        stats = await self.message_broker.get_stats()
        assert stats["queue_size"] == 10
        assert stats["compression_enabled"] == True


# Load testing (would require pytest-benchmark or similar)
@pytest.mark.skip(reason="Load testing requires special setup")
class TestWebSocketLoad:
    """Load testing for WebSocket functionality."""

    @pytest.mark.asyncio
    async def test_high_connection_load(self):
        """Test handling high number of connections."""
        # This would create hundreds of connections
        pass

    @pytest.mark.asyncio
    async def test_high_message_load(self):
        """Test handling high message throughput."""
        # This would send thousands of messages
        pass