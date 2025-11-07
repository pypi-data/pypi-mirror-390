"""
API endpoints for administrative operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...models.schemas import APIResponse, PaginatedResponse
from ...services.admin_service import AdminService
from ...auth.dependencies import get_current_admin
from ...auditing.zk_auditor import ZKAuditor
from ...core.config import Config


router = APIRouter()


@router.get("/stats", response_model=APIResponse)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Get comprehensive system statistics."""
    try:
        stats = await admin_service.get_system_stats(db=db)

        return APIResponse(
            success=True,
            message="System statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system statistics: {str(e)}")


@router.get("/audit-logs", response_model=PaginatedResponse)
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Get audit logs with filtering."""
    try:
        from datetime import datetime

        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        logs, total = await admin_service.get_audit_logs(
            db=db,
            skip=skip,
            limit=limit,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt
        )

        return PaginatedResponse(
            success=True,
            message="Audit logs retrieved successfully",
            data=logs,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit logs: {str(e)}")


@router.post("/audit-report", response_model=APIResponse)
async def generate_audit_report(
    audit_period_days: int = Query(30, ge=1, le=365, description="Audit period in days"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Generate comprehensive audit report."""
    try:
        report = await admin_service.generate_audit_report(
            db=db,
            audit_period_days=audit_period_days
        )

        return APIResponse(
            success=True,
            message="Audit report generated successfully",
            data=report
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audit report: {str(e)}")


@router.post("/nodes/{node_id}/manage", response_model=APIResponse)
async def manage_node_status(
    node_id: str,
    action: str = Query(..., description="Action: activate, suspend, ban, verify"),
    reason: str = Query(..., description="Reason for the action"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Manage node status (activate, suspend, ban, verify)."""
    try:
        result = await admin_service.manage_node_status(
            db=db,
            node_id=node_id,
            action=action,
            reason=reason,
            admin_user_id=current_admin["user_id"]
        )

        return APIResponse(
            success=True,
            message=f"Node {action} successful",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing node status: {str(e)}")


@router.post("/sessions/{session_id}/manage", response_model=APIResponse)
async def manage_session(
    session_id: str,
    action: str = Query(..., description="Action: pause, resume, cancel"),
    reason: str = Query(..., description="Reason for the action"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Manage session status (pause, resume, cancel)."""
    try:
        result = await admin_service.manage_session(
            db=db,
            session_id=session_id,
            action=action,
            reason=reason,
            admin_user_id=current_admin["user_id"]
        )

        return APIResponse(
            success=True,
            message=f"Session {action} successful",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing session: {str(e)}")


@router.get("/failed-operations", response_model=APIResponse)
async def get_failed_operations(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of failed operations to return"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Get list of failed operations for review."""
    try:
        failed_ops = await admin_service.get_failed_operations(db=db, limit=limit)

        return APIResponse(
            success=True,
            message="Failed operations retrieved successfully",
            data=failed_ops
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving failed operations: {str(e)}")


@router.post("/cleanup", response_model=APIResponse)
async def cleanup_old_data(
    older_than_days: int = Query(..., ge=30, le=3650, description="Clean data older than this many days"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
    admin_service: AdminService = Depends()
):
    """Clean up old data for performance and compliance."""
    try:
        result = await admin_service.cleanup_old_data(
            db=db,
            older_than_days=older_than_days,
            admin_user_id=current_admin["user_id"]
        )

        return APIResponse(
            success=True,
            message="Data cleanup plan generated successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during data cleanup: {str(e)}")


@router.get("/zk-audit/stats", response_model=APIResponse)
async def get_zk_audit_stats(
    admin_service: AdminService = Depends()
):
    """Get ZK auditing statistics."""
    try:
        stats = admin_service.zk_auditor.get_audit_stats()

        return APIResponse(
            success=True,
            message="ZK audit statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ZK audit statistics: {str(e)}")


@router.post("/zk-audit/network", response_model=APIResponse)
async def audit_network_state(
    node_stats: dict = Query(..., description="Node statistics for audit"),
    contribution_stats: dict = Query(..., description="Contribution statistics for audit"),
    admin_service: AdminService = Depends(),
    current_admin: dict = Depends(get_current_admin)
):
    """Perform ZK audit of network state."""
    try:
        audit = await admin_service.zk_auditor.audit_network_state(
            node_stats=node_stats,
            contribution_stats=contribution_stats
        )

        return APIResponse(
            success=True,
            message="Network state audit completed successfully",
            data={
                "audit_id": "network_audit",
                "total_nodes": audit.total_nodes,
                "active_nodes": audit.active_nodes,
                "network_reputation_avg": audit.network_reputation_avg,
                "zk_proofs_count": len(audit.zk_proofs)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error auditing network state: {str(e)}")


@router.post("/zk-audit/compliance", response_model=APIResponse)
async def audit_compliance(
    kyc_data: dict = Query(..., description="KYC compliance data"),
    privacy_data: dict = Query(..., description="Privacy compliance data"),
    transaction_data: dict = Query(..., description="Transaction transparency data"),
    admin_service: AdminService = Depends(),
    current_admin: dict = Depends(get_current_admin)
):
    """Perform ZK audit of regulatory compliance."""
    try:
        audit = await admin_service.zk_auditor.audit_compliance(
            kyc_data=kyc_data,
            privacy_data=privacy_data,
            transaction_data=transaction_data
        )

        return APIResponse(
            success=True,
            message="Compliance audit completed successfully",
            data={
                "audit_id": "compliance_audit",
                "regulations_checked": audit.regulations_checked,
                "compliance_rate": audit.compliance_rate,
                "violations_found": audit.violations_found,
                "zk_proofs_count": len(audit.zk_proofs)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error auditing compliance: {str(e)}")