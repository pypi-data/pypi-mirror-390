"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class NodeBase(BaseModel):
    """Base node schema."""
    id: str = Field(..., description="Unique node identifier")
    public_key: str = Field(..., description="Node's public key for authentication")
    status: str = Field(default="registered", description="Node status")
    reputation_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Reputation score")
    trust_level: str = Field(default="basic", description="Trust level")
    hardware_specs: Optional[Dict[str, Any]] = Field(None, description="Hardware specifications")
    location: Optional[Dict[str, Any]] = Field(None, description="Geographic location")
    is_verified: bool = Field(default=False, description="Verification status")


class NodeCreate(NodeBase):
    """Schema for creating a new node."""
    # Inherits all fields from NodeBase for creation
    # Additional validation can be added here if needed


class NodeUpdate(BaseModel):
    """Schema for updating node information."""
    status: Optional[str] = None
    reputation_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    trust_level: Optional[str] = None
    hardware_specs: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    is_verified: Optional[bool] = None


class NodeResponse(NodeBase):
    """Schema for node response."""
    last_heartbeat: Optional[datetime] = None
    total_contributions: int = Field(default=0)
    total_rewards_earned: float = Field(default=0.0)
    verification_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class FederatedSessionBase(BaseModel):
    """Base federated session schema."""
    id: str = Field(..., description="Unique session identifier")
    name: str = Field(..., description="Session name")
    description: Optional[str] = Field(None, description="Session description")
    model_type: str = Field(..., description="Type of model being trained")
    dataset_info: Optional[Dict[str, Any]] = Field(None, description="Dataset metadata")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Training configuration")
    min_nodes: int = Field(default=3, ge=1, description="Minimum number of nodes")
    max_nodes: int = Field(default=50, ge=1, description="Maximum number of nodes")
    total_rounds: int = Field(..., ge=1, description="Total training rounds")


class FederatedSessionCreate(FederatedSessionBase):
    """Schema for creating a new federated session."""
    # Inherits all fields from FederatedSessionBase for creation
    # Additional validation can be added here if needed


class FederatedSessionUpdate(BaseModel):
    """Schema for updating session information."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    min_nodes: Optional[int] = Field(None, ge=1)
    max_nodes: Optional[int] = Field(None, ge=1)
    total_rounds: Optional[int] = Field(None, ge=1)


class FederatedSessionResponse(FederatedSessionBase):
    """Schema for session response."""
    status: str
    coordinator_node_id: Optional[str] = None
    current_round: int = Field(default=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SessionParticipantBase(BaseModel):
    """Base session participant schema."""
    session_id: str = Field(..., description="Session identifier")
    node_id: str = Field(..., description="Node identifier")
    status: str = Field(default="invited", description="Participation status")


class SessionParticipantResponse(SessionParticipantBase):
    """Schema for participant response."""
    joined_at: Optional[datetime] = None
    last_contribution_at: Optional[datetime] = None
    contributions_count: int = Field(default=0)
    rewards_earned: float = Field(default=0.0)
    performance_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ModelBase(BaseModel):
    """Base model schema."""
    id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    model_type: str = Field(..., description="Model type")
    architecture: Optional[Dict[str, Any]] = Field(None, description="Model architecture")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Training hyperparameters")
    is_public: bool = Field(default=False, description="Public availability")


class ModelCreate(ModelBase):
    """Schema for creating a new model."""
    session_id: Optional[str] = Field(None, description="Associated session")


class ModelUpdate(BaseModel):
    """Schema for updating model information."""
    name: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    architecture: Optional[Dict[str, Any]] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class ModelResponse(ModelBase):
    """Schema for model response."""
    session_id: Optional[str] = None
    status: str
    metrics: Optional[Dict[str, Any]] = None
    global_parameters_hash: Optional[str] = None
    storage_location: Optional[str] = None
    owner_node_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ContributionBase(BaseModel):
    """Base contribution schema."""
    session_id: str = Field(..., description="Session identifier")
    node_id: str = Field(..., description="Node identifier")
    round_number: int = Field(..., ge=0, description="Training round number")
    parameters_trained: int = Field(..., ge=0, description="Number of parameters trained")
    data_samples_used: int = Field(..., ge=0, description="Number of data samples used")
    training_time_seconds: float = Field(..., ge=0, description="Training time in seconds")
    model_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Model accuracy")
    loss_value: Optional[float] = Field(None, ge=0.0, description="Loss value")
    hardware_specs: Optional[Dict[str, Any]] = Field(None, description="Hardware specifications")
    proof_of_work: Optional[str] = Field(None, description="Proof of work or ZK proof")


class ContributionCreate(ContributionBase):
    """Schema for creating a new contribution."""
    # Inherits all fields from ContributionBase for creation
    # Additional validation can be added here if needed


class ContributionResponse(ContributionBase):
    """Schema for contribution response."""
    id: int
    status: str
    validation_hash: Optional[str] = None
    rewards_calculated: Optional[float] = None
    submitted_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class RewardTransactionBase(BaseModel):
    """Base reward transaction schema."""
    session_id: str = Field(..., description="Session identifier")
    node_id: str = Field(..., description="Node identifier")
    transaction_type: str = Field(..., description="Transaction type")
    drachma_amount: float = Field(..., ge=0, description="DRACMA amount")


class RewardTransactionResponse(RewardTransactionBase):
    """Schema for reward transaction response."""
    id: int
    contribution_id: Optional[int] = None
    status: str
    blockchain_tx_hash: Optional[str] = None
    blockchain_tx_status: Optional[str] = None
    processed_at: Optional[datetime] = None
    distribution_proof: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: int
    entity_type: str
    entity_id: str
    action: str
    user_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    audit_proof: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# API Response wrappers
class APIResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = Field(default=True, description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class PaginatedResponse(APIResponse):
    """Paginated API response."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class WebSocketMessage(BaseModel):
    """WebSocket message schema."""
    type: str = Field(..., description="Message type")
    session_id: Optional[str] = Field(None, description="Session identifier")
    node_id: Optional[str] = Field(None, description="Node identifier")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")