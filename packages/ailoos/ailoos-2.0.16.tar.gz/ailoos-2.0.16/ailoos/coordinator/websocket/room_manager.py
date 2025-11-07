"""
Room Manager for WebSocket channels and subscriptions.
"""

from typing import Dict, Set, List, Optional
from enum import Enum
import asyncio
from datetime import datetime

# from .manager import manager  # Commented out to avoid circular import
from ..models.schemas import WebSocketMessage


class RoomType(Enum):
    """Types of WebSocket rooms."""
    SESSION = "session"
    NODE = "node"
    GLOBAL = "global"
    METRICS = "metrics"
    ADMIN = "admin"


class RoomManager:
    """Manages WebSocket rooms and subscriptions."""

    def __init__(self):
        # Room subscriptions: room_id -> set of node_ids
        self.room_subscriptions: Dict[str, Set[str]] = {}
        # Node subscriptions: node_id -> set of room_ids
        self.node_subscriptions: Dict[str, Set[str]] = {}
        # Room metadata: room_id -> room_info
        self.room_metadata: Dict[str, Dict] = {}
        # Event subscriptions: event_type -> set of node_ids
        self.event_subscriptions: Dict[str, Set[str]] = {}

    def create_room(self, room_id: str, room_type: RoomType, metadata: Optional[Dict] = None):
        """Create a new room."""
        if room_id not in self.room_subscriptions:
            self.room_subscriptions[room_id] = set()
            self.room_metadata[room_id] = {
                "type": room_type.value,
                "created_at": datetime.utcnow(),
                "metadata": metadata or {},
                "active_connections": 0
            }
            print(f"Created room {room_id} of type {room_type.value}")

    def delete_room(self, room_id: str):
        """Delete a room and remove all subscriptions."""
        if room_id in self.room_subscriptions:
            # Remove all node subscriptions to this room
            for node_id in self.room_subscriptions[room_id]:
                if node_id in self.node_subscriptions:
                    self.node_subscriptions[node_id].discard(room_id)
                    if not self.node_subscriptions[node_id]:
                        del self.node_subscriptions[node_id]

            del self.room_subscriptions[room_id]
            if room_id in self.room_metadata:
                del self.room_metadata[room_id]
            print(f"Deleted room {room_id}")

    def subscribe_node_to_room(self, node_id: str, room_id: str):
        """Subscribe a node to a room."""
        # Create room if it doesn't exist
        if room_id not in self.room_subscriptions:
            room_type = self._infer_room_type(room_id)
            self.create_room(room_id, room_type)

        # Add subscription
        if node_id not in self.node_subscriptions:
            self.node_subscriptions[node_id] = set()
        self.node_subscriptions[node_id].add(room_id)

        self.room_subscriptions[room_id].add(node_id)
        self.room_metadata[room_id]["active_connections"] += 1

        print(f"Node {node_id} subscribed to room {room_id}")

    def unsubscribe_node_from_room(self, node_id: str, room_id: str):
        """Unsubscribe a node from a room."""
        if node_id in self.node_subscriptions:
            self.node_subscriptions[node_id].discard(room_id)
            if not self.node_subscriptions[node_id]:
                del self.node_subscriptions[node_id]

        if room_id in self.room_subscriptions:
            self.room_subscriptions[room_id].discard(node_id)
            self.room_metadata[room_id]["active_connections"] -= 1

            # Clean up empty rooms
            if not self.room_subscriptions[room_id]:
                self.delete_room(room_id)

        print(f"Node {node_id} unsubscribed from room {room_id}")

    def subscribe_to_event(self, node_id: str, event_type: str):
        """Subscribe a node to specific event types."""
        if event_type not in self.event_subscriptions:
            self.event_subscriptions[event_type] = set()
        self.event_subscriptions[event_type].add(node_id)
        print(f"Node {node_id} subscribed to event {event_type}")

    def unsubscribe_from_event(self, node_id: str, event_type: str):
        """Unsubscribe a node from specific event types."""
        if event_type in self.event_subscriptions:
            self.event_subscriptions[event_type].discard(node_id)
            if not self.event_subscriptions[event_type]:
                del self.event_subscriptions[event_type]
        print(f"Node {node_id} unsubscribed from event {event_type}")

    async def broadcast_to_room(self, room_id: str, message: WebSocketMessage, exclude_node: str = None):
        """Broadcast message to all nodes in a room."""
        if room_id not in self.room_subscriptions:
            return

        # Get session_id from room_id for compatibility
        session_id = self._get_session_id_from_room(room_id)

        for node_id in self.room_subscriptions[room_id]:
            if node_id != exclude_node:
                # await manager.send_personal_message(message, session_id, node_id)  # Commented out - manager not available
                print(f"Would send message to {node_id} in room {room_id}")

    async def broadcast_event(self, event_type: str, message: WebSocketMessage):
        """Broadcast event to all subscribed nodes."""
        if event_type not in self.event_subscriptions:
            return

        # Send to all subscribed nodes across their sessions
        for node_id in self.event_subscriptions[event_type]:
            # Find active sessions for this node
            # sessions = manager.get_node_sessions(node_id)  # Commented out - manager not available
            sessions = []  # Placeholder
            for session_id in sessions:
                # await manager.send_personal_message(message, session_id, node_id)  # Commented out
                print(f"Would send event {event_type} to {node_id}")

    def get_room_nodes(self, room_id: str) -> List[str]:
        """Get list of nodes subscribed to a room."""
        if room_id in self.room_subscriptions:
            return list(self.room_subscriptions[room_id])
        return []

    def get_node_rooms(self, node_id: str) -> List[str]:
        """Get list of rooms a node is subscribed to."""
        if node_id in self.node_subscriptions:
            return list(self.node_subscriptions[node_id])
        return []

    def get_event_subscribers(self, event_type: str) -> List[str]:
        """Get list of nodes subscribed to an event type."""
        if event_type in self.event_subscriptions:
            return list(self.event_subscriptions[event_type])
        return []

    def _infer_room_type(self, room_id: str) -> RoomType:
        """Infer room type from room_id."""
        if room_id.startswith("session_"):
            return RoomType.SESSION
        elif room_id.startswith("node_"):
            return RoomType.NODE
        elif room_id == "global":
            return RoomType.GLOBAL
        elif room_id == "metrics":
            return RoomType.METRICS
        elif room_id.startswith("admin_"):
            return RoomType.ADMIN
        else:
            return RoomType.SESSION  # Default

    def _get_session_id_from_room(self, room_id: str) -> str:
        """Extract session_id from room_id for compatibility."""
        if room_id.startswith("session_"):
            return room_id.replace("session_", "")
        elif room_id.startswith("node_"):
            return room_id  # Use room_id as session_id for node rooms
        else:
            return room_id  # For global, metrics, etc.

    def cleanup_node_subscriptions(self, node_id: str):
        """Clean up all subscriptions for a node."""
        if node_id in self.node_subscriptions:
            rooms = list(self.node_subscriptions[node_id])
            for room_id in rooms:
                self.unsubscribe_node_from_room(node_id, room_id)

        # Clean up event subscriptions
        for event_type in list(self.event_subscriptions.keys()):
            self.event_subscriptions[event_type].discard(node_id)
            if not self.event_subscriptions[event_type]:
                del self.event_subscriptions[event_type]


# Global room manager instance
room_manager = RoomManager()