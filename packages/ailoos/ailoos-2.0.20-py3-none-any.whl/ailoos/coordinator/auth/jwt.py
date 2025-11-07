"""
JWT authentication and authorization utilities with refresh tokens and revocation.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import jwt
from fastapi import HTTPException, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..database.connection import get_db
from ..models.base import RevokedToken, RefreshToken, NodeRole


security = HTTPBearer()


class TokenData(BaseModel):
    """JWT token payload data."""
    sub: str  # Subject (node_id or user_id)
    type: str  # Token type: 'node' or 'user'
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for uniqueness
    role: Optional[str] = None  # User role for hierarchical permissions
    permissions: Optional[list] = None  # Explicit permissions


class NodeTokenData(TokenData):
    """Node-specific token data."""
    permissions: list = ["node:read", "node:contribute"]


def create_access_token(subject: str, token_type: str = "node", role: Optional[str] = None,
                       permissions: Optional[list] = None, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with short expiration (15 minutes)."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)  # Short-lived access tokens

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
    }

    # Add role and permissions for hierarchical access control
    if role:
        to_encode["role"] = role
    if permissions:
        to_encode["permissions"] = permissions
    elif token_type == "node":
        # Default node permissions
        from .permissions import RolePermissions, Role
        if role:
            try:
                role_enum = Role(role.upper())
                to_encode["permissions"] = list(RolePermissions.get_inherited_permissions(role_enum))
            except ValueError:
                to_encode["permissions"] = ["node:read", "node:contribute"]
        else:
            to_encode["permissions"] = ["node:read", "node:contribute"]

    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(subject: str, token_type: str = "node", expires_delta: Optional[timedelta] = None,
                        db: Optional[Session] = None) -> Tuple[str, str]:
    """Create JWT refresh token with long expiration and store in database."""
    if expires_delta is None:
        expires_delta = timedelta(days=30)  # Long-lived refresh tokens

    expire = datetime.utcnow() + expires_delta
    jti = str(uuid.uuid4())

    to_encode = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": jti,
        "token_type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm
    )

    # Store refresh token in database for revocation capability
    if db:
        refresh_token = RefreshToken(
            token_jti=jti,
            node_id=subject if token_type == "node" else None,
            user_id=subject if token_type == "user" else None,
            token_type=token_type,
            expires_at=expire
        )
        db.add(refresh_token)
        db.commit()

    return encoded_jwt, jti


def create_node_token(node_id: str, db: Optional[Session] = None) -> Tuple[str, str]:
    """Create JWT access and refresh tokens for node authentication."""
    # Get node role from database
    role = "node"  # Default role
    if db:
        node_role = db.query(NodeRole).filter(
            NodeRole.node_id == node_id,
            NodeRole.is_active == True
        ).first()
        if node_role:
            role = node_role.role

    # Create access token
    access_token = create_access_token(node_id, "node", role)

    # Create refresh token
    refresh_token, refresh_jti = create_refresh_token(node_id, "node", db=db)

    return access_token, refresh_token


def create_user_token(user_id: str, permissions: list = None, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token for user authentication."""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.auth.jwt_expiration_hours)

    if permissions is None:
        permissions = ["admin:read"]

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": user_id,
        "type": "user",
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "permissions": permissions
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str, db: Optional[Session] = None) -> TokenData:
    """Verify and decode JWT token with revocation check."""
    try:
        payload = jwt.decode(
            token,
            settings.auth.jwt_secret_key,
            algorithms=[settings.auth.jwt_algorithm]
        )

        # Check if token is revoked
        if db and payload.get("jti"):
            revoked = db.query(RevokedToken).filter(
                RevokedToken.token_jti == payload["jti"]
            ).first()
            if revoked:
                raise HTTPException(status_code=401, detail="Token has been revoked")

        # Convert timestamp to datetime
        payload["exp"] = datetime.fromtimestamp(payload["exp"])
        payload["iat"] = datetime.fromtimestamp(payload["iat"])

        return TokenData(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def refresh_access_token(refresh_token: str, db: Session) -> Tuple[str, str]:
    """Refresh access token using valid refresh token."""
    try:
        # Verify refresh token
        payload = jwt.decode(
            refresh_token,
            settings.auth.jwt_secret_key,
            algorithms=[settings.auth.jwt_algorithm]
        )

        if payload.get("token_type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        # Check if refresh token exists and is not revoked
        stored_token = db.query(RefreshToken).filter(
            RefreshToken.token_jti == payload["jti"],
            RefreshToken.is_revoked == False
        ).first()

        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh token not found or revoked")

        # Check expiration
        if datetime.utcnow() > stored_token.expires_at:
            raise HTTPException(status_code=401, detail="Refresh token has expired")

        # Update last used timestamp
        stored_token.last_used_at = datetime.utcnow()
        db.commit()

        # Create new access token
        subject = payload["sub"]
        token_type = payload["type"]
        role = payload.get("role")

        new_access_token = create_access_token(subject, token_type, role)

        return new_access_token, refresh_token

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def revoke_token(token_jti: str, token_type: str, revoked_by: Optional[str] = None,
                reason: str = "logout", db: Session = None):
    """Revoke a token by adding it to the revoked tokens list."""
    if not db:
        return

    # Check if already revoked
    existing = db.query(RevokedToken).filter(RevokedToken.token_jti == token_jti).first()
    if existing:
        return

    # Add to revoked tokens
    revoked_token = RevokedToken(
        token_jti=token_jti,
        token_type=token_type,
        revoked_by=revoked_by,
        revocation_reason=reason,
        expires_at=datetime.utcnow() + timedelta(days=30)  # Keep revocation record for 30 days
    )
    db.add(revoked_token)
    db.commit()


def revoke_all_node_tokens(node_id: str, reason: str = "security", db: Session = None):
    """Revoke all tokens for a specific node."""
    if not db:
        return

    # Revoke all refresh tokens for the node
    refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.node_id == node_id,
        RefreshToken.is_revoked == False
    ).all()

    for token in refresh_tokens:
        token.is_revoked = True
        revoke_token(token.token_jti, token.token_type, reason, db=db)

    db.commit()


def get_current_node(credentials: HTTPAuthorizationCredentials = Security(security),
                    db: Session = Depends(get_db)) -> str:
    """Get current authenticated node ID with database verification."""
    token_data = verify_token(credentials.credentials, db)

    if token_data.type != "node":
        raise HTTPException(status_code=403, detail="Node authentication required")

    return token_data.sub


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security),
                    db: Session = Depends(get_db)) -> TokenData:
    """Get current authenticated user with database verification."""
    token_data = verify_token(credentials.credentials, db)

    if token_data.type != "user":
        raise HTTPException(status_code=403, detail="User authentication required")

    return token_data


