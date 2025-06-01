"""
Configuration settings for the RAG system.
Supports both local Ollama and RunPod deployments.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class DeploymentType(Enum):
    """Deployment types supported by the system."""
    LOCAL = "local"
    RUNPOD = "runpod"

class DeploymentConfig:
    """Configuration manager for deployment settings."""
    _instance = None
    _deployment_type = DeploymentType.RUNPOD  # Default to RunPod
    _config = {
        # Base URL can be either:
        # 1. Proxy URL: https://<pod-id>-11434.proxy.runpod.net
        # 2. API URL: https://api.runpod.ai/v2
        "base_url": os.getenv("RUNPOD_API_URL", "http://localhost:11434"),
        
        # API key is required for RunPod API endpoints but not for proxy URLs
        "api_key": os.getenv("RUNPOD_API_KEY", ""),
        
        # Endpoint ID is required for RunPod API endpoints but not for proxy URLs
        "endpoint_id": os.getenv("RUNPOD_ENDPOINT_ID", ""),
        
        "model_name": "llama3",
        "timeout": 120,
        
        # Security settings
        "require_auth": os.getenv("REQUIRE_AUTH", "true").lower() == "true"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeploymentConfig, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_active_config(cls) -> Dict[str, Any]:
        """Get the active configuration."""
        return cls._config

# RAG System Configuration
RAG_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "similarity_threshold": 0.7
}

# Document Processing Configuration
DOC_PROCESSING_CONFIG = {
    "supported_formats": [".pdf", ".docx"],
    "max_file_size_mb": 10
} 