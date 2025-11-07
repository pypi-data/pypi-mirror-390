"""
Load tests for WebSocket functionality.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock
from concurrent.futures import ThreadPoolExecutor
import statistics

from ..manager import ConnectionManager
from ..room_manager import RoomManager
from ..message_broker import MessageBroker
from ..heartbeat import HeartbeatManager
from ..message_types import WebSocketMessageFactory


class TestWebSocketLoadConnectionManager:
    """Load tests for ConnectionManager."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()

    @pytest.mark.asyncio
    async def test_massive_connections(self):
        """Test handling 1000+ simultaneous connections."""
        start_time = time.time()

        # Create 1000 mock connections
        for i in range(1000):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{i}"
            token_data.permissions = ["node:read"]

            await self.manager.connect(mock_ws, f"session{i % 10}", f"node{i}", token_data)

        connection_time = time.time() - start_time

        # Verify connections
        assert len(self.manager.active_connections) == 10  # 10 sessions
        total_connections = sum(len(conns) for conns in self.manager.active_connections.values())
        assert total_connections == 1000

        print(f"Created 1000 connections in {connection_time:.2f} seconds")

    @pytest.mark.asyncio
    async def test_connection_cleanup_load(self):
        """Test connection cleanup under load."""
        # Setup connections
        for i in range(500):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{i}"
            token_data.permissions = ["node:read"]

            await self.manager.connect(mock_ws, f"session{i % 5}", f"node{i}", token_data)

        start_time = time.time()

        # Disconnect all connections
        for i in range(500):
            self.manager.disconnect(f"session{i % 5}", f"node{i}")

        cleanup_time = time.time() - start_time

        # Verify cleanup
        assert len(self.manager.active_connections) == 0
        assert len(self.manager.node_subscriptions) == 0

        print(f"Cleaned up 500 connections in {cleanup_time:.2f} seconds")


class TestWebSocketLoadMessageBroker:
    """Load tests for MessageBroker."""

    def setup_method(self):
        """Setup test fixtures."""
        self.broker = MessageBroker(max_workers=4)

    @pytest.mark.asyncio
    async def test_high_message_throughput(self):
        """Test processing 10,000 messages."""
        start_time = time.time()

        # Send 10,000 messages
        for i in range(10000):
            message = WebSocketMessageFactory.create_training_metrics(
                f"session{i % 100}", i % 10, {"accuracy": 0.8 + (i % 20) * 0.005}
            )
            await self.broker.publish(message, "broadcast")

        publish_time = time.time() - start_time

        # Check queue size
        assert self.broker.message_queue.qsize() == 10000

        print(f"Published 10,000 messages in {publish_time:.2f} seconds")

    @pytest.mark.asyncio
    async def test_compression_load(self):
        """Test compression with large messages."""
        # Create 100 large messages
        large_messages = []
        for i in range(100):
            message = WebSocketMessageFactory.create_session_update(
                "session123",
                "large_update",
                {"data": "x" * 5000}  # 5KB of data
            )
            large_messages.append(message)

        start_time = time.time()

        # Compress all messages
        compressed_messages = []
        for msg in large_messages:
            compressed = self.broker._compress_message(msg)
            compressed_messages.append(compressed)

        compression_time = time.time() - start_time

        # Verify compression
        for compressed in compressed_messages:
            assert compressed.type.startswith("compressed.")
            assert "compressed" in compressed.data

        print(f"Compressed 100 large messages in {compression_time:.2f} seconds")


class TestWebSocketLoadRoomManager:
    """Load tests for RoomManager."""

    def setup_method(self):
        """Setup test fixtures."""
        self.room_manager = RoomManager()

    def test_massive_room_subscriptions(self):
        """Test handling 1000+ room subscriptions."""
        start_time = time.time()

        # Create 100 rooms
        for i in range(100):
            self.room_manager.create_room(f"room{i}", "session")

        # Subscribe 1000 nodes across rooms
        for i in range(1000):
            room_id = f"room{i % 100}"
            node_id = f"node{i}"
            self.room_manager.subscribe_node_to_room(node_id, room_id)

        subscription_time = time.time() - start_time

        # Verify subscriptions
        total_subscriptions = sum(len(nodes) for nodes in self.room_manager.room_subscriptions.values())
        assert total_subscriptions == 1000

        print(f"Created 1000 subscriptions in {subscription_time:.2f} seconds")

    def test_room_broadcast_load(self):
        """Test broadcasting to rooms with many subscribers."""
        # Setup room with 100 subscribers
        room_id = "load_test_room"
        self.room_manager.create_room(room_id, "session")

        for i in range(100):
            self.room_manager.subscribe_node_to_room(f"node{i}", room_id)

        # Create broadcast message
        message = WebSocketMessageFactory.create_system_alert(
            "test", "Load test message"
        )

        start_time = time.time()

        # This would normally broadcast, but we'll just test the room lookup
        nodes = self.room_manager.get_room_nodes(room_id)

        lookup_time = time.time() - start_time

        assert len(nodes) == 100
        print(f"Room lookup for 100 nodes took {lookup_time:.4f} seconds")


