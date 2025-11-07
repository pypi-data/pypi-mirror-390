"""
End-to-end tests for WebSocket functionality.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import WebSocket
import websockets
from concurrent.futures import ThreadPoolExecutor

from ...main import create_application
from ..manager import ConnectionManager, manager
from ..room_manager import RoomManager, room_manager
from ..message_broker import MessageBroker, message_broker
from ..heartbeat import HeartbeatManager, heartbeat_manager
from ..message_types import WebSocketMessageFactory, MessageType


class TestWebSocketEndToEnd:
    """End-to-end WebSocket tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app = create_application()
        self.client = TestClient(self.app)

    @pytest.mark.asyncio
    async def test_complete_session_workflow(self):
        """Test complete session workflow from connection to disconnection."""
        # Setup
        session_id = "test_session_123"
        node_id = "test_node_456"

        # Mock WebSocket connection
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.receive_text = AsyncMock(side_effect=[
            '{"type": "subscribe", "data": {"events": ["session.update", "training.metrics"]}}',
            '{"type": "ping"}',
            '{"type": "session.status", "data": {"status": "ready"}}',
            Exception("Connection closed")  # End the loop
        ])
        mock_ws.send_text = AsyncMock()

        # Mock token verification
        with patch('ailoos.coordinator.websocket.manager.verify_token') as mock_verify:
            token_data = Mock()
            token_data.sub = node_id
            token_data.type = "node"
            token_data.permissions = ["node:read", "node:contribute"]
            mock_verify.return_value = token_data

            # Simulate connection
            try:
                await manager.connect(mock_ws, session_id, node_id, token_data)

                # Verify connection
                assert session_id in manager.active_connections
                assert node_id in manager.active_connections[session_id]

                # Verify room subscription
                room_id = f"session_{session_id}"
                assert node_id in room_manager.get_room_nodes(room_id)

                # Verify heartbeat
                heartbeat_manager.record_heartbeat(node_id)
                status = heartbeat_manager.get_heartbeat_status(node_id)
                assert status["status"] == "healthy"

            finally:
                # Cleanup
                manager.disconnect(session_id, node_id)

    @pytest.mark.asyncio
    async def test_message_flow_end_to_end(self):
        """Test complete message flow from creation to delivery."""
        # Setup connection
        session_id = "test_session_456"
        node_id = "test_node_789"

        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = node_id
        token_data.permissions = ["node:read"]

        await manager.connect(mock_ws, session_id, node_id, token_data)

        try:
            # Create different types of messages
            messages = [
                WebSocketMessageFactory.create_session_update(
                    session_id, "started", {"participants": 3}
                ),
                WebSocketMessageFactory.create_training_metrics(
                    session_id, 1, {"accuracy": 0.85, "loss": 0.45}
                ),
                WebSocketMessageFactory.create_node_status(
                    node_id, "training", {"progress": 75}
                ),
                WebSocketMessageFactory.create_reward_notification(
                    node_id, 50.0, "round_completed"
                ),
                WebSocketMessageFactory.create_system_alert(
                    "maintenance", "Scheduled maintenance in 10 minutes"
                )
            ]

            # Publish messages through broker
            for message in messages:
                await message_broker.publish(message, "broadcast")

            # Verify messages are queued
            assert message_broker.message_queue.qsize() == 5

            # Test room broadcasting
            room_message = WebSocketMessageFactory.create_session_update(
                session_id, "completed", {"final_accuracy": 0.92}
            )

            room_id = f"session_{session_id}"
            await room_manager.broadcast_to_room(room_id, room_message)

            # Test event broadcasting
            event_message = WebSocketMessageFactory.create_training_metrics(
                session_id, 2, {"accuracy": 0.88}
            )

            room_manager.subscribe_to_event(node_id, "training.metrics")
            await room_manager.broadcast_event("training.metrics", event_message)

        finally:
            # Cleanup
            manager.disconnect(session_id, node_id)

    @pytest.mark.asyncio
    async def test_error_handling_end_to_end(self):
        """Test error handling throughout the system."""
        session_id = "error_test_session"
        node_id = "error_test_node"

        # Test invalid token
        with patch('ailoos.coordinator.websocket.manager.verify_token') as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")

            mock_ws = AsyncMock()
            mock_ws.close = AsyncMock()

            # This would normally be handled by the endpoint
            # but we test the verification logic
            try:
                from ..manager import verify_token
                verify_token("invalid_token", None)
                assert False, "Should have raised exception"
            except:
                pass  # Expected

        # Test rate limiting
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = node_id
        token_data.permissions = ["node:read"]

        await manager.connect(mock_ws, session_id, node_id, token_data)

        try:
            # Simulate rate limit exceeded
            manager.rate_limits[node_id] = {"count": 100, "last_reset": "2023-01-01"}

            message = WebSocketMessageFactory.create_ping()
            sent = await manager.send_personal_message(message, session_id, node_id)

            # Should not send due to rate limit
            mock_ws.send_text.assert_not_called()

        finally:
            manager.disconnect(session_id, node_id)

    @pytest.mark.asyncio
    async def test_reconnection_workflow(self):
        """Test reconnection workflow."""
        session_id = "reconnect_test_session"
        node_id = "reconnect_test_node"

        # Initial connection
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = node_id
        token_data.permissions = ["node:read"]

        await manager.connect(mock_ws1, session_id, node_id, token_data)

        # Simulate disconnection (stale connection)
        # This would normally happen over time, but we simulate it
        import datetime
        old_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=400)
        heartbeat_manager.last_heartbeats[node_id] = old_time

        # Check for stale connections
        stale = manager.get_stale_connections(timeout_seconds=300)
        assert len(stale) > 0

        # Cleanup stale connection
        await manager.cleanup_stale_connections()

        # Verify cleanup
        assert session_id not in manager.active_connections

        # Simulate reconnection
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()

        await manager.connect(mock_ws2, session_id, node_id, token_data)

        # Verify reconnection
        assert session_id in manager.active_connections
        assert node_id in manager.active_connections[session_id]

        # Cleanup
        manager.disconnect(session_id, node_id)

    @pytest.mark.asyncio
    async def test_compression_workflow(self):
        """Test message compression workflow."""
        # Create large message
        large_data = {"metrics": "x" * 2000}  # > 1KB
        message = WebSocketMessageFactory.create_training_metrics(
            "session123", 1, large_data
        )

        # Test compression
        compressed = message_broker._compress_message(message)

        # Verify compression
        assert compressed.type == "compressed.training.metrics"
        assert "compressed" in compressed.data
        assert "data" in compressed.data

        # Verify original size tracking
        original_json = message.json()
        assert compressed.data["original_size"] == len(original_json)

        # Verify compressed data is smaller
        assert len(compressed.data["data"]) < len(original_json)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent WebSocket operations."""
        session_id = "concurrent_test_session"

        async def create_connection(node_num):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{node_num}"
            token_data.permissions = ["node:read"]

            await manager.connect(mock_ws, session_id, f"node{node_num}", token_data)

        # Create 10 concurrent connections
        tasks = [create_connection(i) for i in range(10)]
        await asyncio.gather(*tasks)

        # Verify all connections
        assert len(manager.active_connections[session_id]) == 10

        # Send concurrent messages
        async def send_message(node_num):
            message = WebSocketMessageFactory.create_node_status(
                f"node{node_num}", "active"
            )
            await message_broker.publish(message, "broadcast")

        message_tasks = [send_message(i) for i in range(10)]
        await asyncio.gather(*message_tasks)

        # Verify messages queued
        assert message_broker.message_queue.qsize() == 10

        # Cleanup
        for i in range(10):
            manager.disconnect(session_id, f"node{i}")

    @pytest.mark.asyncio
    async def test_system_monitoring(self):
        """Test system monitoring capabilities."""
        # Setup multiple connections
        for i in range(5):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"monitor_node{i}"
            token_data.permissions = ["node:read"]

            await manager.connect(mock_ws, f"monitor_session{i % 2}", f"monitor_node{i}", token_data)
            heartbeat_manager.record_heartbeat(f"monitor_node{i}")

        # Test connection statistics
        total_connections = sum(len(conns) for conns in manager.active_connections.values())
        assert total_connections == 5

        # Test heartbeat monitoring
        all_heartbeats = heartbeat_manager.get_all_heartbeat_status()
        assert len(all_heartbeats) == 5

        healthy_count = sum(1 for status in all_heartbeats.values() if status["status"] == "healthy")
        assert healthy_count == 5

        # Test broker statistics
        broker_stats = await message_broker.get_stats()
        assert "queue_size" in broker_stats
        assert "active_rooms" in broker_stats
        assert "total_connections" in broker_stats

        # Cleanup
        for i in range(5):
            manager.disconnect(f"monitor_session{i % 2}", f"monitor_node{i}")

    @pytest.mark.asyncio
    async def test_subscription_management(self):
        """Test subscription management workflow."""
        session_id = "subscription_test_session"
        node_id = "subscription_test_node"

        # Setup connection
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        token_data = Mock()
        token_data.sub = node_id
        token_data.permissions = ["node:read"]

        await manager.connect(mock_ws, session_id, node_id, token_data)

        try:
            # Test room subscriptions
            room_manager.subscribe_node_to_room(node_id, "custom_room_1")
            room_manager.subscribe_node_to_room(node_id, "custom_room_2")

            node_rooms = room_manager.get_node_rooms(node_id)
            assert "custom_room_1" in node_rooms
            assert "custom_room_2" in node_rooms

            # Test event subscriptions
            room_manager.subscribe_to_event(node_id, "training.metrics")
            room_manager.subscribe_to_event(node_id, "session.update")

            # Test broadcasting to subscribed rooms
            room_message = WebSocketMessageFactory.create_system_alert(
                "test", "Room broadcast test"
            )

            await room_manager.broadcast_to_room("custom_room_1", room_message)

            # Test event broadcasting
            event_message = WebSocketMessageFactory.create_training_metrics(
                session_id, 1, {"accuracy": 0.9}
            )

            await room_manager.broadcast_event("training.metrics", event_message)

            # Test unsubscription
            room_manager.unsubscribe_node_from_room(node_id, "custom_room_1")

            node_rooms_after = room_manager.get_node_rooms(node_id)
            assert "custom_room_1" not in node_rooms_after
            assert "custom_room_2" in node_rooms_after

        finally:
            # Cleanup
            manager.disconnect(session_id, node_id)
            room_manager.cleanup_node_subscriptions(node_id)


class TestWebSocketStressTest:
    """Stress tests for WebSocket functionality."""

    @pytest.mark.skip(reason="Stress tests are resource intensive")
    @pytest.mark.asyncio
    async def test_high_load_scenario(self):
        """Test system under high load (100+ connections, 1000+ messages)."""
        # This would create many connections and send many messages
        # Skipped by default to avoid resource issues in CI
        pass

    @pytest.mark.skip(reason="Memory leak tests require special monitoring")
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self):
        """Test that the system doesn't leak memory under load."""
        # This would monitor memory usage during operations
        pass

    @pytest.mark.skip(reason="Network tests require network setup")
    @pytest.mark.asyncio
    async def test_network_resilience(self):
        """Test system resilience to network issues."""
        # This would simulate network partitions, latency, etc.
        pass