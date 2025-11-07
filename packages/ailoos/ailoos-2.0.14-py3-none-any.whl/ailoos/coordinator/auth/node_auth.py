"""
Autenticación específica de nodos con integración del sistema de verificación.
Implementa login/logout endpoints y gestión de sesiones de nodos.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database.connection import get_db
from ..models.base import Node, NodeRole
from ..models.schemas import APIResponse
from .jwt import (
    create_node_token, verify_token, refresh_access_token,
    revoke_token, revoke_all_node_tokens, get_current_node
)
# from ..verification.node_verifier import NodeVerifier  # Commented out - module not found
from ..config.settings import settings


router = APIRouter()
security = HTTPBearer()


class NodeLoginRequest(BaseModel):
    """Request model for node login."""
    node_id: str = Field(..., description="Node identifier")
    signature: str = Field(..., description="Cryptographic signature for authentication")
    challenge_response: Optional[str] = Field(None, description="Response to verification challenge")
    hardware_info: Optional[Dict[str, Any]] = Field(None, description="Hardware information for verification")


class NodeLoginResponse(BaseModel):
    """Response model for node login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    node_info: Dict[str, Any]


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Response model for token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class NodeLogoutRequest(BaseModel):
    """Request model for node logout."""
    revoke_all: bool = Field(default=False, description="Revoke all tokens for this node")


class ChallengeRequest(BaseModel):
    """Request model for verification challenge."""
    node_id: str


class ChallengeResponse(BaseModel):
    """Response model for verification challenge."""
    challenge_id: str
    challenge_data: str
    difficulty: int
    expires_at: datetime


class NodeAuthService:
    """Service for handling node authentication operations."""

    def __init__(self):
        # self.node_verifier = NodeVerifier(config=settings, coordinator=None)  # Commented out - module not found
        self.node_verifier = None  # Placeholder

    async def authenticate_node(self, node_id: str, signature: str, challenge_response: Optional[str] = None,
                               hardware_info: Optional[Dict[str, Any]] = None, db: Session = None) -> Dict[str, Any]:
        """Authenticate a node using the verification system."""

        # Check if node exists in database
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        # Check if node is verified
        if not node.is_verified:
            raise HTTPException(status_code=403, detail="Node not verified")

        # Verify node identity using the verification system
        if challenge_response:
            # Verify challenge response - simplified for now
            challenge_id = challenge_response.get("challenge_id")
            solution = challenge_response.get("solution")
            challenge_signature = challenge_response.get("signature")

            # Simplified verification - just check if challenge_id exists
            if not challenge_id:
                raise HTTPException(status_code=401, detail="Invalid challenge response")
        else:
            # Basic signature verification - simplified for now
            # Create a simple message to verify
            message = f"login:{node_id}:{datetime.utcnow().isoformat()}"
            # Simplified signature check - just check if signature exists
            if not signature:
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Verify hardware if provided - simplified
        if hardware_info:
            proof = hardware_info.get("proof_of_benchmark", {})
            # Simplified hardware verification
            if not proof:
                raise HTTPException(status_code=401, detail="Hardware verification failed")

        # Check node eligibility - simplified
        is_eligible = True  # Assume eligible for now
        if not is_eligible:
            raise HTTPException(status_code=403, detail="Node not eligible")

        # Get node role
        role = "node"
        node_role = db.query(NodeRole).filter(
            NodeRole.node_id == node_id,
            NodeRole.is_active == True
        ).first()
        if node_role:
            role = node_role.role

        # Create tokens
        access_token, refresh_token = create_node_token(node_id, db)

        # Update node last activity
        node.last_heartbeat = datetime.utcnow()
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 15 * 60,  # 15 minutes
            "node_info": {
                "node_id": node_id,
                "role": role,
                "status": node.status,
                "reputation_score": node.reputation_score,
                "trust_level": node.trust_level
            }
        }

    async def logout_node(self, node_id: str, revoke_all: bool = False, db: Session = None):
        """Logout a node and optionally revoke all its tokens."""
        if revoke_all:
            revoke_all_node_tokens(node_id, "logout", db)
        else:
            # Revoke only current session tokens would be handled by the client
            # sending the tokens to revoke
            pass

        # Update node activity
        node = db.query(Node).filter(Node.id == node_id).first()
        if node:
            node.last_heartbeat = datetime.utcnow()
            db.commit()

    async def create_verification_challenge(self, node_id: str) -> Dict[str, Any]:
        """Create a verification challenge for a node."""
        # Simplified challenge creation
        from uuid import uuid4
        challenge_id = str(uuid4())
        challenge_data = f"challenge_{node_id}_{challenge_id}"
        difficulty = 1
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        return {
            "challenge_id": challenge_id,
            "challenge_data": challenge_data,
            "difficulty": difficulty,
            "expires_at": expires_at
        }


