"""
Authentication and authorization module for Ailoos Coordinator.
Provides JWT-based authentication, role-based access control, and security middleware.
"""

from .jwt import (
    create_access_token,
    create_refresh_token,
    create_node_token,
    verify_token,
    refresh_access_token,
    revoke_token,
    revoke_all_node_tokens,
    get_current_node,
    get_current_user,
    get_current_token_data,
    require_permissions,
    require_role
)

from .permissions import (
    Role,
    Permission,
    RolePermissions,
    PermissionChecker,
    NODE_PERMISSIONS,
    SESSION_PERMISSIONS,
    MODEL_PERMISSIONS,
    VALIDATION_PERMISSIONS,
    ADMIN_PERMISSIONS,
    AUDIT_PERMISSIONS
)

from .middleware import (
    AuthorizationMiddleware,
    PermissionMiddleware,
    require_endpoint_permissions,
    setup_security_middleware,
    cleanup_expired_tokens
)

from .node_auth import (
    NodeAuthService,
    node_auth_service
)

__all__ = [
    # JWT functions
    "create_access_token",
    "create_refresh_token",
    "create_node_token",
    "verify_token",
    "refresh_access_token",
    "revoke_token",
    "revoke_all_node_tokens",
    "get_current_node",
    "get_current_user",
    "get_current_token_data",
    "require_permissions",
    "require_role",

    # Permission classes
    "Role",
    "Permission",
    "RolePermissions",
    "PermissionChecker",
    "NODE_PERMISSIONS",
    "SESSION_PERMISSIONS",
    "MODEL_PERMISSIONS",
    "VALIDATION_PERMISSIONS",
    "ADMIN_PERMISSIONS",
    "AUDIT_PERMISSIONS",

    # Middleware
    "AuthorizationMiddleware",
    "PermissionMiddleware",
    "require_endpoint_permissions",
    "setup_security_middleware",
    "cleanup_expired_tokens",

    # Node auth service
    "NodeAuthService",
    "node_auth_service"
]