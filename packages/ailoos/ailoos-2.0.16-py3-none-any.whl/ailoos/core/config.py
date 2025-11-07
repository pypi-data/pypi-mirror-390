#!/usr/bin/env python3
"""
Configuration management for Ailoos
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for Ailoos"""

    # API settings
    api_key: str = ""
    base_url: str = "http://localhost:5001"
    timeout: int = 30

    # Node settings
    node_id: str = ""
    coordinator_url: str = "http://localhost:5001"
    auto_start: bool = False

    # Federated learning settings
    default_model: str = "empoorio-lm"
    default_rounds: int = 5
    batch_size: int = 32
    learning_rate: float = 0.001

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/ailoos.log"

    # GCP settings
    gcp_project_id: str = "ailoos-ia"
    gcp_region: str = "us-central1"

    # Blockchain settings
    dracma_contract_address: str = "0x1234567890abcdef"
    eth_rpc_url: str = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"

    # Database settings
    mongodb_uri: str = "mongodb://localhost:27017/ailoos"
    redis_url: str = "redis://localhost:6379"

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration"""
        self.load_defaults()

        if config_file:
            self.load_from_file(config_file)

        self.load_from_env()

    def load_defaults(self):
        """Load default configuration values"""
        pass  # Already set in dataclass defaults

    def load_from_file(self, config_file: str):
        """Load configuration from YAML file"""
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                self._update_from_dict(data)

    def load_from_env(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'AILOOS_API_KEY': 'api_key',
            'AILOOS_BASE_URL': 'base_url',
            'AILOOS_NODE_ID': 'node_id',
            'AILOOS_COORDINATOR_URL': 'coordinator_url',
            'AILOOS_AUTO_START': 'auto_start',
            'AILOOS_DEFAULT_MODEL': 'default_model',
            'AILOOS_DEFAULT_ROUNDS': 'default_rounds',
            'AILOOS_LOG_LEVEL': 'log_level',
            'AILOOS_LOG_FILE': 'log_file',
            'GCP_PROJECT_ID': 'gcp_project_id',
            'GCP_REGION': 'gcp_region',
            'DRACMA_CONTRACT_ADDRESS': 'dracma_contract_address',
            'ETH_RPC_URL': 'eth_rpc_url',
            'MONGODB_URI': 'mongodb_uri',
            'REDIS_URL': 'redis_url'
        }

        for env_var, attr_name in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(getattr(self, attr_name), bool):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(getattr(self, attr_name), int):
                    value = int(value)
                elif isinstance(getattr(self, attr_name), float):
                    value = float(value)
                setattr(self, attr_name, value)

    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save_to_file(self, config_file: str):
        """Save configuration to YAML file"""
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                data[attr_name] = getattr(self, attr_name)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def get(self, key: str, default=None):
        """Get configuration value with default"""
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            attr_name: getattr(self, attr_name)
            for attr_name in dir(self)
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name))
        }


# Global configuration instance
_config_instance = None


def get_config(config_file: Optional[str] = None) -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_file)
    return _config_instance


def reload_config(config_file: Optional[str] = None) -> Config:
    """Reload global configuration instance"""
    global _config_instance
    _config_instance = Config(config_file)
    return _config_instance