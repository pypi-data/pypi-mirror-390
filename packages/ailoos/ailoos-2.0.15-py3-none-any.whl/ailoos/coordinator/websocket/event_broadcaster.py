"""
Event broadcaster for real-time system events in federated learning.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json

from .manager import manager
from .message_broker import message_broker
from .message_types import WebSocketMessageFactory, MessageType
from ..models.schemas import WebSocketMessage
from ..services.session_service import SessionService
from ..services.node_service import NodeService
from ..services.reward_service import RewardService
# from ..monitoring.alerts import AlertManager  # Commented out - module not found
# from ..monitoring.metrics_api import MetricsAPI  # Commented out - module not found


class EventBroadcaster:
    """Broadcasts real-time events to WebSocket clients."""

    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.is_running = False
        self._background_tasks = []

    async def start(self):
        """Start the event broadcaster."""
        self.is_running = True
        # Start background monitoring tasks
        self._background_tasks = [
            asyncio.create_task(self._monitor_session_events()),
            asyncio.create_task(self._monitor_node_events()),
            asyncio.create_task(self._monitor_reward_events()),
            asyncio.create_task(self._monitor_system_events()),
            asyncio.create_task(self._monitor_training_events())
        ]
        print("Event broadcaster started")

    async def stop(self):
        """Stop the event broadcaster."""
        self.is_running = False
        for task in self._background_tasks:
            task.cancel()
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        print("Event broadcaster stopped")

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def broadcast_session_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Broadcast session-related events."""
        try:
            message = WebSocketMessageFactory.create_session_update(
                session_id=session_id,
                update_type=event_type,
                data=data
            )

            # Broadcast to session participants
            await manager.broadcast_to_session(message, session_id)

            # Publish to message broker for additional processing
            await message_broker.publish(message, target_type="session", target_ids=[session_id])

            # Trigger event handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(session_id, event_type, data)
                    except Exception as e:
                        print(f"Error in event handler for {event_type}: {e}")

        except Exception as e:
            print(f"Error broadcasting session event {event_type}: {e}")

    async def broadcast_node_event(self, node_id: str, event_type: str, data: Dict[str, Any]):
        """Broadcast node-related events."""
        try:
            message = WebSocketMessageFactory.create_node_status(
                node_id=node_id,
                status=event_type,
                data=data
            )

            # Broadcast to node's sessions
            await manager.broadcast_to_node_sessions(message, node_id)

            # Publish to message broker
            await message_broker.publish(message, target_type="node", target_ids=[node_id])

            # Trigger event handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(node_id, event_type, data)
                    except Exception as e:
                        print(f"Error in event handler for {event_type}: {e}")

        except Exception as e:
            print(f"Error broadcasting node event {event_type}: {e}")

    async def broadcast_reward_event(self, node_id: str, reward_data: Dict[str, Any]):
        """Broadcast reward-related events."""
        try:
            message = WebSocketMessageFactory.create_reward_notification(
                node_id=node_id,
                amount=reward_data.get("amount", 0),
                reason=reward_data.get("reason", "reward_earned"),
                data=reward_data
            )

            # Send to specific node
            await manager.send_node_notification(node_id, "reward_earned", reward_data)

            # Publish to message broker
            await message_broker.publish(message, target_type="node", target_ids=[node_id])

        except Exception as e:
            print(f"Error broadcasting reward event: {e}")

    async def broadcast_system_alert(self, alert_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Broadcast system-wide alerts."""
        try:
            alert_message = WebSocketMessageFactory.create_system_alert(
                alert_type=alert_type,
                message=message,
                data=data or {}
            )

            # Broadcast to all connected clients
            await message_broker.publish(alert_message, target_type="broadcast")

        except Exception as e:
            print(f"Error broadcasting system alert: {e}")

    async def broadcast_training_metrics(self, session_id: str, round_number: int, metrics: Dict[str, Any]):
        """Broadcast training metrics updates."""
        try:
            message = WebSocketMessageFactory.create_training_metrics(
                session_id=session_id,
                round_number=round_number,
                metrics=metrics
            )

            # Broadcast to session participants
            await manager.broadcast_to_session(message, session_id)

            # Publish to message broker
            await message_broker.publish(message, target_type="session", target_ids=[session_id])

        except Exception as e:
            print(f"Error broadcasting training metrics: {e}")

    async def broadcast_training_progress(self, session_id: str, progress_data: Dict[str, Any]):
        """Broadcast training progress updates."""
        try:
            message = WebSocketMessage(
                type=MessageType.TRAINING_PROGRESS.value,
                session_id=session_id,
                data={
                    **progress_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            # Broadcast to session participants
            await manager.broadcast_to_session(message, session_id)

        except Exception as e:
            print(f"Error broadcasting training progress: {e}")

    async def _monitor_session_events(self):
        """Monitor session lifecycle events."""
        while self.is_running:
            try:
                # This would typically integrate with session service events
                # For now, we'll poll for changes periodically
                await asyncio.sleep(30)  # Check every 30 seconds

                # In a real implementation, this would listen to database change events
                # or use a pub/sub system for session updates

            except Exception as e:
                print(f"Error in session event monitoring: {e}")
                await asyncio.sleep(5)

    async def _monitor_node_events(self):
        """Monitor node status events."""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Check for stale connections and broadcast disconnect events
                stale_connections = manager.get_stale_connections()
                for session_id, node_id in stale_connections:
                    await self.broadcast_node_event(
                        node_id=node_id,
                        event_type="disconnected",
                        data={
                            "session_id": session_id,
                            "reason": "heartbeat_timeout",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )

            except Exception as e:
                print(f"Error in node event monitoring: {e}")
                await asyncio.sleep(5)

    async def _monitor_reward_events(self):
        """Monitor reward distribution events."""
        while self.is_running:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes

                # Integrate with reward service events
                try:
                    # Get recent reward distributions from the last monitoring period
                    recent_rewards = await self._get_recent_reward_distributions()

                    for reward_data in recent_rewards:
                        session_id = reward_data.get("session_id")
                        node_id = reward_data.get("node_id")
                        amount = reward_data.get("amount", 0)

                        if node_id and amount > 0:
                            # Broadcast reward event to the specific node
                            await self.broadcast_reward_event(node_id, {
                                "session_id": session_id,
                                "amount": amount,
                                "reason": reward_data.get("reason", "training_contribution"),
                                "round_number": reward_data.get("round_number"),
                                "timestamp": reward_data.get("timestamp", datetime.utcnow().isoformat()),
                                "transaction_hash": reward_data.get("transaction_hash"),
                                "blockchain_status": reward_data.get("blockchain_status", "confirmed")
                            })

                            # Also broadcast to session participants for transparency
                            if session_id:
                                await self.broadcast_session_event(
                                    session_id=session_id,
                                    event_type="reward_distributed",
                                    data={
                                        "node_id": node_id,
                                        "amount": amount,
                                        "round_number": reward_data.get("round_number"),
                                        "timestamp": reward_data.get("timestamp", datetime.utcnow().isoformat())
                                    }
                                )

                except Exception as e:
                    print(f"Error processing reward events: {e}")

            except Exception as e:
                print(f"Error in reward event monitoring: {e}")
                await asyncio.sleep(5)

    async def _get_recent_reward_distributions(self) -> List[Dict[str, Any]]:
        """Get recent reward distributions from the reward service with real database queries."""
        try:
            from ..database.connection import get_db_connection
            from datetime import datetime, timedelta

            # Get database connection
            conn = await get_db_connection()
            if not conn:
                print("Database connection failed, falling back to simulation")
                return []

            try:
                # Query recent reward distributions from the last 2 minutes
                since_time = datetime.utcnow() - timedelta(minutes=2)

                query = """
                SELECT
                    rd.session_id,
                    rd.node_id,
                    rd.amount,
                    rd.reason,
                    rd.round_number,
                    rd.transaction_hash,
                    rd.blockchain_status,
                    rd.created_at,
                    s.name as session_name
                FROM reward_distributions rd
                LEFT JOIN sessions s ON rd.session_id = s.id
                WHERE rd.created_at >= $1
                ORDER BY rd.created_at DESC
                LIMIT 50
                """

                rows = await conn.fetch(query, since_time)

                recent_rewards = []
                for row in rows:
                    reward_data = {
                        "session_id": str(row['session_id']),
                        "node_id": str(row['node_id']),
                        "amount": float(row['amount']),
                        "reason": row['reason'] or "training_contribution",
                        "round_number": row['round_number'],
                        "transaction_hash": row['transaction_hash'],
                        "blockchain_status": row['blockchain_status'] or "confirmed",
                        "timestamp": row['created_at'].isoformat() if row['created_at'] else datetime.utcnow().isoformat(),
                        "session_name": row['session_name']
                    }
                    recent_rewards.append(reward_data)

                print(f"Found {len(recent_rewards)} recent reward distributions")
                return recent_rewards

            finally:
                await conn.close()

        except ImportError:
            print("Database module not available, using simulation")
            return []
        except Exception as e:
            print(f"Error querying reward distributions from database: {e}")
            return []

    async def _monitor_system_events(self):
        """Monitor system-wide events."""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Broadcast periodic system health updates
                try:
                    broker_stats = await message_broker.get_stats()
                    await self.broadcast_system_alert(
                        alert_type="system_health",
                        message="Periodic system health update",
                        data={
                            "connections": broker_stats.get("total_connections", 0),
                            "active_rooms": broker_stats.get("active_rooms", 0),
                            "queue_size": broker_stats.get("queue_size", 0),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                except Exception as e:
                    print(f"Error getting system stats: {e}")

            except Exception as e:
                print(f"Error in system event monitoring: {e}")
                await asyncio.sleep(5)

    async def _monitor_training_events(self):
        """Monitor training progress events."""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Integrate with training progress updates
                try:
                    # Get active training sessions and their progress
                    active_sessions = await self._get_active_training_sessions()

                    for session_data in active_sessions:
                        session_id = session_data.get("session_id")
                        current_round = session_data.get("current_round", 0)
                        total_rounds = session_data.get("total_rounds", 0)
                        status = session_data.get("status", "unknown")

                        if session_id and status in ["active", "running"]:
                            # Get detailed progress for current round
                            round_progress = await self._get_round_progress(session_id, current_round)

                            if round_progress:
                                # Broadcast training progress update
                                await self.broadcast_training_progress(session_id, {
                                    "current_round": current_round,
                                    "total_rounds": total_rounds,
                                    "round_progress": round_progress.get("progress_percentage", 0.0),
                                    "participants_submitted": round_progress.get("participants_submitted", 0),
                                    "participants_expected": round_progress.get("participants_expected", 0),
                                    "status": status,
                                    "estimated_completion": session_data.get("estimated_completion"),
                                    "last_update": datetime.utcnow().isoformat()
                                })

                                # If round is complete, broadcast completion event
                                if round_progress.get("completed", False):
                                    await self.notify_training_round_completed(
                                        session_id=session_id,
                                        round_number=current_round,
                                        metrics=round_progress.get("metrics", {})
                                    )

                except Exception as e:
                    print(f"Error processing training events: {e}")

            except Exception as e:
                print(f"Error in training event monitoring: {e}")
                await asyncio.sleep(5)

    async def _get_active_training_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active training sessions with real database queries."""
        try:
            from ..database.connection import get_db_connection

            # Get database connection
            conn = await get_db_connection()
            if not conn:
                print("Database connection failed, falling back to simulation")
                return []

            try:
                # Query active training sessions
                query = """
                SELECT
                    s.id,
                    s.name,
                    s.status,
                    s.model_type,
                    s.current_round,
                    s.total_rounds,
                    s.min_nodes,
                    s.max_nodes,
                    s.created_at,
                    s.estimated_completion,
                    COUNT(sp.node_id) as participant_count
                FROM sessions s
                LEFT JOIN session_participants sp ON s.id = sp.session_id
                WHERE s.status IN ('active', 'running', 'waiting_for_participants')
                GROUP BY s.id, s.name, s.status, s.model_type, s.current_round,
                         s.total_rounds, s.min_nodes, s.max_nodes, s.created_at, s.estimated_completion
                ORDER BY s.created_at DESC
                """

                rows = await conn.fetch(query)

                active_sessions = []
                for row in rows:
                    session_data = {
                        "session_id": str(row['id']),
                        "name": row['name'],
                        "status": row['status'],
                        "model_type": row['model_type'],
                        "current_round": row['current_round'] or 0,
                        "total_rounds": row['total_rounds'] or 0,
                        "min_nodes": row['min_nodes'] or 0,
                        "max_nodes": row['max_nodes'] or 0,
                        "participant_count": row['participant_count'] or 0,
                        "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                        "estimated_completion": row['estimated_completion'].isoformat() if row['estimated_completion'] else None
                    }
                    active_sessions.append(session_data)

                print(f"Found {len(active_sessions)} active training sessions")
                return active_sessions

            finally:
                await conn.close()

        except ImportError:
            print("Database module not available, using simulation")
            return []
        except Exception as e:
            print(f"Error querying active training sessions from database: {e}")
            return []

    async def _get_round_progress(self, session_id: str, round_number: int) -> Optional[Dict[str, Any]]:
        """Get progress details for a specific training round with real database queries."""
        try:
            from ..database.connection import get_db_connection

            # Get database connection
            conn = await get_db_connection()
            if not conn:
                print("Database connection failed, falling back to simulation")
                return None

            try:
                # Query round progress and submissions
                query = """
                SELECT
                    tr.round_number,
                    tr.status,
                    tr.started_at,
                    tr.completed_at,
                    COUNT(CASE WHEN ts.status = 'submitted' THEN 1 END) as participants_submitted,
                    COUNT(sp.node_id) as participants_expected,
                    AVG(CASE WHEN ts.accuracy IS NOT NULL THEN ts.accuracy END) as avg_accuracy,
                    AVG(CASE WHEN ts.loss IS NOT NULL THEN ts.loss END) as avg_loss,
                    SUM(CASE WHEN ts.samples_processed IS NOT NULL THEN ts.samples_processed END) as total_samples
                FROM training_rounds tr
                LEFT JOIN training_submissions ts ON tr.session_id = ts.session_id AND tr.round_number = ts.round_number
                LEFT JOIN session_participants sp ON tr.session_id = sp.session_id
                WHERE tr.session_id = $1 AND tr.round_number = $2
                GROUP BY tr.round_number, tr.status, tr.started_at, tr.completed_at
                """

                row = await conn.fetchrow(query, session_id, round_number)

                if not row:
                    return None

                # Calculate progress percentage
                participants_submitted = row['participants_submitted'] or 0
                participants_expected = row['participants_expected'] or 1  # Avoid division by zero
                progress_percentage = min(100.0, (participants_submitted / participants_expected) * 100)

                # Determine if round is completed
                completed = row['status'] == 'completed' or progress_percentage >= 100.0

                round_progress = {
                    "round_number": round_number,
                    "progress_percentage": progress_percentage,
                    "participants_submitted": participants_submitted,
                    "participants_expected": participants_expected,
                    "completed": completed,
                    "status": row['status'],
                    "started_at": row['started_at'].isoformat() if row['started_at'] else None,
                    "completed_at": row['completed_at'].isoformat() if row['completed_at'] else None,
                    "metrics": {
                        "avg_accuracy": float(row['avg_accuracy']) if row['avg_accuracy'] else None,
                        "avg_loss": float(row['avg_loss']) if row['avg_loss'] else None,
                        "total_samples_processed": row['total_samples'] or 0
                    },
                    "last_update": datetime.utcnow().isoformat()
                }

                print(f"Round {round_number} progress: {progress_percentage:.1f}% ({participants_submitted}/{participants_expected} participants)")
                return round_progress

            finally:
                await conn.close()

        except ImportError:
            print("Database module not available, using simulation")
            return None
        except Exception as e:
            print(f"Error querying round progress from database: {e}")
            return None

    # Integration methods for services

    async def notify_session_started(self, session_id: str, session_data: Dict[str, Any]):
        """Notify when a session starts."""
        await self.broadcast_session_event(
            session_id=session_id,
            event_type="started",
            data={
                "session_name": session_data.get("name", ""),
                "model_type": session_data.get("model_type", ""),
                "min_nodes": session_data.get("min_nodes", 0),
                "max_nodes": session_data.get("max_nodes", 0),
                "total_rounds": session_data.get("total_rounds", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_session_completed(self, session_id: str, results: Dict[str, Any]):
        """Notify when a session completes."""
        await self.broadcast_session_event(
            session_id=session_id,
            event_type="completed",
            data={
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_node_joined_session(self, session_id: str, node_id: str):
        """Notify when a node joins a session."""
        await self.broadcast_session_event(
            session_id=session_id,
            event_type="participant_joined",
            data={
                "node_id": node_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_training_round_started(self, session_id: str, round_number: int):
        """Notify when a training round starts."""
        await self.broadcast_session_event(
            session_id=session_id,
            event_type="training_round_started",
            data={
                "round_number": round_number,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_training_round_completed(self, session_id: str, round_number: int, metrics: Dict[str, Any]):
        """Notify when a training round completes."""
        await self.broadcast_training_metrics(session_id, round_number, metrics)

        await self.broadcast_session_event(
            session_id=session_id,
            event_type="training_round_completed",
            data={
                "round_number": round_number,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_rewards_distributed(self, session_id: str, rewards_data: List[Dict[str, Any]]):
        """Notify when rewards are distributed."""
        for reward in rewards_data:
            node_id = reward.get("node_id")
            if node_id:
                await self.broadcast_reward_event(node_id, reward)

        await self.broadcast_session_event(
            session_id=session_id,
            event_type="rewards_distributed",
            data={
                "rewards": rewards_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Global event broadcaster instance
event_broadcaster = EventBroadcaster()