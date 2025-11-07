"""
WebSocket management endpoints for the coordinator service.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ...database.connection import get_db
from ...auth.dependencies import get_current_user, require_admin
from ...websocket.manager import manager
from ...websocket.room_manager import room_manager
from ...websocket.message_broker import message_broker
from ...models.schemas import WebSocketMessage
from ...websocket.message_types import WebSocketMessageFactory


# Pydantic models for API responses
class WebSocketSessionInfo(BaseModel):
    session_id: str
    connected_nodes: List[str]
    active_connections: int
    created_at: str

class WebSocketNodeInfo(BaseModel):
    node_id: str
    sessions: List[str]
    active_connections: int
    last_heartbeat: Optional[str]

class WebSocketStats(BaseModel):
    total_connections: int
    active_sessions: int
    active_nodes: int
    total_rooms: int
    message_queue_size: int

class RoomInfo(BaseModel):
    room_id: str
    room_type: str
    active_connections: int
    created_at: str
    metadata: Dict[str, Any]

class BroadcastRequest(BaseModel):
    message_type: str
    data: Dict[str, Any]
    target_type: str = "broadcast"  # broadcast, room, node, session
    target_ids: Optional[List[str]] = None

class NotificationRequest(BaseModel):
    node_id: str
    notification_type: str
    data: Dict[str, Any]


# Create router
router = APIRouter()


@router.get("/sessions", response_model=List[WebSocketSessionInfo])
async def list_websocket_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all active WebSocket sessions."""
    sessions = []
    for session_id in manager.active_connections.keys():
        connected_nodes = manager.get_session_connections(session_id)
        # Get session metadata if available
        metadata = manager.connection_metadata.get(session_id, {})
        created_at = None
        if metadata and connected_nodes:
            first_node = connected_nodes[0]
            if first_node in metadata:
                created_at = metadata[first_node]["connected_at"].isoformat()

        sessions.append(WebSocketSessionInfo(
            session_id=session_id,
            connected_nodes=connected_nodes,
            active_connections=len(connected_nodes),
            created_at=created_at or "unknown"
        ))

    return sessions


