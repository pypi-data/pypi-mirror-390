"""
Google Cloud Platform integration for Ailoos federated learning.
Provides enterprise-grade infrastructure components and deployment automation.
"""

from .gcp_integration import (
    GCPIntegration,
    GCPCluster,
    GCPStorageBucket,
    GCPDataset,
    GCPFunction
)

__all__ = [
    'GCPIntegration',
    'GCPCluster',
    'GCPStorageBucket',
    'GCPDataset',
    'GCPFunction'
]