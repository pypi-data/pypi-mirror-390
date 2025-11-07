#!/usr/bin/env python3
"""
P2P Network Communication API
API de comunicación peer-to-peer para nodos federados de EmpoorioLM
"""

import asyncio
import json
import logging
import os
import socket
import ssl
import threading
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import secrets

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psutil
import aiohttp
# import websockets  # Commented out to avoid dependency issues

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/p2p_network.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class NodeInfo(BaseModel):
    """Node information"""
    node_id: str
    ip_address: str
    port: int
    public_key: str
    capabilities: List[str]  # ["training", "inference", "coordinator"]
    reputation_score: float = 1.0
    last_seen: str
    location: Optional[str] = None
    hardware_info: Dict[str, Any] = {}

class Message(BaseModel):
    """P2P message"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str  # "handshake", "model_update", "heartbeat", "request", "response"
    payload: Dict[str, Any]
    timestamp: str
    signature: str
    ttl: int = 64  # Time to live for message routing

class FederatedUpdate(BaseModel):
    """Federated learning model update"""
    session_id: str
    round_number: int
    node_id: str
    model_weights: Dict[str, Any]  # Serialized model weights
    gradients: Optional[Dict[str, Any]] = None
    metrics: Dict[str, float] = {}
    sample_count: int
    checksum: str
    signature: str

class P2PRequest(BaseModel):
    """P2P request"""
    request_id: str
    requester_id: str
    request_type: str  # "model_sync", "data_request", "validation"
    parameters: Dict[str, Any]
    timeout: int = 30  # seconds

class P2PResponse(BaseModel):
    """P2P response"""
    request_id: str
    responder_id: str
    response_type: str
    data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

# Global state
known_nodes: Dict[str, Dict[str, Any]] = {}
active_connections: Dict[str, WebSocket] = {}
message_queue: asyncio.Queue = asyncio.Queue()
pending_requests: Dict[str, Dict[str, Any]] = {}
routing_table: Dict[str, List[str]] = {}  # node_id -> list of neighbor node_ids

# P2P Node class
class P2PNode:
    """Individual P2P node in the federated network"""

    def __init__(self, node_id: str, host: str = "0.0.0.0", port: int = 8002):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.public_key = secrets.token_hex(32)  # Mock public key
        self.private_key = secrets.token_hex(32)  # Mock private key

        self.capabilities = ["training", "inference"]
        self.neighbors: Set[str] = set()
        self.is_running = False
        self.message_handlers: Dict[str, Callable] = {}

        # Register default message handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers.update({
            "handshake": self._handle_handshake,
            "heartbeat": self._handle_heartbeat,
            "model_update": self._handle_model_update,
            "federated_request": self._handle_federated_request,
            "federated_response": self._handle_federated_response,
        })

    async def start(self):
        """Start the P2P node"""
        self.is_running = True
        logger.info(f"🚀 Starting P2P node {self.node_id} on {self.host}:{self.port}")

        # Note: WebSocket server commented out due to dependency issues
        # In production, uncomment and install websockets package
        """
        # Start WebSocket server
        server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10
        )
        """

        # Start background tasks
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._message_processor())

        logger.info(f"✅ P2P node {self.node_id} started successfully (WebSocket disabled)")
        return None

    async def stop(self):
        """Stop the P2P node"""
        self.is_running = False
        logger.info(f"🛑 Stopping P2P node {self.node_id}")

    async def connect_to_peer(self, peer_host: str, peer_port: int, peer_id: str):
        """Connect to another P2P peer"""
        try:
            # Note: WebSocket connection commented out due to dependency issues
            # In production, uncomment and install websockets package
            """
            uri = f"ws://{peer_host}:{peer_port}"
            websocket = await websockets.connect(uri)

            # Send handshake
            handshake_msg = {
                "message_id": str(uuid.uuid4()),
                "sender_id": self.node_id,
                "receiver_id": peer_id,
                "message_type": "handshake",
                "payload": {
                    "node_info": self.get_node_info()
                },
                "timestamp": datetime.now().isoformat(),
                "signature": self._sign_message("handshake"),
                "ttl": 64
            }

            await websocket.send(json.dumps(handshake_msg))

            # Store connection
            active_connections[peer_id] = websocket
            self.neighbors.add(peer_id)

            # Start message handler for this connection
            asyncio.create_task(self._handle_peer_connection(peer_id, websocket))
            """

            # Mock connection for testing
            self.neighbors.add(peer_id)
            logger.info(f"🤝 Mock connected to peer {peer_id} at {peer_host}:{peer_port}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to peer {peer_id}: {e}")
            return False

    async def send_message(self, receiver_id: str, message_type: str, payload: Dict[str, Any]) -> bool:
        """Send message to another node"""
        if receiver_id not in active_connections:
            logger.warning(f"No active connection to {receiver_id}")
            return False

        try:
            message = {
                "message_id": str(uuid.uuid4()),
                "sender_id": self.node_id,
                "receiver_id": receiver_id,
                "message_type": message_type,
                "payload": payload,
                "timestamp": datetime.now().isoformat(),
                "signature": self._sign_message(message_type),
                "ttl": 64
            }

            websocket = active_connections[receiver_id]
            await websocket.send(json.dumps(message))

            logger.debug(f"📤 Sent {message_type} to {receiver_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to {receiver_id}: {e}")
            return False

    async def broadcast_message(self, message_type: str, payload: Dict[str, Any]):
        """Broadcast message to all connected peers"""
        for peer_id in list(self.neighbors):
            await self.send_message(peer_id, message_type, payload)

    async def send_federated_update(self, session_id: str, round_number: int, model_weights: Dict[str, Any], metrics: Dict[str, float]):
        """Send federated learning model update"""
        update = FederatedUpdate(
            session_id=session_id,
            round_number=round_number,
            node_id=self.node_id,
            model_weights=model_weights,
            metrics=metrics,
            sample_count=100,  # Mock sample count
            checksum=self._calculate_checksum(model_weights),
            signature=self._sign_message("model_update")
        )

        # Send to coordinator (assuming coordinator is known)
        coordinator_id = "coordinator_001"  # In real implementation, this would be discovered
        if coordinator_id in active_connections:
            await self.send_message(coordinator_id, "model_update", update.dict())
        else:
            logger.warning("No coordinator connection available for federated update")

    def get_node_info(self) -> Dict[str, Any]:
        """Get node information"""
        return {
            "node_id": self.node_id,
            "ip_address": self.host,
            "port": self.port,
            "public_key": self.public_key,
            "capabilities": self.capabilities,
            "reputation_score": 1.0,
            "last_seen": datetime.now().isoformat(),
            "hardware_info": self._get_hardware_info()
        }

    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent
            }
        except:
            return {"cpu_count": 4, "memory_gb": 8.0}

    def _sign_message(self, message_type: str) -> str:
        """Sign message with private key (mock implementation)"""
        return hashlib.sha256(f"{self.node_id}{message_type}{self.private_key}".encode()).hexdigest()

    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum of data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def _handle_connection(self, websocket: WebSocket, path: str):
        """Handle incoming WebSocket connection"""
        try:
            await websocket.accept()

            # Wait for handshake
            raw_message = await websocket.receive_text()
            message = json.loads(raw_message)

            if message.get("message_type") == "handshake":
                peer_id = message["sender_id"]
                active_connections[peer_id] = websocket
                self.neighbors.add(peer_id)

                # Send handshake response
                response = {
                    "message_id": str(uuid.uuid4()),
                    "sender_id": self.node_id,
                    "receiver_id": peer_id,
                    "message_type": "handshake_ack",
                    "payload": {"node_info": self.get_node_info()},
                    "timestamp": datetime.now().isoformat(),
                    "signature": self._sign_message("handshake_ack"),
                    "ttl": 64
                }

                await websocket.send(json.dumps(response))
                logger.info(f"🤝 Handshake completed with {peer_id}")

                # Start message handler
                asyncio.create_task(self._handle_peer_connection(peer_id, websocket))

        except Exception as e:
            logger.error(f"Connection handler error: {e}")

    async def _handle_peer_connection(self, peer_id: str, websocket: WebSocket):
        """Handle messages from a connected peer"""
        try:
            while self.is_running:
                raw_message = await websocket.receive_text()
                message = json.loads(raw_message)

                # Process message
                await self._process_message(message)

        except WebSocketDisconnect:
            logger.info(f"Peer {peer_id} disconnected")
            if peer_id in active_connections:
                del active_connections[peer_id]
            if peer_id in self.neighbors:
                self.neighbors.remove(peer_id)

        except Exception as e:
            logger.error(f"Peer connection error with {peer_id}: {e}")

    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        message_type = message.get("message_type", "")
        sender_id = message.get("sender_id", "")

        logger.debug(f"📥 Received {message_type} from {sender_id}")

        # Handle message based on type
        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Message handler error for {message_type}: {e}")
        else:
            logger.warning(f"No handler for message type: {message_type}")

    async def _handle_handshake(self, message: Dict[str, Any]):
        """Handle handshake message"""
        peer_info = message.get("payload", {}).get("node_info", {})
        peer_id = message["sender_id"]

        # Store peer information
        known_nodes[peer_id] = peer_info
        logger.info(f"🤝 Handshake from {peer_id}")

    async def _handle_heartbeat(self, message: Dict[str, Any]):
        """Handle heartbeat message"""
        peer_id = message["sender_id"]
        # Update last seen time
        if peer_id in known_nodes:
            known_nodes[peer_id]["last_seen"] = datetime.now().isoformat()

    async def _handle_model_update(self, message: Dict[str, Any]):
        """Handle model update message"""
        # Forward to coordinator or process locally
        payload = message.get("payload", {})
        logger.info(f"📥 Model update from {message['sender_id']}: round {payload.get('round_number')}")

        # In a real implementation, this would be forwarded to the coordinator
        # or processed by the local federated learning algorithm

    async def _handle_federated_request(self, message: Dict[str, Any]):
        """Handle federated learning request"""
        request_id = message.get("payload", {}).get("request_id")
        if request_id:
            pending_requests[request_id] = message

    async def _handle_federated_response(self, message: Dict[str, Any]):
        """Handle federated learning response"""
        request_id = message.get("payload", {}).get("request_id")
        if request_id and request_id in pending_requests:
            # Process response
            del pending_requests[request_id]

    async def _heartbeat_loop(self):
        """Send periodic heartbeats to connected peers"""
        while self.is_running:
            try:
                heartbeat_msg = {
                    "message_type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "node_info": self.get_node_info()
                }

                await self.broadcast_message("heartbeat", heartbeat_msg)
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(5)

    async def _message_processor(self):
        """Process messages from the queue"""
        while self.is_running:
            try:
                # Process any queued messages
                if not message_queue.empty():
                    message = await message_queue.get()
                    await self._process_message(message)
                    message_queue.task_done()

                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Message processor error: {e}")

# P2P Network class
class P2PNetwork:
    """P2P Network coordinator for federated learning"""

    def __init__(self):
        self.nodes: Dict[str, P2PNode] = {}
        self.is_running = False

    def create_node(self, node_id: str, host: str = "0.0.0.0", port: int = 8002) -> P2PNode:
        """Create a new P2P node"""
        node = P2PNode(node_id, host, port)
        self.nodes[node_id] = node
        return node

    async def start_network(self):
        """Start the P2P network"""
        self.is_running = True
        logger.info("🌐 Starting P2P Network")

        # Start all nodes
        for node in self.nodes.values():
            await node.start()

    async def stop_network(self):
        """Stop the P2P network"""
        self.is_running = False
        logger.info("🛑 Stopping P2P Network")

        # Stop all nodes
        for node in self.nodes.values():
            await node.stop()

    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        return {
            "total_nodes": len(self.nodes),
            "active_connections": len(active_connections),
            "known_nodes": len(known_nodes),
            "pending_requests": len(pending_requests)
        }

# FastAPI app for P2P network management
app = FastAPI(
    title="P2P Network API",
    description="API de gestión de red P2P para aprendizaje federado",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global P2P network
p2p_network = P2PNetwork()

@app.post("/api/nodes/create")
async def create_node(node_id: str, host: str = "0.0.0.0", port: int = 8002):
    """Create a new P2P node"""
    node = p2p_network.create_node(node_id, host, port)
    return {"node_id": node_id, "status": "created", "host": host, "port": port}

@app.post("/api/nodes/{node_id}/start")
async def start_node(node_id: str):
    """Start a P2P node"""
    if node_id not in p2p_network.nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node = p2p_network.nodes[node_id]
    await node.start()
    return {"node_id": node_id, "status": "started"}

@app.post("/api/nodes/{node_id}/connect")
async def connect_node(node_id: str, peer_host: str, peer_port: int, peer_id: str):
    """Connect node to a peer"""
    if node_id not in p2p_network.nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node = p2p_network.nodes[node_id]
    success = await node.connect_to_peer(peer_host, peer_port, peer_id)
    return {"success": success, "peer_id": peer_id}

@app.post("/api/nodes/{node_id}/send")
async def send_message(node_id: str, receiver_id: str, message_type: str, payload: Dict[str, Any]):
    """Send message from node"""
    if node_id not in p2p_network.nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node = p2p_network.nodes[node_id]
    success = await node.send_message(receiver_id, message_type, payload)
    return {"success": success}

@app.get("/api/network/info")
async def get_network_info():
    """Get network information"""
    return p2p_network.get_network_info()

@app.get("/api/nodes")
async def list_nodes():
    """List all nodes"""
    return {
        "nodes": [
            {
                "node_id": node_id,
                "host": node.host,
                "port": node.port,
                "neighbors": list(node.neighbors),
                "capabilities": node.capabilities
            }
            for node_id, node in p2p_network.nodes.items()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "network_info": p2p_network.get_network_info(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "P2P Network API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "create_node": "POST /api/nodes/create",
            "start_node": "POST /api/nodes/{id}/start",
            "connect_node": "POST /api/nodes/{id}/connect",
            "send_message": "POST /api/nodes/{id}/send",
            "network_info": "GET /api/network/info",
            "list_nodes": "GET /api/nodes"
        }
    }

def create_p2p_network(host: str = "0.0.0.0", port: int = 8003) -> None:
    """Create and run the P2P network API server"""
    logger.info(f"🚀 Starting P2P Network API on {host}:{port}")

    uvicorn.run(
        "src.ai.p2p.p2p_network:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    # Run server directly
    create_p2p_network()