#!/usr/bin/env python3
"""
Federated Learning Session Management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FederatedSession:
    """Federated learning session"""

    session_id: str
    model_name: str
    rounds: int = 5
    min_nodes: int = 3
    max_nodes: int = 100
    status: str = "created"
    created_at: str = ""
    participants: List[str] = None
    current_round: int = 0
    total_rounds: int = 5

    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def add_participant(self, node_id: str):
        """Add a participant to the session"""
        if node_id not in self.participants:
            self.participants.append(node_id)
            logger.info(f"Added participant {node_id} to session {self.session_id}")

    def remove_participant(self, node_id: str):
        """Remove a participant from the session"""
        if node_id in self.participants:
            self.participants.remove(node_id)
            logger.info(f"Removed participant {node_id} from session {self.session_id}")

    def can_start(self) -> bool:
        """Check if session can start"""
        return len(self.participants) >= self.min_nodes

    def is_complete(self) -> bool:
        """Check if session is complete"""
        return self.current_round >= self.total_rounds

    def next_round(self):
        """Advance to next round"""
        if not self.is_complete():
            self.current_round += 1
            logger.info(f"Session {self.session_id} advanced to round {self.current_round}")

    def get_status(self) -> Dict[str, Any]:
        """Get session status"""
        return {
            "session_id": self.session_id,
            "model_name": self.model_name,
            "status": self.status,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "participants": len(self.participants),
            "min_nodes": self.min_nodes,
            "can_start": self.can_start(),
            "is_complete": self.is_complete(),
            "created_at": self.created_at
        }