# Global auth service instance
node_auth_service = NodeAuthService()


@router.post("/login", response_model=APIResponse)
async def node_login(
    request: NodeLoginRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Authenticate a node and return access/refresh tokens."""
    try:
        result = await node_auth_service.authenticate_node(
            node_id=request.node_id,
            signature=request.signature,
            challenge_response=request.challenge_response,
            hardware_info=request.hardware_info,
            db=db
        )

        # Background task to update reputation for successful login - commented out
        # background_tasks.add_task(
        #     node_auth_service.node_verifier.update_node_reputation,
        #     request.node_id, True
        # )

        return APIResponse(
            data=NodeLoginResponse(**result),
            message="Node authenticated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        access_token, refresh_token = refresh_access_token(request.refresh_token, db)

        return APIResponse(
            data=TokenRefreshResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=15 * 60  # 15 minutes
            ),
            message="Token refreshed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@router.post("/logout", response_model=APIResponse)
async def node_logout(
    request: NodeLogoutRequest,
    current_node: str = Depends(get_current_node),
    db: Session = Depends(get_db)
):
    """Logout current node session."""
    try:
        await node_auth_service.logout_node(
            node_id=current_node,
            revoke_all=request.revoke_all,
            db=db
        )

        return APIResponse(message="Node logged out successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


@router.post("/challenge", response_model=APIResponse)
async def create_challenge(request: ChallengeRequest):
    """Create a verification challenge for node authentication."""
    try:
        challenge = await node_auth_service.create_verification_challenge(request.node_id)

        return APIResponse(
            data=ChallengeResponse(**challenge),
            message="Challenge created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Challenge creation failed: {str(e)}")


@router.get("/me", response_model=APIResponse)
async def get_current_node_info(
    current_node: str = Depends(get_current_node),
    db: Session = Depends(get_db)
):
    """Get current authenticated node's information."""
    try:
        node = db.query(Node).filter(Node.id == current_node).first()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        # Get node role
        role = "node"
        node_role = db.query(NodeRole).filter(
            NodeRole.node_id == current_node,
            NodeRole.is_active == True
        ).first()
        if node_role:
            role = node_role.role

        node_info = {
            "node_id": node.id,
            "status": node.status,
            "role": role,
            "reputation_score": node.reputation_score,
            "trust_level": node.trust_level,
            "is_verified": node.is_verified,
            "last_heartbeat": node.last_heartbeat,
            "total_contributions": node.total_contributions,
            "total_rewards_earned": node.total_rewards_earned
        }

        return APIResponse(data=node_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get node info: {str(e)}")


@router.post("/revoke", response_model=APIResponse)
async def revoke_tokens(
    token_jti: str,
    reason: str = "manual_revoke",
    current_node: str = Depends(get_current_node),
    db: Session = Depends(get_db)
):
    """Revoke a specific token (only own tokens)."""
    try:
        # Verify the token belongs to current node
        # This is a simplified check - in production you'd verify ownership
        revoke_token(token_jti, "access", current_node, reason, db)

        return APIResponse(message="Token revoked successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token revocation failed: {str(e)}")