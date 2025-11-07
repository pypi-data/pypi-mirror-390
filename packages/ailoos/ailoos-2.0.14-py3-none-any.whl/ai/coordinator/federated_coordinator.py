#!/usr/bin/env python3
"""
Federated Learning Coordinator
Servidor coordinador para el aprendizaje federado de EmpoorioLM
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/federated_coordinator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class NodeRegistration(BaseModel):
    """Node registration request"""
    node_id: str = Field(..., description="Unique node identifier")
    ip_address: str = Field(..., description="Node IP address")
    hardware_info: Dict[str, Any] = Field(..., description="Hardware specifications")
    location: Optional[str] = Field(None, description="Geographic location")
    reputation_score: float = Field(1.0, description="Node reputation score")

class TrainingSessionRequest(BaseModel):
    """Training session creation request"""
    model_name: str = Field("empoorio-lm", description="Model to train")
    dataset_id: str = Field(..., description="Dataset identifier")
    rounds: int = Field(5, description="Number of training rounds")
    min_nodes: int = Field(2, description="Minimum nodes required")
    max_nodes: int = Field(100, description="Maximum nodes allowed")
    privacy_budget: float = Field(0.1, description="Differential privacy budget")
    learning_rate: float = Field(0.001, description="Learning rate")
    local_epochs: int = Field(3, description="Local epochs per round")
    batch_size: int = Field(32, description="Batch size")

class ModelUpdate(BaseModel):
    """Model update from node"""
    node_id: str
    session_id: str
    round_number: int
    model_weights: Dict[str, Any]  # Serialized model weights
    metrics: Dict[str, float]  # Training metrics
    sample_count: int
    checksum: str  # Integrity check

class SessionStatus(BaseModel):
    """Training session status"""
    session_id: str
    status: str  # "waiting", "active", "completed", "failed"
    current_round: int
    total_rounds: int
    active_nodes: int
    total_nodes: int
    start_time: Optional[str]
    estimated_completion: Optional[str]
    global_metrics: Dict[str, Any]

class NodeHeartbeat(BaseModel):
    """Node heartbeat"""
    node_id: str
    status: str  # "active", "training", "idle"
    current_session: Optional[str]
    last_update: str
    metrics: Optional[Dict[str, Any]] = None

# Global state
active_sessions: Dict[str, Dict[str, Any]] = {}
registered_nodes: Dict[str, Dict[str, Any]] = {}
node_connections: Dict[str, WebSocket] = {}
session_rounds: Dict[str, Dict[str, Any]] = {}

# Coordinator class
class FederatedCoordinator:
    """Main federated learning coordinator"""

    def __init__(self):
        self.active_sessions = {}
        self.registered_nodes = {}
        self.node_connections = {}
        self.session_rounds = {}

    async def register_node(self, node_data: NodeRegistration) -> Dict[str, Any]:
        """Register a new node in the network"""
        node_id = node_data.node_id

        self.registered_nodes[node_id] = {
            "node_id": node_id,
            "ip_address": node_data.ip_address,
            "hardware_info": node_data.hardware_info,
            "location": node_data.location,
            "reputation_score": node_data.reputation_score,
            "status": "registered",
            "last_heartbeat": datetime.now().isoformat(),
            "joined_sessions": [],
            "total_contributions": 0,
            "total_rewards": 0
        }

        logger.info(f"✅ Node registered: {node_id}")
        return {"status": "registered", "node_id": node_id}

    async def create_training_session(self, session_request: TrainingSessionRequest) -> str:
        """Create a new training session"""
        session_id = str(uuid.uuid4())

        session = {
            "session_id": session_id,
            "model_name": session_request.model_name,
            "dataset_id": session_request.dataset_id,
            "rounds": session_request.rounds,
            "current_round": 0,
            "min_nodes": session_request.min_nodes,
            "max_nodes": session_request.max_nodes,
            "privacy_budget": session_request.privacy_budget,
            "learning_rate": session_request.learning_rate,
            "local_epochs": session_request.local_epochs,
            "batch_size": session_request.batch_size,
            "status": "waiting",
            "registered_nodes": [],
            "active_nodes": [],
            "completed_nodes": [],
            "global_model": None,
            "round_metrics": [],
            "start_time": None,
            "end_time": None,
            "created_at": datetime.now().isoformat()
        }

        self.active_sessions[session_id] = session
        logger.info(f"🎯 Training session created: {session_id}")
        return session_id

    async def join_session(self, session_id: str, node_id: str) -> Dict[str, Any]:
        """Node joins a training session"""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = self.active_sessions[session_id]

        if node_id not in self.registered_nodes:
            raise HTTPException(status_code=404, detail="Node not registered")

        if node_id in session["registered_nodes"]:
            return {"status": "already_joined"}

        if len(session["registered_nodes"]) >= session["max_nodes"]:
            raise HTTPException(status_code=400, detail="Session full")

        session["registered_nodes"].append(node_id)
        self.registered_nodes[node_id]["joined_sessions"].append(session_id)

        # Check if we can start the session
        if len(session["registered_nodes"]) >= session["min_nodes"] and session["status"] == "waiting":
            await self.start_session(session_id)

        logger.info(f"🤝 Node {node_id} joined session {session_id}")
        return {"status": "joined", "session_id": session_id}

    async def start_session(self, session_id: str):
        """Start a training session"""
        session = self.active_sessions[session_id]
        session["status"] = "active"
        session["start_time"] = datetime.now().isoformat()
        session["active_nodes"] = session["registered_nodes"].copy()

        # Initialize global model (simplified)
        session["global_model"] = {
            "weights": {},
            "version": 1,
            "round": 0
        }

        # Start first round
        await self.start_round(session_id, 1)

        logger.info(f"🚀 Training session started: {session_id}")

    async def start_round(self, session_id: str, round_number: int):
        """Start a new training round"""
        session = self.active_sessions[session_id]
        session["current_round"] = round_number

        round_data = {
            "round_number": round_number,
            "start_time": datetime.now().isoformat(),
            "expected_nodes": len(session["active_nodes"]),
            "received_updates": [],
            "status": "training"
        }

        self.session_rounds[f"{session_id}_{round_number}"] = round_data

        # Notify all nodes in session to start training
        await self.broadcast_to_session(session_id, {
            "type": "start_round",
            "session_id": session_id,
            "round_number": round_number,
            "global_model": session["global_model"],
            "config": {
                "learning_rate": session["learning_rate"],
                "local_epochs": session["local_epochs"],
                "batch_size": session["batch_size"]
            }
        })

        logger.info(f"🔄 Round {round_number} started for session {session_id}")

    async def receive_model_update(self, update: ModelUpdate) -> Dict[str, Any]:
        """Receive model update from a node"""
        session_id = update.session_id
        round_number = update.round_number
        node_id = update.node_id

        round_key = f"{session_id}_{round_number}"
        if round_key not in self.session_rounds:
            raise HTTPException(status_code=400, detail="Round not active")

        round_data = self.session_rounds[round_key]
        session = self.active_sessions[session_id]

        # Record the update
        update_record = {
            "node_id": node_id,
            "model_weights": update.model_weights,
            "metrics": update.metrics,
            "sample_count": update.sample_count,
            "received_at": datetime.now().isoformat(),
            "checksum": update.checksum
        }

        round_data["received_updates"].append(update_record)

        # Check if round is complete
        if len(round_data["received_updates"]) >= len(session["active_nodes"]):
            await self.complete_round(session_id, round_number)

        logger.info(f"📥 Model update received from {node_id} for round {round_number}")
        return {"status": "received", "round_complete": len(round_data["received_updates"]) >= len(session["active_nodes"])}

    async def complete_round(self, session_id: str, round_number: int):
        """Complete a training round and aggregate updates"""
        round_key = f"{session_id}_{round_number}"
        round_data = self.session_rounds[round_key]
        session = self.active_sessions[session_id]

        # Simple FedAvg aggregation (simplified)
        updates = round_data["received_updates"]
        if updates:
            # Aggregate weights (simplified - in real implementation would use proper FedAvg)
            aggregated_weights = self.aggregate_weights(updates)
            session["global_model"] = {
                "weights": aggregated_weights,
                "version": round_number + 1,
                "round": round_number
            }

            # Calculate round metrics
            round_metrics = {
                "round": round_number,
                "nodes_participated": len(updates),
                "total_samples": sum(u["sample_count"] for u in updates),
                "avg_accuracy": sum(u["metrics"].get("accuracy", 0) for u in updates) / len(updates),
                "avg_loss": sum(u["metrics"].get("loss", 0) for u in updates) / len(updates),
                "completed_at": datetime.now().isoformat()
            }

            session["round_metrics"].append(round_metrics)
            round_data["status"] = "completed"

        # Check if session is complete
        if round_number >= session["rounds"]:
            await self.complete_session(session_id)
        else:
            # Start next round
            await self.start_round(session_id, round_number + 1)

        logger.info(f"✅ Round {round_number} completed for session {session_id}")

    async def complete_session(self, session_id: str):
        """Complete a training session"""
        session = self.active_sessions[session_id]
        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()

        # Calculate final metrics
        final_metrics = {
            "total_rounds": session["rounds"],
            "total_nodes": len(session["registered_nodes"]),
            "total_contributions": sum(len(r["received_updates"]) for r in self.session_rounds.values() if r["round_number"] <= session["rounds"]),
            "final_model_version": session["global_model"]["version"] if session["global_model"] else None
        }

        session["final_metrics"] = final_metrics

        # Notify all nodes
        await self.broadcast_to_session(session_id, {
            "type": "session_completed",
            "session_id": session_id,
            "final_metrics": final_metrics,
            "final_model": session["global_model"]
        })

        logger.info(f"🎉 Training session completed: {session_id}")

    def aggregate_weights(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple FedAvg aggregation (simplified)"""
        if not updates:
            return {}

        # In a real implementation, this would properly aggregate PyTorch model weights
        # For now, return a simplified aggregation
        return {
            "aggregated": True,
            "num_updates": len(updates),
            "total_samples": sum(u["sample_count"] for u in updates),
            "timestamp": datetime.now().isoformat()
        }

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """Broadcast message to all nodes in session"""
        session = self.active_sessions[session_id]

        for node_id in session["active_nodes"]:
            if node_id in self.node_connections:
                try:
                    await self.node_connections[node_id].send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to {node_id}: {e}")

    async def handle_heartbeat(self, heartbeat: NodeHeartbeat):
        """Handle node heartbeat"""
        node_id = heartbeat.node_id

        if node_id in self.registered_nodes:
            self.registered_nodes[node_id]["last_heartbeat"] = heartbeat.last_update
            self.registered_nodes[node_id]["status"] = heartbeat.status
            self.registered_nodes[node_id]["current_session"] = heartbeat.current_session

            # Update metrics
            if "metrics" in heartbeat.__dict__:
                self.registered_nodes[node_id]["metrics"] = heartbeat.metrics

    def get_session_status(self, session_id: str) -> SessionStatus:
        """Get status of a training session"""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = self.active_sessions[session_id]

        return SessionStatus(
            session_id=session_id,
            status=session["status"],
            current_round=session["current_round"],
            total_rounds=session["rounds"],
            active_nodes=len(session["active_nodes"]),
            total_nodes=len(session["registered_nodes"]),
            start_time=session["start_time"],
            estimated_completion=None,  # Would calculate based on progress
            global_metrics={"rounds": session.get("round_metrics", [])}
        )

