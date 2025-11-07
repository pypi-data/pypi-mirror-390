#!/usr/bin/env python3
"""
EmpoorioLM Inference Server
Servidor de inferencia real para el modelo EmpoorioLM con FastAPI
"""

import asyncio
import json
import logging
import os
import sys
import time
import torch
import uvicorn
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psutil
import GPUtil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Custom model loading function
async def load_empoorio_model(model_path: str):
    """Load EmpoorioLM model and tokenizer"""
    import torch
    from transformers import GPT2Config, GPT2Model, GPT2Tokenizer

    try:
        # Load configuration
        config_path = os.path.join(model_path, 'config.json')
        config = GPT2Config.from_json_file(config_path)

        # Load model
        model = GPT2Model(config)
        model_path_file = os.path.join(model_path, 'pytorch_model.bin')
        state_dict = torch.load(model_path_file, map_location='cpu')
        model.load_state_dict(state_dict)
        model.eval()

        # Load tokenizer (fallback to GPT-2 if custom not available)
        try:
            tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        except:
            tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            tokenizer.pad_token = tokenizer.eos_token

        # Determine device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)

        return model, tokenizer, device

    except Exception as e:
        logger.error(f"Failed to load EmpoorioLM model: {e}")
        raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/empoorio_lm_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class InferenceRequest(BaseModel):
    """Request model for inference"""
    text: str = Field(..., description="Input text for generation")
    max_length: int = Field(100, description="Maximum length of generated text")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: float = Field(0.9, description="Top-p sampling parameter")
    top_k: int = Field(50, description="Top-k sampling parameter")
    do_sample: bool = Field(True, description="Whether to use sampling")
    num_return_sequences: int = Field(1, description="Number of sequences to return")
    repetition_penalty: float = Field(1.1, description="Repetition penalty")
    length_penalty: float = Field(1.0, description="Length penalty")

class InferenceResponse(BaseModel):
    """Response model for inference"""
    generated_text: str
    input_text: str
    generation_time: float
    model_name: str
    parameters: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    gpu_available: bool
    memory_usage: Dict[str, Any]
    uptime: float
    version: str

class MetricsResponse(BaseModel):
    """Metrics response"""
    total_requests: int
    active_requests: int
    average_generation_time: float
    total_tokens_generated: int
    gpu_utilization: Optional[float]
    memory_utilization: float
    uptime_seconds: float

# Global variables
model = None
tokenizer = None
device = None
server_start_time = time.time()
request_count = 0
total_generation_time = 0.0
total_tokens_generated = 0
active_requests = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global model, tokenizer, device

    # Startup
    logger.info("🚀 Starting EmpoorioLM Inference Server...")

    try:
        # Load model
        model_path = Path(__file__).parent.parent / "models" / "EmpoorioLM"
        logger.info(f"📥 Loading model from: {model_path}")

        model, tokenizer, device = await load_empoorio_model(str(model_path))
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down EmpoorioLM Inference Server...")
    if model:
        del model
    if tokenizer:
        del tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Create FastAPI app
app = FastAPI(
    title="EmpoorioLM Inference Server",
    description="Servidor de inferencia para el modelo EmpoorioLM de Ailoos",
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

async def generate_text(request: InferenceRequest) -> Dict[str, Any]:
    """Generate text using EmpoorioLM"""
    global active_requests, request_count, total_generation_time, total_tokens_generated

    active_requests += 1
    start_time = time.time()

    try:
        # Tokenize input
        inputs = tokenizer(
            request.text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(device)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_length=min(len(inputs["input_ids"][0]) + request.max_length, 1024),
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                repetition_penalty=request.repetition_penalty,
                length_penalty=request.length_penalty,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove input text from output if present
        if generated_text.startswith(request.text):
            generated_text = generated_text[len(request.text):].strip()

        generation_time = time.time() - start_time
        tokens_generated = len(tokenizer.encode(generated_text))

        # Update metrics
        request_count += 1
        total_generation_time += generation_time
        total_tokens_generated += tokens_generated

        return {
            "generated_text": generated_text,
            "input_text": request.text,
            "generation_time": generation_time,
            "model_name": "EmpoorioLM",
            "parameters": request.dict(),
            "timestamp": datetime.now().isoformat(),
            "tokens_generated": tokens_generated
        }

    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    finally:
        active_requests -= 1

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check GPU memory
        gpu_memory = {}
        if torch.cuda.is_available():
            gpu_memory = {
                "allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f}GB",
                "reserved": f"{torch.cuda.memory_reserved() / 1024**3:.2f}GB"
            }

        # System memory
        memory = psutil.virtual_memory()
        system_memory = {
            "total": f"{memory.total / 1024**3:.2f}GB",
            "available": f"{memory.available / 1024**3:.2f}GB",
            "used_percent": f"{memory.percent}%"
        }

        return HealthResponse(
            status="healthy",
            model_loaded=model is not None,
            gpu_available=torch.cuda.is_available(),
            memory_usage={
                "gpu": gpu_memory,
                "system": system_memory
            },
            uptime=time.time() - server_start_time,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/generate", response_model=InferenceResponse)
async def generate(request: InferenceRequest, background_tasks: BackgroundTasks):
    """Text generation endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if active_requests >= 5:  # Limit concurrent requests
        raise HTTPException(status_code=429, detail="Server busy, try again later")

    result = await generate_text(request)
    return InferenceResponse(**result)

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get server metrics"""
    gpu_utilization = None
    if torch.cuda.is_available():
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_utilization = gpus[0].load * 100
        except:
            pass

    memory = psutil.virtual_memory()

    return MetricsResponse(
        total_requests=request_count,
        active_requests=active_requests,
        average_generation_time=total_generation_time / max(request_count, 1),
        total_tokens_generated=total_tokens_generated,
        gpu_utilization=gpu_utilization,
        memory_utilization=memory.percent,
        uptime_seconds=time.time() - server_start_time
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EmpoorioLM Inference Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "metrics": "/metrics"
        }
    }

def create_inference_server(host: str = "0.0.0.0", port: int = 8003) -> None:
    """Create and run the inference server"""
    logger.info(f"🚀 Starting EmpoorioLM server on {host}:{port}")

    uvicorn.run(
        "src.ai.inference.empoorio_lm_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    # Run server directly
    create_inference_server()