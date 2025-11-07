"""
Model registry and download system for Ailoos.
Provides interactive model selection and download functionality.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import tqdm


@dataclass
class ModelInfo:
    """Information about a downloadable model."""
    name: str
    version: str
    size_mb: float
    release_date: str
    description: str
    download_url: str
    ipfs_cid: Optional[str] = None
    checksum: Optional[str] = None
    category: str = "general"

    @property
    def display_name(self) -> str:
        """Formatted display name for the model."""
        return f"{self.name} #{self.version}"

    @property
    def size_str(self) -> str:
        """Human-readable size string."""
        if self.size_mb >= 1024:
            return ".2f"
        else:
            return ".2f"

    def __str__(self) -> str:
        return f"{self.display_name} {self.release_date} {self.size_str}"


class ModelRegistry:
    """
    Registry of available models for download.
    Provides interactive selection and download functionality.
    """

    def __init__(self):
        self.models_dir = Path.home() / ".ailoos" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.registry_url = "https://raw.githubusercontent.com/Empoorio/ailoos-models/main/registry.json"

        # Modelos disponibles (fallback si no se puede descargar registry)
        self.available_models = self._get_default_models()

    def _get_default_models(self) -> List[ModelInfo]:
        """Modelos por defecto disponibles."""
        return [
            ModelInfo(
                name="EmpoorioLM",
                version="4",
                size_mb=1890,
                release_date="november",
                description="Large language model for general AI tasks",
                download_url="https://github.com/empoorio/ailoos-models/releases/download/v1.0/empooriolm_4.pth",
                ipfs_cid="QmEmpoorioLM4CID",
                category="language"
            ),
            ModelInfo(
                name="EmpoorioLM Lite",
                version="3",
                size_mb=456.82,
                release_date="november",
                description="Lightweight version for resource-constrained devices",
                download_url="https://github.com/empoorio/ailoos-models/releases/download/v1.0/empooriolm_lite_3.pth",
                ipfs_cid="QmEmpoorioLMLite3CID",
                category="language"
            ),
            ModelInfo(
                name="EmpoorioLM Medical",
                version="3",
                size_mb=4220,
                release_date="november",
                description="Specialized model for medical text analysis",
                download_url="https://github.com/empoorio/ailoos-models/releases/download/v1.0/empooriolm_medical_3.pth",
                ipfs_cid="QmEmpoorioMedical3CID",
                category="medical"
            ),
            ModelInfo(
                name="EmpoorioLM BioTech",
                version="1",
                size_mb=1024,
                release_date="november",
                description="Biotechnology and research specialized model",
                download_url="https://github.com/empoorio/ailoos-models/releases/download/v1.0/empooriolm_biotech_1.pth",
                ipfs_cid="QmEmpoorioBioTech1CID",
                category="biotech"
            ),
            ModelInfo(
                name="TinyModel",
                version="1",
                size_mb=0.05,
                release_date="november",
                description="Tiny model for testing and federated learning",
                download_url="",  # Will be generated locally
                ipfs_cid="QmTinyModelV1CID",
                category="test"
            )
        ]

    def refresh_registry(self) -> bool:
        """Refresh model registry from remote source."""
        try:
            response = requests.get(self.registry_url, timeout=10)
            if response.status_code == 200:
                remote_models = response.json()
                self.available_models = [
                    ModelInfo(**model_data) for model_data in remote_models
                ]
                return True
        except Exception as e:
            print(f"⚠️ Could not refresh registry: {e}")
        return False

    def list_models(self, category: Optional[str] = None) -> List[ModelInfo]:
        """List available models, optionally filtered by category."""
        models = self.available_models
        if category:
            models = [m for m in models if m.category == category]
        return sorted(models, key=lambda x: (x.category, x.name, x.version))

    def is_downloaded(self, model: ModelInfo) -> bool:
        """Check if a model is already downloaded."""
        model_path = self.models_dir / f"{model.name.lower().replace(' ', '_')}_v{model.version}.pth"
        return model_path.exists()

    def get_downloaded_models(self) -> List[ModelInfo]:
        """Get list of downloaded models."""
        downloaded = []
        for model in self.available_models:
            if self.is_downloaded(model):
                downloaded.append(model)
        return downloaded

    def download_model(self, model: ModelInfo, show_progress: bool = True) -> Optional[Path]:
        """
        Download a model to the local cache.

        Args:
            model: ModelInfo object to download
            show_progress: Whether to show download progress

        Returns:
            Path to downloaded model file, or None if failed
        """
        model_filename = f"{model.name.lower().replace(' ', '_')}_v{model.version}.pth"
        model_path = self.models_dir / model_filename

        # Check if already downloaded
        if model_path.exists():
            print(f"✅ Model {model.display_name} already downloaded")
            return model_path

        # Special case for TinyModel - generate locally
        if model.name == "TinyModel":
            return self._generate_tiny_model(model, model_path)

        try:
            print(f"📥 Downloading {model.display_name} ({model.size_str})...")

            # Try primary download URL
            response = requests.get(model.download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(model_path, 'wb') as f:
                if show_progress and total_size > 0:
                    with tqdm.tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            # Verify checksum if available
            if model.checksum:
                if not self._verify_checksum(model_path, model.checksum):
                    print(f"❌ Checksum verification failed for {model.display_name}")
                    model_path.unlink()  # Delete corrupted file
                    return None

            print(f"✅ Successfully downloaded {model.display_name}")
            return model_path

        except Exception as e:
            print(f"❌ Failed to download {model.display_name}: {e}")
            if model_path.exists():
                model_path.unlink()  # Clean up partial download
            return None

    def _generate_tiny_model(self, model: ModelInfo, model_path: Path) -> Optional[Path]:
        """Generate TinyModel locally instead of downloading."""
        try:
            print(f"🏗️ Generating {model.display_name} locally...")

            # Import here to avoid circular imports
            from .tiny_model import create_model

            # Create and save the model
            tiny_model = create_model()
            tiny_model.save_model(str(model_path))

            print(f"✅ Successfully generated {model.display_name}")
            return model_path

        except Exception as e:
            print(f"❌ Failed to generate {model.display_name}: {e}")
            return None

    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_checksum

    def load_model(self, model_name: str, version: Optional[str] = None) -> Optional[Any]:
        """
        Load a downloaded model.

        Args:
            model_name: Name of the model
            version: Specific version (optional)

        Returns:
            Loaded model object, or None if not found
        """
        # Find the model
        model = None
        for m in self.available_models:
            if m.name == model_name and (version is None or m.version == version):
                model = m
                break

        if not model:
            print(f"❌ Model {model_name} v{version} not found in registry")
            return None

        # Check if downloaded
        if not self.is_downloaded(model):
            print(f"📥 Model {model.display_name} not downloaded. Downloading...")
            model_path = self.download_model(model)
            if not model_path:
                return None
        else:
            model_path = self.models_dir / f"{model.name.lower().replace(' ', '_')}_v{model.version}.pth"

        try:
            # Import torch here to avoid circular imports
            import torch
            from .tiny_model import TinyModel

            # For now, assume all models are TinyModel format
            # In production, this would load different model types
            loaded_model = TinyModel()
            state_dict = torch.load(model_path, map_location='cpu')
            loaded_model.load_state_dict(state_dict)

            print(f"✅ Loaded model {model.display_name}")
            return loaded_model

        except Exception as e:
            print(f"❌ Failed to load model {model.display_name}: {e}")
            return None

    def delete_model(self, model: ModelInfo) -> bool:
        """Delete a downloaded model."""
        model_path = self.models_dir / f"{model.name.lower().replace(' ', '_')}_v{model.version}.pth"
        if model_path.exists():
            model_path.unlink()
            print(f"🗑️ Deleted model {model.display_name}")
            return True
        else:
            print(f"❌ Model {model.display_name} not found")
            return False

    def get_cache_size(self) -> float:
        """Get total size of downloaded models in MB."""
        total_size = 0
        for model_file in self.models_dir.glob("*.pth"):
            total_size += model_file.stat().st_size
        return total_size / (1024 * 1024)  # Convert to MB

    def cleanup_cache(self, max_size_mb: float = 2048) -> float:
        """Clean up cache if it exceeds max size. Returns freed space in MB."""
        current_size = self.get_cache_size()
        if current_size <= max_size_mb:
            return 0

        # Simple cleanup: delete oldest models first
        # In production, this would be more sophisticated
        model_files = list(self.models_dir.glob("*.pth"))
        model_files.sort(key=lambda x: x.stat().st_mtime)  # Sort by modification time

        freed_space = 0
        for model_file in model_files:
            if current_size - freed_space <= max_size_mb:
                break
            file_size = model_file.stat().st_size / (1024 * 1024)
            model_file.unlink()
            freed_space += file_size

        print(f"🧹 Cleaned up {freed_space:.2f} MB from cache")
        return freed_space