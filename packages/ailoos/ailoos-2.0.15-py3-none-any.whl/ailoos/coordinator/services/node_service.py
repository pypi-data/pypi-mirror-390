"""
Service layer for node management operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.base import Node
from ..models.schemas import NodeResponse, NodeUpdate
from ..core.exceptions import NodeNotFoundError, ValidationError


class NodeService:
    """Service for managing federated learning nodes."""

    @staticmethod
    async def list_nodes(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        trust_level: Optional[str] = None
    ) -> Tuple[List[NodeResponse], int]:
        """List nodes with optional filtering."""
        query = db.query(Node)

        # Apply filters
        if status:
            query = query.filter(Node.status == status)
        if trust_level:
            query = query.filter(Node.trust_level == trust_level)

        # Get total count
        total = query.count()

        # Apply pagination
        nodes = query.offset(skip).limit(limit).all()

        # Convert to response models
        node_responses = [
            NodeResponse(
                id=node.id,
                public_key=node.public_key,
                status=node.status,
                reputation_score=node.reputation_score,
                trust_level=node.trust_level,
                hardware_specs=node.hardware_specs,
                location=node.location,
                last_heartbeat=node.last_heartbeat,
                total_contributions=node.total_contributions,
                total_rewards_earned=node.total_rewards_earned,
                is_verified=node.is_verified,
                verification_expires_at=node.verification_expires_at,
                created_at=node.created_at,
                updated_at=node.updated_at
            )
            for node in nodes
        ]

        return node_responses, total

    @staticmethod
    async def get_node_by_id(db: Session, node_id: str) -> NodeResponse:
        """Get a node by ID."""
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise NodeNotFoundError(node_id)

        return NodeResponse(
            id=node.id,
            public_key=node.public_key,
            status=node.status,
            reputation_score=node.reputation_score,
            trust_level=node.trust_level,
            hardware_specs=node.hardware_specs,
            location=node.location,
            last_heartbeat=node.last_heartbeat,
            total_contributions=node.total_contributions,
            total_rewards_earned=node.total_rewards_earned,
            is_verified=node.is_verified,
            verification_expires_at=node.verification_expires_at,
            created_at=node.created_at,
            updated_at=node.updated_at
        )

    @staticmethod
    async def create_node(db: Session, node_data: dict) -> NodeResponse:
        """Create a new node."""
        # Validate required fields
        if not node_data.get("id"):
            raise ValidationError("Node ID is required")
        if not node_data.get("public_key"):
            raise ValidationError("Public key is required")

        # Check if node already exists
        existing = db.query(Node).filter(Node.id == node_data["id"]).first()
        if existing:
            raise ValidationError(f"Node {node_data['id']} already exists")

        # Create node
        node = Node(
            id=node_data["id"],
            public_key=node_data["public_key"],
            status=node_data.get("status", "registered"),
            reputation_score=node_data.get("reputation_score", 0.5),
            trust_level=node_data.get("trust_level", "basic"),
            hardware_specs=node_data.get("hardware_specs"),
            location=node_data.get("location"),
            is_verified=node_data.get("is_verified", False)
        )

        db.add(node)
        db.commit()
        db.refresh(node)

        return await NodeService.get_node_by_id(db, node.id)

    @staticmethod
    async def update_node(
        db: Session,
        node_id: str,
        node_update: NodeUpdate
    ) -> NodeResponse:
        """Update node information."""
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise NodeNotFoundError(node_id)

        # Update fields
        update_data = node_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)

        node.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(node)

        return await NodeService.get_node_by_id(db, node_id)

    @staticmethod
    async def delete_node(db: Session, node_id: str) -> None:
        """Delete a node."""
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise NodeNotFoundError(node_id)

        db.delete(node)
        db.commit()

    @staticmethod
    async def update_heartbeat(db: Session, node_id: str) -> None:
        """Update node heartbeat timestamp."""
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise NodeNotFoundError(node_id)

        node.last_heartbeat = datetime.utcnow()
        db.commit()

    @staticmethod
    async def get_active_nodes_count(db: Session) -> int:
        """Get count of active nodes."""
        from ..config.settings import settings
        timeout_threshold = datetime.utcnow() - settings.coordinator.node_timeout_seconds

        return db.query(Node).filter(
            and_(
                Node.status == "active",
                Node.last_heartbeat > timeout_threshold
            )
        ).count()

    @staticmethod
    async def get_nodes_by_trust_level(
        db: Session,
        trust_level: str,
        limit: Optional[int] = None
    ) -> List[NodeResponse]:
        """Get nodes by trust level."""
        query = db.query(Node).filter(Node.trust_level == trust_level)

        if limit:
            query = query.limit(limit)

        nodes = query.all()

        return [
            NodeResponse(
                id=node.id,
                public_key=node.public_key,
                status=node.status,
                reputation_score=node.reputation_score,
                trust_level=node.trust_level,
                hardware_specs=node.hardware_specs,
                location=node.location,
                last_heartbeat=node.last_heartbeat,
                total_contributions=node.total_contributions,
                total_rewards_earned=node.total_rewards_earned,
                is_verified=node.is_verified,
                verification_expires_at=node.verification_expires_at,
                created_at=node.created_at,
                updated_at=node.updated_at
            )
            for node in nodes
        ]