@router.get("/sessions/{session_id}", response_model=WebSocketSessionInfo)
async def get_websocket_session_info(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a WebSocket session."""
    if session_id not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Session not found")

    connected_nodes = manager.get_session_connections(session_id)
    metadata = manager.connection_metadata.get(session_id, {})
    created_at = None
    if metadata and connected_nodes:
        first_node = connected_nodes[0]
        if first_node in metadata:
            created_at = metadata[first_node]["connected_at"].isoformat()

    return WebSocketSessionInfo(
        session_id=session_id,
        connected_nodes=connected_nodes,
        active_connections=len(connected_nodes),
        created_at=created_at or "unknown"
    )


@router.get("/nodes", response_model=List[WebSocketNodeInfo])
async def list_websocket_nodes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all nodes with WebSocket connections."""
    nodes = []
    for node_id in manager.node_subscriptions.keys():
        sessions = manager.get_node_sessions(node_id)
        # Get heartbeat info
        last_heartbeat = None
        for session_id in sessions:
            if session_id in manager.heartbeats and node_id in manager.heartbeats[session_id]:
                heartbeat = manager.heartbeats[session_id][node_id]
                if last_heartbeat is None or heartbeat > last_heartbeat:
                    last_heartbeat = heartbeat

        nodes.append(WebSocketNodeInfo(
            node_id=node_id,
            sessions=sessions,
            active_connections=len(sessions),
            last_heartbeat=last_heartbeat.isoformat() if last_heartbeat else None
        ))

    return nodes


@router.get("/nodes/{node_id}", response_model=WebSocketNodeInfo)
async def get_websocket_node_info(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a node's WebSocket connections."""
    if node_id not in manager.node_subscriptions:
        raise HTTPException(status_code=404, detail="Node not found")

    sessions = manager.get_node_sessions(node_id)
    last_heartbeat = None
    for session_id in sessions:
        if session_id in manager.heartbeats and node_id in manager.heartbeats[session_id]:
            heartbeat = manager.heartbeats[session_id][node_id]
            if last_heartbeat is None or heartbeat > last_heartbeat:
                last_heartbeat = heartbeat

    return WebSocketNodeInfo(
        node_id=node_id,
        sessions=sessions,
        active_connections=len(sessions),
        last_heartbeat=last_heartbeat.isoformat() if last_heartbeat else None
    )


@router.get("/stats", response_model=WebSocketStats)
async def get_websocket_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WebSocket system statistics."""
    broker_stats = await message_broker.get_stats()

    return WebSocketStats(
        total_connections=sum(len(connections) for connections in manager.active_connections.values()),
        active_sessions=len(manager.active_connections),
        active_nodes=len(manager.node_subscriptions),
        total_rooms=len(room_manager.room_subscriptions),
        message_queue_size=broker_stats.get("queue_size", 0)
    )


@router.get("/rooms", response_model=List[RoomInfo])
async def list_websocket_rooms(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all WebSocket rooms."""
    rooms = []
    for room_id, metadata in room_manager.room_metadata.items():
        rooms.append(RoomInfo(
            room_id=room_id,
            room_type=metadata["type"],
            active_connections=metadata["active_connections"],
            created_at=metadata["created_at"].isoformat(),
            metadata=metadata["metadata"]
        ))

    return rooms


@router.post("/broadcast")
async def broadcast_message(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Broadcast a message to WebSocket clients (admin only)."""
    try:
        # Create message using factory
        message = WebSocketMessageFactory.create_system_alert(
            alert_type=request.message_type,
            message="Admin broadcast",
            data=request.data
        )

        # Publish message
        await message_broker.publish(
            message=message,
            target_type=request.target_type,
            target_ids=request.target_ids
        )

        return {"status": "success", "message": "Broadcast sent"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")


@router.post("/notify/{node_id}")
async def send_node_notification(
    node_id: str,
    request: NotificationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Send a notification to a specific node (admin only)."""
    try:
        # Create notification message
        message = WebSocketMessageFactory.create_node_status(
            node_id=node_id,
            status=request.notification_type,
            data=request.data
        )

        # Send to node
        await manager.send_node_notification(node_id, request.notification_type, request.data)

        return {"status": "success", "message": f"Notification sent to node {node_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")


@router.delete("/sessions/{session_id}")
async def disconnect_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Force disconnect all nodes from a session (admin only)."""
    if session_id not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Session not found")

    disconnected_nodes = []
    for node_id in list(manager.active_connections[session_id].keys()):
        manager.disconnect(session_id, node_id)
        disconnected_nodes.append(node_id)

    return {
        "status": "success",
        "message": f"Disconnected {len(disconnected_nodes)} nodes from session {session_id}",
        "disconnected_nodes": disconnected_nodes
    }


@router.delete("/nodes/{node_id}")
async def disconnect_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Force disconnect a node from all sessions (admin only)."""
    if node_id not in manager.node_subscriptions:
        raise HTTPException(status_code=404, detail="Node not found")

    disconnected_sessions = []
    for session_id in list(manager.node_subscriptions[node_id]):
        manager.disconnect(session_id, node_id)
        disconnected_sessions.append(session_id)

    return {
        "status": "success",
        "message": f"Disconnected node {node_id} from {len(disconnected_sessions)} sessions",
        "disconnected_sessions": disconnected_sessions
    }


@router.post("/cleanup")
async def cleanup_stale_connections(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Clean up stale WebSocket connections (admin only)."""
    try:
        await manager.cleanup_stale_connections()
        await message_broker._cleanup_empty_rooms()

        return {"status": "success", "message": "Stale connections cleaned up"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


# Notification endpoints

@router.get("/notifications/{node_id}")
async def get_node_notifications(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for a specific node."""
    try:
        from ...websocket.notification_service import notification_service

        pending = await notification_service.get_pending_notifications(node_id)
        return {
            "node_id": node_id,
            "pending_notifications": pending,
            "count": len(pending)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.post("/notifications/{node_id}/mark-read")
async def mark_notification_read(
    node_id: str,
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read."""
    try:
        from ...websocket.notification_service import notification_service

        await notification_service.mark_notification_read(node_id, notification_id)
        return {"status": "success", "message": "Notification marked as read"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification: {str(e)}")


@router.post("/notifications/{node_id}/clear")
async def clear_node_notifications(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clear all pending notifications for a node."""
    try:
        from ...websocket.notification_service import notification_service

        await notification_service.clear_pending_notifications(node_id)
        return {"status": "success", "message": "Notifications cleared"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear notifications: {str(e)}")


@router.get("/notifications/{node_id}/history")
async def get_notification_history(
    node_id: str,
    limit: int = Query(50, description="Maximum number of notifications to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get notification history for a node."""
    try:
        from ...websocket.notification_service import notification_service

        history = await notification_service.get_notification_history(node_id, limit)
        return {
            "node_id": node_id,
            "notification_history": history,
            "count": len(history)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.post("/notifications/broadcast")
async def broadcast_notification(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Broadcast a notification to nodes (admin only)."""
    try:
        from ...websocket.notification_service import notification_service

        await notification_service.broadcast_notification(
            notification_type=request.message_type,
            title=f"Broadcast: {request.message_type}",
            message="System broadcast message",
            data=request.data,
            target_nodes=request.target_ids
        )

        return {"status": "success", "message": "Notification broadcast sent"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")


@router.post("/notifications/{node_id}/preferences")
async def update_notification_preferences(
    node_id: str,
    preferences: Dict[str, bool],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update notification preferences for a node."""
    try:
        from ...websocket.notification_service import notification_service

        await notification_service.update_node_preferences(node_id, preferences)
        return {"status": "success", "message": "Preferences updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


# Metrics endpoints

@router.get("/metrics/current")
async def get_current_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current system metrics."""
    try:
        from ...websocket.metrics_monitor import metrics_monitor

        metrics = metrics_monitor.get_current_metrics()
        return metrics or {"message": "No metrics available yet"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics/history")
async def get_metrics_history(
    limit: int = Query(10, description="Number of historical entries to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get metrics history."""
    try:
        from ...websocket.metrics_monitor import metrics_monitor

        history = metrics_monitor.get_metrics_history(limit)
        return {"metrics_history": history, "count": len(history)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/metrics/performance")
async def get_performance_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Get performance report (admin only)."""
    try:
        from ...websocket.metrics_monitor import metrics_monitor

        report = await metrics_monitor.get_performance_report()
        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")


@router.post("/metrics/alert-threshold")
async def update_alert_threshold(
    metric: str = Query(..., description="Metric name"),
    threshold: float = Query(..., description="Threshold value"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update alert threshold for a metric (admin only)."""
    try:
        from ...websocket.metrics_monitor import metrics_monitor

        metrics_monitor.update_alert_threshold(metric, threshold)
        return {"status": "success", "message": f"Threshold updated for {metric}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update threshold: {str(e)}")