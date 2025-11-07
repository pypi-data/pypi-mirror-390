"""
Federated learning modules for decentralized AI training.
"""

from .trainer import FederatedTrainer
from .aggregator import FedAvgAggregator

__all__ = ["FederatedTrainer", "FedAvgAggregator"]