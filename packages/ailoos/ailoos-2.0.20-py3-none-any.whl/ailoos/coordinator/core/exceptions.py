"""
Custom exceptions for the coordinator service.
"""

from typing import Optional, Dict, Any


class CoordinatorException(Exception):
    """Base exception for coordinator service."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NodeNotFoundError(CoordinatorException):
    """Exception raised when a node is not found."""

    def __init__(self, node_id: str):
        super().__init__(
            message=f"Node {node_id} not found",
            status_code=404,
            details={"node_id": node_id}
        )


class SessionNotFoundError(CoordinatorException):
    """Exception raised when a session is not found."""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session {session_id} not found",
            status_code=404,
            details={"session_id": session_id}
        )


class ModelNotFoundError(CoordinatorException):
    """Exception raised when a model is not found."""

    def __init__(self, model_id: str):
        super().__init__(
            message=f"Model {model_id} not found",
            status_code=404,
            details={"model_id": model_id}
        )


class ContributionNotFoundError(CoordinatorException):
    """Exception raised when a contribution is not found."""

    def __init__(self, contribution_id: int):
        super().__init__(
            message=f"Contribution {contribution_id} not found",
            status_code=404,
            details={"contribution_id": contribution_id}
        )


class RewardTransactionNotFoundError(CoordinatorException):
    """Exception raised when a reward transaction is not found."""

    def __init__(self, transaction_id: int):
        super().__init__(
            message=f"Reward transaction {transaction_id} not found",
            status_code=404,
            details={"transaction_id": transaction_id}
        )


class ValidationError(CoordinatorException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )


class AuthenticationError(CoordinatorException):
    """Exception raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401
        )


class AuthorizationError(CoordinatorException):
    """Exception raised for authorization errors."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=403
        )


class RateLimitError(CoordinatorException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=429
        )


class BlockchainError(CoordinatorException):
    """Exception raised for blockchain-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Blockchain error: {message}",
            status_code=500,
            details=details
        )


class AuditError(CoordinatorException):
    """Exception raised for audit-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Audit error: {message}",
            status_code=500,
            details=details
        )


class VerificationError(CoordinatorException):
    """Exception raised for verification-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Verification error: {message}",
            status_code=400,
            details=details
        )