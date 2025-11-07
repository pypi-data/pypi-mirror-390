"""
WebSocket module for real-time communication in federated learning.
"""

from .manager import ConnectionManager, manager, websocket_router
from .room_manager import RoomManager, room_manager
from .message_broker import MessageBroker, message_broker
from .heartbeat import HeartbeatManager, heartbeat_manager
from .event_broadcaster import EventBroadcaster, event_broadcaster
from .metrics_monitor import MetricsMonitor, metrics_monitor
from .notification_service import NotificationService, notification_service
from .message_types import (
    MessageType, MessagePriority, WebSocketMessageFactory,
    MessageHandler, get_message_type, get_message_priority
)

__all__ = [
    # Connection management
    "ConnectionManager",
    "manager",

    # Room management
    "RoomManager",
    "room_manager",

    # Message broker
    "MessageBroker",
    "message_broker",

    # Heartbeat management
    "HeartbeatManager",
    "heartbeat_manager",

    # Event broadcaster
    "EventBroadcaster",
    "event_broadcaster",

    # Metrics monitor
    "MetricsMonitor",
    "metrics_monitor",

    # Notification service
    "NotificationService",
    "notification_service",

    # Message types
    "MessageType",
    "MessagePriority",
    "WebSocketMessageFactory",
    "MessageHandler",
    "get_message_type",
    "get_message_priority",

    # Router
    "websocket_router",
]