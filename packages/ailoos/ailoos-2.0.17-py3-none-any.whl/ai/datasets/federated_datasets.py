#!/usr/bin/env python3
"""
Federated Datasets System
Sistema de datasets federados para aprendizaje distribuido sin compartir datos privados
"""

import asyncio
import json
import logging
import os
import sys
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
# from fastapi import UploadFile, File  # Commented out to avoid multipart dependency
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
# import aiofiles  # Commented out - using standard files for compatibility
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/federated_datasets.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class DatasetMetadata(BaseModel):
    """Dataset metadata"""
    dataset_id: str
    name: str
    description: str
    data_type: str  # "text", "image", "tabular", "multimodal"
    total_samples: int
    features: List[str]
    labels: Optional[List[str]]
    privacy_level: str  # "public", "federated", "private"
    license: str
    created_at: str
    updated_at: str
    checksum: str
    size_bytes: int

class DatasetRequest(BaseModel):
    """Dataset creation/update request"""
    name: str
    description: str
    data_type: str
    privacy_level: str = "federated"
    license: str = "MIT"

class DatasetPartition(BaseModel):
    """Dataset partition for federated learning"""
    partition_id: str
    node_id: str
    dataset_id: str
    sample_indices: List[int]
    checksum: str
    created_at: str
    size_bytes: int

class PrivacyBudgetRequest(BaseModel):
    """Privacy budget request for differential privacy"""
    dataset_id: str
    epsilon: float = 1.0
    delta: float = 1e-5
    mechanism: str = "gaussian"  # "gaussian", "laplace", "exponential"

class DatasetQuery(BaseModel):
    """Query for dataset access"""
    dataset_id: str
    node_id: str
    query_type: str  # "metadata", "partition", "statistics"
    privacy_budget: Optional[PrivacyBudgetRequest]

class DatasetStatistics(BaseModel):
    """Dataset statistics with privacy"""
    total_samples: int
    feature_distributions: Dict[str, Any]  # Privatized distributions
    label_distribution: Optional[Dict[str, Any]]
    privacy_parameters: Dict[str, float]
    computed_at: str

# Global state
datasets: Dict[str, Dict[str, Any]] = {}
dataset_partitions: Dict[str, List[Dict[str, Any]]] = {}
dataset_statistics: Dict[str, Dict[str, Any]] = {}
active_queries: Set[str] = set()

