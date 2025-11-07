"""
Main FastAPI application for the Ailoos Coordinator Service.
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config.settings import settings
from .database.connection import create_tables
from .api.routes import api_router
from .websocket.manager import websocket_router
from .websocket.message_broker import message_broker
from .websocket.heartbeat import heartbeat_manager
from .websocket.event_broadcaster import event_broadcaster
from .websocket.metrics_monitor import metrics_monitor
from .websocket.notification_service import notification_service
from .core.exceptions import CoordinatorException
from .auth.middleware import setup_security_middleware


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""

    # Create FastAPI app
    app = FastAPI(
        title="Ailoos Federated Coordinator",
        description="Central coordination service for federated learning sessions",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add trusted host middleware
    if not settings.api.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure for production
        )

    # Setup security middleware (authorization, audit, rate limiting)
    setup_security_middleware(app, exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"])

    # Global exception handler
    @app.exception_handler(CoordinatorException)
    async def coordinator_exception_handler(request: Request, exc: CoordinatorException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "details": exc.details
            }
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "ailoos-coordinator"}

    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(websocket_router, prefix="/ws")

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        # Create database tables - commented out to avoid PostgreSQL requirement
        # create_tables()
        print("Mock: Skipping database table creation")

        # Start message broker
        await message_broker.start()

        # Start heartbeat manager
        await heartbeat_manager.start()

        # Start event broadcaster
        await event_broadcaster.start()

        # Start metrics monitor
        await metrics_monitor.start()

        # Initialize notification service
        # Notification service is initialized on-demand

        print("All WebSocket services started successfully")

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        # Stop message broker
        await message_broker.stop()

        # Stop heartbeat manager
        await heartbeat_manager.stop()

        # Stop event broadcaster
        await event_broadcaster.stop()

        # Stop metrics monitor
        await metrics_monitor.stop()

        print("All WebSocket services stopped successfully")

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="info"
    )