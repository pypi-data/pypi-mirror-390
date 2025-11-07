"""
WebSocket message types and handlers for federated learning coordination.
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.schemas import WebSocketMessage


class MessageType(Enum):
    """WebSocket message types."""

    # Session messages
    SESSION_START = "session.start"
    SESSION_UPDATE = "session.update"
    SESSION_COMPLETE = "session.complete"
    SESSION_ERROR = "session.error"
    SESSION_PARTICIPANT_JOIN = "session.participant.join"
    SESSION_PARTICIPANT_LEAVE = "session.participant.leave"

    # Training messages
    TRAINING_ROUND_START = "training.round.start"
    TRAINING_ROUND_COMPLETE = "training.round.complete"
    TRAINING_METRICS = "training.metrics"
    TRAINING_PROGRESS = "training.progress"

    # Node messages
    NODE_STATUS = "node.status"
    NODE_HEARTBEAT = "node.heartbeat"
    NODE_DISCONNECT = "node.disconnect"
    NODE_RECONNECT = "node.reconnect"

    # Reward messages
    REWARD_EARNED = "reward.earned"
    REWARD_DISTRIBUTED = "reward.distributed"
    REWARD_CLAIMED = "reward.claimed"

    # System messages
    SYSTEM_ALERT = "system.alert"
    SYSTEM_MAINTENANCE = "system.maintenance"
    SYSTEM_UPDATE = "system.update"

    # Control messages
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ACK = "ack"
    ERROR = "error"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class WebSocketMessageFactory:
    """Factory for creating WebSocket messages."""

    @staticmethod
    def create_session_update(session_id: str, update_type: str, data: Dict[str, Any]) -> WebSocketMessage:
        """Create a session update message."""
        return WebSocketMessage(
            type=MessageType.SESSION_UPDATE.value,
            session_id=session_id,
            data={
                "update_type": update_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def create_training_metrics(session_id: str, round_number: int, metrics: Dict[str, Any]) -> WebSocketMessage:
        """Create a training metrics message."""
        return WebSocketMessage(
            type=MessageType.TRAINING_METRICS.value,
            session_id=session_id,
            data={
                "round_number": round_number,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def create_node_status(node_id: str, status: str, data: Optional[Dict[str, Any]] = None) -> WebSocketMessage:
        """Create a node status message."""
        return WebSocketMessage(
            type=MessageType.NODE_STATUS.value,
            node_id=node_id,
            data={
                "status": status,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def create_reward_notification(node_id: str, amount: float, reason: str, data: Optional[Dict[str, Any]] = None) -> WebSocketMessage:
        """Create a reward notification message."""
        return WebSocketMessage(
            type=MessageType.REWARD_EARNED.value,
            node_id=node_id,
            data={
                "amount": amount,
                "reason": reason,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def create_system_alert(alert_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> WebSocketMessage:
        """Create a system alert message."""
        return WebSocketMessage(
            type=MessageType.SYSTEM_ALERT.value,
            data={
                "alert_type": alert_type,
                "message": message,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def create_ping(node_id: Optional[str] = None) -> WebSocketMessage:
        """Create a ping message."""
        return WebSocketMessage(
            type=MessageType.PING.value,
            node_id=node_id,
            data={"timestamp": datetime.utcnow().isoformat()}
        )

    @staticmethod
    def create_pong(node_id: Optional[str] = None) -> WebSocketMessage:
        """Create a pong message."""
        return WebSocketMessage(
            type=MessageType.PONG.value,
            node_id=node_id,
            data={"timestamp": datetime.utcnow().isoformat()}
        )

    @staticmethod
    def create_ack(message_id: str, success: bool = True, error: Optional[str] = None) -> WebSocketMessage:
        """Create an acknowledgment message."""
        return WebSocketMessage(
            type=MessageType.ACK.value,
            data={
                "message_id": message_id,
                "success": success,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def create_error(error_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> WebSocketMessage:
        """Create an error message."""
        return WebSocketMessage(
            type=MessageType.ERROR.value,
            data={
                "error_type": error_type,
                "message": message,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )


class MessageHandler:
    """Base class for message handlers."""

    def can_handle(self, message_type: str) -> bool:
        """Check if this handler can handle the message type."""
        raise NotImplementedError("Subclasses must implement can_handle method")

    async def handle(self, message: WebSocketMessage) -> None:
        """Handle the message."""
        raise NotImplementedError("Subclasses must implement handle method")


# Message type mappings
MESSAGE_TYPE_MAPPING = {
    # Session messages
    "session.start": MessageType.SESSION_START,
    "session.update": MessageType.SESSION_UPDATE,
    "session.complete": MessageType.SESSION_COMPLETE,
    "session.error": MessageType.SESSION_ERROR,
    "session.participant.join": MessageType.SESSION_PARTICIPANT_JOIN,
    "session.participant.leave": MessageType.SESSION_PARTICIPANT_LEAVE,

    # Training messages
    "training.round.start": MessageType.TRAINING_ROUND_START,
    "training.round.complete": MessageType.TRAINING_ROUND_COMPLETE,
    "training.metrics": MessageType.TRAINING_METRICS,
    "training.progress": MessageType.TRAINING_PROGRESS,

    # Node messages
    "node.status": MessageType.NODE_STATUS,
    "node.heartbeat": MessageType.NODE_HEARTBEAT,
    "node.disconnect": MessageType.NODE_DISCONNECT,
    "node.reconnect": MessageType.NODE_RECONNECT,

    # Reward messages
    "reward.earned": MessageType.REWARD_EARNED,
    "reward.distributed": MessageType.REWARD_DISTRIBUTED,
    "reward.claimed": MessageType.REWARD_CLAIMED,

    # System messages
    "system.alert": MessageType.SYSTEM_ALERT,
    "system.maintenance": MessageType.SYSTEM_MAINTENANCE,
    "system.update": MessageType.SYSTEM_UPDATE,

    # Control messages
    "ping": MessageType.PING,
    "pong": MessageType.PONG,
    "subscribe": MessageType.SUBSCRIBE,
    "unsubscribe": MessageType.UNSUBSCRIBE,
    "ack": MessageType.ACK,
    "error": MessageType.ERROR,
}


def get_message_type(message_type_str: str) -> Optional[MessageType]:
    """Get MessageType enum from string."""
    return MESSAGE_TYPE_MAPPING.get(message_type_str)


def get_message_priority(message_type: MessageType) -> MessagePriority:
    """Get priority for a message type."""
    priority_map = {
        # Critical messages
        MessageType.SYSTEM_ALERT: MessagePriority.CRITICAL,
        MessageType.SESSION_ERROR: MessagePriority.CRITICAL,
        MessageType.NODE_DISCONNECT: MessagePriority.HIGH,

        # High priority
        MessageType.SESSION_START: MessagePriority.HIGH,
        MessageType.SESSION_COMPLETE: MessagePriority.HIGH,
        MessageType.TRAINING_ROUND_START: MessagePriority.HIGH,
        MessageType.REWARD_EARNED: MessagePriority.HIGH,

        # Normal priority
        MessageType.SESSION_UPDATE: MessagePriority.NORMAL,
        MessageType.TRAINING_METRICS: MessagePriority.NORMAL,
        MessageType.NODE_STATUS: MessagePriority.NORMAL,
        MessageType.PING: MessagePriority.NORMAL,
        MessageType.PONG: MessagePriority.NORMAL,

        # Low priority
        MessageType.TRAINING_PROGRESS: MessagePriority.LOW,
        MessageType.NODE_HEARTBEAT: MessagePriority.LOW,
    }

    return priority_map.get(message_type, MessagePriority.NORMAL)