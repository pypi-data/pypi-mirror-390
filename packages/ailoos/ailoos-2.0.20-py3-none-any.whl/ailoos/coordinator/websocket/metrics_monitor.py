"""
Real-time metrics monitoring for WebSocket connections and system events.
"""

import asyncio
import psutil
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque

from .manager import manager
from .message_broker import message_broker
from .event_broadcaster import event_broadcaster
from ..models.schemas import WebSocketMessage
# from ..monitoring.metrics_api import MetricsAPI  # Commented out - module not found


class MetricsMonitor:
    """Monitors and broadcasts real-time system metrics."""

    def __init__(self, metrics_interval: int = 30):
        self.metrics_interval = metrics_interval  # seconds
        self.is_running = False
        self._background_tasks = []
        self.metrics_history = deque(maxlen=100)  # Keep last 100 metric snapshots
        self.alert_thresholds = {
            "cpu_percent": 90.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "active_connections": 1000,
            "message_queue_size": 10000
        }

    async def start(self):
        """Start the metrics monitor."""
        self.is_running = True
        self._background_tasks = [
            asyncio.create_task(self._collect_system_metrics()),
            asyncio.create_task(self._collect_websocket_metrics()),
            asyncio.create_task(self._check_alerts()),
            asyncio.create_task(self._broadcast_metrics())
        ]
        print("Metrics monitor started")

    async def stop(self):
        """Stop the metrics monitor."""
        self.is_running = False
        for task in self._background_tasks:
            task.cancel()
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        print("Metrics monitor stopped")

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        while self.is_running:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)

                # Memory metrics
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used = memory.used
                memory_total = memory.total

                # Disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                disk_used = disk.used
                disk_total = disk.total

                # Network metrics
                network = psutil.net_io_counters()
                bytes_sent = network.bytes_sent
                bytes_recv = network.bytes_recv

                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_percent,
                        "memory_used": memory_used,
                        "memory_total": memory_total,
                        "disk_percent": disk_percent,
                        "disk_used": disk_used,
                        "disk_total": disk_total,
                        "network_bytes_sent": bytes_sent,
                        "network_bytes_recv": bytes_recv
                    }
                }

                self.metrics_history.append(metrics)

                await asyncio.sleep(self.metrics_interval)

            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(5)

    async def _collect_websocket_metrics(self):
        """Collect WebSocket-specific metrics."""
        while self.is_running:
            try:
                # Connection metrics
                total_connections = sum(len(connections) for connections in manager.active_connections.values())
                active_sessions = len(manager.active_connections)
                active_nodes = len(manager.node_subscriptions)

                # Message broker metrics
                broker_stats = await message_broker.get_stats()
                queue_size = broker_stats.get("queue_size", 0)
                active_rooms = broker_stats.get("active_rooms", 0)

                # Heartbeat metrics
                stale_connections = len(manager.get_stale_connections())

                # Rate limiting metrics
                rate_limited_nodes = sum(1 for rate_data in manager.rate_limits.values()
                                       if rate_data["count"] > 0)

                websocket_metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "websocket": {
                        "total_connections": total_connections,
                        "active_sessions": active_sessions,
                        "active_nodes": active_nodes,
                        "active_rooms": active_rooms,
                        "message_queue_size": queue_size,
                        "stale_connections": stale_connections,
                        "rate_limited_nodes": rate_limited_nodes
                    }
                }

                # Add to latest metrics entry or create new one
                if self.metrics_history:
                    self.metrics_history[-1].update(websocket_metrics)
                else:
                    self.metrics_history.append(websocket_metrics)

                await asyncio.sleep(self.metrics_interval)

            except Exception as e:
                print(f"Error collecting WebSocket metrics: {e}")
                await asyncio.sleep(5)

    async def _check_alerts(self):
        """Check metrics against alert thresholds."""
        while self.is_running:
            try:
                if not self.metrics_history:
                    await asyncio.sleep(10)
                    continue

                latest_metrics = self.metrics_history[-1]

                # System alerts
                system_metrics = latest_metrics.get("system", {})
                if system_metrics.get("cpu_percent", 0) > self.alert_thresholds["cpu_percent"]:
                    await event_broadcaster.broadcast_system_alert(
                        alert_type="high_cpu_usage",
                        message=f"CPU usage is {system_metrics['cpu_percent']:.1f}%",
                        data={"cpu_percent": system_metrics["cpu_percent"]}
                    )

                if system_metrics.get("memory_percent", 0) > self.alert_thresholds["memory_percent"]:
                    await event_broadcaster.broadcast_system_alert(
                        alert_type="high_memory_usage",
                        message=f"Memory usage is {system_metrics['memory_percent']:.1f}%",
                        data={"memory_percent": system_metrics["memory_percent"]}
                    )

                if system_metrics.get("disk_percent", 0) > self.alert_thresholds["disk_percent"]:
                    await event_broadcaster.broadcast_system_alert(
                        alert_type="high_disk_usage",
                        message=f"Disk usage is {system_metrics['disk_percent']:.1f}%",
                        data={"disk_percent": system_metrics["disk_percent"]}
                    )

                # WebSocket alerts
                websocket_metrics = latest_metrics.get("websocket", {})
                if websocket_metrics.get("total_connections", 0) > self.alert_thresholds["active_connections"]:
                    await event_broadcaster.broadcast_system_alert(
                        alert_type="high_connection_count",
                        message=f"Active connections: {websocket_metrics['total_connections']}",
                        data={"active_connections": websocket_metrics["total_connections"]}
                    )

                if websocket_metrics.get("message_queue_size", 0) > self.alert_thresholds["message_queue_size"]:
                    await event_broadcaster.broadcast_system_alert(
                        alert_type="high_message_queue",
                        message=f"Message queue size: {websocket_metrics['message_queue_size']}",
                        data={"queue_size": websocket_metrics["message_queue_size"]}
                    )

                await asyncio.sleep(60)  # Check alerts every minute

            except Exception as e:
                print(f"Error checking alerts: {e}")
                await asyncio.sleep(5)

    async def _broadcast_metrics(self):
        """Broadcast metrics to metrics subscribers."""
        while self.is_running:
            try:
                if not self.metrics_history:
                    await asyncio.sleep(10)
                    continue

                latest_metrics = self.metrics_history[-1]

                # Create metrics message
                metrics_message = WebSocketMessage(
                    type="system.metrics",
                    data=latest_metrics
                )

                # Send to metrics room subscribers
                from .room_manager import room_manager
                await room_manager.broadcast_to_room("metrics", metrics_message)

                await asyncio.sleep(self.metrics_interval)

            except Exception as e:
                print(f"Error broadcasting metrics: {e}")
                await asyncio.sleep(5)

    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the most recent metrics snapshot."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics history."""
        return list(self.metrics_history)[-limit:] if self.metrics_history else []

    def update_alert_threshold(self, metric: str, threshold: float):
        """Update alert threshold for a metric."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold

    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report from metrics history."""
        if not self.metrics_history:
            return {"error": "No metrics data available"}

        # Calculate averages and trends
        system_metrics = []
        websocket_metrics = []

        for entry in self.metrics_history:
            if "system" in entry:
                system_metrics.append(entry["system"])
            if "websocket" in entry:
                websocket_metrics.append(entry["websocket"])

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "period": f"{len(self.metrics_history)} snapshots",
            "system_performance": self._calculate_system_performance(system_metrics),
            "websocket_performance": self._calculate_websocket_performance(websocket_metrics)
        }

        return report

    def _calculate_system_performance(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate system performance statistics."""
        if not metrics:
            return {}

        cpu_values = [m.get("cpu_percent", 0) for m in metrics]
        memory_values = [m.get("memory_percent", 0) for m in metrics]

        return {
            "cpu_average": sum(cpu_values) / len(cpu_values),
            "cpu_peak": max(cpu_values),
            "memory_average": sum(memory_values) / len(memory_values),
            "memory_peak": max(memory_values),
            "samples": len(metrics)
        }

    def _calculate_websocket_performance(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate WebSocket performance statistics."""
        if not metrics:
            return {}

        connection_values = [m.get("total_connections", 0) for m in metrics]
        queue_values = [m.get("message_queue_size", 0) for m in metrics]

        return {
            "connections_average": sum(connection_values) / len(connection_values),
            "connections_peak": max(connection_values),
            "queue_average": sum(queue_values) / len(queue_values),
            "queue_peak": max(queue_values),
            "samples": len(metrics)
        }


# Global metrics monitor instance
metrics_monitor = MetricsMonitor()