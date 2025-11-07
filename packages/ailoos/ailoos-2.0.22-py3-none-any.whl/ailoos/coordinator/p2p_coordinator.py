"""
P2P Federated Learning Coordinator.
Replaces centralized GCP coordinator with distributed P2P coordination.
"""

import asyncio
import json
import time
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class NodeInfo:
    """Information about a federated learning node."""
    node_id: str
    ip_address: str
    hardware_info: Dict[str, Any]
    location: str
    joined_at: float
    last_seen: float
    status: str = "active"


@dataclass
class SessionConfig:
    """Configuration for a federated learning session."""
    model_name: str
    num_rounds: int
    min_participants: int
    max_participants: int
    local_epochs: int
    batch_size: int
    learning_rate: float
    dataset_info: Dict[str, Any]


@dataclass
class FederatedSession:
    """A federated learning session."""
    session_id: str
    config: SessionConfig
    coordinator_node: str
    participants: List[str]
    status: str
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    current_round: int = 0
    total_rounds: int = 0
    global_weights_hash: Optional[str] = None


class P2PCoordinator:
    """
    P2P Coordinator for federated learning.
    Manages sessions and coordinates between nodes without central server.
    """

    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or f"coord_{uuid.uuid4().hex[:8]}"
        self.known_nodes: Dict[str, NodeInfo] = {}
        self.active_sessions: Dict[str, FederatedSession] = {}
        self.round_data: Dict[str, Dict[str, Any]] = {}  # session_id -> round_data
        self.ipfs_client = None
        self.discovery_topic = "ailoos.session.discovery"
        self.session_topic_prefix = "ailoos.session."

    def initialize(self, ipfs_client=None):
        """
        Initialize coordinator with IPFS connection.

        Args:
            ipfs_client: IPFS client instance (optional)
        """
        self.ipfs_client = ipfs_client
        logger.info(f"🎯 P2P Coordinator initialized: {self.node_id}")

    async def register_node(self, node_info: Dict[str, Any]) -> bool:
        """
        Register a new node in the network.

        Args:
            node_info: Node information dictionary

        Returns:
            True if registration successful
        """
        try:
            node = NodeInfo(
                node_id=node_info["node_id"],
                ip_address=node_info.get("ip_address", "unknown"),
                hardware_info=node_info.get("hardware_info", {}),
                location=node_info.get("location", "unknown"),
                joined_at=time.time(),
                last_seen=time.time(),
                status="active"
            )

            self.known_nodes[node.node_id] = node

            # Announce node registration via IPFS PubSub
            if self.ipfs_client:
                await self._publish_to_topic(
                    self.discovery_topic,
                    {
                        "type": "node_registered",
                        "node_info": asdict(node)
                    }
                )

            logger.info(f"✅ Node registered: {node.node_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to register node: {e}")
            return False

    async def create_session(self, session_config: Dict[str, Any]) -> Optional[str]:
        """
        Create a new federated learning session.

        Args:
            session_config: Session configuration

        Returns:
            Session ID if created successfully
        """
        try:
            session_id = f"session_{int(time.time())}_{self.node_id}"

            config = SessionConfig(**session_config)

            session = FederatedSession(
                session_id=session_id,
                config=config,
                coordinator_node=self.node_id,
                participants=[self.node_id],  # Coordinator is always a participant
                status="waiting",
                created_at=time.time(),
                total_rounds=config.num_rounds
            )

            self.active_sessions[session_id] = session

            # Publish session creation
            if self.ipfs_client:
                await self._publish_to_topic(
                    self.discovery_topic,
                    {
                        "type": "session_created",
                        "session_info": asdict(session)
                    }
                )

            logger.info(f"🎯 Session created: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            return None

    async def join_session(self, session_id: str, node_id: str) -> bool:
        """
        Join an existing federated learning session.

        Args:
            session_id: ID of session to join
            node_id: ID of joining node

        Returns:
            True if joined successfully
        """
        if session_id not in self.active_sessions:
            logger.error(f"❌ Session not found: {session_id}")
            return False

        session = self.active_sessions[session_id]

        if node_id in session.participants:
            logger.warning(f"⚠️ Node {node_id} already in session {session_id}")
            return True

        if len(session.participants) >= session.config.max_participants:
            logger.error(f"❌ Session {session_id} is full")
            return False

        session.participants.append(node_id)

        # Publish join event
        if self.ipfs_client:
            await self._publish_to_topic(
                f"{self.session_topic_prefix}{session_id}",
                {
                    "type": "node_joined",
                    "session_id": session_id,
                    "node_id": node_id
                }
            )

        logger.info(f"✅ Node {node_id} joined session {session_id}")
        return True

    async def start_session(self, session_id: str) -> bool:
        """
        Start a federated learning session.

        Args:
            session_id: ID of session to start

        Returns:
            True if started successfully
        """
        if session_id not in self.active_sessions:
            logger.error(f"❌ Session not found: {session_id}")
            return False

        session = self.active_sessions[session_id]

        if len(session.participants) < session.config.min_participants:
            logger.error(f"❌ Not enough participants for session {session_id}")
            return False

        session.status = "active"
        session.started_at = time.time()
        session.current_round = 1

        # Publish session start
        if self.ipfs_client:
            await self._publish_to_topic(
                f"{self.session_topic_prefix}{session_id}",
                {
                    "type": "session_started",
                    "session_id": session_id,
                    "participants": session.participants
                }
            )

        logger.info(f"🚀 Session started: {session_id} with {len(session.participants)} participants")
        return True

    async def submit_weights(self, session_id: str, node_id: str,
                           weights_data: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """
        Submit local weights from a node.

        Args:
            session_id: Session ID
            node_id: Node ID
            weights_data: Serialized model weights
            metrics: Training metrics

        Returns:
            True if submitted successfully
        """
        if session_id not in self.active_sessions:
            logger.error(f"❌ Session not found: {session_id}")
            return False

        session = self.active_sessions[session_id]

        if node_id not in session.participants:
            logger.error(f"❌ Node {node_id} not in session {session_id}")
            return False

        # Initialize round data if needed
        if session_id not in self.round_data:
            self.round_data[session_id] = {}

        round_key = f"round_{session.current_round}"
        if round_key not in self.round_data[session_id]:
            self.round_data[session_id][round_key] = {}

        # Store submission
        self.round_data[session_id][round_key][node_id] = {
            "weights": weights_data,
            "metrics": metrics,
            "submitted_at": time.time()
        }

        # Check if round is complete
        round_participants = self.round_data[session_id][round_key]
        if len(round_participants) == len(session.participants):
            await self._complete_round(session_id, round_key)

        logger.info(f"✅ Weights submitted by {node_id} for session {session_id}")
        return True

    async def _complete_round(self, session_id: str, round_key: str):
        """
        Complete a round by aggregating weights.

        Args:
            session_id: Session ID
            round_key: Round identifier
        """
        session = self.active_sessions[session_id]
        round_data = self.round_data[session_id][round_key]

        # Aggregate weights (FedAvg)
        global_weights = self._aggregate_weights(round_data)

        # Store aggregated weights hash
        weights_json = json.dumps(global_weights, sort_keys=True)
        session.global_weights_hash = hashlib.sha256(weights_json.encode()).hexdigest()

        # Publish aggregated weights
        if self.ipfs_client:
            # Add to IPFS
            weights_cid = await self._add_to_ipfs(weights_json)

            await self._publish_to_topic(
                f"{self.session_topic_prefix}{session_id}",
                {
                    "type": "round_completed",
                    "session_id": session_id,
                    "round": session.current_round,
                    "weights_cid": weights_cid,
                    "weights_hash": session.global_weights_hash
                }
            )

        # Move to next round or complete session
        if session.current_round >= session.total_rounds:
            await self._complete_session(session_id)
        else:
            session.current_round += 1
            await self._start_next_round(session_id)

    def _aggregate_weights(self, round_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate weights using Federated Averaging.

        Args:
            round_data: Weight submissions for the round

        Returns:
            Aggregated global weights
        """
        if not round_data:
            return {}

        # Get all weight keys
        first_node = list(round_data.keys())[0]
        weight_keys = round_data[first_node]["weights"].keys()

        aggregated_weights = {}

        for key in weight_keys:
            # Collect tensors from all nodes
            tensors = []
            for node_data in round_data.values():
                # Convert back to tensor if needed
                weight_value = node_data["weights"][key]
                if isinstance(weight_value, list):
                    # Assume it's a list of floats
                    import torch
                    tensor = torch.tensor(weight_value)
                else:
                    tensor = weight_value
                tensors.append(tensor)

            # Average tensors
            if tensors:
                import torch
                aggregated_weights[key] = torch.stack(tensors).mean(dim=0).tolist()

        return aggregated_weights

    async def _complete_session(self, session_id: str):
        """Mark session as completed."""
        session = self.active_sessions[session_id]
        session.status = "completed"
        session.completed_at = time.time()

        # Publish completion
        if self.ipfs_client:
            await self._publish_to_topic(
                f"{self.session_topic_prefix}{session_id}",
                {
                    "type": "session_completed",
                    "session_id": session_id
                }
            )

        logger.info(f"🎉 Session completed: {session_id}")

    async def _start_next_round(self, session_id: str):
        """Start the next round."""
        session = self.active_sessions[session_id]

        # Publish next round start
        if self.ipfs_client:
            await self._publish_to_topic(
                f"{self.session_topic_prefix}{session_id}",
                {
                    "type": "round_started",
                    "session_id": session_id,
                    "round": session.current_round
                }
            )

        logger.info(f"🎯 Round {session.current_round} started for session {session_id}")

    async def _publish_to_topic(self, topic: str, message: Dict[str, Any]):
        """Publish message to IPFS PubSub topic."""
        if self.ipfs_client:
            try:
                await self.ipfs_client.publish_message(topic, json.dumps(message))
            except Exception as e:
                logger.warning(f"⚠️ Failed to publish to topic {topic}: {e}")

    async def _add_to_ipfs(self, data: str) -> Optional[str]:
        """Add data to IPFS."""
        if self.ipfs_client:
            try:
                # Create temporary file
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(data)
                    temp_path = f.name

                try:
                    cid = await self.ipfs_client.add_file(temp_path)
                    return cid
                finally:
                    os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"⚠️ Failed to add data to IPFS: {e}")
        return None

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a session."""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]
        return {
            "session_id": session.session_id,
            "status": session.status,
            "participants": session.participants,
            "current_round": session.current_round,
            "total_rounds": session.total_rounds,
            "created_at": session.created_at,
            "started_at": session.started_at,
            "completed_at": session.completed_at
        }

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        return [
            self.get_session_status(session_id)
            for session_id in self.active_sessions.keys()
            if self.active_sessions[session_id].status in ["waiting", "active"]
        ]

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        return {
            "total_nodes": len(self.known_nodes),
            "active_sessions": len([
                s for s in self.active_sessions.values()
                if s.status == "active"
            ]),
            "completed_sessions": len([
                s for s in self.active_sessions.values()
                if s.status == "completed"
            ]),
            "coordinator_id": self.node_id
        }


# Convenience functions
_coordinator_instance = None

def get_p2p_coordinator() -> P2PCoordinator:
    """Get singleton P2P coordinator instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = P2PCoordinator()
    return _coordinator_instance

async def create_federated_session(config: Dict[str, Any]) -> Optional[str]:
    """Create a new federated learning session."""
    coordinator = get_p2p_coordinator()
    return await coordinator.create_session(config)

async def join_federated_session(session_id: str, node_id: str) -> bool:
    """Join an existing federated learning session."""
    coordinator = get_p2p_coordinator()
    return await coordinator.join_session(session_id, node_id)