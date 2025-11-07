#!/usr/bin/env python3
"""
Coordinator for Ailoos Federated Learning
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Coordinator:
    """Main coordinator for federated learning sessions"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.connected_nodes: Dict[str, Dict[str, Any]] = {}
        self.session_counter = 0

    async def create_session(self, session_config: Dict[str, Any]) -> str:
        """Create a new federated learning session"""
        session_id = f"session_{self.session_counter}"
        self.session_counter += 1

        session = {
            "session_id": session_id,
            "config": session_config,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "participants": [],
            "rounds_completed": 0,
            "total_rounds": session_config.get("rounds", 5)
        }

        self.active_sessions[session_id] = session
        logger.info(f"Created session {session_id}")
        return session_id

    async def register_node(self, node_id: str, node_info: Dict[str, Any]):
        """Register a node with the coordinator"""
        self.connected_nodes[node_id] = {
            "node_id": node_id,
            "info": node_info,
            "registered_at": datetime.now().isoformat(),
            "status": "active"
        }
        logger.info(f"Registered node {node_id}")

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a session"""
        return self.active_sessions.get(session_id)

    def get_connected_nodes(self) -> List[str]:
        """Get list of connected node IDs"""
        return list(self.connected_nodes.keys())

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_sessions.keys())