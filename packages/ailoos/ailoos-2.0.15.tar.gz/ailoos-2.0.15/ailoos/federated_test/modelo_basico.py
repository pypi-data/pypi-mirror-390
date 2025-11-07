"""
Modelo básico para pruebas de entrenamiento federado.
Un MLP simple para clasificación MNIST que se puede entrenar rápidamente.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any
import json
import os
from pathlib import Path


class TinyModel(nn.Module):
    """
    Modelo muy básico para pruebas federadas.
    Arquitectura: 784 → 64 → 32 → 10 (clasificación MNIST)
    """

    def __init__(self, input_size: int = 784, hidden1: int = 64, hidden2: int = 32, output_size: int = 10):
        super(TinyModel, self).__init__()
        self.layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_size, hidden1),
            nn.ReLU(),
            nn.Dropout(0.1),  # Regularización ligera
            nn.Linear(hidden1, hidden2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden2, output_size)
        )

        # Inicialización de pesos
        self._initialize_weights()

    def _initialize_weights(self):
        """Inicialización de pesos Xavier para mejor convergencia."""
        for layer in self.layers:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.layers(x)

    def get_num_parameters(self) -> int:
        """Retorna el número total de parámetros entrenables."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def save_model(self, path: str):
        """Guarda el modelo en formato PyTorch."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.state_dict(), path)

    def load_model(self, path: str):
        """Carga el modelo desde archivo."""
        if os.path.exists(path):
            self.load_state_dict(torch.load(path))
            return True
        return False

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo."""
        return {
            "architecture": "TinyMLP",
            "input_size": 784,
            "hidden_layers": [64, 32],
            "output_size": 10,
            "parameters": self.get_num_parameters(),
            "layers": len(list(self.parameters()))
        }


class FederatedMetrics:
    """
    Métricas para seguimiento del entrenamiento federado.
    """

    def __init__(self):
        self.round_metrics = []
        self.node_metrics = {}

    def add_round_metrics(self, round_num: int, accuracy: float, loss: float, time_taken: float):
        """Agrega métricas de una ronda de entrenamiento."""
        self.round_metrics.append({
            "round": round_num,
            "accuracy": accuracy,
            "loss": loss,
            "time": time_taken,
            "timestamp": torch.cuda.Event().elapsed_time() if torch.cuda.is_available() else 0
        })

    def add_node_metrics(self, node_id: str, metrics: Dict[str, Any]):
        """Agrega métricas específicas de un nodo."""
        if node_id not in self.node_metrics:
            self.node_metrics[node_id] = []
        self.node_metrics[node_id].append(metrics)

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen de todas las métricas."""
        if not self.round_metrics:
            return {"error": "No metrics available"}

        accuracies = [m["accuracy"] for m in self.round_metrics]
        losses = [m["loss"] for m in self.round_metrics]
        times = [m["time"] for m in self.round_metrics]

        return {
            "total_rounds": len(self.round_metrics),
            "final_accuracy": accuracies[-1] if accuracies else 0,
            "best_accuracy": max(accuracies) if accuracies else 0,
            "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
            "final_loss": losses[-1] if losses else 0,
            "best_loss": min(losses) if losses else 0,
            "total_time": sum(times),
            "avg_time_per_round": sum(times) / len(times) if times else 0,
            "active_nodes": len(self.node_metrics)
        }

    def save_metrics(self, path: str):
        """Guarda métricas en archivo JSON."""
        data = {
            "summary": self.get_summary(),
            "round_metrics": self.round_metrics,
            "node_metrics": self.node_metrics
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def load_metrics(self, path: str):
        """Carga métricas desde archivo JSON."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                self.round_metrics = data.get("round_metrics", [])
                self.node_metrics = data.get("node_metrics", {})
                return True
        return False


def create_model() -> TinyModel:
    """Factory function para crear una instancia del modelo."""
    return TinyModel()


def test_model_basic():
    """Función de prueba básica del modelo."""
    model = create_model()

    # Test con datos dummy
    x = torch.randn(32, 784)  # Batch de 32 imágenes MNIST
    y = model(x)

    assert y.shape == (32, 10), f"Output shape incorrect: {y.shape}"
    print("✅ Modelo básico funciona correctamente")
    print(f"📊 Parámetros totales: {model.get_num_parameters()}")
    print(f"🏗️ Arquitectura: {model.get_model_info()}")

    return model


if __name__ == "__main__":
    # Test básico
    model = test_model_basic()

    # Test de guardado/carga
    test_path = "./test_model.pth"
    model.save_model(test_path)
    print(f"💾 Modelo guardado en {test_path}")

    new_model = create_model()
    success = new_model.load_model(test_path)
    print(f"📂 Modelo cargado: {'✅' if success else '❌'}")

    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)