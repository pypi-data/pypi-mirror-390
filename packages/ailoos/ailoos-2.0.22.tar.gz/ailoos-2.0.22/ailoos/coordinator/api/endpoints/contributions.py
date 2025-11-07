"""
API endpoints for contribution management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...models.schemas import (
    ContributionResponse, ContributionCreate, APIResponse, PaginatedResponse
)
from ...services.contribution_service import ContributionService
from ...auth.dependencies import get_current_node, get_current_admin
from ...verification.node_verifier import NodeVerifier
from ...core.exceptions import CoordinatorException


router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_contributions(
    skip: int = Query(0, ge=0, description="Number of contributions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of contributions to return"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    round_number: Optional[int] = Query(None, ge=0, description="Filter by round number"),
    status: Optional[str] = Query(None, description="Filter by contribution status"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """List contributions with optional filtering and pagination."""
    try:
        contributions, total = await ContributionService.list_contributions(
            db=db,
            skip=skip,
            limit=limit,
            session_id=session_id,
            node_id=node_id,
            round_number=round_number,
            status=status
        )

        return PaginatedResponse(
            success=True,
            message="Contributions retrieved successfully",
            data=contributions,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contributions: {str(e)}")


@router.post("/", response_model=APIResponse)
async def create_contribution(
    contribution_data: ContributionCreate,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node),
    node_verifier: NodeVerifier = Depends(lambda: None)  # Would be injected
):
    """Create a new contribution."""
    try:
        # Ensure the node_id matches the authenticated node
        if contribution_data.node_id != current_node["node_id"]:
            raise HTTPException(status_code=403, detail="Cannot create contribution for different node")

        contribution = await ContributionService.create_contribution(
            db=db,
            contribution_data=contribution_data,
            node_verifier=node_verifier
        )

        return APIResponse(
            success=True,
            message="Contribution created successfully",
            data=contribution
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating contribution: {str(e)}")


@router.get("/{contribution_id}", response_model=APIResponse)
async def get_contribution(
    contribution_id: int,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get a specific contribution by ID."""
    try:
        contribution = await ContributionService.get_contribution_by_id(
            db=db,
            contribution_id=contribution_id
        )

        return APIResponse(
            success=True,
            message="Contribution retrieved successfully",
            data=contribution
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contribution: {str(e)}")


@router.post("/{contribution_id}/validate", response_model=APIResponse)
async def validate_contribution(
    contribution_id: int,
    validation_hash: str = Query(..., description="Validation hash"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    node_verifier: NodeVerifier = Depends(lambda: None)
):
    """Validate a contribution."""
    try:
        contribution = await ContributionService.validate_contribution(
            db=db,
            contribution_id=contribution_id,
            validation_hash=validation_hash,
            node_verifier=node_verifier
        )

        return APIResponse(
            success=True,
            message="Contribution validated successfully",
            data=contribution
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating contribution: {str(e)}")


@router.put("/{contribution_id}/rewards", response_model=APIResponse)
async def calculate_contribution_rewards(
    contribution_id: int,
    reward_amount: float = Query(..., gt=0, description="Reward amount in DRACMA"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Calculate and set rewards for a contribution."""
    try:
        contribution = await ContributionService.calculate_contribution_rewards(
            db=db,
            contribution_id=contribution_id,
            reward_amount=reward_amount
        )

        return APIResponse(
            success=True,
            message="Contribution rewards calculated successfully",
            data=contribution
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating contribution rewards: {str(e)}")


@router.get("/session/{session_id}/round/{round_number}", response_model=APIResponse)
async def get_contributions_by_session_and_round(
    session_id: str,
    round_number: int,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get all contributions for a specific session round."""
    try:
        contributions = await ContributionService.get_contributions_by_session_and_round(
            db=db,
            session_id=session_id,
            round_number=round_number
        )

        return APIResponse(
            success=True,
            message="Round contributions retrieved successfully",
            data=contributions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving round contributions: {str(e)}")


@router.get("/node/{node_id}", response_model=APIResponse)
async def get_node_contributions(
    node_id: str,
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of contributions to return"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get contributions by a specific node."""
    try:
        # Check if requesting own contributions or admin access
        if node_id != current_node["node_id"] and "admin" not in current_node.get("roles", []):
            raise HTTPException(status_code=403, detail="Cannot access other node's contributions")

        contributions = await ContributionService.get_node_contributions(
            db=db,
            node_id=node_id,
            session_id=session_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            message="Node contributions retrieved successfully",
            data=contributions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving node contributions: {str(e)}")


@router.get("/stats/session/{session_id}", response_model=APIResponse)
async def get_contribution_stats(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get contribution statistics."""
    try:
        stats = await ContributionService.get_contribution_stats(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Contribution statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contribution statistics: {str(e)}")


@router.get("/my-contributions", response_model=APIResponse)
async def get_my_contributions(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of contributions to return"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get current node's contributions."""
    try:
        contributions = await ContributionService.get_node_contributions(
            db=db,
            node_id=current_node["node_id"],
            session_id=session_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            message="Your contributions retrieved successfully",
            data=contributions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving your contributions: {str(e)}")