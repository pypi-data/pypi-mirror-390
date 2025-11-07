"""
Tests for WebSocket functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket
import websockets

from ..manager import ConnectionManager, manager
from ..room_manager import RoomManager, room_manager
from ..message_broker import MessageBroker, message_broker
from ..heartbeat import HeartbeatManager, heartbeat_manager
from ..message_types import (
    WebSocketMessage, MessageType, MessagePriority,
    WebSocketMessageFactory, get_message_priority
)
from ...models.schemas import WebSocketMessage as SchemaMessage


class TestConnectionManager:
    """Test ConnectionManager functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    def test_initialization(self):
        """Test manager initialization."""
        assert self.manager.active_connections == {}
        assert self.manager.node_subscriptions == {}
        assert self.manager.connection_metadata == {}
        assert self.manager.rate_limits == {}
        assert self.manager.heartbeats == {}

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test WebSocket connection."""
        # Mock WebSocket
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        # Mock token data
        token_data = Mock()
        token_data.sub = "node123"
        token_data.permissions = ["node:read"]

        await self.manager.connect(mock_ws, "session123", "node123", token_data)

        assert "session123" in self.manager.active_connections
        assert "node123" in self.manager.active_connections["session123"]
        assert "node123" in self.manager.node_subscriptions
        assert "session123" in self.manager.node_subscriptions["node123"]

    def test_disconnect(self):
        """Test WebSocket disconnection."""
        # Setup connection
        self.manager.active_connections = {"session123": {"node123": Mock()}}
        self.manager.node_subscriptions = {"node123": {"session123"}}
        self.manager.connection_metadata = {"session123": {"node123": {"connected_at": "2023-01-01"}}}
        self.manager.heartbeats = {"session123": {"node123": "2023-01-01"}}

        self.manager.disconnect("session123", "node123")

        assert self.manager.active_connections == {}
        assert self.manager.node_subscriptions == {}
        assert self.manager.connection_metadata == {}
        assert self.manager.heartbeats == {}

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Test within limits
        assert self.manager._check_rate_limit("node123") == True

        # Simulate rate limit exceeded
        self.manager.rate_limits["node123"] = {"count": 100, "last_reset": "2023-01-01"}
        assert self.manager._check_rate_limit("node123") == False


class TestRoomManager:
    """Test RoomManager functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.room_manager = RoomManager()

    def test_create_room(self):
        """Test room creation."""
        self.room_manager.create_room("test_room", "session")

        assert "test_room" in self.room_manager.room_subscriptions
        assert "test_room" in self.room_manager.room_metadata
        assert self.room_manager.room_metadata["test_room"]["type"] == "session"

    def test_subscribe_unsubscribe(self):
        """Test node subscription to rooms."""
        self.room_manager.create_room("test_room", "session")

        self.room_manager.subscribe_node_to_room("node123", "test_room")
        assert "node123" in self.room_manager.room_subscriptions["test_room"]
        assert "test_room" in self.room_manager.node_subscriptions["node123"]

        self.room_manager.unsubscribe_node_from_room("node123", "test_room")
        assert "node123" not in self.room_manager.room_subscriptions["test_room"]
        assert "test_room" not in self.room_manager.node_subscriptions["node123"]


class TestMessageBroker:
    """Test MessageBroker functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.broker = MessageBroker(max_workers=1)

    @pytest.mark.asyncio
    async def test_publish(self):
        """Test message publishing."""
        message = WebSocketMessage(
            type="test.message",
            data={"test": "data"}
        )

        await self.broker.publish(message, "broadcast")

        # Check queue has message
        assert self.broker.message_queue.qsize() == 1

    def test_compression(self):
        """Test message compression."""
        message = WebSocketMessage(
            type="test.message",
            data={"large_data": "x" * 2000}  # Large message
        )

        compressed = self.broker._compress_message(message)

        assert compressed.type == "compressed.test.message"
        assert "compressed" in compressed.data
        assert "data" in compressed.data


class TestHeartbeatManager:
    """Test HeartbeatManager functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.heartbeat_manager = HeartbeatManager()

    def test_record_heartbeat(self):
        """Test heartbeat recording."""
        self.heartbeat_manager.record_heartbeat("node123")

        assert "node123" in self.heartbeat_manager.last_heartbeats
        assert "node123" in self.heartbeat_manager.missed_heartbeats
        assert self.heartbeat_manager.missed_heartbeats["node123"] == 0

    def test_heartbeat_status(self):
        """Test heartbeat status retrieval."""
        from datetime import datetime, timedelta

        # Test unknown node
        status = self.heartbeat_manager.get_heartbeat_status("unknown")
        assert status["status"] == "unknown"

        # Test healthy node
        past_time = datetime.utcnow() - timedelta(seconds=10)
        self.heartbeat_manager.last_heartbeats["node123"] = past_time

        status = self.heartbeat_manager.get_heartbeat_status("node123")
        assert status["status"] == "healthy"