# Dataset Manager class
class FederatedDatasetManager:
    """Manager for federated datasets with privacy preservation"""

    def __init__(self, storage_path: str = "data/federated_datasets"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.datasets = {}
        self.partitions = {}
        self.statistics = {}

    async def create_dataset(self, request: DatasetRequest, files=None) -> str:
        """Create a new federated dataset"""
        dataset_id = secrets.token_hex(16)

        # Create dataset directory
        dataset_path = self.storage_path / dataset_id
        dataset_path.mkdir(exist_ok=True)

        total_size = 0
        file_info = []

        # Save uploaded files (if provided)
        if files:
            for file in files:
                file_path = dataset_path / file.filename
                content = await file.read()

                # Use synchronous file writing for compatibility
                with open(file_path, 'wb') as f:
                    f.write(content)
                    total_size += len(content)

                file_info.append({
                    "filename": file.filename,
                    "size": len(content),
                    "path": str(file_path)
                })
        else:
            # Create sample dataset for testing
            sample_data = [
                {"text": "Sample text for federated learning", "label": "positive"},
                {"text": "Another example of training data", "label": "neutral"},
                {"text": "More sample content for the dataset", "label": "positive"}
            ]
            sample_file = dataset_path / "sample_data.jsonl"
            with open(sample_file, 'w', encoding='utf-8') as f:
                for item in sample_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    total_size += len(json.dumps(item, ensure_ascii=False)) + 1

            file_info.append({
                "filename": "sample_data.jsonl",
                "size": total_size,
                "path": str(sample_file)
            })

        # Calculate checksum
        checksum = self._calculate_dataset_checksum(dataset_path)

        # Extract basic metadata (simplified)
        features, labels, sample_count = await self._analyze_dataset_files(dataset_path, request.data_type)

        # Create metadata
        metadata = {
            "dataset_id": dataset_id,
            "name": request.name,
            "description": request.description,
            "data_type": request.data_type,
            "total_samples": sample_count,
            "features": features,
            "labels": labels,
            "privacy_level": request.privacy_level,
            "license": request.license,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "checksum": checksum,
            "size_bytes": total_size,
            "files": file_info,
            "status": "active"
        }

        # Store metadata
        self.datasets[dataset_id] = metadata

        # Save metadata to disk
        metadata_file = dataset_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Dataset created: {dataset_id} ({request.name})")
        return dataset_id

    async def get_dataset_metadata(self, dataset_id: str) -> DatasetMetadata:
        """Get dataset metadata"""
        if dataset_id not in self.datasets:
            raise HTTPException(status_code=404, detail="Dataset not found")

        metadata = self.datasets[dataset_id]
        return DatasetMetadata(**metadata)

    async def create_partitions(self, dataset_id: str, num_partitions: int, privacy_budget: Optional[PrivacyBudgetRequest] = None) -> List[DatasetPartition]:
        """Create federated partitions for a dataset"""
        if dataset_id not in self.datasets:
            raise HTTPException(status_code=404, detail="Dataset not found")

        dataset = self.datasets[dataset_id]
        total_samples = dataset["total_samples"]

        if total_samples < num_partitions:
            raise HTTPException(status_code=400, detail="Not enough samples for requested partitions")

        # Create partitions (simplified - equal distribution)
        samples_per_partition = total_samples // num_partitions
        partitions = []

        for i in range(num_partitions):
            start_idx = i * samples_per_partition
            end_idx = start_idx + samples_per_partition if i < num_partitions - 1 else total_samples

            partition_id = f"{dataset_id}_part_{i}"
            sample_indices = list(range(start_idx, end_idx))

            # Calculate partition checksum
            partition_data = {
                "dataset_id": dataset_id,
                "partition_id": partition_id,
                "sample_indices": sample_indices,
                "privacy_budget": privacy_budget.dict() if privacy_budget else None
            }
            checksum = hashlib.sha256(json.dumps(partition_data, sort_keys=True).encode()).hexdigest()

            partition = DatasetPartition(
                partition_id=partition_id,
                node_id="",  # Will be assigned when requested
                dataset_id=dataset_id,
                sample_indices=sample_indices,
                checksum=checksum,
                created_at=datetime.now().isoformat(),
                size_bytes=len(json.dumps(sample_indices))  # Simplified
            )

            partitions.append(partition)

        # Store partitions
        self.partitions[dataset_id] = [p.dict() for p in partitions]

        logger.info(f"✅ Created {num_partitions} partitions for dataset {dataset_id}")
        return partitions

    async def request_partition(self, dataset_id: str, node_id: str, partition_index: int = 0) -> DatasetPartition:
        """Request access to a dataset partition"""
        if dataset_id not in self.partitions:
            # Create partitions if they don't exist
            await self.create_partitions(dataset_id, 10)  # Default 10 partitions

        available_partitions = self.partitions[dataset_id]
        if partition_index >= len(available_partitions):
            raise HTTPException(status_code=400, detail="Partition index out of range")

        partition_data = available_partitions[partition_index].copy()
        partition_data["node_id"] = node_id

        partition = DatasetPartition(**partition_data)

        logger.info(f"✅ Partition {partition.partition_id} assigned to node {node_id}")
        return partition

    async def get_dataset_statistics(self, dataset_id: str, privacy_budget: Optional[PrivacyBudgetRequest] = None) -> DatasetStatistics:
        """Get dataset statistics with privacy guarantees"""
        if dataset_id not in self.datasets:
            raise HTTPException(status_code=404, detail="Dataset not found")

        dataset = self.datasets[dataset_id]

        # Calculate privatized statistics
        if privacy_budget:
            # Apply differential privacy
            statistics = await self._compute_private_statistics(dataset, privacy_budget)
        else:
            # Public statistics (no privacy)
            statistics = await self._compute_public_statistics(dataset)

        return DatasetStatistics(**statistics)

    async def _analyze_dataset_files(self, dataset_path: Path, data_type: str) -> Tuple[List[str], Optional[List[str]], int]:
        """Analyze dataset files to extract metadata"""
        # Simplified analysis - in production would parse actual data files
        if data_type == "text":
            # Assume JSONL format for text data
            jsonl_files = list(dataset_path.glob("*.jsonl"))
            if jsonl_files:
                # Count lines in first file as sample count
                with open(jsonl_files[0], 'r') as f:
                    sample_count = sum(1 for _ in f)

                # Extract features from first sample
                with open(jsonl_files[0], 'r') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        try:
                            sample = json.loads(first_line)
                            features = list(sample.keys())
                            labels = None  # Assume unsupervised or will be determined later
                        except:
                            features = ["text"]
                            labels = None
                    else:
                        features = ["text"]
                        labels = None
            else:
                features = ["text"]
                labels = None
                sample_count = 0
        else:
            # Generic analysis for other data types
            features = ["data"]
            labels = None
            sample_count = 1000  # Placeholder

        return features, labels, sample_count

    def _calculate_dataset_checksum(self, dataset_path: Path) -> str:
        """Calculate SHA256 checksum of dataset files"""
        sha256 = hashlib.sha256()

        # Sort files for consistent checksum
        files = sorted(dataset_path.glob("*"))
        for file_path in files:
            if file_path.is_file() and file_path.name != "metadata.json":
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        sha256.update(chunk)

        return sha256.hexdigest()

    async def _compute_private_statistics(self, dataset: Dict[str, Any], privacy_budget: PrivacyBudgetRequest) -> Dict[str, Any]:
        """Compute statistics with differential privacy"""
        # Simplified DP implementation
        epsilon = privacy_budget.epsilon
        delta = privacy_budget.delta

        # Add noise to statistics
        total_samples = dataset["total_samples"]
        noisy_count = total_samples + np.random.laplace(0, 1/epsilon)

        # Simulate feature distributions with noise
        features = dataset.get("features", [])
        feature_distributions = {}
        for feature in features:
            # Add Laplace noise to distribution
            base_dist = {"mean": 0.5, "std": 0.2}  # Placeholder
            noisy_dist = {
                "mean": base_dist["mean"] + np.random.laplace(0, 1/epsilon),
                "std": base_dist["std"] + np.random.laplace(0, 1/epsilon)
            }
            feature_distributions[feature] = noisy_dist

        return {
            "total_samples": max(0, int(noisy_count)),
            "feature_distributions": feature_distributions,
            "label_distribution": None,
            "privacy_parameters": {
                "epsilon": epsilon,
                "delta": delta,
                "mechanism": privacy_budget.mechanism
            },
            "computed_at": datetime.now().isoformat()
        }

    async def _compute_public_statistics(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Compute public statistics without privacy"""
        return {
            "total_samples": dataset["total_samples"],
            "feature_distributions": {feature: {"mean": 0.5, "std": 0.2} for feature in dataset.get("features", [])},
            "label_distribution": None,
            "privacy_parameters": {"epsilon": float('inf'), "delta": 0.0, "mechanism": "none"},
            "computed_at": datetime.now().isoformat()
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Federated Datasets Server...")
    yield
    logger.info("🛑 Shutting down Federated Datasets Server...")

# Create FastAPI app
app = FastAPI(
    title="Federated Datasets Server",
    description="Sistema de datasets federados con preservación de privacidad",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dataset manager
dataset_manager = FederatedDatasetManager()

@app.post("/api/datasets/create")
async def create_dataset(request: DatasetRequest, files=None):
    """Create a new federated dataset"""
    dataset_id = await dataset_manager.create_dataset(request, files)
    return {"dataset_id": dataset_id, "status": "created"}

@app.get("/api/datasets/{dataset_id}/metadata")
async def get_dataset_metadata(dataset_id: str):
    """Get dataset metadata"""
    return await dataset_manager.get_dataset_metadata(dataset_id)

@app.post("/api/datasets/{dataset_id}/partitions")
async def create_dataset_partitions(dataset_id: str, num_partitions: int, privacy_budget: Optional[PrivacyBudgetRequest] = None):
    """Create partitions for a dataset"""
    partitions = await dataset_manager.create_partitions(dataset_id, num_partitions, privacy_budget)
    return {"partitions": [p.dict() for p in partitions]}

@app.post("/api/datasets/{dataset_id}/request-partition")
async def request_partition(dataset_id: str, node_id: str, partition_index: int = 0):
    """Request access to a dataset partition"""
    partition = await dataset_manager.request_partition(dataset_id, node_id, partition_index)
    return partition.dict()

@app.get("/api/datasets/{dataset_id}/statistics")
async def get_dataset_statistics(dataset_id: str, privacy_budget: Optional[PrivacyBudgetRequest] = None):
    """Get dataset statistics with privacy"""
    statistics = await dataset_manager.get_dataset_statistics(dataset_id, privacy_budget)
    return statistics.dict()

@app.get("/api/datasets")
async def list_datasets():
    """List all available datasets"""
    return {
        "datasets": [
            {
                "dataset_id": ds_id,
                "name": ds["name"],
                "data_type": ds["data_type"],
                "total_samples": ds["total_samples"],
                "privacy_level": ds["privacy_level"],
                "status": ds["status"]
            }
            for ds_id, ds in dataset_manager.datasets.items()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "datasets_count": len(dataset_manager.datasets),
        "partitions_count": sum(len(parts) for parts in dataset_manager.partitions.values()),
        "uptime": 0,  # Would track actual uptime
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Federated Datasets Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "create_dataset": "POST /api/datasets/create",
            "get_metadata": "GET /api/datasets/{id}/metadata",
            "create_partitions": "POST /api/datasets/{id}/partitions",
            "request_partition": "POST /api/datasets/{id}/request-partition",
            "get_statistics": "GET /api/datasets/{id}/statistics",
            "list_datasets": "GET /api/datasets"
        }
    }

def create_dataset_server(host: str = "0.0.0.0", port: int = 8001) -> None:
    """Create and run the dataset server"""
    logger.info(f"🚀 Starting Federated Datasets Server on {host}:{port}")

    uvicorn.run(
        "src.ai.datasets.federated_datasets:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    # Run server directly
    create_dataset_server()