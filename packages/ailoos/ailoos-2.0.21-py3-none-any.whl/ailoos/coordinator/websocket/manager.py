"""
WebSocket connection manager for real-time communication.
"""

import json
import asyncio
from typing import Dict, List, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session

from ..models.schemas import WebSocketMessage
from ..auth.jwt import verify_token, TokenData
from ..config.settings import settings
from ..database.connection import get_db
from .room_manager import room_manager
from .message_broker import message_broker
from .heartbeat import heartbeat_manager
from .message_types import MessageType


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # Active connections by session_id -> node_id -> websocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Node subscriptions: node_id -> set of session_ids
        self.node_subscriptions: Dict[str, Set[str]] = {}
        # Connection metadata: session_id -> node_id -> connection_info
        self.connection_metadata: Dict[str, Dict[str, Dict]] = {}
        # Rate limiting: node_id -> message_count, last_reset
        self.rate_limits: Dict[str, Dict[str, int]] = {}
        # Heartbeat tracking: session_id -> node_id -> last_heartbeat
        self.heartbeats: Dict[str, Dict[str, datetime]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, node_id: str, token_data: TokenData):
        """Connect a WebSocket for a specific session and node with authentication."""
        await websocket.accept()

        # Initialize session connections if not exists
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
            self.connection_metadata[session_id] = {}
            self.heartbeats[session_id] = {}

        # Add connection
        self.active_connections[session_id][node_id] = websocket

        # Store connection metadata
        self.connection_metadata[session_id][node_id] = {
            "connected_at": datetime.utcnow(),
            "token_data": token_data,
            "ip_address": getattr(websocket, 'client', {}).get('host', 'unknown'),
            "user_agent": getattr(websocket, 'headers', {}).get('user-agent', 'unknown')
        }

        # Initialize rate limiting
        if node_id not in self.rate_limits:
            self.rate_limits[node_id] = {"count": 0, "last_reset": datetime.utcnow()}

        # Track node subscriptions
        if node_id not in self.node_subscriptions:
            self.node_subscriptions[node_id] = set()
        self.node_subscriptions[node_id].add(session_id)

        # Subscribe to room
        room_id = f"session_{session_id}"
        room_manager.subscribe_node_to_room(node_id, room_id)

        # Set initial heartbeat
        self.heartbeats[session_id][node_id] = datetime.utcnow()
        heartbeat_manager.record_heartbeat(node_id)

        print(f"Node {node_id} connected to session {session_id} with permissions: {token_data.permissions}")

    def disconnect(self, session_id: str, node_id: str):
        """Disconnect a WebSocket connection."""
        # Calculate connection duration
        duration = None
        if (session_id in self.connection_metadata and
            node_id in self.connection_metadata[session_id]):
            connected_at = self.connection_metadata[session_id][node_id]["connected_at"]
            duration = datetime.utcnow() - connected_at

        if session_id in self.active_connections:
            if node_id in self.active_connections[session_id]:
                del self.active_connections[session_id][node_id]

                # Clean up empty session connections
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                    if session_id in self.connection_metadata:
                        del self.connection_metadata[session_id]
                    if session_id in self.heartbeats:
                        del self.heartbeats[session_id]

        # Remove from node subscriptions
        if node_id in self.node_subscriptions:
            self.node_subscriptions[node_id].discard(session_id)
            if not self.node_subscriptions[node_id]:
                del self.node_subscriptions[node_id]

        # Unsubscribe from room
        room_id = f"session_{session_id}"
        room_manager.unsubscribe_node_from_room(node_id, room_id)

        # Clean up room manager subscriptions
        room_manager.cleanup_node_subscriptions(node_id)

        # Reset heartbeat tracking
        heartbeat_manager.reset_node_heartbeat(node_id)

        # Clean up rate limiting and heartbeats
        if node_id in self.rate_limits:
            del self.rate_limits[node_id]

        if session_id in self.heartbeats and node_id in self.heartbeats[session_id]:
            del self.heartbeats[session_id][node_id]

        duration_str = f" after {duration.total_seconds():.1f}s" if duration else ""
        print(f"Node {node_id} disconnected from session {session_id}{duration_str}")

    async def send_personal_message(self, message: WebSocketMessage, session_id: str, node_id: str):
        """Send message to a specific node in a session."""
        if (session_id in self.active_connections and
            node_id in self.active_connections[session_id]):
            websocket = self.active_connections[session_id][node_id]

            # Check rate limiting
            if not self._check_rate_limit(node_id):
                print(f"Rate limit exceeded for node {node_id}")
                return

            await websocket.send_text(message.json())
            self.rate_limits[node_id]["count"] += 1

    async def broadcast_to_session(self, message: WebSocketMessage, session_id: str, exclude_node: str = None):
        """Broadcast message to all nodes in a session."""
        if session_id in self.active_connections:
            for node_id, websocket in self.active_connections[session_id].items():
                if node_id != exclude_node:
                    try:
                        await websocket.send_text(message.json())
                    except Exception as e:
                        print(f"Failed to send message to {node_id}: {e}")

    async def broadcast_to_node_sessions(self, message: WebSocketMessage, node_id: str):
        """Broadcast message to all sessions a node is subscribed to."""
        if node_id in self.node_subscriptions:
            for session_id in self.node_subscriptions[node_id]:
                await self.send_personal_message(message, session_id, node_id)

    async def send_session_update(self, session_id: str, update_type: str, data: dict):
        """Send session update to all connected nodes."""
        message = WebSocketMessage(
            type=f"session.{update_type}",
            session_id=session_id,
            data=data
        )
        await self.broadcast_to_session(message, session_id)

    async def send_node_notification(self, node_id: str, notification_type: str, data: dict):
        """Send notification to a specific node across all their sessions."""
        message = WebSocketMessage(
            type=f"node.{notification_type}",
            node_id=node_id,
            data=data
        )
        await self.broadcast_to_node_sessions(message, node_id)

    def get_session_connections(self, session_id: str) -> List[str]:
        """Get list of connected node IDs for a session."""
        if session_id in self.active_connections:
            return list(self.active_connections[session_id].keys())
        return []

    def get_node_sessions(self, node_id: str) -> List[str]:
        """Get list of sessions a node is connected to."""
        if node_id in self.node_subscriptions:
            return list(self.node_subscriptions[node_id])
        return []

    def _check_rate_limit(self, node_id: str, max_messages: int = 100, window_seconds: int = 60) -> bool:
        """Check if node has exceeded rate limit."""
        if node_id not in self.rate_limits:
            return True

        now = datetime.utcnow()
        rate_data = self.rate_limits[node_id]

        # Reset counter if window has passed
        if (now - rate_data["last_reset"]).total_seconds() > window_seconds:
            rate_data["count"] = 0
            rate_data["last_reset"] = now

        return rate_data["count"] < max_messages

    def update_heartbeat(self, session_id: str, node_id: str):
        """Update heartbeat timestamp for a connection."""
        if session_id not in self.heartbeats:
            self.heartbeats[session_id] = {}
        self.heartbeats[session_id][node_id] = datetime.utcnow()

    def get_stale_connections(self, timeout_seconds: int = 300) -> List[tuple]:
        """Get list of stale connections that haven't sent heartbeat."""
        stale_connections = []
        now = datetime.utcnow()

        for session_id, node_heartbeats in self.heartbeats.items():
            for node_id, last_heartbeat in node_heartbeats.items():
                if (now - last_heartbeat).total_seconds() > timeout_seconds:
                    stale_connections.append((session_id, node_id))

        return stale_connections

    async def cleanup_stale_connections(self):
        """Clean up connections that have exceeded heartbeat timeout."""
        stale_connections = self.get_stale_connections()

        for session_id, node_id in stale_connections:
            print(f"Cleaning up stale connection for node {node_id} in session {session_id}")
            self.disconnect(session_id, node_id)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str, node_id: str, token: str, db: Session = None):
    """WebSocket endpoint for session communication with authentication."""
    try:
        # Verify JWT token
        token_data = verify_token(token, db)
        if token_data.type != "node":
            await websocket.close(code=1008, reason="Invalid token type")
            return

        # Check if node_id matches token subject
        if token_data.sub != node_id:
            await websocket.close(code=1008, reason="Node ID mismatch")
            return

        await manager.connect(websocket, session_id, node_id, token_data)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                    message = WebSocketMessage(**message_data)

                    # Update heartbeat on any message
                    manager.update_heartbeat(session_id, node_id)
                    heartbeat_manager.record_heartbeat(node_id)

                    # Handle different message types
                    if message.type == "ping":
                        # Respond with pong
                        pong_message = WebSocketMessage(
                            type="pong",
                            session_id=session_id,
                            node_id=node_id,
                            data={"timestamp": datetime.utcnow().isoformat()}
                        )
                        await manager.send_personal_message(pong_message, session_id, node_id)

                    else:
                        # Use real message handlers
                        from .message_handlers import get_message_handler
                        handler = get_message_handler(message.type)
                        if handler:
                            await handler.handle(message)
                        else:
                            # Fallback for unhandled messages
                            print(f"No handler found for message type: {message.type}")

                except json.JSONDecodeError:
                    # Invalid JSON, ignore
                    continue
                except Exception as e:
                    print(f"Error processing message from {node_id}: {e}")
                    continue

        except WebSocketDisconnect:
            manager.disconnect(session_id, node_id)

    except Exception as e:
        print(f"Authentication failed for node {node_id}: {e}")
        await websocket.close(code=1008, reason="Authentication failed")


# FastAPI router for WebSocket endpoints
websocket_router = APIRouter()

@websocket_router.websocket("/ws/sessions/{session_id}")
async def session_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for session participation with authentication."""
    # Extract node_id from JWT token
    try:
        token_data = verify_token(token, db)
        node_id = token_data.sub
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await websocket_endpoint(websocket, session_id, node_id, token, db)

@websocket_router.websocket("/ws/node/{node_id}")
async def node_websocket(
    websocket: WebSocket,
    node_id: str,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for node-specific messages."""
    await websocket_endpoint(websocket, f"node_{node_id}", node_id, token, db)

@websocket_router.websocket("/ws/global")
async def global_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for global broadcasts (admin only)."""
    try:
        token_data = verify_token(token, db)
        if "admin:read" not in (token_data.permissions or []):
            await websocket.close(code=1008, reason="Admin access required")
            return

        node_id = f"admin_{token_data.sub}"
        await websocket_endpoint(websocket, "global", node_id, token, db)
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")

@websocket_router.websocket("/ws/metrics")
async def metrics_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time metrics."""
    try:
        token_data = verify_token(token, db)
        node_id = f"metrics_{token_data.sub}"
        await websocket_endpoint(websocket, "metrics", node_id, token, db)
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")