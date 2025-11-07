"""
Ailoos SDK - Decentralized AI Training Platform
===============================================

A comprehensive SDK for federated learning and decentralized AI training.
Provides zero-configuration setup with embedded IPFS, P2P coordination,
automatic node discovery, and seamless model management.
"""

__version__ = "2.0.21"
__author__ = "Ailoos Technologies & Empoorio Ecosystem"
__license__ = "Proprietary"

# Core imports for easy access
from .setup.auto_setup import AutoSetup, get_embedded_ipfs, start_ipfs_daemon
from .coordinator.p2p_coordinator import P2PCoordinator, get_p2p_coordinator
from .discovery.node_discovery import NodeDiscovery, get_node_discovery
from .updates.auto_updates import UpdateManager, get_update_manager
from .infrastructure.ipfs_embedded import EmbeddedIPFS
from .models.registry import ModelRegistry

# Convenience functions for quick setup
def quick_setup(verbose: bool = True) -> bool:
    """
    Quick setup for Ailoos - configures everything automatically.

    Args:
        verbose: Whether to show detailed progress

    Returns:
        True if setup successful
    """
    setup = AutoSetup()
    return setup.setup_everything(verbose=verbose)

async def start_federated_node():
    """Start a federated learning node with all services."""
    from .setup.auto_setup import AutoSetup

    setup = AutoSetup()
    if setup.setup_everything():
        # Start all services
        from .discovery.node_discovery import start_node_discovery
        from .updates.auto_updates import schedule_automatic_updates

        await start_node_discovery()
        schedule_automatic_updates(enabled=True)

        print("🎯 Federated learning node started successfully!")
        print("Your node is now participating in the Ailoos network.")
        return True

    return False

# Export main classes
__all__ = [
    # Core classes
    'AutoSetup',
    'P2PCoordinator',
    'NodeDiscovery',
    'UpdateManager',
    'EmbeddedIPFS',
    'ModelRegistry',

    # Convenience functions
    'quick_setup',
    'start_federated_node',
    'get_embedded_ipfs',
    'get_p2p_coordinator',
    'get_node_discovery',
    'get_update_manager',
    'start_ipfs_daemon',
]