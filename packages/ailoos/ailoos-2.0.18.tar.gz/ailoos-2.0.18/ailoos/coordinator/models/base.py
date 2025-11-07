"""
SQLAlchemy database models for the coordinator service.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Node(Base):
    """Node model for federated learning participants."""
    __tablename__ = "nodes"

    id = Column(String(64), primary_key=True, index=True)
    public_key = Column(Text, nullable=False)
    status = Column(String(20), default="registered", index=True)
    reputation_score = Column(Float, default=0.5)
    trust_level = Column(String(20), default="basic", index=True)
    hardware_specs = Column(JSON)
    location = Column(JSON)
    last_heartbeat = Column(DateTime)
    total_contributions = Column(Integer, default=0)
    total_rewards_earned = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    verification_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contributions = relationship("Contribution", back_populates="node")
    session_participants = relationship("SessionParticipant", back_populates="node")


class FederatedSession(Base):
    """Federated learning session model."""
    __tablename__ = "federated_sessions"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    model_type = Column(String(100), nullable=False, index=True)
    dataset_info = Column(JSON)
    configuration = Column(JSON)
    min_nodes = Column(Integer, default=3)
    max_nodes = Column(Integer, default=50)
    total_rounds = Column(Integer, nullable=False)
    status = Column(String(20), default="created", index=True)
    coordinator_node_id = Column(String(64), ForeignKey("nodes.id"))
    current_round = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participants = relationship("SessionParticipant", back_populates="session")
    contributions = relationship("Contribution", back_populates="session")
    models = relationship("Model", back_populates="session")


class SessionParticipant(Base):
    """Session participant model."""
    __tablename__ = "session_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("federated_sessions.id"), nullable=False, index=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=False, index=True)
    status = Column(String(20), default="invited", index=True)
    joined_at = Column(DateTime)
    last_contribution_at = Column(DateTime)
    contributions_count = Column(Integer, default=0)
    rewards_earned = Column(Float, default=0.0)
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("FederatedSession", back_populates="participants")
    node = relationship("Node", back_populates="session_participants")


class Model(Base):
    """Model version and metadata model."""
    __tablename__ = "models"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False, index=True)
    architecture = Column(JSON)
    hyperparameters = Column(JSON)
    metrics = Column(JSON)
    is_public = Column(Boolean, default=False)
    session_id = Column(String(64), ForeignKey("federated_sessions.id"), index=True)
    status = Column(String(20), default="created", index=True)
    global_parameters_hash = Column(String(128))
    storage_location = Column(String(500))
    owner_node_id = Column(String(64), ForeignKey("nodes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("FederatedSession", back_populates="models")


class Contribution(Base):
    """Contribution model for training rounds."""
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("federated_sessions.id"), nullable=False, index=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False, index=True)
    parameters_trained = Column(Integer, nullable=False)
    data_samples_used = Column(Integer, nullable=False)
    training_time_seconds = Column(Float, nullable=False)
    model_accuracy = Column(Float)
    loss_value = Column(Float)
    hardware_specs = Column(JSON)
    proof_of_work = Column(Text)
    status = Column(String(20), default="submitted", index=True)
    validation_hash = Column(String(128))
    rewards_calculated = Column(Float)
    submitted_at = Column(DateTime)
    validated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("FederatedSession", back_populates="contributions")
    node = relationship("Node", back_populates="contributions")
    reward_transactions = relationship("RewardTransaction", back_populates="contribution")


class RewardTransaction(Base):
    """Reward transaction model."""
    __tablename__ = "reward_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("federated_sessions.id"), nullable=False, index=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    drachma_amount = Column(Float, nullable=False)
    contribution_id = Column(Integer, ForeignKey("contributions.id"), index=True)
    status = Column(String(20), default="pending", index=True)
    blockchain_tx_hash = Column(String(128), index=True)
    blockchain_tx_status = Column(String(20))
    processed_at = Column(DateTime)
    distribution_proof = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contribution = relationship("Contribution", back_populates="reward_transactions")


class RevokedToken(Base):
    """Revoked token model for JWT token revocation."""
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_jti = Column(String(64), nullable=False, unique=True, index=True)
    token_type = Column(String(20), nullable=False, index=True)
    revoked_by = Column(String(64))
    revocation_reason = Column(String(100))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_revoked_tokens_jti_type', 'token_jti', 'token_type'),
        Index('idx_revoked_tokens_expires', 'expires_at'),
    )


class RefreshToken(Base):
    """Refresh token model for JWT refresh tokens."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_jti = Column(String(64), nullable=False, unique=True, index=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), index=True)
    user_id = Column(String(64), index=True)
    token_type = Column(String(20), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_refresh_tokens_node_revoked', 'node_id', 'is_revoked'),
        Index('idx_refresh_tokens_expires', 'expires_at'),
    )


class NodeRole(Base):
    """Node role model for role-based access control."""
    __tablename__ = "node_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    assigned_by = Column(String(64))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_node_roles_node_active', 'node_id', 'is_active'),
        Index('idx_node_roles_role', 'role'),
    )


class AccessLog(Base):
    """Access log model for API access tracking."""
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(64), ForeignKey("nodes.id"), index=True)
    user_id = Column(String(64), index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(64))
    response_time_ms = Column(Integer)
    error_message = Column(Text)
    permissions_checked = Column(JSON)
    token_jti = Column(String(64), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_access_logs_node_endpoint', 'node_id', 'endpoint'),
        Index('idx_access_logs_created_at', 'created_at'),
    )


class RateLimit(Base):
    """Rate limiting model for API protection."""
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(String(64), nullable=False, index=True)
    identifier_type = Column(String(20), nullable=False, index=True)  # 'node', 'user', 'ip'
    endpoint = Column(String(255), nullable=False, index=True)
    window_start = Column(Integer, nullable=False, index=True)  # Unix timestamp
    request_count = Column(Integer, default=0, nullable=False)
    window_seconds = Column(Integer, nullable=False)
    is_blocked = Column(Boolean, default=False, index=True)
    blocked_until = Column(Integer)  # Unix timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_rate_limits_identifier_endpoint', 'identifier', 'endpoint'),
        Index('idx_rate_limits_window', 'window_start'),
    )


class AuditLog(Base):
    """Audit log model for compliance and tracking."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    user_id = Column(String(64), index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    audit_proof = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_audit_entity_action', 'entity_type', 'action'),
        Index('idx_audit_user_timestamp', 'user_id', 'created_at'),
    )


# Create indexes for performance
Index('idx_nodes_status_reputation', Node.status, Node.reputation_score)
Index('idx_sessions_status_created', FederatedSession.status, FederatedSession.created_at)
Index('idx_contributions_session_round', Contribution.session_id, Contribution.round_number)
Index('idx_rewards_node_status', RewardTransaction.node_id, RewardTransaction.status)