class TestWebSocketMessageFactory:
    """Test WebSocketMessageFactory functionality."""

    def test_create_session_update(self):
        """Test session update message creation."""
        message = WebSocketMessageFactory.create_session_update(
            "session123", "status_changed", {"status": "running"}
        )

        assert message.type == "session.update"
        assert message.session_id == "session123"
        assert message.data["update_type"] == "status_changed"
        assert message.data["data"]["status"] == "running"

    def test_create_training_metrics(self):
        """Test training metrics message creation."""
        metrics = {"accuracy": 0.95, "loss": 0.05}
        message = WebSocketMessageFactory.create_training_metrics(
            "session123", 1, metrics
        )

        assert message.type == "training.metrics"
        assert message.session_id == "session123"
        assert message.data["round_number"] == 1
        assert message.data["metrics"] == metrics

    def test_create_node_status(self):
        """Test node status message creation."""
        message = WebSocketMessageFactory.create_node_status(
            "node123", "online", {"cpu": 80}
        )

        assert message.type == "node.status"
        assert message.node_id == "node123"
        assert message.data["status"] == "online"
        assert message.data["data"]["cpu"] == 80

    def test_create_reward_notification(self):
        """Test reward notification message creation."""
        message = WebSocketMessageFactory.create_reward_notification(
            "node123", 100.0, "training_completed"
        )

        assert message.type == "reward.earned"
        assert message.node_id == "node123"
        assert message.data["amount"] == 100.0
        assert message.data["reason"] == "training_completed"

    def test_create_system_alert(self):
        """Test system alert message creation."""
        message = WebSocketMessageFactory.create_system_alert(
            "maintenance", "System maintenance in 30 minutes"
        )

        assert message.type == "system.alert"
        assert message.data["alert_type"] == "maintenance"
        assert "System maintenance" in message.data["message"]


class TestMessageTypes:
    """Test message type utilities."""

    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.SESSION_UPDATE.value == "session.update"
        assert MessageType.TRAINING_METRICS.value == "training.metrics"
        assert MessageType.PING.value == "ping"
        assert MessageType.PONG.value == "pong"

    def test_get_message_type(self):
        """Test message type retrieval."""
        from ..message_types import get_message_type

        msg_type = get_message_type("session.update")
        assert msg_type == MessageType.SESSION_UPDATE

        unknown_type = get_message_type("unknown.type")
        assert unknown_type is None

    def test_get_message_priority(self):
        """Test message priority retrieval."""
        priority = get_message_priority(MessageType.SYSTEM_ALERT)
        assert priority == MessagePriority.CRITICAL

        normal_priority = get_message_priority(MessageType.SESSION_UPDATE)
        assert normal_priority == MessagePriority.NORMAL


# Integration test
@pytest.mark.asyncio
async def test_websocket_integration():
    """Test WebSocket integration with all components."""
    # This would require a test WebSocket server
    # For now, just test component interactions

    # Test message flow
    message = WebSocketMessageFactory.create_session_update(
        "session123", "started", {"participants": 5}
    )

    # Test room subscription
    room_manager.create_room("session_session123", "session")
    room_manager.subscribe_node_to_room("node123", "session_session123")

    assert "node123" in room_manager.get_room_nodes("session_session123")

    # Test heartbeat
    heartbeat_manager.record_heartbeat("node123")
    status = heartbeat_manager.get_heartbeat_status("node123")
    assert status["status"] == "healthy"

    # Cleanup
    room_manager.delete_room("session_session123")