"""
Federated learning trainer for decentralized AI training.
Implements the client-side federated learning logic.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
import torch
import torch.nn as nn
import torch.optim as optim

from ..core.node import Node
from ..core.model_manager import ModelManager

logger = logging.getLogger(__name__)


class FederatedTrainer:
    """
    Federated learning trainer for decentralized model training.

    This class handles:
    - Local model training on private data
    - Communication with aggregator nodes
    - Privacy-preserving weight sharing
    - Training coordination and synchronization

    Example:
        trainer = FederatedTrainer(model_name="empoorio-lm", rounds=10)
        await trainer.train()
    """

    def __init__(
        self,
        model_name: str = "empoorio-lm",
        rounds: int = 5,
        local_epochs: int = 3,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        coordinator_url: str = "http://localhost:5000",
        node_id: Optional[str] = None,
        data_loader: Optional[Callable] = None
    ):
        """
        Initialize federated trainer.

        Args:
            model_name: Name of the model to train
            rounds: Number of federated learning rounds
            local_epochs: Epochs to train locally per round
            batch_size: Training batch size
            learning_rate: Learning rate for optimizer
            coordinator_url: Coordinator API URL
            node_id: Node ID (auto-generated if None)
            data_loader: Function to load local training data
        """
        self.model_name = model_name
        self.rounds = rounds
        self.local_epochs = local_epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.coordinator_url = coordinator_url

        # Generate node ID if not provided
        if node_id is None:
            import uuid
            node_id = f"node_{uuid.uuid4().hex[:8]}"
        self.node_id = node_id

        # Initialize components
        self.node = Node(node_id, coordinator_url)
        self.model_manager = ModelManager(coordinator_url=coordinator_url)
        self.data_loader = data_loader or self._default_data_loader

        # Training state
        self.current_round = 0
        self.local_model = None
        self.global_weights = None
        self.training_stats = []

    def _default_data_loader(self):
        """Default synthetic data loader for demonstration."""
        # Generate synthetic data similar to training-demo.py
        for _ in range(10):  # 10 batches
            # MNIST-like data
            x = torch.randn(self.batch_size, 784)  # 28x28 flattened
            y = torch.randint(0, 10, (self.batch_size,))  # 10 classes
            yield x, y

    async def initialize(self) -> bool:
        """
        Initialize the trainer and join the network.

        Returns:
            True if initialization successful
        """
        try:
            # For testing/development, skip node registration if coordinator is not available
            try:
                node_started = await self.node.start()
                if not node_started:
                    logger.warning("Coordinator not available, running in offline mode")
            except Exception:
                logger.warning("Coordinator not available, running in offline mode")

            # Load model
            if not await self.model_manager.load_model(self.model_name):
                logger.error(f"Failed to load model {self.model_name}")
                return False

            # Initialize local model (simplified - would use actual model in real impl)
            self.local_model = self._create_model()
            self.global_weights = self.local_model.state_dict()

            logger.info(f"Federated trainer initialized for node {self.node_id}")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    def _create_model(self):
        """Create a simple model for demonstration."""
        # Simple MLP for MNIST-like classification
        model = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 10)
        )
        return model

    async def train_round(self, round_num: int) -> Dict[str, Any]:
        """
        Train for one federated learning round.

        Args:
            round_num: Current round number

        Returns:
            Training statistics for this round
        """
        logger.info(f"Starting training round {round_num}")

        # Load global weights
        self.local_model.load_state_dict(self.global_weights)

        # Setup optimizer and loss
        optimizer = optim.Adam(self.local_model.parameters(), lr=self.learning_rate)
        criterion = nn.CrossEntropyLoss()

        # Train locally
        start_time = time.time()
        total_loss = 0
        total_accuracy = 0
        samples_processed = 0

        self.local_model.train()
        for epoch in range(self.local_epochs):
            epoch_loss = 0
            epoch_correct = 0
            epoch_total = 0

            for batch_x, batch_y in self.data_loader():
                optimizer.zero_grad()

                outputs = self.local_model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                _, predicted = outputs.max(1)
                epoch_total += batch_y.size(0)
                epoch_correct += predicted.eq(batch_y).sum().item()

            # Average over batches
            epoch_accuracy = 100. * epoch_correct / epoch_total
            epoch_loss /= len(list(self.data_loader()))

            logger.debug(f"Epoch {epoch + 1}/{self.local_epochs}: Loss={epoch_loss:.4f}, Acc={epoch_accuracy:.1f}%")

            total_loss += epoch_loss
            total_accuracy += epoch_accuracy
            samples_processed += epoch_total

        # Calculate averages
        avg_loss = total_loss / self.local_epochs
        avg_accuracy = total_accuracy / self.local_epochs
        training_time = time.time() - start_time

        # Update training progress
        await self.node.update_training_progress(
            parameters_trained=int(samples_processed * 1000),  # Mock parameter count
            accuracy=avg_accuracy,
            loss=avg_loss,
            status="completed" if round_num == self.rounds else "running"
        )

        round_stats = {
            "round": round_num,
            "loss": avg_loss,
            "accuracy": avg_accuracy,
            "samples_processed": samples_processed,
            "training_time": training_time,
            "parameters_trained": samples_processed * 1000
        }

        logger.info(f"Round {round_num} completed: Acc={avg_accuracy:.1f}%, Loss={avg_loss:.4f}")
        return round_stats

    async def receive_global_weights(self) -> bool:
        """
        Receive updated global weights from aggregator.

        Returns:
            True if weights received successfully
        """
        try:
            # In real implementation, this would fetch from coordinator
            # For now, simulate receiving weights
            await asyncio.sleep(0.1)  # Simulate network delay

            # Mock: Keep current weights (in real impl, would receive from network)
            logger.debug("Received global weights")
            return True

        except Exception as e:
            logger.error(f"Failed to receive global weights: {e}")
            return False

    async def send_local_weights(self) -> bool:
        """
        Send local trained weights to aggregator.

        Returns:
            True if sent successfully
        """
        try:
            # In real implementation, this would send to coordinator
            # For now, simulate sending
            await asyncio.sleep(0.1)  # Simulate network delay

            local_weights = self.local_model.state_dict()
            # In real impl: send local_weights to coordinator

            logger.debug("Sent local weights to aggregator")
            return True

        except Exception as e:
            logger.error(f"Failed to send local weights: {e}")
            return False

    async def train(self) -> Dict[str, Any]:
        """
        Run complete federated training process.

        Returns:
            Complete training statistics
        """
        if not await self.initialize():
            raise RuntimeError("Failed to initialize federated trainer")

        logger.info(f"Starting federated training: {self.rounds} rounds, {self.local_epochs} local epochs each")

        all_stats = []

        for round_num in range(1, self.rounds + 1):
            self.current_round = round_num

            # Receive global weights
            if not await self.receive_global_weights():
                logger.warning(f"Failed to receive weights for round {round_num}")
                continue

            # Train locally
            round_stats = await self.train_round(round_num)
            all_stats.append(round_stats)

            # Send local weights
            if not await self.send_local_weights():
                logger.warning(f"Failed to send weights for round {round_num}")

        # Finalize training
        await self.node.stop()

        # Calculate final statistics
        final_stats = {
            "total_rounds": len(all_stats),
            "average_accuracy": sum(s["accuracy"] for s in all_stats) / len(all_stats),
            "average_loss": sum(s["loss"] for s in all_stats) / len(all_stats),
            "total_samples": sum(s["samples_processed"] for s in all_stats),
            "total_training_time": sum(s["training_time"] for s in all_stats),
            "round_stats": all_stats
        }

        logger.info(f"Federated training completed: {final_stats['average_accuracy']:.1f}% avg accuracy")
        return final_stats

    async def join_session(self, session_id: str) -> bool:
        """
        Join a federated training session.

        Connects to the coordinator, registers in the specified session,
        and obtains the initial state.

        Args:
            session_id: ID of the training session to join

        Returns:
            True if joined successfully and initial state obtained
        """
        try:
            # Join the training session via node
            if not await self.node.join_training_session(session_id):
                logger.error(f"Failed to join session {session_id}")
                return False

            # Receive initial global weights
            if not await self.receive_global_weights():
                logger.error("Failed to receive initial global weights")
                return False

            logger.info(f"Successfully joined session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error joining session: {e}")
            return False

    async def run_training_loop(self, max_rounds: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the federated training loop.

        Executes rounds of federated training after joining a session.

        Args:
            max_rounds: Maximum number of rounds to run (overrides self.rounds)

        Returns:
            Complete training statistics
        """
        rounds_to_run = max_rounds if max_rounds is not None else self.rounds
        logger.info(f"Starting federated training loop: {rounds_to_run} rounds")

        all_stats = []

        for round_num in range(1, rounds_to_run + 1):
            self.current_round = round_num

            # Receive global weights
            if not await self.receive_global_weights():
                logger.warning(f"Failed to receive weights for round {round_num}")
                continue

            # Train locally
            round_stats = await self.train_round(round_num)
            all_stats.append(round_stats)

            # Send local weights
            if not await self.send_local_weights():
                logger.warning(f"Failed to send weights for round {round_num}")

        # Calculate final statistics
        if all_stats:
            final_stats = {
                "total_rounds": len(all_stats),
                "average_accuracy": sum(s["accuracy"] for s in all_stats) / len(all_stats),
                "average_loss": sum(s["loss"] for s in all_stats) / len(all_stats),
                "total_samples": sum(s["samples_processed"] for s in all_stats),
                "total_training_time": sum(s["training_time"] for s in all_stats),
                "round_stats": all_stats
            }
        else:
            final_stats = {
                "total_rounds": 0,
                "average_accuracy": 0.0,
                "average_loss": 0.0,
                "total_samples": 0,
                "total_training_time": 0.0,
                "round_stats": []
            }

        logger.info(f"Training loop completed: {final_stats['average_accuracy']:.1f}% avg accuracy")
        return final_stats

    async def get_training_status(self) -> Dict[str, Any]:
        """Get current training status."""
        return {
            "node_id": self.node_id,
            "model_name": self.model_name,
            "current_round": self.current_round,
            "total_rounds": self.rounds,
            "is_training": self.current_round < self.rounds,
            "stats": self.training_stats
        }

    async def stop(self):
        """Stop training and cleanup."""
        await self.node.stop()
        logger.info("Federated trainer stopped")