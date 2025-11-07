"""
Middleware de autorización FastAPI para control de acceso basado en roles y permisos.
Implementa auditoría completa de accesos y rate limiting por nodo.
"""

import time
from typing import Callable, Optional
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from ..database.connection import SessionLocal
from ..models.base import AccessLog, RateLimit, RevokedToken
from .jwt import get_current_token_data, verify_token
from .permissions import PermissionChecker
from ..config.settings import settings


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Middleware para autorización y auditoría de accesos."""

    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/auth/login", "/auth/refresh", "/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Skip middleware for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        db = None
        try:
            # Get database session
            db = SessionLocal()

            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            token_data = None
            token_jti = None

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    token_data = verify_token(token, db)
                    token_jti = token_data.jti
                except HTTPException:
                    # Token invalid, but we'll still log the attempt
                    pass

            # Check rate limiting
            await self._check_rate_limit(request, token_data, db)

            # Process request
            response = await call_next(request)

            # Log access
            await self._log_access(
                request, response, token_data, token_jti,
                time.time() - start_time, db
            )

            return response

        except HTTPException as e:
            # Log failed access
            if db:
                await self._log_access(
                    request, JSONResponse(status_code=e.status_code, content={"detail": e.detail}),
                    token_data, token_jti, time.time() - start_time, db, error=str(e.detail)
                )
            raise e
        finally:
            if db:
                db.close()

    async def _check_rate_limit(self, request: Request, token_data: Optional[object], db: Session):
        """Check rate limiting for the request."""
        # Determine identifier (node_id or IP)
        identifier = None
        identifier_type = "ip"

        if token_data and hasattr(token_data, 'sub') and hasattr(token_data, 'type'):
            if token_data.type == "node":
                identifier = token_data.sub
                identifier_type = "node"
            elif token_data.type == "user":
                identifier = token_data.sub
                identifier_type = "user"

        if not identifier:
            # Fallback to IP address
            identifier = request.client.host if request.client else "unknown"
            identifier_type = "ip"

        # Get rate limit settings for this endpoint
        endpoint_limits = self._get_endpoint_rate_limits(request.url.path, request.method)

        for limit_config in endpoint_limits:
            window_seconds = limit_config["window_seconds"]
            max_requests = limit_config["max_requests"]

            # Check current window
            window_start = int(time.time() // window_seconds) * window_seconds

            rate_limit = db.query(RateLimit).filter(
                RateLimit.identifier == identifier,
                RateLimit.identifier_type == identifier_type,
                RateLimit.endpoint == request.url.path,
                RateLimit.window_start == window_start
            ).first()

            if rate_limit:
                if rate_limit.is_blocked:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded for {identifier_type}: {identifier}"
                    )
                rate_limit.request_count += 1
                if rate_limit.request_count > max_requests:
                    rate_limit.is_blocked = True
                    rate_limit.blocked_until = window_start + window_seconds
                    db.commit()
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded for {identifier_type}: {identifier}"
                    )
            else:
                # Create new rate limit record
                rate_limit = RateLimit(
                    identifier=identifier,
                    identifier_type=identifier_type,
                    endpoint=request.url.path,
                    window_start=window_start,
                    request_count=1,
                    window_seconds=window_seconds
                )
                db.add(rate_limit)

            db.commit()

    def _get_endpoint_rate_limits(self, path: str, method: str) -> list:
        """Get rate limiting configuration for endpoint."""
        # Default rate limits
        default_limits = [{
            "window_seconds": 60,  # 1 minute
            "max_requests": settings.api.rate_limit_requests
        }]

        # Stricter limits for sensitive endpoints
        sensitive_endpoints = {
            "/auth/login": [{"window_seconds": 300, "max_requests": 5}],  # 5 attempts per 5 minutes
            "/auth/refresh": [{"window_seconds": 60, "max_requests": 10}],
            "/nodes": [{"window_seconds": 60, "max_requests": 100}],
            "/sessions": [{"window_seconds": 60, "max_requests": 50}],
        }

        return sensitive_endpoints.get(path, default_limits)

    async def _log_access(self, request: Request, response, token_data: Optional[object],
                         token_jti: Optional[str], response_time: float, db: Session,
                         error: Optional[str] = None):
        """Log access attempt to database."""
        try:
            # Extract request info
            user_agent = request.headers.get("User-Agent", "")
            ip_address = request.client.host if request.client else None

            # Extract token info
            node_id = None
            user_id = None
            permissions_checked = None

            if token_data and hasattr(token_data, 'sub') and hasattr(token_data, 'type'):
                if token_data.type == "node":
                    node_id = token_data.sub
                elif token_data.type == "user":
                    user_id = token_data.sub

                if hasattr(token_data, 'permissions'):
                    permissions_checked = token_data.permissions

            # Create access log
            access_log = AccessLog(
                node_id=node_id,
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=getattr(response, 'status_code', 500),
                ip_address=ip_address,
                user_agent=user_agent[:500],  # Truncate if too long
                request_id=getattr(request.state, 'request_id', None),
                response_time_ms=int(response_time * 1000),
                error_message=error[:500] if error else None,
                permissions_checked=permissions_checked,
                token_jti=token_jti
            )

            db.add(access_log)
            db.commit()

        except Exception as e:
            # Don't let logging errors break the request
            print(f"Error logging access: {e}")


class PermissionMiddleware:
    """Middleware for checking permissions on specific routes."""

    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions

    async def __call__(self, request: Request, token_data: object = Depends(get_current_token_data)):
        """Check if the current user has required permissions."""
        if not hasattr(token_data, 'permissions') or not token_data.permissions:
            raise HTTPException(
                status_code=403,
                detail="No permissions found in token"
            )

        checker = PermissionChecker(token_data.permissions)

        if not checker.has_any_permission(self.required_permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {self.required_permissions}"
            )

        # Add permission info to request state for logging
        request.state.permissions_checked = self.required_permissions
        request.state.user_permissions = token_data.permissions

        return token_data


def require_endpoint_permissions(required_permissions: list):
    """Decorator factory for requiring permissions on endpoints."""
    async def permission_dependency(token_data: object = Depends(get_current_token_data)):
        if not hasattr(token_data, 'permissions') or not token_data.permissions:
            raise HTTPException(
                status_code=403,
                detail="No permissions found in token"
            )

        checker = PermissionChecker(token_data.permissions)

        if not checker.has_any_permission(required_permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_permissions}"
            )

        return token_data

    return permission_dependency


# Utility functions for middleware setup
def setup_security_middleware(app, exclude_paths: Optional[list] = None):
    """Setup security middleware for FastAPI app."""
    app.add_middleware(AuthorizationMiddleware, exclude_paths=exclude_paths)


def cleanup_expired_tokens(db: Session):
    """Clean up expired revoked tokens and rate limits (to be called periodically)."""
    from datetime import datetime

    # Remove expired revoked tokens (keep for 30 days after expiration)
    expired_revoked = db.query(RevokedToken).filter(
        RevokedToken.expires_at < datetime.utcnow()
    ).delete()

    # Remove old rate limit records (older than 1 hour)
    old_rate_limits = db.query(RateLimit).filter(
        RateLimit.window_start < (time.time() - 3600)
    ).delete()

    db.commit()

    return expired_revoked, old_rate_limits