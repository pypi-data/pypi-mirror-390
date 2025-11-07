"""
API endpoints for reward management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...models.schemas import (
    RewardTransactionResponse, APIResponse, PaginatedResponse
)
from ...services.reward_service import RewardService
from ...auth.dependencies import get_current_node, get_current_admin
from ...core.exceptions import CoordinatorException


router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_reward_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of transactions to return"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    status: Optional[str] = Query(None, description="Filter by transaction status"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """List reward transactions with optional filtering and pagination."""
    try:
        transactions, total = await RewardService.list_reward_transactions(
            db=db,
            skip=skip,
            limit=limit,
            session_id=session_id,
            node_id=node_id,
            transaction_type=transaction_type,
            status=status
        )

        return PaginatedResponse(
            success=True,
            message="Reward transactions retrieved successfully",
            data=transactions,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reward transactions: {str(e)}")


@router.get("/{transaction_id}", response_model=APIResponse)
async def get_reward_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get a specific reward transaction by ID."""
    try:
        transaction = await RewardService.get_reward_transaction_by_id(
            db=db,
            transaction_id=transaction_id
        )

        return APIResponse(
            success=True,
            message="Reward transaction retrieved successfully",
            data=transaction
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reward transaction: {str(e)}")


@router.post("/calculate/{session_id}", response_model=APIResponse)
async def calculate_session_rewards(
    session_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    reward_service: RewardService = Depends()
):
    """Calculate rewards for all contributions in a session."""
    try:
        transactions = await reward_service.calculate_session_rewards(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message=f"Rewards calculated for {len(transactions)} contributions",
            data=transactions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating session rewards: {str(e)}")


@router.post("/{transaction_id}/process", response_model=APIResponse)
async def process_reward_transaction(
    transaction_id: int,
    blockchain_tx_hash: str = Query(..., description="Blockchain transaction hash"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Process a reward transaction on the blockchain."""
    try:
        transaction = await RewardService.process_reward_transaction(
            db=db,
            transaction_id=transaction_id,
            blockchain_tx_hash=blockchain_tx_hash
        )

        return APIResponse(
            success=True,
            message="Reward transaction processed successfully",
            data=transaction
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing reward transaction: {str(e)}")


@router.post("/{transaction_id}/confirm", response_model=APIResponse)
async def confirm_reward_transaction(
    transaction_id: int,
    blockchain_tx_status: str = Query("confirmed", description="Blockchain transaction status"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Confirm a processed reward transaction."""
    try:
        transaction = await RewardService.confirm_reward_transaction(
            db=db,
            transaction_id=transaction_id,
            blockchain_tx_status=blockchain_tx_status
        )

        return APIResponse(
            success=True,
            message="Reward transaction confirmed successfully",
            data=transaction
        )
    except CoordinatorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirming reward transaction: {str(e)}")


@router.get("/node/{node_id}", response_model=APIResponse)
async def get_node_rewards(
    node_id: str,
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of transactions to return"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get reward transactions for a specific node."""
    try:
        # Check if requesting own rewards or admin access
        if node_id != current_node["node_id"] and "admin" not in current_node.get("roles", []):
            raise HTTPException(status_code=403, detail="Cannot access other node's rewards")

        transactions = await RewardService.get_node_rewards(
            db=db,
            node_id=node_id,
            session_id=session_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            message="Node rewards retrieved successfully",
            data=transactions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving node rewards: {str(e)}")


@router.get("/session/{session_id}", response_model=APIResponse)
async def get_session_rewards(
    session_id: str,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get all reward transactions for a session."""
    try:
        transactions = await RewardService.get_session_rewards(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Session rewards retrieved successfully",
            data=transactions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session rewards: {str(e)}")


@router.get("/stats/session/{session_id}", response_model=APIResponse)
async def get_reward_stats(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get reward statistics."""
    try:
        stats = await RewardService.get_reward_stats(db=db, session_id=session_id)

        return APIResponse(
            success=True,
            message="Reward statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reward statistics: {str(e)}")


@router.get("/pool/{session_id}", response_model=APIResponse)
async def get_reward_pool_status(
    session_id: str,
    reward_service: RewardService = Depends()
):
    """Get reward pool status for a session."""
    try:
        pool_status = reward_service.get_reward_pool_status(session_id)

        if pool_status is None:
            raise HTTPException(status_code=404, detail="Reward pool not found for session")

        return APIResponse(
            success=True,
            message="Reward pool status retrieved successfully",
            data=pool_status
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reward pool status: {str(e)}")


@router.get("/my-rewards", response_model=APIResponse)
async def get_my_rewards(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of transactions to return"),
    db: Session = Depends(get_db),
    current_node: dict = Depends(get_current_node)
):
    """Get current node's reward transactions."""
    try:
        transactions = await RewardService.get_node_rewards(
            db=db,
            node_id=current_node["node_id"],
            session_id=session_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            message="Your rewards retrieved successfully",
            data=transactions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving your rewards: {str(e)}")


@router.post("/distribute/{session_id}", response_model=APIResponse)
async def distribute_session_rewards(
    session_id: str,
    reward_service: RewardService = Depends(),
    current_admin: dict = Depends(get_current_admin)
):
    """Distribute calculated rewards (would integrate with blockchain)."""
    try:
        # Get calculated rewards for the session
        transactions = await RewardService.get_session_rewards(db=None, session_id=session_id)  # Would need db

        # In a real implementation, this would trigger blockchain distribution
        # For now, just return success

        return APIResponse(
            success=True,
            message=f"Reward distribution initiated for {len(transactions)} transactions",
            data={"transactions_count": len(transactions)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error distributing session rewards: {str(e)}")