#!/usr/bin/env python3
"""
Ailoos Dashboard Application
Dashboard web en tiempo real para monitoreo y gestión de la red federada
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp
import psutil

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
system_metrics: Dict[str, Any] = {}
federated_sessions: Dict[str, Any] = {}
node_status: Dict[str, Any] = {}
alerts: List[Dict[str, Any]] = []

# FastAPI app
app = FastAPI(
    title="Ailoos Dashboard",
    description="Dashboard web en tiempo real para la red federada EmpoorioLM",
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

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Service endpoints (will be configured dynamically)
SERVICE_ENDPOINTS = {
    "inference": "http://localhost:8000",
    "coordinator": "http://localhost:8001",
    "datasets": "http://localhost:8006",
    "p2p": "http://localhost:8003",
    "rewards": "http://localhost:8004",
    "zkp": "http://localhost:8005"
}

async def fetch_service_data(service_name: str, endpoint: str) -> Dict[str, Any]:
    """Fetch data from a service endpoint"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get(f"{SERVICE_ENDPOINTS[service_name]}{endpoint}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}", "service": service_name}
    except Exception as e:
        return {"error": str(e), "service": service_name}

async def collect_system_metrics():
    """Collect comprehensive system metrics"""
    while True:
        try:
            # System metrics
            system_metrics.update({
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
                "uptime_seconds": time.time() - psutil.boot_time()
            })

            # Service health checks
            health_status = {}
            for service_name in SERVICE_ENDPOINTS:
                health_data = await fetch_service_data(service_name, "/health")
                health_status[service_name] = health_data

            system_metrics["services"] = health_status

            # Federated learning metrics
            coordinator_data = await fetch_service_data("coordinator", "/api/coordinator/sessions/active")
            if "sessions" in coordinator_data:
                federated_sessions.update(coordinator_data)

            # Node status
            p2p_data = await fetch_service_data("p2p", "/api/network/info")
            if "total_nodes" in p2p_data:
                node_status.update(p2p_data)

            # Rewards metrics
            rewards_data = await fetch_service_data("rewards", "/api/rewards/stats")
            if "total_distributed" in rewards_data:
                system_metrics["rewards"] = rewards_data

            # ZKP metrics
            zkp_data = await fetch_service_data("zkp", "/api/zkp/stats")
            if "total_proofs_processed" in zkp_data:
                system_metrics["zkp"] = zkp_data

            # Check for alerts
            await check_alerts()

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

        await asyncio.sleep(5)  # Update every 5 seconds

async def check_alerts():
    """Check for system alerts and warnings"""
    alerts.clear()

    # CPU usage alert
    if system_metrics.get("cpu_percent", 0) > 90:
        alerts.append({
            "type": "warning",
            "message": f"High CPU usage: {system_metrics['cpu_percent']:.1f}%",
            "timestamp": datetime.now().isoformat(),
            "service": "system"
        })

    # Memory usage alert
    if system_metrics.get("memory_percent", 0) > 90:
        alerts.append({
            "type": "warning",
            "message": f"High memory usage: {system_metrics['memory_percent']:.1f}%",
            "timestamp": datetime.now().isoformat(),
            "service": "system"
        })

    # Service health alerts
    services = system_metrics.get("services", {})
    for service_name, health in services.items():
        if health.get("status") != "healthy":
            alerts.append({
                "type": "error",
                "message": f"Service {service_name} is not healthy",
                "timestamp": datetime.now().isoformat(),
                "service": service_name
            })

    # Low node count alert
    if node_status.get("total_nodes", 0) < 3:
        alerts.append({
            "type": "info",
            "message": f"Low network participation: {node_status.get('total_nodes', 0)} nodes",
            "timestamp": datetime.now().isoformat(),
            "service": "network"
        })

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/dashboard/metrics")
async def get_metrics():
    """Get comprehensive system metrics"""
    return {
        "system": system_metrics,
        "federated": federated_sessions,
        "network": node_status,
        "alerts": alerts[-10:],  # Last 10 alerts
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard/sessions")
async def get_sessions():
    """Get federated learning sessions"""
    return federated_sessions

@app.get("/api/dashboard/nodes")
async def get_nodes():
    """Get network nodes information"""
    return node_status

@app.get("/api/dashboard/rewards")
async def get_rewards():
    """Get rewards system information"""
    rewards_data = await fetch_service_data("rewards", "/api/rewards/stats")
    return rewards_data

@app.get("/api/dashboard/zkp")
async def get_zkp():
    """Get ZKP verification information"""
    zkp_data = await fetch_service_data("zkp", "/api/zkp/stats")
    return zkp_data

@app.get("/api/dashboard/alerts")
async def get_alerts():
    """Get system alerts"""
    return {"alerts": alerts[-50:]}  # Last 50 alerts

@app.post("/api/dashboard/services/restart/{service_name}")
async def restart_service(service_name: str):
    """Restart a service (simplified implementation)"""
    if service_name not in SERVICE_ENDPOINTS:
        raise HTTPException(status_code=404, detail="Service not found")

    # In a real implementation, this would trigger service restart
    logger.info(f"Restarting service: {service_name}")

    return {"status": "restart_initiated", "service": service_name}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": len(SERVICE_ENDPOINTS),
        "metrics_collected": bool(system_metrics),
        "alerts_count": len(alerts),
        "version": "1.0.0"
    }

# WebSocket endpoint for real-time updates
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()

    try:
        while True:
            # Send current metrics
            metrics_data = {
                "system": system_metrics,
                "federated": federated_sessions,
                "network": node_status,
                "alerts": alerts[-5:],  # Last 5 alerts
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send_json(metrics_data)
            await asyncio.sleep(2)  # Update every 2 seconds

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    # Start background metrics collection
    asyncio.create_task(collect_system_metrics())

def create_dashboard_app(host: str = "0.0.0.0", port: int = 3000) -> None:
    """Create and run the dashboard application"""

    # Create necessary directories
    Path("static").mkdir(parents=True, exist_ok=True)
    Path("templates").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    logger.info(f"🚀 Starting Ailoos Dashboard on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    # Run dashboard directly
    create_dashboard_app()