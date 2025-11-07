"""
Real message handlers for WebSocket messages in federated learning.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from .manager import manager
from .event_broadcaster import event_broadcaster
from .message_types import MessageType, MessageHandler
from ..models.schemas import WebSocketMessage
from ..services.session_service import SessionService
from ..services.node_service import NodeService
from ..services.reward_service import RewardService
from ..database.connection import get_db
from sqlalchemy.orm import Session


class SessionMessageHandler(MessageHandler):
    """Handles session-related WebSocket messages."""

    def can_handle(self, message_type: str) -> bool:
        return message_type.startswith("session.")

    async def handle(self, message: WebSocketMessage) -> None:
        """Handle session messages."""
        try:
            session_id = message.session_id
            if not session_id:
                return

            # Get database session
            db = next(get_db())

            if message.type == "session.join":
                await self._handle_session_join(db, session_id, message.node_id, message.data)

            elif message.type == "session.leave":
                await self._handle_session_leave(db, session_id, message.node_id)

            elif message.type == "session.status":
                await self._handle_session_status_request(db, session_id, message.node_id)

            elif message.type == "session.participants":
                await self._handle_session_participants_request(db, session_id, message.node_id)

        except Exception as e:
            print(f"Error handling session message {message.type}: {e}")

    async def _handle_session_join(self, db: Session, session_id: str, node_id: str, data: Dict[str, Any]):
        """Handle session join request."""
        try:
            # Add participant to session
            participant = await SessionService.add_participant(db, session_id, node_id)

            # Join the session
            await SessionService.join_session(db, session_id, node_id)

            # Broadcast join event
            await event_broadcaster.notify_node_joined_session(session_id, node_id)

            # Send confirmation
            confirmation = WebSocketMessage(
                type="session.joined",
                session_id=session_id,
                node_id=node_id,
                data={
                    "status": "success",
                    "participant": {
                        "session_id": participant.session_id,
                        "node_id": participant.node_id,
                        "status": participant.status,
                        "joined_at": participant.joined_at.isoformat() if participant.joined_at else None
                    }
                }
            )
            await manager.send_personal_message(confirmation, session_id, node_id)

        except Exception as e:
            # Send error response
            error_msg = WebSocketMessage(
                type="session.error",
                session_id=session_id,
                node_id=node_id,
                data={"error": str(e), "action": "join"}
            )
            await manager.send_personal_message(error_msg, session_id, node_id)

    async def _handle_session_leave(self, db: Session, session_id: str, node_id: str):
        """Handle session leave request."""
        try:
            # Update participant status (would need to add this method to SessionService)
            # For now, just disconnect the WebSocket
            manager.disconnect(session_id, node_id)

            # Broadcast leave event
            await event_broadcaster.broadcast_session_event(
                session_id=session_id,
                event_type="participant_left",
                data={"node_id": node_id, "timestamp": datetime.utcnow().isoformat()}
            )

        except Exception as e:
            print(f"Error handling session leave: {e}")

    async def _handle_session_status_request(self, db: Session, session_id: str, node_id: str):
        """Handle session status request."""
        try:
            session = await SessionService.get_session_by_id(db, session_id)

            status_msg = WebSocketMessage(
                type="session.status",
                session_id=session_id,
                node_id=node_id,
                data={
                    "session": {
                        "id": session.id,
                        "name": session.name,
                        "status": session.status,
                        "current_round": session.current_round,
                        "total_rounds": session.total_rounds,
                        "started_at": session.started_at.isoformat() if session.started_at else None,
                        "completed_at": session.completed_at.isoformat() if session.completed_at else None
                    }
                }
            )
            await manager.send_personal_message(status_msg, session_id, node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="session.error",
                session_id=session_id,
                node_id=node_id,
                data={"error": str(e), "action": "status"}
            )
            await manager.send_personal_message(error_msg, session_id, node_id)

    async def _handle_session_participants_request(self, db: Session, session_id: str, node_id: str):
        """Handle session participants request."""
        try:
            participants = await SessionService.get_session_participants(db, session_id)

            participants_msg = WebSocketMessage(
                type="session.participants",
                session_id=session_id,
                node_id=node_id,
                data={
                    "participants": [
                        {
                            "node_id": p.node_id,
                            "status": p.status,
                            "joined_at": p.joined_at.isoformat() if p.joined_at else None,
                            "contributions_count": p.contributions_count,
                            "rewards_earned": p.rewards_earned
                        }
                        for p in participants
                    ]
                }
            )
            await manager.send_personal_message(participants_msg, session_id, node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="session.error",
                session_id=session_id,
                node_id=node_id,
                data={"error": str(e), "action": "participants"}
            )
            await manager.send_personal_message(error_msg, session_id, node_id)


class TrainingMessageHandler(MessageHandler):
    """Handles training-related WebSocket messages."""

    def can_handle(self, message_type: str) -> bool:
        return message_type.startswith("training.")

    async def handle(self, message: WebSocketMessage) -> None:
        """Handle training messages."""
        try:
            session_id = message.session_id
            if not session_id:
                return

            if message.type == "training.metrics":
                await self._handle_training_metrics(session_id, message.node_id, message.data)

            elif message.type == "training.progress":
                await self._handle_training_progress(session_id, message.node_id, message.data)

            elif message.type == "training.round_complete":
                await self._handle_training_round_complete(session_id, message.node_id, message.data)

        except Exception as e:
            print(f"Error handling training message {message.type}: {e}")

    async def _handle_training_metrics(self, session_id: str, node_id: str, data: Dict[str, Any]):
        """Handle training metrics submission."""
        try:
            round_number = data.get("round_number")
            metrics = data.get("metrics", {})

            if round_number is not None:
                # Broadcast metrics to all session participants
                await event_broadcaster.broadcast_training_metrics(session_id, round_number, {
                    "node_id": node_id,
                    **metrics
                })

                # Send acknowledgment
                ack_msg = WebSocketMessage(
                    type="training.metrics_ack",
                    session_id=session_id,
                    node_id=node_id,
                    data={"round_number": round_number, "status": "received"}
                )
                await manager.send_personal_message(ack_msg, session_id, node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="training.error",
                session_id=session_id,
                node_id=node_id,
                data={"error": str(e), "action": "metrics"}
            )
            await manager.send_personal_message(error_msg, session_id, node_id)

    async def _handle_training_progress(self, session_id: str, node_id: str, data: Dict[str, Any]):
        """Handle training progress updates."""
        try:
            progress_data = {
                "node_id": node_id,
                **data
            }

            # Broadcast progress to session
            await event_broadcaster.broadcast_training_progress(session_id, progress_data)

        except Exception as e:
            print(f"Error handling training progress: {e}")

    async def _handle_training_round_complete(self, session_id: str, node_id: str, data: Dict[str, Any]):
        """Handle training round completion."""
        try:
            round_number = data.get("round_number")
            final_metrics = data.get("final_metrics", {})

            if round_number is not None:
                # Broadcast round completion
                await event_broadcaster.notify_training_round_completed(
                    session_id, round_number, final_metrics
                )

                # Send acknowledgment
                ack_msg = WebSocketMessage(
                    type="training.round_complete_ack",
                    session_id=session_id,
                    node_id=node_id,
                    data={"round_number": round_number, "status": "completed"}
                )
                await manager.send_personal_message(ack_msg, session_id, node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="training.error",
                session_id=session_id,
                node_id=node_id,
                data={"error": str(e), "action": "round_complete"}
            )
            await manager.send_personal_message(error_msg, session_id, node_id)


class NodeMessageHandler(MessageHandler):
    """Handles node-related WebSocket messages."""

    def can_handle(self, message_type: str) -> bool:
        return message_type.startswith("node.")

    async def handle(self, message: WebSocketMessage) -> None:
        """Handle node messages."""
        try:
            node_id = message.node_id
            if not node_id:
                return

            # Get database session
            db = next(get_db())

            if message.type == "node.status":
                await self._handle_node_status_update(db, node_id, message.data)

            elif message.type == "node.heartbeat":
                await self._handle_node_heartbeat(db, node_id)

            elif message.type == "node.info":
                await self._handle_node_info_request(db, node_id)

        except Exception as e:
            print(f"Error handling node message {message.type}: {e}")

    async def _handle_node_status_update(self, db: Session, node_id: str, data: Dict[str, Any]):
        """Handle node status update."""
        try:
            status = data.get("status")
            if status:
                # Update node status in database
                await NodeService.update_node(db, node_id, {"status": status})

                # Broadcast status change
                await event_broadcaster.broadcast_node_event(
                    node_id=node_id,
                    event_type="status_changed",
                    data={"new_status": status, "timestamp": datetime.utcnow().isoformat()}
                )

        except Exception as e:
            print(f"Error updating node status: {e}")

    async def _handle_node_heartbeat(self, db: Session, node_id: str):
        """Handle node heartbeat."""
        try:
            # Update heartbeat in database
            await NodeService.update_heartbeat(db, node_id)

            # Update heartbeat in WebSocket manager
            # This is handled automatically in the WebSocket endpoint

        except Exception as e:
            print(f"Error handling heartbeat: {e}")

    async def _handle_node_info_request(self, db: Session, node_id: str):
        """Handle node info request."""
        try:
            node = await NodeService.get_node_by_id(db, node_id)

            info_msg = WebSocketMessage(
                type="node.info",
                node_id=node_id,
                data={
                    "node": {
                        "id": node.id,
                        "status": node.status,
                        "reputation_score": node.reputation_score,
                        "trust_level": node.trust_level,
                        "total_contributions": node.total_contributions,
                        "total_rewards_earned": node.total_rewards_earned,
                        "last_heartbeat": node.last_heartbeat.isoformat() if node.last_heartbeat else None
                    }
                }
            )

            # Send to requesting node (find session)
            sessions = manager.get_node_sessions(node_id)
            if sessions:
                await manager.send_personal_message(info_msg, sessions[0], node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="node.error",
                node_id=node_id,
                data={"error": str(e), "action": "info"}
            )
            sessions = manager.get_node_sessions(node_id)
            if sessions:
                await manager.send_personal_message(error_msg, sessions[0], node_id)


class RewardMessageHandler(MessageHandler):
    """Handles reward-related WebSocket messages."""

    def can_handle(self, message_type: str) -> bool:
        return message_type.startswith("reward.")

    async def handle(self, message: WebSocketMessage) -> None:
        """Handle reward messages."""
        try:
            node_id = message.node_id
            if not node_id:
                return

            # Get database session
            db = next(get_db())

            if message.type == "reward.claim":
                await self._handle_reward_claim(db, node_id, message.data)

            elif message.type == "reward.history":
                await self._handle_reward_history_request(db, node_id)

        except Exception as e:
            print(f"Error handling reward message {message.type}: {e}")

    async def _handle_reward_claim(self, db: Session, node_id: str, data: Dict[str, Any]):
        """Handle reward claim request."""
        try:
            # This would integrate with reward claiming logic
            # For now, send acknowledgment
            claim_msg = WebSocketMessage(
                type="reward.claim_ack",
                node_id=node_id,
                data={"status": "processing", "message": "Reward claim submitted"}
            )

            sessions = manager.get_node_sessions(node_id)
            if sessions:
                await manager.send_personal_message(claim_msg, sessions[0], node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="reward.error",
                node_id=node_id,
                data={"error": str(e), "action": "claim"}
            )
            sessions = manager.get_node_sessions(node_id)
            if sessions:
                await manager.send_personal_message(error_msg, sessions[0], node_id)

    async def _handle_reward_history_request(self, db: Session, node_id: str):
        """Handle reward history request."""
        try:
            # Get recent rewards for node
            rewards = await RewardService.get_node_rewards(db, node_id, limit=10)

            history_msg = WebSocketMessage(
                type="reward.history",
                node_id=node_id,
                data={
                    "rewards": [
                        {
                            "id": r.id,
                            "session_id": r.session_id,
                            "amount": r.drachma_amount,
                            "status": r.status,
                            "created_at": r.created_at.isoformat()
                        }
                        for r in rewards
                    ]
                }
            )

            sessions = manager.get_node_sessions(node_id)
            if sessions:
                await manager.send_personal_message(history_msg, sessions[0], node_id)

        except Exception as e:
            error_msg = WebSocketMessage(
                type="reward.error",
                node_id=node_id,
                data={"error": str(e), "action": "history"}
            )
            sessions = manager.get_node_sessions(node_id)
            if sessions:
                await manager.send_personal_message(error_msg, sessions[0], node_id)


# Global message handler instances
session_handler = SessionMessageHandler()
training_handler = TrainingMessageHandler()
node_handler = NodeMessageHandler()
reward_handler = RewardMessageHandler()

# Handler registry
message_handlers = {
    "session": session_handler,
    "training": training_handler,
    "node": node_handler,
    "reward": reward_handler
}


def get_message_handler(message_type: str) -> Optional[MessageHandler]:
    """Get the appropriate handler for a message type."""
    for prefix, handler in message_handlers.items():
        if message_type.startswith(f"{prefix}."):
            return handler
    return None