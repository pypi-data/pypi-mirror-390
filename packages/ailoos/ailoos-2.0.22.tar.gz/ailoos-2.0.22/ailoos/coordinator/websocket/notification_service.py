"""
Push notification service for WebSocket clients.
"""

import asyncio
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from .manager import manager
from .event_broadcaster import event_broadcaster
from ..models.schemas import WebSocketMessage
from ..services.node_service import NodeService
from ..database.connection import get_db
from sqlalchemy.orm import Session


class NotificationService:
    """Service for managing push notifications to WebSocket clients."""

    def __init__(self):
        self.notification_preferences: Dict[str, Dict[str, bool]] = {}  # node_id -> notification_type -> enabled
        self.pending_notifications: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # node_id -> notifications
        self.notification_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # node_id -> history
        self.max_history_size = 100

    async def register_node_preferences(self, node_id: str, preferences: Dict[str, bool]):
        """Register notification preferences for a node."""
        self.notification_preferences[node_id] = preferences.copy()
        print(f"Registered notification preferences for node {node_id}: {preferences}")

    async def update_node_preferences(self, node_id: str, preferences: Dict[str, bool]):
        """Update notification preferences for a node."""
        if node_id not in self.notification_preferences:
            self.notification_preferences[node_id] = {}

        self.notification_preferences[node_id].update(preferences)
        print(f"Updated notification preferences for node {node_id}: {preferences}")

    async def send_notification(self, node_id: str, notification_type: str, title: str,
                              message: str, data: Optional[Dict[str, Any]] = None,
                              priority: str = "normal"):
        """Send a notification to a specific node."""
        # Check if node has enabled this notification type
        if node_id in self.notification_preferences:
            preferences = self.notification_preferences[node_id]
            if not preferences.get(notification_type, True):  # Default to enabled
                return  # Skip if disabled

        notification = {
            "id": f"{node_id}_{notification_type}_{int(datetime.utcnow().timestamp())}",
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }

        # Add to pending notifications
        self.pending_notifications[node_id].append(notification)

        # Add to history
        self.notification_history[node_id].append(notification)
        if len(self.notification_history[node_id]) > self.max_history_size:
            self.notification_history[node_id].pop(0)

        # Send via WebSocket if node is connected
        await self._deliver_notification(node_id, notification)

    async def broadcast_notification(self, notification_type: str, title: str,
                                   message: str, data: Optional[Dict[str, Any]] = None,
                                   priority: str = "normal", target_nodes: Optional[List[str]] = None):
        """Broadcast notification to multiple nodes or all connected nodes."""
        notification = {
            "id": f"broadcast_{notification_type}_{int(datetime.utcnow().timestamp())}",
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }

        if target_nodes:
            # Send to specific nodes
            for node_id in target_nodes:
                if node_id in self.notification_preferences:
                    preferences = self.notification_preferences[node_id]
                    if preferences.get(notification_type, True):
                        self.pending_notifications[node_id].append(notification)
                        self.notification_history[node_id].append(notification)
                        if len(self.notification_history[node_id]) > self.max_history_size:
                            self.notification_history[node_id].pop(0)
                        await self._deliver_notification(node_id, notification)
        else:
            # Broadcast to all connected nodes
            for node_id in manager.node_subscriptions.keys():
                if node_id in self.notification_preferences:
                    preferences = self.notification_preferences[node_id]
                    if preferences.get(notification_type, True):
                        self.pending_notifications[node_id].append(notification)
                        self.notification_history[node_id].append(notification)
                        if len(self.notification_history[node_id]) > self.max_history_size:
                            self.notification_history[node_id].pop(0)
                        await self._deliver_notification(node_id, notification)

    async def _deliver_notification(self, node_id: str, notification: Dict[str, Any]):
        """Deliver notification via WebSocket."""
        try:
            message = WebSocketMessage(
                type="notification.push",
                node_id=node_id,
                data=notification
            )

            # Send to all sessions for this node
            await manager.broadcast_to_node_sessions(message, node_id)

        except Exception as e:
            print(f"Failed to deliver notification to {node_id}: {e}")

    async def mark_notification_read(self, node_id: str, notification_id: str):
        """Mark a notification as read."""
        # Update in pending notifications
        for notification in self.pending_notifications[node_id]:
            if notification["id"] == notification_id:
                notification["read"] = True
                break

        # Update in history
        for notification in self.notification_history[node_id]:
            if notification["id"] == notification_id:
                notification["read"] = True
                break

    async def get_pending_notifications(self, node_id: str) -> List[Dict[str, Any]]:
        """Get pending notifications for a node."""
        return self.pending_notifications[node_id].copy()

    async def get_notification_history(self, node_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notification history for a node."""
        return self.notification_history[node_id][-limit:].copy()

    async def clear_pending_notifications(self, node_id: str):
        """Clear all pending notifications for a node."""
        self.pending_notifications[node_id].clear()

    async def send_reward_notification(self, node_id: str, amount: float, reason: str):
        """Send reward earned notification."""
        await self.send_notification(
            node_id=node_id,
            notification_type="reward_earned",
            title="¡Recompensa Ganada!",
            message=f"Has ganado {amount:.2f} DRACMA por {reason}",
            data={"amount": amount, "reason": reason},
            priority="high"
        )

    async def send_session_notification(self, node_id: str, session_id: str, event: str, message: str):
        """Send session-related notification."""
        await self.send_notification(
            node_id=node_id,
            notification_type="session_update",
            title="Actualización de Sesión",
            message=message,
            data={"session_id": session_id, "event": event},
            priority="normal"
        )

    async def send_system_notification(self, node_id: str, alert_type: str, message: str):
        """Send system alert notification."""
        priority = "high" if alert_type in ["error", "critical"] else "normal"

        await self.send_notification(
            node_id=node_id,
            notification_type="system_alert",
            title="Alerta del Sistema",
            message=message,
            data={"alert_type": alert_type},
            priority=priority
        )

    async def send_training_notification(self, node_id: str, session_id: str, round_number: int, status: str):
        """Send training-related notification."""
        messages = {
            "started": f"Ronda {round_number} de entrenamiento iniciada",
            "completed": f"Ronda {round_number} de entrenamiento completada",
            "failed": f"Ronda {round_number} de entrenamiento fallida"
        }

        await self.send_notification(
            node_id=node_id,
            notification_type="training_update",
            title="Actualización de Entrenamiento",
            message=messages.get(status, f"Estado de ronda {round_number}: {status}"),
            data={"session_id": session_id, "round_number": round_number, "status": status},
            priority="normal"
        )

    async def send_maintenance_notification(self, node_id: str, maintenance_type: str, scheduled_time: str):
        """Send maintenance notification."""
        await self.send_notification(
            node_id=node_id,
            notification_type="maintenance",
            title="Mantenimiento Programado",
            message=f"Mantenimiento {maintenance_type} programado para {scheduled_time}",
            data={"maintenance_type": maintenance_type, "scheduled_time": scheduled_time},
            priority="normal"
        )

    async def send_security_notification(self, node_id: str, event_type: str, details: str):
        """Send security-related notification."""
        await self.send_notification(
            node_id=node_id,
            notification_type="security_alert",
            title="Alerta de Seguridad",
            message=f"Evento de seguridad: {event_type}",
            data={"event_type": event_type, "details": details},
            priority="critical"
        )

    # Integration methods for automatic notifications

    async def notify_on_session_start(self, session_id: str, session_data: Dict[str, Any]):
        """Automatically notify participants when session starts."""
        db = next(get_db())
        try:
            from ..services.session_service import SessionService
            participants = await SessionService.get_session_participants(db, session_id)

            for participant in participants:
                if participant.status == 'joined':
                    await self.send_session_notification(
                        node_id=participant.node_id,
                        session_id=session_id,
                        event="started",
                        message=f"La sesión '{session_data.get('name', session_id)}' ha comenzado"
                    )
        except Exception as e:
            print(f"Error sending session start notifications: {e}")

    async def notify_on_session_complete(self, session_id: str, results: Dict[str, Any]):
        """Automatically notify participants when session completes."""
        db = next(get_db())
        try:
            from ..services.session_service import SessionService
            participants = await SessionService.get_session_participants(db, session_id)

            for participant in participants:
                if participant.status == 'joined':
                    await self.send_session_notification(
                        node_id=participant.node_id,
                        session_id=session_id,
                        event="completed",
                        message=f"La sesión {session_id} se ha completado exitosamente"
                    )
        except Exception as e:
            print(f"Error sending session complete notifications: {e}")

    async def notify_on_rewards_distributed(self, session_id: str, rewards_data: List[Dict[str, Any]]):
        """Automatically notify nodes when rewards are distributed."""
        for reward in rewards_data:
            node_id = reward.get("node_id")
            amount = reward.get("amount", 0)
            reason = reward.get("reason", "contribution")

            if node_id:
                await self.send_reward_notification(node_id, amount, reason)

    async def notify_on_node_status_change(self, node_id: str, new_status: str):
        """Notify relevant parties about node status changes."""
        if new_status == "disconnected":
            await self.send_system_notification(
                node_id=node_id,
                alert_type="warning",
                message="Tu nodo se ha desconectado del sistema"
            )
        elif new_status == "reconnected":
            await self.send_system_notification(
                node_id=node_id,
                alert_type="info",
                message="Tu nodo se ha reconectado al sistema"
            )

    async def cleanup_old_notifications(self, days: int = 30):
        """Clean up old notifications from history."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        for node_id in list(self.notification_history.keys()):
            # Filter out old notifications
            self.notification_history[node_id] = [
                n for n in self.notification_history[node_id]
                if datetime.fromisoformat(n["timestamp"]) > cutoff_date
            ]

            # Remove empty histories
            if not self.notification_history[node_id]:
                del self.notification_history[node_id]


# Global notification service instance
notification_service = NotificationService()