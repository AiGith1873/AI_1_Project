"""
Unified LLM Client for handling both local Ollama and RunPod deployments.
Provides a consistent interface for LLM operations with robust error handling.
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional, Union
from ..config.settings import DeploymentConfig, DeploymentType

class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass

class LLMClient:
    def __init__(self):
        self.config = DeploymentConfig.get_active_config()
        self.deployment_type = DeploymentConfig._deployment_type
        self.logger = logging.getLogger(__name__)
        
        # Log initialization
        self.logger.info(f"Initializing LLM client with model: {self.config['model_name']}")
        self.logger.info(f"Using base URL: {self.config['base_url']}")

    def generate_response(self, 
                         prompt: str, 
                         context: Optional[List[str]] = None,
                         temperature: float = 0.7,
                         max_tokens: int = 1000) -> Dict[str, Union[str, float]]:
        """
        Generate a response using either local Ollama or RunPod.
        
        Args:
            prompt (str): The user's prompt
            context (Optional[List[str]]): Additional context for the prompt
            temperature (float): Controls randomness (0.0 to 1.0)
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            Dict containing the response and metadata
            
        Raises:
            LLMError: If there's an error with the LLM service
        """
        try:
            full_prompt = self._prepare_prompt(prompt, context)
            
            if self.deployment_type == DeploymentType.RUNPOD:
                return self._generate_runpod_response(full_prompt, temperature, max_tokens)
            return self._generate_local_response(full_prompt, temperature, max_tokens)
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise LLMError(f"Failed to generate response: {str(e)}")

    def _prepare_prompt(self, prompt: str, context: Optional[List[str]] = None) -> str:
        """Prepare the full prompt by combining context and main prompt."""
        if not context:
            return prompt
            
        context_text = "\n\n".join(context)
        return f"""Context:
{context_text}

Question:
{prompt}

Answer:"""

    def _generate_local_response(self, 
                               prompt: str, 
                               temperature: float = 0.7,
                               max_tokens: int = 1000) -> Dict[str, Union[str, float]]:
        """Generate response using local Ollama instance."""
        url = f"{self.config['base_url']}/api/generate"
        
        payload = {
            "model": self.config["model_name"],
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.config["timeout"])
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result.get("response", ""),
                "tokens": result.get("total_tokens", 0)
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with Ollama: {str(e)}")
            raise LLMError(f"Failed to generate response from local Ollama: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing Ollama response: {str(e)}")
            raise LLMError(f"Invalid response from Ollama: {str(e)}")

    def _generate_runpod_response(self, 
                                prompt: str, 
                                temperature: float = 0.7,
                                max_tokens: int = 1000) -> Dict[str, Union[str, float]]:
        """Generate response using RunPod API."""
        # Check if we're using a proxy URL or API endpoint
        is_proxy_url = "proxy.runpod.net" in self.config['base_url']
        
        if is_proxy_url:
            # Using proxy URL - direct Ollama API
            base_url = self.config['base_url'].rstrip('/')  # Remove trailing slash if present
            url = f"{base_url}/api/generate"
            
            # First check if Ollama is running
            try:
                health_check = requests.get(f"{base_url}/api/tags", timeout=5)
                health_check.raise_for_status()
                self.logger.info("Ollama health check passed")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Ollama health check failed: {str(e)}")
                raise LLMError("Ollama service is not accessible. Please check if the pod is running and Ollama is started.")
            
            headers = {}  # No auth needed for proxy
            payload = {
                "model": self.config["model_name"],
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
        else:
            # Using RunPod API - requires authentication
            if not self.config['api_key']:
                raise LLMError("API key is required for RunPod API endpoints")
                
            url = f"{self.config['base_url']}/{self.config['endpoint_id']}/run"
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": {
                    "prompt": prompt,
                    "model": self.config["model_name"],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
        
        try:
            self.logger.info(f"Sending request to: {url}")
            self.logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.config["timeout"])
            response.raise_for_status()
            result = response.json()
            
            if is_proxy_url:
                return {
                    "text": result.get("response", ""),
                    "tokens": result.get("total_tokens", 0)
                }
            else:
                return {
                    "text": result.get("output", {}).get("text", ""),
                    "tokens": result.get("output", {}).get("total_tokens", 0)
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with RunPod: {str(e)}")
            if is_proxy_url:
                raise LLMError(f"Failed to communicate with Ollama at {url}. Please check if Ollama is running in the pod.")
            else:
                raise LLMError(f"Failed to generate response from RunPod: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing RunPod response: {str(e)}")
            raise LLMError(f"Invalid response from RunPod: {str(e)}")

    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        try:
            if self.deployment_type == DeploymentType.RUNPOD:
                is_proxy_url = "proxy.runpod.net" in self.config['base_url']
                if is_proxy_url:
                    # Check Ollama health
                    url = f"{self.config['base_url'].rstrip('/')}/api/tags"
                    response = requests.get(url, timeout=5)
                else:
                    # Check RunPod API
                    url = f"{self.config['base_url']}/{self.config['endpoint_id']}/status"
                    headers = {"Authorization": f"Bearer {self.config['api_key']}"}
                    response = requests.get(url, headers=headers, timeout=5)
            
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Service availability check failed: {str(e)}")
            return False 