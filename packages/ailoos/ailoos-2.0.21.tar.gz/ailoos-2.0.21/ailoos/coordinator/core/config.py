"""
Configuration management for the coordinator service.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class CoordinatorConfig(BaseSettings):
    """Configuration settings for the coordinator service."""

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    api_cors_origins: List[str] = ["*"]

    # Database Settings
    database_url: str = "postgresql://user:password@localhost/ailoos_coordinator"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # JWT Settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_expiration_hours: int = 24

    # Coordinator Settings
    coordinator_node_timeout_seconds: int = 300  # 5 minutes
    coordinator_max_sessions_per_node: int = 5

    # Reward Settings
    reward_base_reward_per_param: float = 0.001
    reward_max_reward_per_session: float = 100.0
    reward_decay_factor: float = 0.95
    reward_session_pool_size: float = 1000.0

    # Verification Settings
    verification_min_reputation_score: float = 0.3
    verification_challenge_timeout: int = 300
    verification_cert_validity_days: int = 365

    # Audit Settings
    audit_interval_hours: int = 24
    audit_max_anomalies_threshold: float = 0.05
    audit_compliance_threshold: float = 0.95

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_limit: int = 10

    class Config:
        env_prefix = "AILOOS_"
        case_sensitive = False


# Global config instance
config = CoordinatorConfig()


def get_config() -> CoordinatorConfig:
    """Get the global configuration instance."""
    return config


def load_config_from_env() -> CoordinatorConfig:
    """Load configuration from environment variables."""
    return CoordinatorConfig()


# Backward compatibility
Config = CoordinatorConfig