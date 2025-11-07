"""
P2P Communication API
API de comunicación peer-to-peer para nodos federados
"""

from .p2p_network import P2PNetwork, P2PNode, create_p2p_network

__all__ = ['P2PNetwork', 'P2PNode', 'create_p2p_network']