def get_current_token_data(credentials: HTTPAuthorizationCredentials = Security(security),
                          db: Session = Depends(get_db)) -> TokenData:
    """Get current token data with full verification."""
    return verify_token(credentials.credentials, db)


def check_permissions(required_permissions: list, user_permissions: list) -> bool:
    """Check if user has required permissions."""
    return any(perm in user_permissions for perm in required_permissions)


def require_permissions(required_permissions: list):
    """Dependency to require specific permissions."""
    def permission_checker(token_data: TokenData = Depends(get_current_token_data)):
        user_permissions = token_data.permissions or []
        if not check_permissions(required_permissions, user_permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_permissions}"
            )
        return token_data
    return permission_checker


def require_role(minimum_role: str):
    """Dependency to require minimum role level."""
    from .permissions import Role

    def role_checker(token_data: TokenData = Depends(get_current_token_data)):
        if not token_data.role:
            raise HTTPException(status_code=403, detail="Role-based access required")

        try:
            user_role = Role(token_data.role.upper())
            required_role = Role(minimum_role.upper())

            # Simple hierarchy check (admin > validator > node)
            role_hierarchy = {Role.NODE: 1, Role.VALIDATOR: 2, Role.ADMIN: 3}
            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient role level. Required: {minimum_role}, Current: {token_data.role}"
                )
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid role")

        return token_data
    return role_checker


# Permission constants
NODE_PERMISSIONS = {
    "read": ["node:read"],
    "contribute": ["node:contribute"],
    "manage": ["node:read", "node:write", "node:delete"]
}

SESSION_PERMISSIONS = {
    "read": ["session:read"],
    "create": ["session:create"],
    "manage": ["session:read", "session:write", "session:delete"],
    "join": ["session:join"]
}

MODEL_PERMISSIONS = {
    "read": ["model:read"],
    "create": ["model:create"],
    "manage": ["model:read", "model:write", "model:delete"]
}

ADMIN_PERMISSIONS = {
    "full": ["admin:read", "admin:write", "admin:delete", "system:manage"]
}