"""
Multi-region deployment and disaster recovery for Ailoos federated learning.
Provides global distribution, geo-aware routing, and automated failover.
"""

from .multi_region_manager import (
    MultiRegionManager,
    RegionConfig,
    GlobalLoadBalancer,
    CrossRegionReplication,
    DisasterRecoveryPlan
)

__all__ = [
    'MultiRegionManager',
    'RegionConfig',
    'GlobalLoadBalancer',
    'CrossRegionReplication',
    'DisasterRecoveryPlan'
]