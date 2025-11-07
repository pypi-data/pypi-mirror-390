"""
Authentication and authorization dependencies for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta

from ..core.config import Config


security = HTTPBearer()
config = Config()


def get_current_node(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated node."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=["HS256"])

        # Check token expiration
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        return {
            "node_id": payload.get("node_id"),
            "public_key": payload.get("public_key"),
            "trust_level": payload.get("trust_level", "basic"),
            "roles": payload.get("roles", [])
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user (alias for get_current_admin)."""
    return get_current_admin(credentials)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated admin user."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=["HS256"])

        # Check token expiration
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        # Check if user has admin role
        roles = payload.get("roles", [])
        if "admin" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )

        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "roles": roles,
            "permissions": payload.get("permissions", [])
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_node_token(node_id: str, public_key: str, trust_level: str = "basic") -> str:
    """Create JWT token for a node."""
    expiration = datetime.utcnow() + timedelta(hours=config.jwt_expiration_hours)

    payload = {
        "node_id": node_id,
        "public_key": public_key,
        "trust_level": trust_level,
        "roles": ["node"],
        "exp": expiration.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "iss": "ailoos-coordinator"
    }

    return jwt.encode(payload, config.jwt_secret_key, algorithm="HS256")


def create_admin_token(user_id: str, username: str, roles: list, permissions: list) -> str:
    """Create JWT token for an admin user."""
    expiration = datetime.utcnow() + timedelta(hours=config.jwt_expiration_hours)

    payload = {
        "user_id": user_id,
        "username": username,
        "roles": roles,
        "permissions": permissions,
        "exp": expiration.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "iss": "ailoos-coordinator"
    }

    return jwt.encode(payload, config.jwt_secret_key, algorithm="HS256")


def require_admin(user: dict = Depends(get_current_admin)) -> dict:
    """Require admin role dependency."""
    return user


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=["HS256"])

        # Check expiration
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            return None

        return payload
    except:
        return None