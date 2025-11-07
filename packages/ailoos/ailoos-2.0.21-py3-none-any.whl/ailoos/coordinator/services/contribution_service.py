"""
Service layer for contribution management operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.base import Contribution, FederatedSession, Node
from ..models.schemas import ContributionResponse, ContributionCreate
from ..core.exceptions import ContributionNotFoundError, ValidationError, SessionNotFoundError, NodeNotFoundError
from ..verification.node_verifier import NodeVerifier


class ContributionService:
    """Service for managing federated learning contributions."""

    def __init__(self, node_verifier: Optional[NodeVerifier] = None):
        self.node_verifier = node_verifier

    @staticmethod
    async def list_contributions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        session_id: Optional[str] = None,
        node_id: Optional[str] = None,
        round_number: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[List[ContributionResponse], int]:
        """List contributions with optional filtering."""
        query = db.query(Contribution)

        # Apply filters
        if session_id:
            query = query.filter(Contribution.session_id == session_id)
        if node_id:
            query = query.filter(Contribution.node_id == node_id)
        if round_number is not None:
            query = query.filter(Contribution.round_number == round_number)
        if status:
            query = query.filter(Contribution.status == status)

        # Get total count
        total = query.count()

        # Apply pagination
        contributions = query.offset(skip).limit(limit).all()

        # Convert to response models
        contribution_responses = []
        for contribution in contributions:
            contribution_responses.append(ContributionResponse(
                id=contribution.id,
                session_id=contribution.session_id,
                node_id=contribution.node_id,
                round_number=contribution.round_number,
                parameters_trained=contribution.parameters_trained,
                data_samples_used=contribution.data_samples_used,
                training_time_seconds=contribution.training_time_seconds,
                model_accuracy=contribution.model_accuracy,
                loss_value=contribution.loss_value,
                hardware_specs=contribution.hardware_specs,
                proof_of_work=contribution.proof_of_work,
                status=contribution.status,
                validation_hash=contribution.validation_hash,
                rewards_calculated=contribution.rewards_calculated,
                submitted_at=contribution.submitted_at,
                validated_at=contribution.validated_at,
                created_at=contribution.created_at,
                updated_at=contribution.updated_at
            ))

        return contribution_responses, total

    @staticmethod
    async def get_contribution_by_id(db: Session, contribution_id: int) -> ContributionResponse:
        """Get a contribution by ID."""
        contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()
        if not contribution:
            raise ContributionNotFoundError(contribution_id)

        return ContributionResponse(
            id=contribution.id,
            session_id=contribution.session_id,
            node_id=contribution.node_id,
            round_number=contribution.round_number,
            parameters_trained=contribution.parameters_trained,
            data_samples_used=contribution.data_samples_used,
            training_time_seconds=contribution.training_time_seconds,
            model_accuracy=contribution.model_accuracy,
            loss_value=contribution.loss_value,
            hardware_specs=contribution.hardware_specs,
            proof_of_work=contribution.proof_of_work,
            status=contribution.status,
            validation_hash=contribution.validation_hash,
            rewards_calculated=contribution.rewards_calculated,
            submitted_at=contribution.submitted_at,
            validated_at=contribution.validated_at,
            created_at=contribution.created_at,
            updated_at=contribution.updated_at
        )

    @staticmethod
    async def create_contribution(
        db: Session,
        contribution_data: ContributionCreate,
        node_verifier: Optional[NodeVerifier] = None
    ) -> ContributionResponse:
        """Create a new contribution."""
        # Validate session
        session = db.query(FederatedSession).filter(FederatedSession.id == contribution_data.session_id).first()
        if not session:
            raise SessionNotFoundError(contribution_data.session_id)

        # Validate node
        node = db.query(Node).filter(Node.id == contribution_data.node_id).first()
        if not node:
            raise NodeNotFoundError(contribution_data.node_id)

        # Check if session is active
        if session.status not in ['active', 'running']:
            raise ValidationError(f"Session {contribution_data.session_id} is not active")

        # Check if node is participant
        from ..models.base import SessionParticipant
        participant = db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == contribution_data.session_id,
                SessionParticipant.node_id == contribution_data.node_id,
                SessionParticipant.status == 'joined'
            )
        ).first()

        if not participant:
            raise ValidationError(f"Node {contribution_data.node_id} is not a participant in session {contribution_data.session_id}")

        # Validate round number
        if contribution_data.round_number > session.total_rounds:
            raise ValidationError(f"Round number {contribution_data.round_number} exceeds total rounds {session.total_rounds}")

        # Check for duplicate contribution (same node, session, round)
        existing = db.query(Contribution).filter(
            and_(
                Contribution.session_id == contribution_data.session_id,
                Contribution.node_id == contribution_data.node_id,
                Contribution.round_number == contribution_data.round_number
            )
        ).first()

        if existing:
            raise ValidationError(f"Contribution already exists for node {contribution_data.node_id} in round {contribution_data.round_number}")

        # Validate contribution data
        await ContributionService._validate_contribution_data(contribution_data, node_verifier)

        # Create contribution
        contribution = Contribution(
            session_id=contribution_data.session_id,
            node_id=contribution_data.node_id,
            round_number=contribution_data.round_number,
            parameters_trained=contribution_data.parameters_trained,
            data_samples_used=contribution_data.data_samples_used,
            training_time_seconds=contribution_data.training_time_seconds,
            model_accuracy=contribution_data.model_accuracy,
            loss_value=contribution_data.loss_value,
            hardware_specs=contribution_data.hardware_specs,
            proof_of_work=contribution_data.proof_of_work,
            submitted_at=datetime.utcnow()
        )

        db.add(contribution)
        db.commit()
        db.refresh(contribution)

        # Update participant stats
        participant.contributions_count += 1
        participant.last_contribution_at = datetime.utcnow()
        db.commit()

        return await ContributionService.get_contribution_by_id(db, contribution.id)

    @staticmethod
    async def validate_contribution(
        db: Session,
        contribution_id: int,
        validation_hash: str,
        node_verifier: Optional[NodeVerifier] = None
    ) -> ContributionResponse:
        """Validate a contribution."""
        contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()
        if not contribution:
            raise ContributionNotFoundError(contribution_id)

        if contribution.status != 'submitted':
            raise ValidationError(f"Contribution is already {contribution.status}")

        # Perform validation
        is_valid = await ContributionService._perform_validation(contribution, validation_hash, node_verifier)

        if is_valid:
            contribution.status = 'validated'
            contribution.validation_hash = validation_hash
            contribution.validated_at = datetime.utcnow()

            # Update node reputation
            if node_verifier:
                await node_verifier.update_node_reputation(
                    contribution.node_id,
                    contribution_success=True,
                    reward_amount=contribution.rewards_calculated or 0.0
                )
        else:
            contribution.status = 'rejected'

            # Update node reputation for failed contribution
            if node_verifier:
                await node_verifier.update_node_reputation(
                    contribution.node_id,
                    contribution_success=False
                )

        db.commit()
        db.refresh(contribution)

        return await ContributionService.get_contribution_by_id(db, contribution_id)

    @staticmethod
    async def calculate_contribution_rewards(
        db: Session,
        contribution_id: int,
        reward_amount: float
    ) -> ContributionResponse:
        """Calculate and set rewards for a contribution."""
        contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()
        if not contribution:
            raise ContributionNotFoundError(contribution_id)

        if contribution.status != 'validated':
            raise ValidationError("Can only calculate rewards for validated contributions")

        contribution.rewards_calculated = reward_amount
        contribution.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(contribution)

        return await ContributionService.get_contribution_by_id(db, contribution_id)

    @staticmethod
    async def get_contributions_by_session_and_round(
        db: Session,
        session_id: str,
        round_number: int
    ) -> List[ContributionResponse]:
        """Get all contributions for a specific session round."""
        contributions = db.query(Contribution).filter(
            and_(
                Contribution.session_id == session_id,
                Contribution.round_number == round_number
            )
        ).all()

        return [
            ContributionResponse(
                id=c.id,
                session_id=c.session_id,
                node_id=c.node_id,
                round_number=c.round_number,
                parameters_trained=c.parameters_trained,
                data_samples_used=c.data_samples_used,
                training_time_seconds=c.training_time_seconds,
                model_accuracy=c.model_accuracy,
                loss_value=c.loss_value,
                hardware_specs=c.hardware_specs,
                proof_of_work=c.proof_of_work,
                status=c.status,
                validation_hash=c.validation_hash,
                rewards_calculated=c.rewards_calculated,
                submitted_at=c.submitted_at,
                validated_at=c.validated_at,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in contributions
        ]

    @staticmethod
    async def get_node_contributions(
        db: Session,
        node_id: str,
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ContributionResponse]:
        """Get contributions by a specific node."""
        query = db.query(Contribution).filter(Contribution.node_id == node_id)

        if session_id:
            query = query.filter(Contribution.session_id == session_id)

        query = query.order_by(Contribution.created_at.desc())

        if limit:
            query = query.limit(limit)

        contributions = query.all()

        return [
            ContributionResponse(
                id=c.id,
                session_id=c.session_id,
                node_id=c.node_id,
                round_number=c.round_number,
                parameters_trained=c.parameters_trained,
                data_samples_used=c.data_samples_used,
                training_time_seconds=c.training_time_seconds,
                model_accuracy=c.model_accuracy,
                loss_value=c.loss_value,
                hardware_specs=c.hardware_specs,
                proof_of_work=c.proof_of_work,
                status=c.status,
                validation_hash=c.validation_hash,
                rewards_calculated=c.rewards_calculated,
                submitted_at=c.submitted_at,
                validated_at=c.validated_at,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in contributions
        ]

    @staticmethod
    async def _validate_contribution_data(
        contribution_data: ContributionCreate,
        node_verifier: Optional[NodeVerifier] = None
    ) -> None:
        """Validate contribution data before creation."""
        # Basic validation
        if contribution_data.parameters_trained <= 0:
            raise ValidationError("Parameters trained must be positive")

        if contribution_data.data_samples_used <= 0:
            raise ValidationError("Data samples used must be positive")

        if contribution_data.training_time_seconds <= 0:
            raise ValidationError("Training time must be positive")

        if contribution_data.model_accuracy is not None and not (0.0 <= contribution_data.model_accuracy <= 1.0):
            raise ValidationError("Model accuracy must be between 0.0 and 1.0")

        if contribution_data.loss_value is not None and contribution_data.loss_value < 0:
            raise ValidationError("Loss value must be non-negative")

        # Additional validation with node verifier if available
        if node_verifier:
            # Check if node is eligible
            eligible, reason = node_verifier.is_node_eligible(contribution_data.node_id)
            if not eligible:
                raise ValidationError(f"Node not eligible: {reason}")

    @staticmethod
    async def _perform_validation(
        contribution: Contribution,
        validation_hash: str,
        node_verifier: Optional[NodeVerifier] = None
    ) -> bool:
        """Perform validation of contribution."""
        # Basic validation checks
        if contribution.parameters_trained < 1000:  # Minimum threshold
            return False

        if contribution.training_time_seconds < 60:  # Minimum 1 minute
            return False

        # Validate proof of work if present
        if contribution.proof_of_work:
            # Simple proof of work validation (would be more sophisticated in production)
            if len(contribution.proof_of_work) < 10:
                return False

        # Additional cryptographic validation could be added here
        # For now, we assume validation passes if basic checks pass
        return True

    @staticmethod
    async def get_contribution_stats(db: Session, session_id: Optional[str] = None) -> dict:
        """Get contribution statistics."""
        query = db.query(Contribution)

        if session_id:
            query = query.filter(Contribution.session_id == session_id)

        total_contributions = query.count()
        validated_contributions = query.filter(Contribution.status == 'validated').count()
        rejected_contributions = query.filter(Contribution.status == 'rejected').count()

        # Calculate averages
        avg_params = db.query(func.avg(Contribution.parameters_trained)).filter(
            Contribution.status == 'validated'
        ).scalar() or 0

        avg_accuracy = db.query(func.avg(Contribution.model_accuracy)).filter(
            and_(
                Contribution.status == 'validated',
                Contribution.model_accuracy.isnot(None)
            )
        ).scalar() or 0

        total_rewards = db.query(func.sum(Contribution.rewards_calculated)).filter(
            Contribution.rewards_calculated.isnot(None)
        ).scalar() or 0

        return {
            'total_contributions': total_contributions,
            'validated_contributions': validated_contributions,
            'rejected_contributions': rejected_contributions,
            'validation_rate': validated_contributions / max(total_contributions, 1),
            'average_parameters_trained': float(avg_params),
            'average_accuracy': float(avg_accuracy),
            'total_rewards_distributed': float(total_rewards)
        }