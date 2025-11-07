"""
API endpoints for node management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...auth.jwt import get_current_node, require_permissions, ADMIN_PERMISSIONS
from ...models.schemas import (
    NodeResponse,
    NodeUpdate,
    APIResponse,
    PaginatedResponse
)
from ...services.node_service import NodeService
from ...core.exceptions import NodeNotFoundError


router = APIRouter()
node_service = NodeService()


@router.get("/", response_model=PaginatedResponse)
async def list_nodes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by node status"),
    trust_level: Optional[str] = Query(None, description="Filter by trust level"),
    db: Session = Depends(get_db),
    current_user: str = Depends(require_permissions(ADMIN_PERMISSIONS["full"]))
):
    """List all nodes with optional filtering."""
    try:
        nodes, total = await node_service.list_nodes(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            trust_level=trust_level
        )

        return PaginatedResponse(
            data=nodes,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{node_id}", response_model=APIResponse)
async def get_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(require_permissions(ADMIN_PERMISSIONS["full"]))
):
    """Get a specific node by ID."""
    try:
        node = await node_service.get_node_by_id(db=db, node_id=node_id)
        return APIResponse(data=node)
    except NodeNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{node_id}", response_model=APIResponse)
async def update_node(
    node_id: str,
    node_update: NodeUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(require_permissions(ADMIN_PERMISSIONS["full"]))
):
    """Update node information."""
    try:
        node = await node_service.update_node(
            db=db,
            node_id=node_id,
            node_update=node_update
        )
        return APIResponse(data=node, message="Node updated successfully")
    except NodeNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{node_id}", response_model=APIResponse)
async def delete_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(require_permissions(ADMIN_PERMISSIONS["full"]))
):
    """Delete a node."""
    try:
        await node_service.delete_node(db=db, node_id=node_id)
        return APIResponse(message="Node deleted successfully")
    except NodeNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/status", response_model=APIResponse)
async def get_my_status(
    current_node: str = Depends(get_current_node),
    db: Session = Depends(get_db)
):
    """Get current node's own status."""
    try:
        node = await node_service.get_node_by_id(db=db, node_id=current_node)
        return APIResponse(data=node)
    except NodeNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{node_id}/heartbeat", response_model=APIResponse)
async def node_heartbeat(
    node_id: str,
    db: Session = Depends(get_db),
    current_node: str = Depends(get_current_node)
):
    """Update node heartbeat timestamp."""
    if current_node != node_id:
        raise HTTPException(status_code=403, detail="Can only update own heartbeat")

    try:
        await node_service.update_heartbeat(db=db, node_id=node_id)
        return APIResponse(message="Heartbeat updated successfully")
    except NodeNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))