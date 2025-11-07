"""
Service layer for federated session management operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.base import FederatedSession, SessionParticipant, Node
from ..models.schemas import (
    FederatedSessionResponse, FederatedSessionCreate, FederatedSessionUpdate,
    SessionParticipantResponse
)
from ..core.exceptions import SessionNotFoundError, ValidationError, NodeNotFoundError
from ..core.config import Config


class SessionService:
    """Service for managing federated learning sessions."""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    @staticmethod
    async def list_sessions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        model_type: Optional[str] = None,
        coordinator_node_id: Optional[str] = None
    ) -> Tuple[List[FederatedSessionResponse], int]:
        """List sessions with optional filtering."""
        query = db.query(FederatedSession)

        # Apply filters
        if status:
            query = query.filter(FederatedSession.status == status)
        if model_type:
            query = query.filter(FederatedSession.model_type == model_type)
        if coordinator_node_id:
            query = query.filter(FederatedSession.coordinator_node_id == coordinator_node_id)

        # Get total count
        total = query.count()

        # Apply pagination
        sessions = query.offset(skip).limit(limit).all()

        # Convert to response models
        session_responses = []
        for session in sessions:
            session_responses.append(FederatedSessionResponse(
                id=session.id,
                name=session.name,
                description=session.description,
                model_type=session.model_type,
                dataset_info=session.dataset_info,
                configuration=session.configuration,
                min_nodes=session.min_nodes,
                max_nodes=session.max_nodes,
                total_rounds=session.total_rounds,
                status=session.status,
                coordinator_node_id=session.coordinator_node_id,
                current_round=session.current_round,
                started_at=session.started_at,
                completed_at=session.completed_at,
                estimated_completion=session.estimated_completion,
                created_at=session.created_at,
                updated_at=session.updated_at
            ))

        return session_responses, total

    @staticmethod
    async def get_session_by_id(db: Session, session_id: str) -> FederatedSessionResponse:
        """Get a session by ID."""
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        return FederatedSessionResponse(
            id=session.id,
            name=session.name,
            description=session.description,
            model_type=session.model_type,
            dataset_info=session.dataset_info,
            configuration=session.configuration,
            min_nodes=session.min_nodes,
            max_nodes=session.max_nodes,
            total_rounds=session.total_rounds,
            status=session.status,
            coordinator_node_id=session.coordinator_node_id,
            current_round=session.current_round,
            started_at=session.started_at,
            completed_at=session.completed_at,
            estimated_completion=session.estimated_completion,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    @staticmethod
    async def create_session(
        db: Session,
        session_data: FederatedSessionCreate,
        coordinator_node_id: Optional[str] = None
    ) -> FederatedSessionResponse:
        """Create a new federated session."""
        # Validate coordinator node if provided
        if coordinator_node_id:
            coordinator = db.query(Node).filter(Node.id == coordinator_node_id).first()
            if not coordinator:
                raise NodeNotFoundError(coordinator_node_id)

        # Create session
        session = FederatedSession(
            id=session_data.id,
            name=session_data.name,
            description=session_data.description,
            model_type=session_data.model_type,
            dataset_info=session_data.dataset_info,
            configuration=session_data.configuration,
            min_nodes=session_data.min_nodes,
            max_nodes=session_data.max_nodes,
            total_rounds=session_data.total_rounds,
            coordinator_node_id=coordinator_node_id
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return await SessionService.get_session_by_id(db, session.id)

    @staticmethod
    async def update_session(
        db: Session,
        session_id: str,
        session_update: FederatedSessionUpdate
    ) -> FederatedSessionResponse:
        """Update session information."""
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        # Update fields
        update_data = session_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)

        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)

        return await SessionService.get_session_by_id(db, session_id)

    @staticmethod
    async def delete_session(db: Session, session_id: str) -> None:
        """Delete a session."""
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        # Check if session can be deleted (not active)
        if session.status in ['active', 'running']:
            raise ValidationError("Cannot delete active session")

        db.delete(session)
        db.commit()

    @staticmethod
    async def start_session(db: Session, session_id: str) -> FederatedSessionResponse:
        """Start a federated session."""
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        if session.status != 'created':
            raise ValidationError(f"Session is already {session.status}")

        # Check minimum participants
        participant_count = db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.status == 'joined'
            )
        ).count()

        if participant_count < session.min_nodes:
            raise ValidationError(f"Insufficient participants: {participant_count}/{session.min_nodes}")

        # Start session
        session.status = 'active'
        session.started_at = datetime.utcnow()
        session.current_round = 1

        # Calculate estimated completion
        avg_round_time = session.configuration.get('estimated_round_time_hours', 24) if session.configuration else 24
        session.estimated_completion = session.started_at + timedelta(hours=avg_round_time * session.total_rounds)

        db.commit()
        db.refresh(session)

        # Broadcast session start event
        from ..websocket.event_broadcaster import event_broadcaster
        from ..websocket.notification_service import notification_service

        await event_broadcaster.notify_session_started(session_id, {
            "name": session.name,
            "model_type": session.model_type,
            "min_nodes": session.min_nodes,
            "max_nodes": session.max_nodes,
            "total_rounds": session.total_rounds
        })

        # Send notifications to participants
        await notification_service.notify_on_session_start(session_id, {
            "name": session.name,
            "model_type": session.model_type
        })

        return await SessionService.get_session_by_id(db, session_id)

    @staticmethod
    async def complete_session(db: Session, session_id: str) -> FederatedSessionResponse:
        """Complete a federated session."""
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        if session.status not in ['active', 'running']:
            raise ValidationError(f"Session is not active: {session.status}")

        session.status = 'completed'
        session.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(session)

        # Broadcast session completion event
        from ..websocket.event_broadcaster import event_broadcaster
        from ..websocket.notification_service import notification_service

        await event_broadcaster.notify_session_completed(session_id, {
            "completed_at": session.completed_at.isoformat(),
            "total_rounds": session.current_round,
            "status": "completed"
        })

        # Send notifications to participants
        await notification_service.notify_on_session_complete(session_id, {
            "completed_at": session.completed_at.isoformat(),
            "total_rounds": session.current_round
        })

        return await SessionService.get_session_by_id(db, session_id)

    @staticmethod
    async def add_participant(
        db: Session,
        session_id: str,
        node_id: str
    ) -> SessionParticipantResponse:
        """Add a node as participant to a session."""
        # Validate session
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        # Validate node
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise NodeNotFoundError(node_id)

        # Check if already participant
        existing = db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.node_id == node_id
            )
        ).first()

        if existing:
            raise ValidationError(f"Node {node_id} is already a participant in session {session_id}")

        # Check max participants
        current_count = db.query(SessionParticipant).filter(
            SessionParticipant.session_id == session_id
        ).count()

        if current_count >= session.max_nodes:
            raise ValidationError(f"Session has reached maximum participants: {session.max_nodes}")

        # Create participant
        participant = SessionParticipant(
            session_id=session_id,
            node_id=node_id,
            status='invited'
        )

        db.add(participant)
        db.commit()
        db.refresh(participant)

        return SessionParticipantResponse(
            session_id=participant.session_id,
            node_id=participant.node_id,
            status=participant.status,
            joined_at=participant.joined_at,
            last_contribution_at=participant.last_contribution_at,
            contributions_count=participant.contributions_count,
            rewards_earned=participant.rewards_earned,
            performance_metrics=participant.performance_metrics,
            created_at=participant.created_at,
            updated_at=participant.updated_at
        )

    @staticmethod
    async def join_session(db: Session, session_id: str, node_id: str) -> SessionParticipantResponse:
        """Node joins a session."""
        participant = db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.node_id == node_id
            )
        ).first()

        if not participant:
            raise ValidationError(f"Node {node_id} is not invited to session {session_id}")

        if participant.status != 'invited':
            raise ValidationError(f"Participant status is {participant.status}")

        participant.status = 'joined'
        participant.joined_at = datetime.utcnow()

        db.commit()
        db.refresh(participant)

        return SessionParticipantResponse(
            session_id=participant.session_id,
            node_id=participant.node_id,
            status=participant.status,
            joined_at=participant.joined_at,
            last_contribution_at=participant.last_contribution_at,
            contributions_count=participant.contributions_count,
            rewards_earned=participant.rewards_earned,
            performance_metrics=participant.performance_metrics,
            created_at=participant.created_at,
            updated_at=participant.updated_at
        )

    @staticmethod
    async def get_session_participants(
        db: Session,
        session_id: str,
        status: Optional[str] = None
    ) -> List[SessionParticipantResponse]:
        """Get participants for a session."""
        query = db.query(SessionParticipant).filter(SessionParticipant.session_id == session_id)

        if status:
            query = query.filter(SessionParticipant.status == status)

        participants = query.all()

        return [
            SessionParticipantResponse(
                session_id=p.session_id,
                node_id=p.node_id,
                status=p.status,
                joined_at=p.joined_at,
                last_contribution_at=p.last_contribution_at,
                contributions_count=p.contributions_count,
                rewards_earned=p.rewards_earned,
                performance_metrics=p.performance_metrics,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in participants
        ]

    @staticmethod
    async def get_active_sessions_count(db: Session) -> int:
        """Get count of active sessions."""
        return db.query(FederatedSession).filter(
            FederatedSession.status.in_(['active', 'running'])
        ).count()

    @staticmethod
    async def get_sessions_by_status(db: Session, status: str, limit: Optional[int] = None) -> List[FederatedSessionResponse]:
        """Get sessions by status."""
        query = db.query(FederatedSession).filter(FederatedSession.status == status)

        if limit:
            query = query.limit(limit)

        sessions = query.all()

        return [
            FederatedSessionResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                model_type=s.model_type,
                dataset_info=s.dataset_info,
                configuration=s.configuration,
                min_nodes=s.min_nodes,
                max_nodes=s.max_nodes,
                total_rounds=s.total_rounds,
                status=s.status,
                coordinator_node_id=s.coordinator_node_id,
                current_round=s.current_round,
                started_at=s.started_at,
                completed_at=s.completed_at,
                estimated_completion=s.estimated_completion,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            for s in sessions
        ]