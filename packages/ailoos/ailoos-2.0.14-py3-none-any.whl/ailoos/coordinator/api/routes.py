"""
API routes for the coordinator service.
"""

from fastapi import APIRouter

from .endpoints import (
    nodes,
    sessions,
    models,
    rewards,
    # verification,  # Commented out - module not found
    # auditing,  # Commented out - module not found
    websocket
)
from ..auth.node_auth import router as auth_router


# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    nodes.router,
    prefix="/nodes",
    tags=["nodes"]
)

api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["sessions"]
)

api_router.include_router(
    models.router,
    prefix="/models",
    tags=["models"]
)

api_router.include_router(
    rewards.router,
    prefix="/rewards",
    tags=["rewards"]
)

# api_router.include_router(  # Commented out - modules not found
#     verification.router,
#     prefix="/verification",
#     tags=["verification"]
# )

# api_router.include_router(  # Commented out - modules not found
#     auditing.router,
#     prefix="/auditing",
#     tags=["auditing"]
# )

api_router.include_router(
    websocket.router,
    prefix="/websocket",
    tags=["websocket"]
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"]
)