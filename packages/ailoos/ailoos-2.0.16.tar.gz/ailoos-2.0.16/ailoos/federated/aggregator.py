"""
Federated learning aggregator implementing FedAvg algorithm.
Handles server-side aggregation of model weights from multiple nodes.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import torch

logger = logging.getLogger(__name__)


class FedAvgAggregator:
    """
    Federated Averaging (FedAvg) aggregator for decentralized learning.

    This class implements the server-side logic for:
    - Collecting model weights from training nodes
    - Weighted averaging based on data size
    - Global model updates
    - Privacy-preserving aggregation

    Example:
        aggregator = FedAvgAggregator()
        global_weights = await aggregator.aggregate(node_weights)
    """

    def __init__(self, min_nodes: int = 3, max_rounds: int = 100):
        """
        Initialize the aggregator.

        Args:
            min_nodes: Minimum nodes required for aggregation
            max_rounds: Maximum training rounds
        """
        self.min_nodes = min_nodes
        self.max_rounds = max_rounds
        self.current_round = 0
        self.global_model = None
        self.node_contributions: Dict[str, Dict] = {}

    async def initialize_global_model(self, model_template: Any) -> bool:
        """
        Initialize the global model with a template.

        Args:
            model_template: Template model to copy structure from

        Returns:
            True if initialized successfully
        """
        try:
            self.global_model = model_template
            logger.info("Global model initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize global model: {e}")
            return False

    async def collect_weights(
        self,
        node_id: str,
        weights: Dict[str, torch.Tensor],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Collect weights from a training node.

        Args:
            node_id: ID of the contributing node
            weights: Model weights from the node
            metadata: Training metadata (samples, accuracy, etc.)

        Returns:
            True if collected successfully
        """
        try:
            self.node_contributions[node_id] = {
                "weights": weights.copy(),
                "metadata": metadata,
                "timestamp": asyncio.get_event_loop().time()
            }
            logger.debug(f"Collected weights from node {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to collect weights from {node_id}: {e}")
            return False

    async def aggregate(self) -> Optional[Dict[str, torch.Tensor]]:
        """
        Perform FedAvg aggregation on collected weights.

        Returns:
            New global weights or None if aggregation failed
        """
        if len(self.node_contributions) < self.min_nodes:
            logger.warning(f"Insufficient nodes: {len(self.node_contributions)} < {self.min_nodes}")
            return None

        try:
            self.current_round += 1
            logger.info(f"Starting FedAvg aggregation for round {self.current_round}")

            # Calculate total samples for weighted averaging
            total_samples = sum(
                contrib["metadata"].get("samples_processed", 1)
                for contrib in self.node_contributions.values()
            )

            if total_samples == 0:
                logger.error("No samples processed by any node")
                return None

            # Initialize aggregated weights
            global_weights = {}
            first_node = next(iter(self.node_contributions.values()))
            for key in first_node["weights"].keys():
                global_weights[key] = torch.zeros_like(first_node["weights"][key])

            # Weighted average of weights
            for node_id, contribution in self.node_contributions.items():
                node_weights = contribution["weights"]
                node_samples = contribution["metadata"].get("samples_processed", 1)
                weight_factor = node_samples / total_samples

                for key in global_weights.keys():
                    if key in node_weights:
                        global_weights[key] += node_weights[key] * weight_factor

            # Update global model
            if self.global_model:
                self.global_model.load_state_dict(global_weights)

            # Clear contributions for next round
            self.node_contributions.clear()

            logger.info(f"FedAvg aggregation completed for round {self.current_round}")
            return global_weights

        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return None

    async def get_aggregation_stats(self) -> Dict[str, Any]:
        """Get statistics about the current aggregation round."""
        if not self.node_contributions:
            return {"status": "waiting", "nodes": 0}

        total_samples = sum(
            contrib["metadata"].get("samples_processed", 0)
            for contrib in self.node_contributions.values()
        )

        avg_accuracy = sum(
            contrib["metadata"].get("accuracy", 0)
            for contrib in self.node_contributions.values()
        ) / len(self.node_contributions)

        return {
            "round": self.current_round,
            "nodes_contributed": len(self.node_contributions),
            "total_samples": total_samples,
            "average_accuracy": avg_accuracy,
            "min_nodes_required": self.min_nodes,
            "status": "ready" if len(self.node_contributions) >= self.min_nodes else "waiting"
        }

    def get_node_contributions(self) -> Dict[str, Dict]:
        """Get information about node contributions."""
        return {
            node_id: {
                "samples": contrib["metadata"].get("samples_processed", 0),
                "accuracy": contrib["metadata"].get("accuracy", 0),
                "timestamp": contrib["timestamp"]
            }
            for node_id, contrib in self.node_contributions.items()
        }

    async def reset_round(self):
        """Reset for a new aggregation round."""
        self.node_contributions.clear()
        logger.info("Aggregation round reset")

    def is_ready_to_aggregate(self) -> bool:
        """Check if enough nodes have contributed for aggregation."""
        return len(self.node_contributions) >= self.min_nodes

    async def validate_contributions(self) -> List[str]:
        """
        Validate that all contributions are consistent.

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []

        if not self.node_contributions:
            errors.append("No contributions to validate")
            return errors

        # Check that all nodes have the same weight keys
        first_node = next(iter(self.node_contributions.values()))
        expected_keys = set(first_node["weights"].keys())

        for node_id, contribution in self.node_contributions.items():
            node_keys = set(contribution["weights"].keys())
            if node_keys != expected_keys:
                errors.append(f"Node {node_id} has mismatched weight keys")

        # Check for reasonable accuracy values
        for node_id, contribution in self.node_contributions.items():
            accuracy = contribution["metadata"].get("accuracy", 0)
            if not (0 <= accuracy <= 100):
                errors.append(f"Node {node_id} has invalid accuracy: {accuracy}")

        return errors

    @property
    def global_weights(self) -> Optional[Dict[str, torch.Tensor]]:
        """Get current global model weights."""
        return self.global_model.state_dict() if self.global_model else None