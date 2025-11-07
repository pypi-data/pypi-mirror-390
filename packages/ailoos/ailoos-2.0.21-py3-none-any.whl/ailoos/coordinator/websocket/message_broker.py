"""
Message Broker for efficient WebSocket broadcasting.
"""

import asyncio
from typing import Dict, List, Set, Optional, Callable, Any
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor
import gzip
import base64

# from .manager import manager  # Commented out to avoid circular import
# from .room_manager import room_manager  # Commented out to avoid circular import
from ..models.schemas import WebSocketMessage


class MessageBroker:
    """Efficient message broker for WebSocket broadcasting."""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.message_queue = asyncio.Queue()
        self.is_running = False
        self.message_handlers: Dict[str, List[Callable]] = {}
        # Compression settings
        self.compression_enabled = True
        self.compression_threshold = 1024  # Compress messages larger than 1KB

    async def start(self):
        """Start the message broker."""
        self.is_running = True
        asyncio.create_task(self._process_message_queue())
        asyncio.create_task(self._cleanup_task())
        print("Message broker started")

    async def stop(self):
        """Stop the message broker."""
        self.is_running = False
        self.executor.shutdown(wait=True)
        print("Message broker stopped")

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler for specific message types."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def publish(self, message: WebSocketMessage, target_type: str = "broadcast",
                     target_ids: Optional[List[str]] = None, compress: bool = None):
        """Publish a message to the broker."""
        await self.message_queue.put({
            "message": message,
            "target_type": target_type,
            "target_ids": target_ids or [],
            "compress": compress if compress is not None else self.compression_enabled,
            "timestamp": datetime.utcnow()
        })

    async def _process_message_queue(self):
        """Process messages from the queue."""
        while self.is_running:
            try:
                message_data = await self.message_queue.get()

                # Process message in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    self._process_message_sync,
                    message_data
                )

                self.message_queue.task_done()

            except Exception as e:
                print(f"Error processing message: {e}")
                continue

    def _process_message_sync(self, message_data: Dict[str, Any]):
        """Process a message synchronously."""
        message = message_data["message"]
        target_type = message_data["target_type"]
        target_ids = message_data["target_ids"]
        compress = message_data["compress"]

        # Handle message type specific processing
        if message.type in self.message_handlers:
            for handler in self.message_handlers[message.type]:
                try:
                    # Run handler (assuming it's async-capable or sync)
                    if asyncio.iscoroutinefunction(handler):
                        # For async handlers, we need to run them in the event loop
                        asyncio.run(handler(message))
                    else:
                        handler(message)
                except Exception as e:
                    print(f"Error in message handler: {e}")

        # Compress message if needed
        if compress and len(message.json()) > self.compression_threshold:
            message = self._compress_message(message)

        # Route message based on target type
        if target_type == "broadcast":
            self._broadcast_message(message)
        elif target_type == "room":
            self._send_to_rooms(message, target_ids)
        elif target_type == "node":
            self._send_to_nodes(message, target_ids)
        elif target_type == "session":
            self._send_to_sessions(message, target_ids)

    def _broadcast_message(self, message: WebSocketMessage):
        """Broadcast message to all connected clients."""
        # Get all active sessions - simplified
        # for session_id in list(manager.active_connections.keys()):
        #     asyncio.run(manager.broadcast_to_session(message, session_id))
        print(f"Would broadcast message: {message.type}")

    def _send_to_rooms(self, message: WebSocketMessage, room_ids: List[str]):
        """Send message to specific rooms."""
        for room_id in room_ids:
            # asyncio.run(room_manager.broadcast_to_room(room_id, message))  # Commented out
            print(f"Would send to room {room_id}")

    def _send_to_nodes(self, message: WebSocketMessage, node_ids: List[str]):
        """Send message to specific nodes."""
        for node_id in node_ids:
            # sessions = manager.get_node_sessions(node_id)  # Commented out
            sessions = []  # Placeholder
            for session_id in sessions:
                # asyncio.run(manager.send_personal_message(message, session_id, node_id))  # Commented out
                print(f"Would send to node {node_id}")

    def _send_to_sessions(self, message: WebSocketMessage, session_ids: List[str]):
        """Send message to specific sessions."""
        for session_id in session_ids:
            # asyncio.run(manager.broadcast_to_session(message, session_id))  # Commented out
            print(f"Would send to session {session_id}")

    def _compress_message(self, message: WebSocketMessage) -> WebSocketMessage:
        """Compress message data."""
        try:
            message_json = message.json()
            compressed = gzip.compress(message_json.encode('utf-8'))
            compressed_b64 = base64.b64encode(compressed).decode('utf-8')

            # Create compressed message
            compressed_message = WebSocketMessage(
                type=f"compressed.{message.type}",
                session_id=message.session_id,
                node_id=message.node_id,
                data={
                    "compressed": True,
                    "data": compressed_b64,
                    "original_size": len(message_json)
                },
                timestamp=message.timestamp
            )
            return compressed_message
        except Exception as e:
            print(f"Compression failed: {e}")
            return message

    async def _cleanup_task(self):
        """Periodic cleanup task."""
        while self.is_running:
            try:
                # Clean up stale connections every 5 minutes
                await asyncio.sleep(300)
                # await manager.cleanup_stale_connections()  # Commented out

                # Clean up empty rooms
                await self._cleanup_empty_rooms()

            except Exception as e:
                print(f"Error in cleanup task: {e}")

    async def _cleanup_empty_rooms(self):
        """Clean up rooms with no active connections."""
        rooms_to_delete = []
        # for room_id, metadata in room_manager.room_metadata.items():  # Commented out
        #     if metadata["active_connections"] == 0:
        #         # Check if room has been empty for more than 10 minutes
        #         if (datetime.utcnow() - metadata["created_at"]).total_seconds() > 600:
        #             rooms_to_delete.append(room_id)

        # for room_id in rooms_to_delete:
        #     room_manager.delete_room(room_id)  # Commented out
        pass

    async def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics."""
        return {
            "queue_size": self.message_queue.qsize(),
            # "active_rooms": len(room_manager.room_subscriptions),  # Commented out
            "active_rooms": 0,  # Placeholder
            # "total_connections": sum(  # Commented out
            #     len(connections) for connections in manager.active_connections.values()
            # ),
            "total_connections": 0,  # Placeholder
            "compression_enabled": self.compression_enabled,
            "registered_handlers": list(self.message_handlers.keys())
        }


# Global message broker instance
message_broker = MessageBroker()