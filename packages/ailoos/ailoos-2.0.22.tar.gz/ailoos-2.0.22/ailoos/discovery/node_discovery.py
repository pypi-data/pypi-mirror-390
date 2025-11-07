"""
Node Discovery System for Ailoos P2P Network.
Automatically discovers and connects federated learning nodes.
"""

import asyncio
import json
import time
import hashlib
import platform
import psutil
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredNode:
    """Information about a discovered node."""
    node_id: str
    ip_address: Optional[str]
    platform: str
    architecture: str
    capabilities: List[str]
    hardware_specs: Dict[str, Any]
    location: Optional[str]
    last_seen: float
    status: str = "online"


class NodeDiscovery:
    """
    Automatic node discovery using IPFS PubSub and local network scanning.
    Enables nodes to find each other without central coordination.
    """

    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or self._generate_node_id()
        self.discovered_nodes: Dict[str, DiscoveredNode] = {}
        self.ipfs_client = None
        self.discovery_topic = "ailoos.node.discovery"
        self.heartbeat_topic = "ailoos.node.heartbeat"
        self.is_running = False
        self.heartbeat_interval = 30  # seconds
        self.node_timeout = 120  # seconds (2 minutes)

    def _generate_node_id(self) -> str:
        """Generate unique node ID based on hardware."""
        machine_id = platform.node() + platform.machine()
        return f"node_{hashlib.sha256(machine_id.encode()).hexdigest()[:16]}"

    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get local hardware information."""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
                "disk_gb": round(psutil.disk_usage('/').total / (1024**3), 1),
                "platform": platform.system(),
                "architecture": platform.machine()
            }
        except Exception as e:
            logger.warning(f"Failed to get hardware info: {e}")
            return {
                "cpu_count": 1,
                "memory_gb": 4,
                "platform": platform.system(),
                "architecture": platform.machine()
            }

    def initialize(self, ipfs_client=None):
        """
        Initialize node discovery.

        Args:
            ipfs_client: IPFS client instance
        """
        self.ipfs_client = ipfs_client
        logger.info(f"🔍 Node discovery initialized: {self.node_id}")

    async def start_discovery(self):
        """Start the node discovery process."""
        if self.is_running:
            logger.warning("⚠️ Node discovery already running")
            return

        self.is_running = True
        logger.info("🚀 Starting node discovery...")

        # Announce presence
        await self._announce_presence()

        # Start background tasks
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._listen_for_discovery())
        asyncio.create_task(self._cleanup_stale_nodes())

    async def stop_discovery(self):
        """Stop the node discovery process."""
        self.is_running = False
        logger.info("🛑 Node discovery stopped")

    async def _announce_presence(self):
        """Announce node presence to the network."""
        if not self.ipfs_client:
            return

        node_info = {
            "node_id": self.node_id,
            "platform": platform.system(),
            "architecture": platform.machine(),
            "capabilities": ["federated_learning", "model_training", "inference"],
            "hardware_specs": self._get_hardware_info(),
            "location": self._get_location(),
            "timestamp": time.time(),
            "type": "node_announcement"
        }

        try:
            await self.ipfs_client.publish_message(self.discovery_topic, json.dumps(node_info))
            logger.debug("📢 Node presence announced")
        except Exception as e:
            logger.warning(f"⚠️ Failed to announce presence: {e}")

    async def _heartbeat_loop(self):
        """Send periodic heartbeats to maintain presence."""
        while self.is_running:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.warning(f"⚠️ Heartbeat failed: {e}")
                await asyncio.sleep(5)

    async def _send_heartbeat(self):
        """Send heartbeat message."""
        if not self.ipfs_client:
            return

        heartbeat = {
            "node_id": self.node_id,
            "timestamp": time.time(),
            "type": "heartbeat"
        }

        try:
            await self.ipfs_client.publish_message(self.heartbeat_topic, json.dumps(heartbeat))
        except Exception as e:
            logger.debug(f"Failed to send heartbeat: {e}")

    async def _listen_for_discovery(self):
        """Listen for node discovery messages."""
        if not self.ipfs_client:
            return

        while self.is_running:
            try:
                # Subscribe to discovery topic
                messages = await self.ipfs_client.subscribe_topic(self.discovery_topic)
                if messages:
                    for msg in messages:
                        await self._process_discovery_message(msg)

                # Subscribe to heartbeat topic
                heartbeats = await self.ipfs_client.subscribe_topic(self.heartbeat_topic)
                if heartbeats:
                    for msg in heartbeats:
                        await self._process_heartbeat_message(msg)

                await asyncio.sleep(1)

            except Exception as e:
                logger.warning(f"⚠️ Discovery listening failed: {e}")
                await asyncio.sleep(5)

    async def _process_discovery_message(self, message: Dict[str, Any]):
        """Process incoming discovery message."""
        try:
            if message.get("type") == "node_announcement":
                node_id = message.get("node_id")
                if node_id and node_id != self.node_id:
                    # Update or add node
                    if node_id in self.discovered_nodes:
                        # Update existing node
                        existing = self.discovered_nodes[node_id]
                        existing.last_seen = time.time()
                        existing.status = "online"
                    else:
                        # Add new node
                        node = DiscoveredNode(
                            node_id=node_id,
                            ip_address=message.get("ip_address"),
                            platform=message.get("platform", "unknown"),
                            architecture=message.get("architecture", "unknown"),
                            capabilities=message.get("capabilities", []),
                            hardware_specs=message.get("hardware_specs", {}),
                            location=message.get("location"),
                            last_seen=time.time()
                        )
                        self.discovered_nodes[node_id] = node
                        logger.info(f"🔍 Discovered new node: {node_id}")

        except Exception as e:
            logger.debug(f"Failed to process discovery message: {e}")

    async def _process_heartbeat_message(self, message: Dict[str, Any]):
        """Process incoming heartbeat message."""
        try:
            if message.get("type") == "heartbeat":
                node_id = message.get("node_id")
                if node_id and node_id in self.discovered_nodes:
                    self.discovered_nodes[node_id].last_seen = time.time()
                    self.discovered_nodes[node_id].status = "online"

        except Exception as e:
            logger.debug(f"Failed to process heartbeat: {e}")

    async def _cleanup_stale_nodes(self):
        """Remove nodes that haven't been seen recently."""
        while self.is_running:
            try:
                current_time = time.time()
                stale_nodes = []

                for node_id, node in self.discovered_nodes.items():
                    if current_time - node.last_seen > self.node_timeout:
                        stale_nodes.append(node_id)

                for node_id in stale_nodes:
                    node = self.discovered_nodes[node_id]
                    node.status = "offline"
                    logger.debug(f"📴 Node marked offline: {node_id}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.warning(f"⚠️ Cleanup failed: {e}")
                await asyncio.sleep(30)

    def _get_location(self) -> Optional[str]:
        """Get approximate location (simplified)."""
        try:
            # In a real implementation, this could use IP geolocation
            return "Madrid, Spain"  # Placeholder
        except Exception:
            return None

    def get_discovered_nodes(self, capability_filter: Optional[str] = None) -> List[DiscoveredNode]:
        """
        Get list of discovered nodes.

        Args:
            capability_filter: Filter by specific capability

        Returns:
            List of discovered nodes
        """
        nodes = list(self.discovered_nodes.values())

        if capability_filter:
            nodes = [n for n in nodes if capability_filter in n.capabilities]

        return nodes

    def get_online_nodes(self, capability_filter: Optional[str] = None) -> List[DiscoveredNode]:
        """
        Get list of online nodes.

        Args:
            capability_filter: Filter by specific capability

        Returns:
            List of online nodes
        """
        nodes = [n for n in self.discovered_nodes.values() if n.status == "online"]

        if capability_filter:
            nodes = [n for n in nodes if capability_filter in n.capabilities]

        return nodes

    def find_nodes_for_federated_learning(self, min_nodes: int = 2) -> List[DiscoveredNode]:
        """
        Find nodes suitable for federated learning.

        Args:
            min_nodes: Minimum number of nodes required

        Returns:
            List of suitable nodes
        """
        fl_nodes = self.get_online_nodes("federated_learning")

        if len(fl_nodes) >= min_nodes:
            # Sort by hardware capability (simple heuristic)
            fl_nodes.sort(key=lambda n: n.hardware_specs.get("memory_gb", 0), reverse=True)
            return fl_nodes[:min_nodes]

        return fl_nodes

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network discovery statistics."""
        total_nodes = len(self.discovered_nodes)
        online_nodes = len([n for n in self.discovered_nodes.values() if n.status == "online"])
        offline_nodes = total_nodes - online_nodes

        # Count capabilities
        capabilities = {}
        for node in self.discovered_nodes.values():
            for cap in node.capabilities:
                capabilities[cap] = capabilities.get(cap, 0) + 1

        return {
            "total_discovered": total_nodes,
            "online_nodes": online_nodes,
            "offline_nodes": offline_nodes,
            "capabilities": capabilities,
            "is_running": self.is_running,
            "local_node_id": self.node_id
        }

    async def request_node_info(self, target_node_id: str) -> Optional[Dict[str, Any]]:
        """
        Request detailed information from a specific node.

        Args:
            target_node_id: ID of node to query

        Returns:
            Node information if available
        """
        if not self.ipfs_client:
            return None

        # Send info request
        request = {
            "type": "info_request",
            "from_node": self.node_id,
            "target_node": target_node_id,
            "timestamp": time.time()
        }

        try:
            await self.ipfs_client.publish_message(
                f"ailoos.node.{target_node_id}",
                json.dumps(request)
            )

            # In a real implementation, we'd wait for a response
            # For now, return cached info
            if target_node_id in self.discovered_nodes:
                return asdict(self.discovered_nodes[target_node_id])

        except Exception as e:
            logger.warning(f"⚠️ Failed to request node info: {e}")

        return None


# Convenience functions
_discovery_instance = None

def get_node_discovery() -> NodeDiscovery:
    """Get singleton node discovery instance."""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = NodeDiscovery()
    return _discovery_instance

async def start_node_discovery():
    """Start node discovery service."""
    discovery = get_node_discovery()
    await discovery.start_discovery()

async def stop_node_discovery():
    """Stop node discovery service."""
    discovery = get_node_discovery()
    await discovery.stop_discovery()

def find_federated_nodes(min_nodes: int = 2) -> List[DiscoveredNode]:
    """Find nodes suitable for federated learning."""
    discovery = get_node_discovery()
    return discovery.find_nodes_for_federated_learning(min_nodes)