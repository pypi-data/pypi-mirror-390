"""
Sistema de permisos y roles jerárquicos para Ailoos Coordinator.
Implementa control de acceso granular basado en roles con herencia jerárquica.
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


class Role(Enum):
    """Roles jerárquicos del sistema."""
    NODE = "node"
    VALIDATOR = "validator"
    ADMIN = "admin"


@dataclass
class Permission:
    """Representa un permiso individual."""
    resource: str
    action: str
    scope: Optional[str] = None

    def __str__(self) -> str:
        if self.scope:
            return f"{self.resource}:{self.action}:{self.scope}"
        return f"{self.resource}:{self.action}"

    @classmethod
    def from_string(cls, perm_str: str) -> 'Permission':
        """Crear permiso desde string."""
        parts = perm_str.split(':')
        if len(parts) == 2:
            return cls(parts[0], parts[1])
        elif len(parts) == 3:
            return cls(parts[0], parts[1], parts[2])
        else:
            raise ValueError(f"Formato de permiso inválido: {perm_str}")


class RolePermissions:
    """Gestor de permisos por rol con herencia jerárquica."""

    # Definición jerárquica de permisos por rol
    ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
        Role.NODE: {
            # Permisos básicos de nodo
            "node:read",
            "node:contribute",
            "session:join",
            "contribution:submit",
            "heartbeat:update",
            "self:read",
            "self:update"
        },
        Role.VALIDATOR: {
            # Hereda permisos de NODE
            "node:read",
            "node:contribute",
            "session:join",
            "contribution:submit",
            "heartbeat:update",
            "self:read",
            "self:update",
            # Permisos adicionales de validador
            "contribution:validate",
            "session:read",
            "model:read",
            "reward:read",
            "audit:read",
            "verification:read"
        },
        Role.ADMIN: {
            # Hereda permisos de VALIDATOR
            "node:read",
            "node:contribute",
            "session:join",
            "contribution:submit",
            "heartbeat:update",
            "self:read",
            "self:update",
            "contribution:validate",
            "session:read",
            "model:read",
            "reward:read",
            "audit:read",
            "verification:read",
            # Permisos administrativos completos
            "node:write",
            "node:delete",
            "node:manage",
            "session:create",
            "session:write",
            "session:delete",
            "session:manage",
            "model:create",
            "model:write",
            "model:delete",
            "model:manage",
            "reward:create",
            "reward:write",
            "reward:delete",
            "reward:manage",
            "audit:create",
            "audit:write",
            "audit:delete",
            "audit:manage",
            "verification:create",
            "verification:write",
            "verification:delete",
            "verification:manage",
            "system:read",
            "system:write",
            "system:delete",
            "system:manage",
            "admin:read",
            "admin:write",
            "admin:delete",
            "admin:manage"
        }
    }

    @classmethod
    def get_role_permissions(cls, role: Role) -> Set[str]:
        """Obtener todos los permisos para un rol incluyendo herencia."""
        return cls.ROLE_PERMISSIONS.get(role, set())

    @classmethod
    def get_all_permissions(cls) -> Set[str]:
        """Obtener todos los permisos definidos en el sistema."""
        all_perms = set()
        for perms in cls.ROLE_PERMISSIONS.values():
            all_perms.update(perms)
        return all_perms

    @classmethod
    def has_permission(cls, role: Role, permission: str) -> bool:
        """Verificar si un rol tiene un permiso específico."""
        role_perms = cls.get_role_permissions(role)
        return permission in role_perms

    @classmethod
    def get_role_hierarchy(cls) -> Dict[Role, List[Role]]:
        """Obtener jerarquía de roles (roles que heredan de cada uno)."""
        return {
            Role.NODE: [],
            Role.VALIDATOR: [Role.NODE],
            Role.ADMIN: [Role.VALIDATOR, Role.NODE]
        }

    @classmethod
    def get_inherited_permissions(cls, role: Role) -> Set[str]:
        """Obtener permisos heredados por un rol."""
        permissions = set()
        hierarchy = cls.get_role_hierarchy()

        # Agregar permisos del rol actual
        permissions.update(cls.ROLE_PERMISSIONS.get(role, set()))

        # Agregar permisos de roles padre
        for parent_role in hierarchy.get(role, []):
            permissions.update(cls.get_inherited_permissions(parent_role))

        return permissions


class PermissionChecker:
    """Utilidad para verificar permisos de usuarios/nodos."""

    def __init__(self, user_permissions: List[str]):
        self.user_permissions = set(user_permissions)

    def has_permission(self, required_permission: str) -> bool:
        """Verificar si el usuario tiene el permiso requerido."""
        return required_permission in self.user_permissions

    def has_any_permission(self, required_permissions: List[str]) -> bool:
        """Verificar si el usuario tiene al menos uno de los permisos requeridos."""
        return any(perm in self.user_permissions for perm in required_permissions)

    def has_all_permissions(self, required_permissions: List[str]) -> bool:
        """Verificar si el usuario tiene todos los permisos requeridos."""
        return all(perm in self.user_permissions for perm in required_permissions)

    def get_missing_permissions(self, required_permissions: List[str]) -> List[str]:
        """Obtener lista de permisos faltantes."""
        return [perm for perm in required_permissions if perm not in self.user_permissions]


# Constantes de permisos para facilitar el uso
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

VALIDATION_PERMISSIONS = {
    "read": ["contribution:validate", "verification:read"],
    "manage": ["contribution:validate", "verification:read", "verification:write"]
}

ADMIN_PERMISSIONS = {
    "read": ["admin:read", "system:read"],
    "manage": ["admin:read", "admin:write", "admin:delete", "system:manage"]
}

AUDIT_PERMISSIONS = {
    "read": ["audit:read"],
    "manage": ["audit:read", "audit:write", "audit:delete"]
}