# Global coordinator instance
coordinator = FederatedCoordinator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Federated Coordinator...")
    yield
    logger.info("🛑 Shutting down Federated Coordinator...")

# Create FastAPI app
app = FastAPI(
    title="Federated Learning Coordinator",
    description="Coordinador central para aprendizaje federado de EmpoorioLM",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/nodes/register")
async def register_node(node: NodeRegistration):
    """Register a new node"""
    return await coordinator.register_node(node)

@app.post("/api/sessions/create")
async def create_session(session_request: TrainingSessionRequest):
    """Create a new training session"""
    session_id = await coordinator.create_training_session(session_request)
    return {"session_id": session_id, "status": "created"}

@app.post("/api/sessions/{session_id}/join")
async def join_session(session_id: str, node_id: str):
    """Node joins a training session"""
    return await coordinator.join_session(session_id, node_id)

@app.post("/api/sessions/{session_id}/updates")
async def receive_update(session_id: str, update: ModelUpdate):
    """Receive model update from node"""
    return await coordinator.receive_model_update(update)

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get training session status"""
    return coordinator.get_session_status(session_id)

@app.post("/api/nodes/heartbeat")
async def node_heartbeat(heartbeat: NodeHeartbeat):
    """Handle node heartbeat"""
    await coordinator.handle_heartbeat(heartbeat)
    return {"status": "received"}

@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "status": session["status"],
                "current_round": session["current_round"],
                "total_rounds": session["rounds"],
                "active_nodes": len(session["active_nodes"]),
                "model_name": session["model_name"]
            }
            for sid, session in coordinator.active_sessions.items()
        ]
    }

@app.get("/api/nodes")
async def list_nodes():
    """List all registered nodes"""
    return {
        "nodes": [
            {
                "node_id": nid,
                "status": node["status"],
                "last_heartbeat": node["last_heartbeat"],
                "joined_sessions": len(node["joined_sessions"]),
                "reputation_score": node["reputation_score"]
            }
            for nid, node in coordinator.registered_nodes.items()
        ]
    }
@app.post("/api/training/start")
async def start_training(training_request: Dict[str, Any]):
    """Start training for a node in a session"""
    node_id = training_request.get("node_id")
    session_id = training_request.get("session_id")

    if not node_id or not session_id:
        raise HTTPException(status_code=400, detail="node_id and session_id required")

    # Join the session if not already joined
    await coordinator.join_session(session_id, node_id)

    return {"status": "training_started", "session_id": session_id, "node_id": node_id}

@app.post("/api/training/update")
async def update_training_progress(update_data: Dict[str, Any]):
    """Update training progress for a node"""
    session_id = update_data.get("session_id")
    node_id = update_data.get("node_id", "unknown")
    parameters_trained = update_data.get("parameters_trained", 0)
    accuracy = update_data.get("accuracy", 0.0)
    loss = update_data.get("loss", 0.0)
    status = update_data.get("status", "running")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    # For now, just log the update - in a real implementation this would update session metrics
    logger.info(f"Training update from {node_id}: session={session_id}, accuracy={accuracy}, loss={loss}")

    return {"status": "updated", "session_id": session_id}

@app.get("/api/stats")
async def get_stats():
    """Get coordinator statistics"""
    return {
        "active_sessions": len(coordinator.active_sessions),
        "registered_nodes": len(coordinator.registered_nodes),
        "total_sessions": len(coordinator.active_sessions),
        "uptime": time.time() - psutil.boot_time() if psutil else "unknown"
    }

@app.websocket("/ws/nodes/{node_id}")
async def websocket_endpoint(websocket: WebSocket, node_id: str):
    """WebSocket endpoint for real-time node communication"""
    await websocket.accept()

    # Register connection
    coordinator.node_connections[node_id] = websocket

    try:
        while True:
            # Keep connection alive and handle messages
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "heartbeat":
                await coordinator.handle_heartbeat(NodeHeartbeat(**data))
                await websocket.send_json({"type": "heartbeat_ack"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for node: {node_id}")
    except Exception as e:
        logger.error(f"WebSocket error for node {node_id}: {e}")
    finally:
        # Clean up connection
        if node_id in coordinator.node_connections:
            del coordinator.node_connections[node_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(coordinator.active_sessions),
        "registered_nodes": len(coordinator.registered_nodes),
        "uptime": time.time() - time.time(),  # Would track actual start time
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Federated Learning Coordinator",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "register_node": "POST /api/nodes/register",
            "create_session": "POST /api/sessions/create",
            "join_session": "POST /api/sessions/{session_id}/join",
            "session_status": "GET /api/sessions/{session_id}/status",
            "list_sessions": "GET /api/sessions",
            "list_nodes": "GET /api/nodes",
            "websocket": "WS /ws/nodes/{node_id}"
        }
    }

def create_coordinator_server(host: str = "0.0.0.0", port: int = 5001) -> None:
    """Create and run the coordinator server"""
    logger.info(f"🚀 Starting Federated Coordinator on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    # Run server directly
    create_coordinator_server()