"""
Dataset reducido para pruebas iniciales de entrenamiento federado.
Carga un subconjunto pequeño de MNIST para entrenamiento rápido.
"""

import torch
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Dataset, Subset, DataLoader
import numpy as np
from typing import Tuple


class TinyMNISTDataset(Dataset):
    """
    Dataset reducido de MNIST para pruebas federadas.
    Solo carga un subconjunto pequeño para entrenamiento rápido.
    """

    def __init__(self, num_samples: int = 1000, train: bool = True, download: bool = True):
        """
        Args:
            num_samples: Número de muestras a seleccionar
            train: Si usar conjunto de entrenamiento
            download: Si descargar el dataset
        """
        self.num_samples = min(num_samples, 60000 if train else 10000)  # Límite MNIST

        # Transformaciones estándar de MNIST
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

        # Cargar dataset completo
        self.full_dataset = torchvision.datasets.MNIST(
            root='./data',
            train=train,
            download=download,
            transform=transform
        )

        # Seleccionar índices aleatorios para subconjunto
        np.random.seed(42)  # Seed para reproducibilidad
        indices = np.random.choice(len(self.full_dataset), self.num_samples, replace=False)
        self.indices = indices

        # Crear subset
        self.dataset = Subset(self.full_dataset, indices)

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.dataset[idx]

    def get_class_distribution(self) -> dict:
        """Retorna distribución de clases en el dataset."""
        labels = []
        for _, label in self.dataset:
            # label puede ser tensor o int
            if hasattr(label, 'item'):
                labels.append(label.item())
            else:
                labels.append(int(label))

        distribution = {}
        for i in range(10):  # MNIST tiene 10 clases (0-9)
            distribution[i] = labels.count(i)

        return distribution

    def get_info(self) -> dict:
        """Retorna información del dataset."""
        return {
            "name": "TinyMNIST",
            "total_samples": len(self),
            "input_shape": (1, 28, 28),  # Canales, alto, ancho
            "num_classes": 10,
            "class_distribution": self.get_class_distribution()
        }


def create_federated_datasets(
    num_nodes: int = 2,
    samples_per_node: int = 500,
    train: bool = True
) -> list:
    """
    Crea datasets separados para cada nodo en el entrenamiento federado.
    Cada nodo obtiene un subconjunto diferente de datos.

    Args:
        num_nodes: Número de nodos participantes
        samples_per_node: Muestras por nodo
        train: Si usar datos de entrenamiento

    Returns:
        Lista de datasets, uno por nodo
    """
    datasets = []

    for node_id in range(num_nodes):
        # Seed diferente por nodo para obtener datos diferentes
        np.random.seed(42 + node_id)

        dataset = TinyMNISTDataset(
            num_samples=samples_per_node,
            train=train,
            download=(node_id == 0)  # Solo el primer nodo descarga
        )

        datasets.append(dataset)

        print(f"📊 Nodo {node_id}: {len(dataset)} muestras")
        print(f"   Distribución: {dataset.get_class_distribution()}")

    return datasets


def create_data_loaders(
    datasets: list,
    batch_size: int = 32,
    shuffle: bool = True
) -> list:
    """
    Crea DataLoaders para cada dataset de nodo.

    Args:
        datasets: Lista de datasets por nodo
        batch_size: Tamaño del batch
        shuffle: Si mezclar los datos

    Returns:
        Lista de DataLoaders
    """
    loaders = []

    for i, dataset in enumerate(datasets):
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=0  # Para compatibilidad con macOS
        )
        loaders.append(loader)
        print(f"📦 Nodo {i}: {len(loader)} batches de {batch_size} muestras")

    return loaders


def test_dataset():
    """Función de prueba del dataset reducido."""
    print("🧪 Probando TinyMNIST Dataset...")

    # Crear dataset pequeño
    dataset = TinyMNISTDataset(num_samples=100, train=True)
    print(f"✅ Dataset creado: {len(dataset)} muestras")

    # Verificar distribución
    dist = dataset.get_class_distribution()
    print(f"📊 Distribución de clases: {dist}")

    # Verificar forma de datos
    sample_data, sample_label = dataset[0]
    print(f"📏 Forma de datos: {sample_data.shape}")
    print(f"🏷️ Etiqueta de ejemplo: {sample_label}")

    # Verificar info
    info = dataset.get_info()
    print(f"ℹ️ Información del dataset: {info}")

    return dataset


def test_federated_setup():
    """Prueba la configuración federada con múltiples nodos."""
    print("\n🌐 Probando configuración federada...")

    # Crear datasets para 2 nodos
    datasets = create_federated_datasets(num_nodes=2, samples_per_node=200)

    # Crear data loaders
    loaders = create_data_loaders(datasets, batch_size=32)

    # Verificar que los datasets son diferentes
    sample_0 = datasets[0][0][1]  # Primera etiqueta del nodo 0
    sample_1 = datasets[1][0][1]  # Primera etiqueta del nodo 1

    print(f"🏷️ Primera etiqueta Nodo 0: {sample_0}")
    print(f"🏷️ Primera etiqueta Nodo 1: {sample_1}")

    # Verificar batches
    for i, loader in enumerate(loaders):
        batch_data, batch_labels = next(iter(loader))
        print(f"📦 Nodo {i} - Batch shape: {batch_data.shape}, Labels: {batch_labels[:5].tolist()}")

    print("✅ Configuración federada funcionando correctamente")
    return datasets, loaders


if __name__ == "__main__":
    # Ejecutar pruebas
    dataset = test_dataset()
    datasets, loaders = test_federated_setup()

    print("\n🎉 Todas las pruebas pasaron exitosamente!")
    print("📝 El dataset reducido está listo para entrenamiento federado.")