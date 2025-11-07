"""
AI Inference Module for Ailoos
Servidores de inferencia para modelos de IA, incluyendo EmpoorioLM
"""

from .empoorio_lm_server import create_inference_server

# EmpoorioLMServer class is not defined in the module, only the function
# So we don't import it to avoid ImportError

__all__ = ['create_inference_server']