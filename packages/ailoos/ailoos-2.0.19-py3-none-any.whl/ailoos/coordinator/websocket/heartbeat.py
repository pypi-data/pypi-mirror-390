"""
Heartbeat and reconnection management for WebSocket connections.
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import json

# from .manager import manager  # Commented out to avoid circular import
from .message_types import WebSocketMessage, MessageType
from ..config.settings import settings


class HeartbeatManager:
    """Manages heartbeat monitoring and automatic reconnection."""

    def __init__(self):
        self.heartbeat_interval = settings.coordinator.heartbeat_interval_seconds
        self.timeout_threshold = settings.coordinator.node_timeout_seconds
        self.reconnection_enabled = True
        self.max_reconnection_attempts = 3
        self.reconnection_delay = 5  # seconds

        # Heartbeat tracking
        self.last_heartbeats: Dict[str, datetime] = {}
        self.missed_heartbeats: Dict[str, int] = {}
        self.reconnection_attempts: Dict[str, int] = {}

        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start heartbeat monitoring."""
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        self.cleanup_task = asyncio.create_task(self._cleanup_monitor())
        print(f"Heartbeat manager started (interval: {self.heartbeat_interval}s, timeout: {self.timeout_threshold}s)")

    async def stop(self):
        """Stop heartbeat monitoring."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        print("Heartbeat manager stopped")

    def record_heartbeat(self, node_id: str):
        """Record a heartbeat from a node."""
        self.last_heartbeats[node_id] = datetime.utcnow()
        self.missed_heartbeats[node_id] = 0  # Reset missed count
        self.reconnection_attempts[node_id] = 0  # Reset reconnection attempts

    def get_heartbeat_status(self, node_id: str) -> Dict[str, any]:
        """Get heartbeat status for a node."""
        last_heartbeat = self.last_heartbeats.get(node_id)
        if not last_heartbeat:
            return {"status": "unknown", "last_heartbeat": None, "missed": 0}

        now = datetime.utcnow()
        time_since_heartbeat = (now - last_heartbeat).total_seconds()
        missed = int(time_since_heartbeat / self.heartbeat_interval)

        if time_since_heartbeat > self.timeout_threshold:
            status = "disconnected"
        elif missed > 0:
            status = "delayed"
        else:
            status = "healthy"

        return {
            "status": status,
            "last_heartbeat": last_heartbeat.isoformat(),
            "time_since_heartbeat": time_since_heartbeat,
            "missed_heartbeats": missed,
            "reconnection_attempts": self.reconnection_attempts.get(node_id, 0)
        }

    async def _heartbeat_monitor(self):
        """Monitor heartbeats and send ping messages."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                # Send ping to all active connections
                await self._send_pings()

                # Check for missed heartbeats
                await self._check_missed_heartbeats()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in heartbeat monitor: {e}")

    async def _send_pings(self):
        """Send ping messages to all connected nodes."""
        ping_message = WebSocketMessage(
            type=MessageType.PING.value,
            data={"timestamp": datetime.utcnow().isoformat()}
        )

        # Send ping to all active connections - simplified
        # for session_id, connections in manager.active_connections.items():
        #     for node_id, websocket in connections.items():
        #         try:
        #             await manager.send_personal_message(ping_message, session_id, node_id)
        #         except Exception as e:
        #             print(f"Failed to send ping to {node_id}: {e}")
        print("Would send ping messages")

    async def _check_missed_heartbeats(self):
        """Check for nodes with missed heartbeats."""
        now = datetime.utcnow()

        for node_id, last_heartbeat in list(self.last_heartbeats.items()):
            time_since_heartbeat = (now - last_heartbeat).total_seconds()

            if time_since_heartbeat > self.timeout_threshold:
                # Node has timed out
                missed_count = self.missed_heartbeats.get(node_id, 0) + 1
                self.missed_heartbeats[node_id] = missed_count

                if missed_count == 1:  # Only log once per timeout
                    print(f"Node {node_id} heartbeat timeout (last: {last_heartbeat.isoformat()})")

                    # Send disconnect notification
                    disconnect_message = WebSocketMessage(
                        type=MessageType.NODE_DISCONNECT.value,
                        node_id=node_id,
                        data={
                            "reason": "heartbeat_timeout",
                            "last_heartbeat": last_heartbeat.isoformat(),
                            "timeout_threshold": self.timeout_threshold
                        }
                    )

                    # Broadcast to all sessions this node was in - simplified
                    # sessions = manager.get_node_sessions(node_id)
                    sessions = []  # Placeholder
                    for session_id in sessions:
                        # await manager.broadcast_to_session(disconnect_message, session_id)  # Commented out
                        print(f"Would broadcast disconnect for {node_id}")

    async def _cleanup_monitor(self):
        """Monitor and cleanup stale connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Get stale connections from manager - simplified
                # stale_connections = manager.get_stale_connections(self.timeout_threshold)
                stale_connections = []  # Placeholder

                for session_id, node_id in stale_connections:
                    print(f"Cleaning up stale connection for node {node_id} in session {session_id}")

                    # Attempt reconnection if enabled
                    if self.reconnection_enabled:
                        await self._attempt_reconnection(node_id, session_id)
                    else:
                        # Just disconnect
                        # manager.disconnect(session_id, node_id)  # Commented out
                        print(f"Would disconnect {node_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in cleanup monitor: {e}")

    async def _attempt_reconnection(self, node_id: str, session_id: str):
        """Attempt to reconnect a timed out node."""
        attempts = self.reconnection_attempts.get(node_id, 0)

        if attempts >= self.max_reconnection_attempts:
            print(f"Max reconnection attempts reached for node {node_id}, disconnecting")
            # manager.disconnect(session_id, node_id)  # Commented out
            return

        self.reconnection_attempts[node_id] = attempts + 1

        print(f"Attempting reconnection for node {node_id} (attempt {attempts + 1}/{self.max_reconnection_attempts})")

        # Send reconnection notification
        reconnect_message = WebSocketMessage(
            type=MessageType.NODE_RECONNECT.value,
            node_id=node_id,
            data={
                "attempt": attempts + 1,
                "max_attempts": self.max_reconnection_attempts,
                "delay": self.reconnection_delay
            }
        )

        # Broadcast reconnection attempt - simplified
        # await manager.broadcast_to_session(reconnect_message, session_id)  # Commented out
        print(f"Would broadcast reconnection for {node_id}")

        # Wait before next attempt
        await asyncio.sleep(self.reconnection_delay)

    def get_all_heartbeat_status(self) -> Dict[str, Dict[str, any]]:
        """Get heartbeat status for all nodes."""
        status = {}
        all_node_ids = set()

        # Collect all known nodes
        all_node_ids.update(self.last_heartbeats.keys())
        # all_node_ids.update(manager.active_connections.keys())  # Commented out

        for node_id in all_node_ids:
            status[node_id] = self.get_heartbeat_status(node_id)

        return status

    def reset_node_heartbeat(self, node_id: str):
        """Reset heartbeat tracking for a node."""
        if node_id in self.last_heartbeats:
            del self.last_heartbeats[node_id]
        if node_id in self.missed_heartbeats:
            del self.missed_heartbeats[node_id]
        if node_id in self.reconnection_attempts:
            del self.reconnection_attempts[node_id]


# Global heartbeat manager instance
heartbeat_manager = HeartbeatManager()