"""
Service layer for reward management operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.base import RewardTransaction, Contribution, FederatedSession, Node
from ..models.schemas import RewardTransactionResponse
from ..core.exceptions import RewardTransactionNotFoundError, ValidationError
# from ..rewards.drachma_calculator import DrachmaCalculator, NodeContribution  # Commented out - module not found
from ..core.config import Config


class RewardService:
    """Service for managing DRACMA rewards and transactions."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        # self.drachma_calculator = DrachmaCalculator(self.config)  # Commented out - module not found
        self.drachma_calculator = None  # Placeholder

    @staticmethod
    async def list_reward_transactions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        session_id: Optional[str] = None,
        node_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[RewardTransactionResponse], int]:
        """List reward transactions with optional filtering."""
        query = db.query(RewardTransaction)

        # Apply filters
        if session_id:
            query = query.filter(RewardTransaction.session_id == session_id)
        if node_id:
            query = query.filter(RewardTransaction.node_id == node_id)
        if transaction_type:
            query = query.filter(RewardTransaction.transaction_type == transaction_type)
        if status:
            query = query.filter(RewardTransaction.status == status)

        # Get total count
        total = query.count()

        # Apply pagination
        transactions = query.offset(skip).limit(limit).all()

        # Convert to response models
        transaction_responses = []
        for transaction in transactions:
            transaction_responses.append(RewardTransactionResponse(
                id=transaction.id,
                session_id=transaction.session_id,
                node_id=transaction.node_id,
                transaction_type=transaction.transaction_type,
                drachma_amount=transaction.drachma_amount,
                contribution_id=transaction.contribution_id,
                status=transaction.status,
                blockchain_tx_hash=transaction.blockchain_tx_hash,
                blockchain_tx_status=transaction.blockchain_tx_status,
                processed_at=transaction.processed_at,
                distribution_proof=transaction.distribution_proof,
                created_at=transaction.created_at,
                updated_at=transaction.updated_at
            ))

        return transaction_responses, total

    @staticmethod
    async def get_reward_transaction_by_id(db: Session, transaction_id: int) -> RewardTransactionResponse:
        """Get a reward transaction by ID."""
        transaction = db.query(RewardTransaction).filter(RewardTransaction.id == transaction_id).first()
        if not transaction:
            raise RewardTransactionNotFoundError(transaction_id)

        return RewardTransactionResponse(
            id=transaction.id,
            session_id=transaction.session_id,
            node_id=transaction.node_id,
            transaction_type=transaction.transaction_type,
            drachma_amount=transaction.drachma_amount,
            contribution_id=transaction.contribution_id,
            status=transaction.status,
            blockchain_tx_hash=transaction.blockchain_tx_hash,
            blockchain_tx_status=transaction.blockchain_tx_status,
            processed_at=transaction.processed_at,
            distribution_proof=transaction.distribution_proof,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )

    @staticmethod
    async def create_reward_transaction(
        db: Session,
        session_id: str,
        node_id: str,
        transaction_type: str,
        drachma_amount: float,
        contribution_id: Optional[int] = None
    ) -> RewardTransactionResponse:
        """Create a new reward transaction."""
        # Validate session
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            from ..core.exceptions import SessionNotFoundError
            raise SessionNotFoundError(session_id)

        # Validate node
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            from ..core.exceptions import NodeNotFoundError
            raise NodeNotFoundError(node_id)

        # Validate contribution if provided
        if contribution_id:
            contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()
            if not contribution:
                from ..core.exceptions import ContributionNotFoundError
                raise ContributionNotFoundError(contribution_id)

        # Validate amount
        if drachma_amount <= 0:
            raise ValidationError("DRACMA amount must be positive")

        # Create transaction
        transaction = RewardTransaction(
            session_id=session_id,
            node_id=node_id,
            transaction_type=transaction_type,
            drachma_amount=drachma_amount,
            contribution_id=contribution_id
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return await RewardService.get_reward_transaction_by_id(db, transaction.id)

    async def calculate_session_rewards(
        self,
        db: Session,
        session_id: str
    ) -> List[RewardTransactionResponse]:
        """Calculate rewards for all contributions in a session."""
        # Get all validated contributions for the session
        contributions = db.query(Contribution).filter(
            and_(
                Contribution.session_id == session_id,
                Contribution.status == 'validated'
            )
        ).all()

        if not contributions:
            return []

        # Convert to NodeContribution objects for the calculator - simplified
        node_contributions = []
        for contrib in contributions:
            # Simplified contribution object
            node_contrib = {
                'node_id': contrib.node_id,
                'session_id': contrib.session_id,
                'round_number': contrib.round_number,
                'parameters_trained': contrib.parameters_trained,
                'data_samples': contrib.data_samples_used,
                'training_time_seconds': contrib.training_time_seconds,
                'model_accuracy': contrib.model_accuracy or 0.0,
                'hardware_specs': contrib.hardware_specs or {},
                'timestamp': contrib.created_at,
                'proof_of_work': contrib.proof_of_work or ""
            }
            node_contributions.append(node_contrib)

        # Add contributions to calculator - simplified
        # for contrib in node_contributions:
        #     await self.drachma_calculator.add_contribution(contrib)

        # Calculate rewards - simplified mock
        reward_calculations = []
        for contrib in node_contributions:
            reward_calc = {
                'node_id': contrib['node_id'],
                'round_number': contrib['round_number'],
                'drachma_amount': 0.001  # Mock reward amount
            }
            reward_calculations.append(reward_calc)

        # Create transactions for each reward
        transactions = []
        for calc in reward_calculations:
            # Find corresponding contribution
            contribution = next(
                (c for c in contributions if c.node_id == calc.node_id and c.round_number == calc.round_number),
                None
            )

            if contribution:
                # Update contribution with calculated rewards
                contribution.rewards_calculated = calc.drachma_amount

                # Create reward transaction
                transaction = await self.create_reward_transaction(
                    db=db,
                    session_id=session_id,
                    node_id=calc.node_id,
                    transaction_type='contribution_reward',
                    drachma_amount=calc.drachma_amount,
                    contribution_id=contribution.id
                )
                transactions.append(transaction)

        # Commit contribution updates
        db.commit()

        # Broadcast reward distribution event
        from ..websocket.event_broadcaster import event_broadcaster
        from ..websocket.notification_service import notification_service

        reward_data = [
            {
                "node_id": calc.node_id,
                "amount": calc.drachma_amount,
                "reason": "training_contribution",
                "round_number": calc.round_number
            }
            for calc in reward_calculations
        ]
        await event_broadcaster.notify_rewards_distributed(session_id, reward_data)

        # Send individual notifications
        await notification_service.notify_on_rewards_distributed(session_id, reward_data)

        return transactions

    @staticmethod
    async def process_reward_transaction(
        db: Session,
        transaction_id: int,
        blockchain_tx_hash: str
    ) -> RewardTransactionResponse:
        """Process a reward transaction on the blockchain."""
        transaction = db.query(RewardTransaction).filter(RewardTransaction.id == transaction_id).first()
        if not transaction:
            raise RewardTransactionNotFoundError(transaction_id)

        if transaction.status != 'pending':
            raise ValidationError(f"Transaction is already {transaction.status}")

        # Update transaction with blockchain info
        transaction.blockchain_tx_hash = blockchain_tx_hash
        transaction.status = 'processing'
        transaction.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(transaction)

        return await RewardService.get_reward_transaction_by_id(db, transaction_id)

    @staticmethod
    async def confirm_reward_transaction(
        db: Session,
        transaction_id: int,
        blockchain_tx_status: str = 'confirmed'
    ) -> RewardTransactionResponse:
        """Confirm a processed reward transaction."""
        transaction = db.query(RewardTransaction).filter(RewardTransaction.id == transaction_id).first()
        if not transaction:
            raise RewardTransactionNotFoundError(transaction_id)

        if transaction.status not in ['processing', 'pending']:
            raise ValidationError(f"Transaction is already {transaction.status}")

        # Update transaction status
        transaction.blockchain_tx_status = blockchain_tx_status
        transaction.status = 'completed' if blockchain_tx_status == 'confirmed' else 'failed'

        # Update node total rewards if completed
        if transaction.status == 'completed':
            node = db.query(Node).filter(Node.id == transaction.node_id).first()
            if node:
                node.total_rewards_earned += transaction.drachma_amount
                db.commit()

        db.commit()
        db.refresh(transaction)

        return await RewardService.get_reward_transaction_by_id(db, transaction_id)

    @staticmethod
    async def get_node_rewards(
        db: Session,
        node_id: str,
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[RewardTransactionResponse]:
        """Get reward transactions for a specific node."""
        query = db.query(RewardTransaction).filter(RewardTransaction.node_id == node_id)

        if session_id:
            query = query.filter(RewardTransaction.session_id == session_id)

        query = query.order_by(RewardTransaction.created_at.desc())

        if limit:
            query = query.limit(limit)

        transactions = query.all()

        return [
            RewardTransactionResponse(
                id=t.id,
                session_id=t.session_id,
                node_id=t.node_id,
                transaction_type=t.transaction_type,
                drachma_amount=t.drachma_amount,
                contribution_id=t.contribution_id,
                status=t.status,
                blockchain_tx_hash=t.blockchain_tx_hash,
                blockchain_tx_status=t.blockchain_tx_status,
                processed_at=t.processed_at,
                distribution_proof=t.distribution_proof,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in transactions
        ]

    @staticmethod
    async def get_session_rewards(db: Session, session_id: str) -> List[RewardTransactionResponse]:
        """Get all reward transactions for a session."""
        transactions = db.query(RewardTransaction).filter(RewardTransaction.session_id == session_id).all()

        return [
            RewardTransactionResponse(
                id=t.id,
                session_id=t.session_id,
                node_id=t.node_id,
                transaction_type=t.transaction_type,
                drachma_amount=t.drachma_amount,
                contribution_id=t.contribution_id,
                status=t.status,
                blockchain_tx_hash=t.blockchain_tx_hash,
                blockchain_tx_status=t.blockchain_tx_status,
                processed_at=t.processed_at,
                distribution_proof=t.distribution_proof,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in transactions
        ]

    @staticmethod
    async def get_reward_stats(db: Session, session_id: Optional[str] = None) -> dict:
        """Get reward statistics."""
        query = db.query(RewardTransaction)

        if session_id:
            query = query.filter(RewardTransaction.session_id == session_id)

        total_transactions = query.count()
        completed_transactions = query.filter(RewardTransaction.status == 'completed').count()
        pending_transactions = query.filter(RewardTransaction.status == 'pending').count()
        failed_transactions = query.filter(RewardTransaction.status == 'failed').count()

        # Calculate totals
        total_drachma = db.query(func.sum(RewardTransaction.drachma_amount)).filter(
            RewardTransaction.status == 'completed'
        ).scalar() or 0

        avg_reward = db.query(func.avg(RewardTransaction.drachma_amount)).filter(
            RewardTransaction.status == 'completed'
        ).scalar() or 0

        return {
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'pending_transactions': pending_transactions,
            'failed_transactions': failed_transactions,
            'completion_rate': completed_transactions / max(total_transactions, 1),
            'total_drachma_distributed': float(total_drachma),
            'average_reward_amount': float(avg_reward)
        }

    def get_reward_pool_status(self, session_id: str) -> Optional[dict]:
        """Get reward pool status for a session."""
        # Simplified implementation - return mock data
        return {
            'session_id': session_id,
            'total_pool_drachma': 1000.0,
            'allocated_drachma': 100.0,
            'remaining_drachma': 900.0,
            'distribution_start': datetime.utcnow().isoformat(),
            'distribution_end': None,
            'min_contribution_threshold': 1,
            'reward_curve': 'linear'
        }