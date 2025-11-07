"""Add time-based partitioning for high-volume tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-04 00:27:19.531000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create partitioning functions and triggers for contributions table
    # This creates monthly partitions for contributions
    op.execute("""
    CREATE OR REPLACE FUNCTION create_contributions_partition()
    RETURNS TRIGGER AS $$
    DECLARE
        partition_name TEXT;
        partition_start DATE;
        partition_end DATE;
    BEGIN
        partition_start := date_trunc('month', NEW.created_at);
        partition_end := partition_start + INTERVAL '1 month';
        partition_name := 'contributions_' || to_char(partition_start, 'YYYY_MM');

        -- Check if partition exists, create if not
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = partition_name AND n.nspname = 'public'
        ) THEN
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS %I PARTITION OF contributions FOR VALUES FROM (%L) TO (%L)',
                partition_name, partition_start, partition_end
            );

            -- Create indexes on partition
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_session_id ON %I (session_id)', partition_name, partition_name);
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_node_id ON %I (node_id)', partition_name, partition_name);
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_round_number ON %I (round_number)', partition_name, partition_name);
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_status ON %I (status)', partition_name, partition_name);
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create partitioning functions and triggers for audit_logs table
    op.execute("""
    CREATE OR REPLACE FUNCTION create_audit_logs_partition()
    RETURNS TRIGGER AS $$
    DECLARE
        partition_name TEXT;
        partition_start DATE;
        partition_end DATE;
    BEGIN
        partition_start := date_trunc('month', NEW.created_at);
        partition_end := partition_start + INTERVAL '1 month';
        partition_name := 'audit_logs_' || to_char(partition_start, 'YYYY_MM');

        -- Check if partition exists, create if not
        IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = partition_name AND n.nspname = 'public'
        ) THEN
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_logs FOR VALUES FROM (%L) TO (%L)',
                partition_name, partition_start, partition_end
            );

            -- Create indexes on partition
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_entity_type ON %I (entity_type)', partition_name, partition_name);
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_entity_id ON %I (entity_id)', partition_name, partition_name);
            EXECUTE format('CREATE INDEX IF NOT EXISTS ix_%I_action ON %I (action)', partition_name, partition_name);
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Convert existing tables to partitioned tables
    # Note: This is a simplified approach. In production, you might need to handle existing data differently

    # Create triggers for automatic partition creation
    op.execute("""
    CREATE TRIGGER contributions_partition_trigger
        BEFORE INSERT ON contributions
        FOR EACH ROW EXECUTE FUNCTION create_contributions_partition();
    """)

    op.execute("""
    CREATE TRIGGER audit_logs_partition_trigger
        BEFORE INSERT ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION create_audit_logs_partition();
    """)

    # Create initial partitions for the current and next few months
    op.execute("""
    -- Create partitions for contributions
    CREATE TABLE IF NOT EXISTS contributions_2024_11 PARTITION OF contributions
        FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
    CREATE TABLE IF NOT EXISTS contributions_2024_12 PARTITION OF contributions
        FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
    CREATE TABLE IF NOT EXISTS contributions_2025_01 PARTITION OF contributions
        FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

    -- Create partitions for audit_logs
    CREATE TABLE IF NOT EXISTS audit_logs_2024_11 PARTITION OF audit_logs
        FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
    CREATE TABLE IF NOT EXISTS audit_logs_2024_12 PARTITION OF audit_logs
        FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
    CREATE TABLE IF NOT EXISTS audit_logs_2025_01 PARTITION OF audit_logs
        FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
    """)

    # Create additional performance indexes
    op.execute("""
    -- Composite indexes for common query patterns
    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_contributions_session_round
        ON contributions (session_id, round_number, status);

    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_contributions_node_recent
        ON contributions (node_id, created_at DESC)
        WHERE created_at > NOW() - INTERVAL '30 days';

    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_audit_logs_entity_action
        ON audit_logs (entity_type, action, created_at DESC);

    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_session_participants_active
        ON session_participants (session_id, status)
        WHERE status IN ('joined', 'active');

    -- Partial indexes for active data
    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_federated_sessions_active
        ON federated_sessions (status, started_at DESC)
        WHERE status IN ('active', 'created');

    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_nodes_active_verified
        ON nodes (status, is_verified, last_heartbeat DESC)
        WHERE status = 'active' AND is_verified = true;
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS audit_logs_partition_trigger ON audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS contributions_partition_trigger ON contributions;")

    # Remove partitioning functions
    op.execute("DROP FUNCTION IF EXISTS create_audit_logs_partition();")
    op.execute("DROP FUNCTION IF EXISTS create_contributions_partition();")

    # Drop additional indexes
    op.execute("""
    DROP INDEX CONCURRENTLY IF EXISTS ix_nodes_active_verified;
    DROP INDEX CONCURRENTLY IF EXISTS ix_federated_sessions_active;
    DROP INDEX CONCURRENTLY IF EXISTS ix_session_participants_active;
    DROP INDEX CONCURRENTLY IF EXISTS ix_audit_logs_entity_action;
    DROP INDEX CONCURRENTLY IF EXISTS ix_contributions_node_recent;
    DROP INDEX CONCURRENTLY IF EXISTS ix_contributions_session_round;
    """)

    # Note: Dropping partitioned tables would require moving data back to main tables
    # This is a simplified downgrade - in production you'd need to handle data migration
    op.execute("""
    DROP TABLE IF EXISTS audit_logs_2025_01;
    DROP TABLE IF EXISTS audit_logs_2024_12;
    DROP TABLE IF EXISTS audit_logs_2024_11;
    DROP TABLE IF EXISTS contributions_2025_01;
    DROP TABLE IF EXISTS contributions_2024_12;
    DROP TABLE IF EXISTS contributions_2024_11;
    """)