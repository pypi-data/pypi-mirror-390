"""
Ailoos - Sovereign Decentralized AI Library
==========================================

Ailoos is a comprehensive library for decentralized AI training and inference,
specifically designed for training EmpoorioLM and other models across a global
network of nodes using federated learning.

Key Features:
- Federated Learning with FedAvg algorithm
- Decentralized node management
- EmpoorioLM model training and inference
- Easy-to-use APIs for developers
- VS Code integration support
- CLI tools for quick node activation

Example Usage:
    from ailoos import Node, FederatedTrainer

    # Create and start a training node
    node = Node(node_id="my_node", hardware_info={"gpu": "RTX 3080"})
    node.start()

    # Join federated training
    trainer = FederatedTrainer(model="empoorio-lm", rounds=10)
    trainer.train()
"""

__version__ = "2.0.12"
__author__ = "Empoorio"
__description__ = "Sovereign Decentralized AI Library for EmpoorioLM Training"

from .core import Node, ModelManager
from .federated import FederatedTrainer, FedAvgAggregator
from .utils import setup_logging, get_hardware_info

__all__ = [
    "Node",
    "ModelManager",
    "FederatedTrainer",
    "FedAvgAggregator",
    "setup_logging",
    "get_hardware_info"
]