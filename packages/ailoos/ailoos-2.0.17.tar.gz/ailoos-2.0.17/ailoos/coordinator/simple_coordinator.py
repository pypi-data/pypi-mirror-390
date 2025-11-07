#!/usr/bin/env python3
"""
Simple Federated Learning Coordinator
No complex dependencies - just standard library + requests
"""

import socket
import threading
import json
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FederatedSession:
    """Simple federated learning session."""

    def __init__(self, session_id: str, model_name: str, config: Dict[str, Any]):
        self.session_id = session_id
        self.model_name = model_name
        self.config = config
        self.nodes = {}  # node_id -> node_info
        self.rounds = []  # List of completed rounds
        self.current_round = 0
        self.status = "waiting"  # waiting, training, completed, failed
        self.created_at = time.time()
        self.global_model = None

    def add_node(self, node_id: str, node_info: Dict[str, Any]):
        """Add a node to the session."""
        self.nodes[node_id] = {
            **node_info,
            "joined_at": time.time(),
            "status": "active",
            "contributions": 0
        }
        logger.info(f"Node {node_id} joined session {self.session_id}")

    def start_training(self):
        """Start the training session."""
        if len(self.nodes) < self.config.get("min_nodes", 2):
            raise ValueError(f"Not enough nodes. Need {self.config.get('min_nodes', 2)}, have {len(self.nodes)}")

        self.status = "training"
        self.current_round = 1
        logger.info(f"Started training session {self.session_id} with {len(self.nodes)} nodes")

    def complete_round(self, round_number: int, results: Dict[str, Any]):
        """Complete a training round."""
        self.rounds.append({
            "round": round_number,
            "completed_at": time.time(),
            "results": results
        })

        if round_number >= self.config.get("rounds", 3):
            self.status = "completed"
            logger.info(f"Session {self.session_id} completed after {round_number} rounds")
        else:
            self.current_round = round_number + 1


class SimpleCoordinator:
    """Simple federated learning coordinator without complex dependencies."""

    def __init__(self, host: str = "localhost", port: int = 5001):
        self.host = host
        self.port = port
        self.sessions: Dict[str, FederatedSession] = {}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.server = None
        self.running = False

    def start(self):
        """Start the coordinator server."""
        try:
            self.server = HTTPServer((self.host, self.port), CoordinatorHandler)
            self.server.coordinator = self  # Attach coordinator to handler
            self.running = True

            logger.info(f"🎯 Simple Coordinator started on http://{self.host}:{self.port}")
            logger.info("Ready to accept federated learning sessions!")

            # Start server in a separate thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

        except Exception as e:
            logger.error(f"Failed to start coordinator: {e}")
            raise

    def stop(self):
        """Stop the coordinator."""
        self.running = False
        if self.server:
            self.server.shutdown()
            logger.info("Coordinator stopped")

    def create_session(self, model_name: str, config: Dict[str, Any]) -> str:
        """Create a new federated learning session."""
        session_id = str(uuid.uuid4())[:8]
        session = FederatedSession(session_id, model_name, config)
        self.sessions[session_id] = session
        logger.info(f"Created session {session_id} for model {model_name}")
        return session_id

    def get_session(self, session_id: str) -> Optional[FederatedSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def register_node(self, node_id: str, node_info: Dict[str, Any]):
        """Register a node."""
        self.nodes[node_id] = {
            **node_info,
            "registered_at": time.time(),
            "status": "active"
        }
        logger.info(f"Registered node {node_id}")

    def join_session(self, session_id: str, node_id: str, node_info: Dict[str, Any]) -> bool:
        """Join a node to a session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.add_node(node_id, node_info)
        return True

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions."""
        return [
            {
                "session_id": session.session_id,
                "model_name": session.model_name,
                "status": session.status,
                "nodes": len(session.nodes),
                "current_round": session.current_round,
                "total_rounds": session.config.get("rounds", 3)
            }
            for session in self.sessions.values()
        ]


class CoordinatorHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for the coordinator."""

    def do_GET(self):
        """Handle GET requests."""
        try:
            path = self.path

            if path == "/health":
                self._send_json_response(200, {"status": "healthy", "version": "2.0.12"})

            elif path == "/sessions":
                sessions = self.server.coordinator.get_sessions()
                self._send_json_response(200, {"sessions": sessions})

            elif path.startswith("/sessions/"):
                session_id = path.split("/")[2]
                session = self.server.coordinator.get_session(session_id)
                if session:
                    self._send_json_response(200, {
                        "session_id": session.session_id,
                        "status": session.status,
                        "nodes": list(session.nodes.keys()),
                        "current_round": session.current_round
                    })
                else:
                    self._send_json_response(404, {"error": "Session not found"})

            else:
                self._send_json_response(404, {"error": "Not found"})

        except Exception as e:
            logger.error(f"GET error: {e}")
            self._send_json_response(500, {"error": str(e)})

    def do_POST(self):
        """Handle POST requests."""
        try:
            path = self.path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(post_data) if post_data else {}
            except json.JSONDecodeError:
                data = {}

            if path == "/sessions":
                # Create new session
                model_name = data.get("model_name", "tiny-model")
                config = data.get("config", {"rounds": 3, "min_nodes": 2})
                session_id = self.server.coordinator.create_session(model_name, config)
                self._send_json_response(201, {"session_id": session_id})

            elif path.startswith("/sessions/") and path.endswith("/join"):
                # Join session
                session_id = path.split("/")[2]
                node_id = data.get("node_id")
                node_info = data.get("node_info", {})

                if not node_id:
                    self._send_json_response(400, {"error": "node_id required"})
                    return

                success = self.server.coordinator.join_session(session_id, node_id, node_info)
                if success:
                    self._send_json_response(200, {"status": "joined"})
                else:
                    self._send_json_response(404, {"error": "Session not found"})

            elif path.startswith("/sessions/") and path.endswith("/start"):
                # Start session
                session_id = path.split("/")[2]
                session = self.server.coordinator.get_session(session_id)

                if not session:
                    self._send_json_response(404, {"error": "Session not found"})
                    return

                try:
                    session.start_training()
                    self._send_json_response(200, {"status": "started"})
                except ValueError as e:
                    self._send_json_response(400, {"error": str(e)})

            elif path == "/nodes":
                # Register node
                node_id = data.get("node_id")
                node_info = data.get("node_info", {})

                if not node_id:
                    self._send_json_response(400, {"error": "node_id required"})
                    return

                self.server.coordinator.register_node(node_id, node_info)
                self._send_json_response(201, {"status": "registered"})

            else:
                self._send_json_response(404, {"error": "Not found"})

        except Exception as e:
            logger.error(f"POST error: {e}")
            self._send_json_response(500, {"error": str(e)})

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Simple Ailoos Federated Learning Coordinator")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5001, help="Port to bind to")

    args = parser.parse_args()

    coordinator = SimpleCoordinator(host=args.host, port=args.port)

    try:
        print("🚀 Starting Simple Ailoos Coordinator...")
        print(f"📡 Server: http://{args.host}:{args.port}")
        print("🎯 Ready for federated learning sessions!")
        print("💡 Press Ctrl+C to stop")

        coordinator.start()

    except KeyboardInterrupt:
        print("\n👋 Stopping coordinator...")
        coordinator.stop()


if __name__ == "__main__":
    main()