class TestWebSocketLoadHeartbeat:
    """Load tests for HeartbeatManager."""

    def setup_method(self):
        """Setup test fixtures."""
        self.heartbeat_manager = HeartbeatManager()

    def test_massive_heartbeat_tracking(self):
        """Test heartbeat tracking for 1000 nodes."""
        start_time = time.time()

        # Record heartbeats for 1000 nodes
        for i in range(1000):
            self.heartbeat_manager.record_heartbeat(f"node{i}")

        heartbeat_time = time.time() - start_time

        # Verify heartbeats
        assert len(self.heartbeat_manager.last_heartbeats) == 1000

        print(f"Recorded 1000 heartbeats in {heartbeat_time:.2f} seconds")

    def test_heartbeat_status_load(self):
        """Test heartbeat status retrieval for many nodes."""
        # Setup heartbeats
        for i in range(500):
            self.heartbeat_manager.record_heartbeat(f"node{i}")

        start_time = time.time()

        # Get status for all nodes
        all_status = self.heartbeat_manager.get_all_heartbeat_status()

        status_time = time.time() - start_time

        assert len(all_status) == 500
        print(f"Retrieved heartbeat status for 500 nodes in {status_time:.2f} seconds")


class TestWebSocketLoadIntegration:
    """Integration load tests combining all components."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = ConnectionManager()
        self.room_manager = RoomManager()
        self.heartbeat_manager = HeartbeatManager()
        self.message_broker = MessageBroker(max_workers=4)

    @pytest.mark.asyncio
    async def test_full_system_load(self):
        """Test full system under load with 500 connections."""
        start_time = time.time()

        # Create 500 connections across 10 sessions
        for i in range(500):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{i}"
            token_data.permissions = ["node:read"]

            session_id = f"session{i % 10}"
            node_id = f"node{i}"

            await self.manager.connect(mock_ws, session_id, node_id, token_data)

            # Subscribe to room
            room_id = f"session_{session_id}"
            self.room_manager.subscribe_node_to_room(node_id, room_id)

            # Record heartbeat
            self.heartbeat_manager.record_heartbeat(node_id)

        setup_time = time.time() - start_time

        # Verify setup
        total_connections = sum(len(conns) for conns in self.manager.active_connections.values())
        assert total_connections == 500
        assert len(self.room_manager.room_subscriptions) == 10

        print(f"Setup 500 connections in {setup_time:.2f} seconds")

        # Test message broadcasting
        message_start = time.time()

        # Send 1000 messages
        for i in range(1000):
            message = WebSocketMessageFactory.create_training_metrics(
                f"session{i % 10}", i % 5, {"round": i % 5}
            )
            await self.message_broker.publish(message, "broadcast")

        message_time = time.time() - message_start

        assert self.message_broker.message_queue.qsize() == 1000
        print(f"Published 1000 messages in {message_time:.2f} seconds")

    @pytest.mark.asyncio
    async def test_cleanup_load(self):
        """Test system cleanup under load."""
        # Setup (smaller scale for cleanup test)
        for i in range(200):
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()

            token_data = Mock()
            token_data.sub = f"node{i}"
            token_data.permissions = ["node:read"]

            await self.manager.connect(mock_ws, f"session{i % 5}", f"node{i}", token_data)

        start_time = time.time()

        # Cleanup all connections
        for i in range(200):
            self.manager.disconnect(f"session{i % 5}", f"node{i}")

        cleanup_time = time.time() - start_time

        # Verify cleanup
        assert len(self.manager.active_connections) == 0
        assert len(self.manager.node_subscriptions) == 0

        print(f"Cleaned up 200 connections in {cleanup_time:.2f} seconds")


# Performance benchmarks (would require pytest-benchmark)
@pytest.mark.skip(reason="Benchmark tests require pytest-benchmark plugin")
class TestWebSocketBenchmarks:
    """Performance benchmarks for WebSocket components."""

    def benchmark_connection_creation(self, benchmark):
        """Benchmark connection creation speed."""
        manager = ConnectionManager()

        def create_connection():
            # Synchronous version for benchmarking
            pass

        benchmark(create_connection)

    def benchmark_message_publishing(self, benchmark):
        """Benchmark message publishing speed."""
        broker = MessageBroker(max_workers=1)

        def publish_message():
            # Synchronous version for benchmarking
            pass

        benchmark(publish_message)

    def benchmark_room_operations(self, benchmark):
        """Benchmark room operations speed."""
        room_manager = RoomManager()

        def room_operations():
            # Synchronous version for benchmarking
            pass

        benchmark(room_operations)