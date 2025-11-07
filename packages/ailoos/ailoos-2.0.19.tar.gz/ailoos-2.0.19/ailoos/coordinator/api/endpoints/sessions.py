"""
API endpoints for federated session management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...models.schemas import (
    FederatedSessionResponse, FederatedSessionCreate, FederatedSessionUpdate,
    SessionParticipantResponse, APIResponse, PaginatedResponse
)
from ...services.session_service import SessionService
from ...auth.dependencies import get_current_node, get_current_admin
from ...core.exceptions import CoordinatorException


router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_sessions(
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of sessions to return"),
    status: Optional[str] = Query(None, description="Filter by session status"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    coordinator_node_id: Optional[str] = Query(None, description="Filter by coordinator node"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """List federated sessions with optional filtering and pagination."""
    try:
        sessions, total = await SessionService.list_sessions(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            model_type=model_type,
            coordinator_node_id=coordinator_node_id
        )

        return PaginatedResponse(
            success=True,
            message="Sessions retrieved successfully",
            data=sessions,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")


@router.post("/", response_model=APIResponse)
async def create_session(
    session_data: FederatedSessionCreate,
    coordinator_node_id: Optional[str] = Query(None, description="Coordinator node ID"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new federated session."""
    try:
        session = await SessionService.create_session(
            db=db,
            session_data=session_data,
            coordinator_node_id=coordinator_node_id
        )

        return APIResponse(
            success=True,
            message="Session created successfully",
            data=session
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/{session_id}", response_model=APIResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get a specific federated session by ID."""
    try:
        session = await SessionService.get_session_by_id(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Session retrieved successfully",
            data=session
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


@router.put("/{session_id}", response_model=APIResponse)
async def update_session(
    session_id: str,
    session_update: FederatedSessionUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Update a federated session."""
    try:
        session = await SessionService.update_session(
            db=db,
            session_id=session_id,
            session_update=session_update
        )

        return APIResponse(
            success=True,
            message="Session updated successfully",
            data=session
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")


@router.delete("/{session_id}", response_model=APIResponse)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a federated session."""
    try:
        await SessionService.delete_session(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Session deleted successfully"
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.post("/{session_id}/start", response_model=APIResponse)
async def start_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Start a federated session."""
    try:
        session = await SessionService.start_session(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Session started successfully",
            data=session
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")


@router.post("/{session_id}/complete", response_model=APIResponse)
async def complete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Complete a federated session."""
    try:
        session = await SessionService.complete_session(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Session completed successfully",
            data=session
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing session: {str(e)}")


@router.post("/{session_id}/participants", response_model=APIResponse)
async def add_participant(
    session_id: str,
    node_id: str = Query(..., description="Node ID to add as participant"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Add a node as participant to a session."""
    try:
        participant = await SessionService.add_participant(
            db=db,
            session_id=session_id,
            node_id=node_id
        )

        return APIResponse(
            success=True,
            message="Participant added successfully",
            data=participant
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding participant: {str(e)}")


@router.post("/{session_id}/join", response_model=APIResponse)
async def join_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Node joins a session."""
    try:
        participant = await SessionService.join_session(
            db=db,
            session_id=session_id,
            node_id=current_node["node_id"]
        )

        return APIResponse(
            success=True,
            message="Successfully joined session",
            data=participant
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining session: {str(e)}")


@router.get("/{session_id}/participants", response_model=APIResponse)
async def get_session_participants(
    session_id: str,
    status: Optional[str] = Query(None, description="Filter by participant status"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get participants for a session."""
    try:
        participants = await SessionService.get_session_participants(
            db=db,
            session_id=session_id,
            status=status
        )

        return APIResponse(
            success=True,
            message="Participants retrieved successfully",
            data=participants
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving participants: {str(e)}")


@router.get("/stats/active", response_model=APIResponse)
async def get_active_sessions_count(
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get count of active sessions."""
    try:
        count = await SessionService.get_active_sessions_count(db=db)

        return APIResponse(
            success=True,
            message="Active sessions count retrieved successfully",
            data={"active_sessions_count": count}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving active sessions count: {str(e)}")


@router.get("/status/{status}", response_model=PaginatedResponse)
async def get_sessions_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get sessions by status."""
    try:
        sessions = await SessionService.get_sessions_by_status(
            db=db,
            status=status,
            limit=limit
        )

        # Apply pagination manually since the service method doesn't support skip
        paginated_sessions = sessions[skip:skip + limit]
        total = len(sessions)

        return PaginatedResponse(
            success=True,
            message=f"Sessions with status '{status}' retrieved successfully",
            data=paginated_sessions,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions by status: {str(e)}")