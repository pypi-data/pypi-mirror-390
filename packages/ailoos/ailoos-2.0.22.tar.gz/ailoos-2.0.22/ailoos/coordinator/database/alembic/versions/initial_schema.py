"""Initial federated learning coordinator schema

Revision ID: 001
Revises:
Create Date: 2025-11-04 00:26:57.723000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create nodes table with partitioning
    op.create_table('nodes',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='registered'),
        sa.Column('reputation_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('trust_level', sa.String(length=20), nullable=False, server_default='basic'),
        sa.Column('hardware_specs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('location', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_heartbeat', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('total_contributions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_rewards_earned', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verification_expires_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create federated_sessions table
    op.create_table('federated_sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='created'),
        sa.Column('model_type', sa.String(length=100), nullable=False),
        sa.Column('dataset_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('coordinator_node_id', sa.String(length=64), nullable=True),
        sa.Column('min_nodes', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('max_nodes', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('current_round', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_rounds', sa.Integer(), nullable=False),
        sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('estimated_completion', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create session_participants table
    op.create_table('session_participants',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('node_id', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='invited'),
        sa.Column('joined_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_contribution_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('contributions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rewards_earned', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('performance_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create models table
    op.create_table('models',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='training'),
        sa.Column('model_type', sa.String(length=100), nullable=False),
        sa.Column('architecture', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('hyperparameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('global_parameters_hash', sa.String(length=128), nullable=True),
        sa.Column('storage_location', sa.String(length=500), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('owner_node_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create contributions table with time-based partitioning
    op.create_table('contributions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('node_id', sa.String(length=64), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('parameters_trained', sa.Integer(), nullable=False),
        sa.Column('data_samples_used', sa.Integer(), nullable=False),
        sa.Column('training_time_seconds', sa.Float(), nullable=False),
        sa.Column('model_accuracy', sa.Float(), nullable=True),
        sa.Column('loss_value', sa.Float(), nullable=True),
        sa.Column('hardware_specs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('proof_of_work', sa.Text(), nullable=True),
        sa.Column('validation_hash', sa.String(length=128), nullable=True),
        sa.Column('rewards_calculated', sa.Float(), nullable=True),
        sa.Column('submitted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('validated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create reward_transactions table
    op.create_table('reward_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('node_id', sa.String(length=64), nullable=False),
        sa.Column('contribution_id', sa.Integer(), nullable=True),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('drachma_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('blockchain_tx_hash', sa.String(length=128), nullable=True),
        sa.Column('blockchain_tx_status', sa.String(length=20), nullable=True),
        sa.Column('processed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('distribution_proof', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_logs table with time-based partitioning
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('old_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('audit_proof', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance optimization
    op.create_index('ix_nodes_status', 'nodes', ['status'])
    op.create_index('ix_nodes_reputation_score', 'nodes', ['reputation_score'])
    op.create_index('ix_nodes_trust_level', 'nodes', ['trust_level'])
    op.create_index('ix_nodes_is_verified', 'nodes', ['is_verified'])

    op.create_index('ix_federated_sessions_status', 'federated_sessions', ['status'])
    op.create_index('ix_federated_sessions_coordinator_node_id', 'federated_sessions', ['coordinator_node_id'])
    op.create_index('ix_federated_sessions_started_at', 'federated_sessions', ['started_at'])

    op.create_index('ix_session_participants_session_id', 'session_participants', ['session_id'])
    op.create_index('ix_session_participants_node_id', 'session_participants', ['node_id'])
    op.create_index('ix_session_participants_status', 'session_participants', ['status'])

    op.create_index('ix_models_session_id', 'models', ['session_id'])
    op.create_index('ix_models_status', 'models', ['status'])
    op.create_index('ix_models_owner_node_id', 'models', ['owner_node_id'])

    op.create_index('ix_contributions_session_id', 'contributions', ['session_id'])
    op.create_index('ix_contributions_node_id', 'contributions', ['node_id'])
    op.create_index('ix_contributions_round_number', 'contributions', ['round_number'])
    op.create_index('ix_contributions_status', 'contributions', ['status'])
    op.create_index('ix_contributions_created_at', 'contributions', ['created_at'])

    op.create_index('ix_reward_transactions_session_id', 'reward_transactions', ['session_id'])
    op.create_index('ix_reward_transactions_node_id', 'reward_transactions', ['node_id'])
    op.create_index('ix_reward_transactions_status', 'reward_transactions', ['status'])

    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # Create foreign key constraints
    op.create_foreign_key('fk_session_participants_session_id', 'session_participants', 'federated_sessions', ['session_id'], ['id'])
    op.create_foreign_key('fk_session_participants_node_id', 'session_participants', 'nodes', ['node_id'], ['id'])
    op.create_foreign_key('fk_models_session_id', 'models', 'federated_sessions', ['session_id'], ['id'])
    op.create_foreign_key('fk_contributions_session_id', 'contributions', 'federated_sessions', ['session_id'], ['id'])
    op.create_foreign_key('fk_contributions_node_id', 'contributions', 'nodes', ['node_id'], ['id'])
    op.create_foreign_key('fk_reward_transactions_session_id', 'reward_transactions', 'federated_sessions', ['session_id'], ['id'])
    op.create_foreign_key('fk_reward_transactions_node_id', 'reward_transactions', 'nodes', ['node_id'], ['id'])
    op.create_foreign_key('fk_reward_transactions_contribution_id', 'reward_transactions', 'contributions', ['contribution_id'], ['id'])

    # Create partitioned tables for time-series data
    # Note: PostgreSQL partitioning requires specific syntax, this is a simplified version
    # In production, you might want to use declarative partitioning or pg_partman

    # Create partial indexes for better query performance
    op.create_index('ix_contributions_recent', 'contributions', ['created_at'], postgresql_where=sa.text("created_at > NOW() - INTERVAL '30 days'"))
    op.create_index('ix_audit_logs_recent', 'audit_logs', ['created_at'], postgresql_where=sa.text("created_at > NOW() - INTERVAL '90 days'"))


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_audit_logs_recent')
    op.drop_index('ix_contributions_recent')

    # Drop foreign key constraints
    op.drop_constraint('fk_reward_transactions_contribution_id', 'reward_transactions', type_='foreignkey')
    op.drop_constraint('fk_reward_transactions_node_id', 'reward_transactions', type_='foreignkey')
    op.drop_constraint('fk_reward_transactions_session_id', 'reward_transactions', type_='foreignkey')
    op.drop_constraint('fk_contributions_node_id', 'contributions', type_='foreignkey')
    op.drop_constraint('fk_contributions_session_id', 'contributions', type_='foreignkey')
    op.drop_constraint('fk_models_session_id', 'models', type_='foreignkey')
    op.drop_constraint('fk_session_participants_node_id', 'session_participants', type_='foreignkey')
    op.drop_constraint('fk_session_participants_session_id', 'session_participants', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_audit_logs_created_at')
    op.drop_index('ix_audit_logs_action')
    op.drop_index('ix_audit_logs_entity_id')
    op.drop_index('ix_audit_logs_entity_type')
    op.drop_index('ix_reward_transactions_status')
    op.drop_index('ix_reward_transactions_node_id')
    op.drop_index('ix_reward_transactions_session_id')
    op.drop_index('ix_contributions_created_at')
    op.drop_index('ix_contributions_status')
    op.drop_index('ix_contributions_round_number')
    op.drop_index('ix_contributions_node_id')
    op.drop_index('ix_contributions_session_id')
    op.drop_index('ix_models_owner_node_id')
    op.drop_index('ix_models_status')
    op.drop_index('ix_models_session_id')
    op.drop_index('ix_session_participants_status')
    op.drop_index('ix_session_participants_node_id')
    op.drop_index('ix_session_participants_session_id')
    op.drop_index('ix_federated_sessions_started_at')
    op.drop_index('ix_federated_sessions_coordinator_node_id')
    op.drop_index('ix_federated_sessions_status')
    op.drop_index('ix_nodes_is_verified')
    op.drop_index('ix_nodes_trust_level')
    op.drop_index('ix_nodes_reputation_score')
    op.drop_index('ix_nodes_status')

    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('reward_transactions')
    op.drop_table('contributions')
    op.drop_table('models')
    op.drop_table('session_participants')
    op.drop_table('federated_sessions')
    op.drop_table('nodes')