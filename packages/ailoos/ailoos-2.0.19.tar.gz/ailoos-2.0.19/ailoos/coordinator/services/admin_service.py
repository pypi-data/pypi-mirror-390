"""
Service layer for administrative operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.base import (
    Node, FederatedSession, Contribution, RewardTransaction,
    AuditLog, SessionParticipant
)
from ..core.exceptions import ValidationError
from ..auditing.zk_auditor import ZKAuditor
from ..verification.node_verifier import NodeVerifier
from ..core.config import Config


class AdminService:
    """Service for administrative operations and system management."""

    def __init__(self, config: Config = None, zk_auditor: Optional[ZKAuditor] = None):
        self.config = config or Config()
        self.zk_auditor = zk_auditor or ZKAuditor(self.config)

    async def get_system_stats(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        # Node statistics
        total_nodes = db.query(Node).count()
        active_nodes = db.query(Node).filter(Node.status == 'active').count()
        verified_nodes = db.query(Node).filter(Node.is_verified == True).count()

        # Session statistics
        total_sessions = db.query(FederatedSession).count()
        active_sessions = db.query(FederatedSession).filter(
            FederatedSession.status.in_(['active', 'running'])
        ).count()
        completed_sessions = db.query(FederatedSession).filter(
            FederatedSession.status == 'completed'
        ).count()

        # Contribution statistics
        total_contributions = db.query(Contribution).count()
        validated_contributions = db.query(Contribution).filter(
            Contribution.status == 'validated'
        ).count()

        # Reward statistics
        total_rewards = db.query(func.sum(RewardTransaction.drachma_amount)).filter(
            RewardTransaction.status == 'completed'
        ).scalar() or 0

        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_contributions = db.query(Contribution).filter(
            Contribution.created_at >= yesterday
        ).count()

        recent_sessions = db.query(FederatedSession).filter(
            FederatedSession.created_at >= yesterday
        ).count()

        return {
            'nodes': {
                'total': total_nodes,
                'active': active_nodes,
                'verified': verified_nodes,
                'active_percentage': (active_nodes / max(total_nodes, 1)) * 100
            },
            'sessions': {
                'total': total_sessions,
                'active': active_sessions,
                'completed': completed_sessions,
                'completion_rate': (completed_sessions / max(total_sessions, 1)) * 100
            },
            'contributions': {
                'total': total_contributions,
                'validated': validated_contributions,
                'validation_rate': (validated_contributions / max(total_contributions, 1)) * 100,
                'recent_24h': recent_contributions
            },
            'rewards': {
                'total_distributed': float(total_rewards),
                'average_per_contribution': float(total_rewards) / max(validated_contributions, 1)
            },
            'activity': {
                'sessions_24h': recent_sessions,
                'contributions_24h': recent_contributions
            }
        }

    async def get_audit_logs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get audit logs with filtering."""
        query = db.query(AuditLog)

        # Apply filters
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

        # Convert to dict
        log_responses = []
        for log in logs:
            log_responses.append({
                'id': log.id,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'action': log.action,
                'user_id': log.user_id,
                'old_values': log.old_values,
                'new_values': log.new_values,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'audit_proof': log.audit_proof,
                'created_at': log.created_at
            })

        return log_responses, total

    async def generate_audit_report(
        self,
        db: Session,
        audit_period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        # Get audit data
        node_stats = await self._get_node_stats_for_audit(db)
        contribution_stats = await self._get_contribution_stats_for_audit(db)

        # Generate ZK audit
        audit_report = await self.zk_auditor.generate_comprehensive_audit_report(audit_period_days)

        return {
            'audit_report': {
                'audit_id': audit_report.audit_id,
                'period_start': audit_report.period_start.isoformat(),
                'period_end': audit_report.period_end.isoformat(),
                'total_transactions': audit_report.total_transactions,
                'total_amount': audit_report.total_amount,
                'anomalies_detected': audit_report.anomalies_detected,
                'compliance_score': audit_report.compliance_score,
                'recommendations': audit_report.recommendations,
                'generated_at': audit_report.generated_at.isoformat()
            },
            'findings': audit_report.findings,
            'zk_proofs_count': len(audit_report.zk_proofs)
        }

    async def manage_node_status(
        self,
        db: Session,
        node_id: str,
        action: str,
        reason: str,
        admin_user_id: str
    ) -> Dict[str, Any]:
        """Manage node status (suspend, activate, ban, etc.)."""
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            from ..core.exceptions import NodeNotFoundError
            raise NodeNotFoundError(node_id)

        old_status = node.status
        old_trust_level = node.trust_level

        if action == 'activate':
            node.status = 'active'
            node.trust_level = 'basic'
        elif action == 'suspend':
            node.status = 'suspended'
            node.trust_level = 'untrusted'
        elif action == 'ban':
            node.status = 'banned'
            node.trust_level = 'untrusted'
        elif action == 'verify':
            node.is_verified = True
            node.trust_level = 'verified'
        else:
            raise ValidationError(f"Unknown action: {action}")

        node.updated_at = datetime.utcnow()
        db.commit()

        # Log the action
        await self._log_admin_action(
            db=db,
            entity_type='node',
            entity_id=node_id,
            action=f'node_{action}',
            user_id=admin_user_id,
            old_values={'status': old_status, 'trust_level': old_trust_level},
            new_values={'status': node.status, 'trust_level': node.trust_level},
            reason=reason
        )

        return {
            'node_id': node_id,
            'action': action,
            'old_status': old_status,
            'new_status': node.status,
            'reason': reason
        }

    async def manage_session(
        self,
        db: Session,
        session_id: str,
        action: str,
        reason: str,
        admin_user_id: str
    ) -> Dict[str, Any]:
        """Manage session status (pause, resume, cancel, etc.)."""
        session = db.query(FederatedSession).filter(FederatedSession.id == session_id).first()
        if not session:
            from ..core.exceptions import SessionNotFoundError
            raise SessionNotFoundError(session_id)

        old_status = session.status

        if action == 'pause':
            if session.status not in ['active', 'running']:
                raise ValidationError("Can only pause active sessions")
            session.status = 'paused'
        elif action == 'resume':
            if session.status != 'paused':
                raise ValidationError("Can only resume paused sessions")
            session.status = 'active'
        elif action == 'cancel':
            if session.status in ['completed', 'cancelled']:
                raise ValidationError("Cannot cancel completed or already cancelled sessions")
            session.status = 'cancelled'
            session.completed_at = datetime.utcnow()
        else:
            raise ValidationError(f"Unknown action: {action}")

        session.updated_at = datetime.utcnow()
        db.commit()

        # Log the action
        await self._log_admin_action(
            db=db,
            entity_type='session',
            entity_id=session_id,
            action=f'session_{action}',
            user_id=admin_user_id,
            old_values={'status': old_status},
            new_values={'status': session.status},
            reason=reason
        )

        return {
            'session_id': session_id,
            'action': action,
            'old_status': old_status,
            'new_status': session.status,
            'reason': reason
        }

    async def get_failed_operations(
        self,
        db: Session,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get list of failed operations for review."""
        # Failed contributions
        failed_contributions = db.query(Contribution).filter(
            Contribution.status == 'rejected'
        ).order_by(Contribution.created_at.desc()).limit(limit).all()

        # Failed reward transactions
        failed_rewards = db.query(RewardTransaction).filter(
            RewardTransaction.status == 'failed'
        ).order_by(RewardTransaction.created_at.desc()).limit(limit).all()

        # Suspended/banned nodes
        problematic_nodes = db.query(Node).filter(
            Node.status.in_(['suspended', 'banned'])
        ).order_by(Node.updated_at.desc()).limit(limit).all()

        return {
            'failed_contributions': [
                {
                    'id': c.id,
                    'session_id': c.session_id,
                    'node_id': c.node_id,
                    'round_number': c.round_number,
                    'failure_reason': 'validation_failed',  # Would be stored in the model
                    'created_at': c.created_at
                }
                for c in failed_contributions
            ],
            'failed_rewards': [
                {
                    'id': r.id,
                    'session_id': r.session_id,
                    'node_id': r.node_id,
                    'amount': r.drachma_amount,
                    'failure_reason': r.blockchain_tx_status or 'unknown',
                    'created_at': r.created_at
                }
                for r in failed_rewards
            ],
            'problematic_nodes': [
                {
                    'id': n.id,
                    'status': n.status,
                    'reputation_score': n.reputation_score,
                    'last_updated': n.updated_at
                }
                for n in problematic_nodes
            ]
        }

    async def cleanup_old_data(
        self,
        db: Session,
        older_than_days: int,
        admin_user_id: str
    ) -> Dict[str, Any]:
        """Clean up old data for performance and compliance."""
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)

        # Count what will be deleted
        old_contributions = db.query(Contribution).filter(
            and_(
                Contribution.created_at < cutoff_date,
                Contribution.status.in_(['validated', 'rejected'])
            )
        ).count()

        old_audit_logs = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).count()

        # In a real implementation, you might archive before deleting
        # For now, just count and log

        await self._log_admin_action(
            db=db,
            entity_type='system',
            entity_id='cleanup',
            action='data_cleanup',
            user_id=admin_user_id,
            old_values={},
            new_values={
                'older_than_days': older_than_days,
                'contributions_to_clean': old_contributions,
                'audit_logs_to_clean': old_audit_logs
            },
            reason=f'Cleanup data older than {older_than_days} days'
        )

        # Calculate estimated space saved based on row sizes
        estimated_space_saved = await self._calculate_space_savings(
            db, old_contributions, old_audit_logs, older_than_days
        )

        return {
            'cleanup_plan': {
                'older_than_days': older_than_days,
                'contributions_to_clean': old_contributions,
                'audit_logs_to_clean': old_audit_logs,
                'estimated_space_saved': estimated_space_saved
            },
            'status': 'plan_generated',
            'message': 'Review the cleanup plan before executing'
        }

    async def _calculate_space_savings(
        self,
        db: Session,
        contribution_count: int,
        audit_log_count: int,
        days_old: int
    ) -> str:
        """Calculate estimated space savings from cleanup operation."""
        try:
            # Estimate average row sizes (in bytes)
            # These are rough estimates based on typical database schemas
            avg_contribution_size = 512  # bytes per contribution record
            avg_audit_log_size = 1024    # bytes per audit log record

            # Calculate total bytes to be freed
            contributions_space = contribution_count * avg_contribution_size
            audit_logs_space = audit_log_count * avg_audit_log_size
            total_bytes = contributions_space + audit_logs_space

            # Convert to human readable format
            if total_bytes < 1024:
                return f"{total_bytes} bytes"
            elif total_bytes < 1024 * 1024:
                return f"{total_bytes / 1024:.1f} KB"
            elif total_bytes < 1024 * 1024 * 1024:
                return f"{total_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"

        except Exception as e:
            # Fallback if calculation fails
            return f"Unable to calculate: {str(e)}"

    async def _log_admin_action(
        self,
        db: Session,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ) -> None:
        """Log administrative action."""
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            audit_proof=reason  # Using audit_proof field for admin reason
        )

        db.add(audit_log)
        db.commit()

    async def _get_node_stats_for_audit(self, db: Session) -> Dict[str, Any]:
        """Get node statistics for audit."""
        total_registered = db.query(Node).count()
        active_nodes = db.query(Node).filter(Node.status == 'active').count()
        verified_nodes = db.query(Node).filter(Node.is_verified == True).count()

        avg_reputation = db.query(func.avg(Node.reputation_score)).scalar() or 0

        return {
            'total_registered': total_registered,
            'active_nodes': active_nodes,
            'verified_nodes': verified_nodes,
            'average_reputation': float(avg_reputation)
        }

    async def _get_contribution_stats_for_audit(self, db: Session) -> Dict[str, Any]:
        """Get contribution statistics for audit."""
        total_contributions = db.query(Contribution).count()

        return {
            'total_contributions': total_contributions
        }