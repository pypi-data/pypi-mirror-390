"""
Configuration settings for the Ailoos Coordinator Service.
Simplified version without complex dependencies.
"""

import os
from typing import Optional


class SimpleSettings:
    """Simplified settings without pydantic dependencies."""

    def __init__(self):
        # Database settings (simplified)
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "5432"))
        self.db_name = os.getenv("DB_NAME", "ailoos_coordinator")
        self.db_user = os.getenv("DB_USER", "ailoos_coordinator")
        self.db_password = os.getenv("DB_PASSWORD", "")

        # Redis settings (simplified)
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD")

        # Auth settings (simplified)
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-this-in-production-to-a-secure-random-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

        # API settings (simplified)
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # Coordinator settings (simplified)
        self.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
        self.min_nodes_per_session = int(os.getenv("MIN_NODES_PER_SESSION", "2"))
        self.max_nodes_per_session = int(os.getenv("MAX_NODES_PER_SESSION", "50"))
        self.heartbeat_interval_seconds = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "30"))
        self.node_timeout_seconds = int(os.getenv("NODE_TIMEOUT_SECONDS", "300"))

        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")

        # External services
        self.rewards_service_url = os.getenv("REWARDS_SERVICE_URL", "http://localhost:8001")
        self.verification_service_url = os.getenv("VERIFICATION_SERVICE_URL", "http://localhost:8002")
        self.auditing_service_url = os.getenv("AUDITING_SERVICE_URL", "http://localhost:8003")

    @property
    def database_url(self) -> str:
        """Simple database URL."""
        if self.db_password:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            return f"postgresql://{self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        """Simple Redis URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = SimpleSettings()