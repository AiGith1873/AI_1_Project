import requests
import os
import time
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RunPodManager:
    def __init__(self):
        self.api_key = os.getenv("RUNPOD_API_KEY")
        self.pod_id = os.getenv("RUNPOD_ENDPOINT_ID")
        self.base_url = "https://rest.runpod.io/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Validate environment variables
        if not self.api_key:
            raise ValueError("RUNPOD_API_KEY must be set in environment variables")
        if not self.pod_id:
            raise ValueError("RUNPOD_ENDPOINT_ID must be set in environment variables")
            
        # Validate endpoint ID format
        if not re.match(r'^[a-zA-Z0-9]{8,}$', self.pod_id):
            raise ValueError(f"Invalid RUNPOD_ENDPOINT_ID format: {self.pod_id}. It should be at least 8 alphanumeric characters.")
            
        logger.info(f"Initialized RunPod manager with endpoint ID: {self.pod_id}")

    def get_pod_status(self) -> str:
        """Get the current status of the RunPod pod."""
        try:
            url = f"{self.base_url}/pods/{self.pod_id}"
            logger.debug(f"Checking pod status at: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("desiredStatus", "UNKNOWN")
            logger.info(f"Pod status: {status}")
            return status
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to RunPod: {str(e)}"
            logger.error(error_msg)
            if hasattr(e.response, 'text'):
                logger.error(f"Error Response: {e.response.text}")
            if "404" in str(e):
                error_msg += f"\nEndpoint ID '{self.pod_id}' not found. Please check your RunPod dashboard for the correct endpoint ID."
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error getting pod status: {str(e)}")
            raise

    def start_pod(self) -> None:
        """Start the RunPod pod."""
        try:
            url = f"{self.base_url}/pods/{self.pod_id}/start"
            logger.debug(f"Starting pod at: {url}")
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            logger.info("Successfully started RunPod pod")
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to start pod: {str(e)}"
            logger.error(error_msg)
            if hasattr(e.response, 'text'):
                logger.error(f"Error Response: {e.response.text}")
            if "404" in str(e):
                error_msg += f"\nEndpoint ID '{self.pod_id}' not found. Please check your RunPod dashboard for the correct endpoint ID."
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error starting pod: {str(e)}")
            raise

    def stop_pod(self) -> None:
        """Stop the RunPod pod."""
        try:
            url = f"{self.base_url}/pods/{self.pod_id}/stop"
            logger.debug(f"Stopping pod at: {url}")
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            logger.info("Successfully stopped RunPod pod")
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to stop pod: {str(e)}"
            logger.error(error_msg)
            if hasattr(e.response, 'text'):
                logger.error(f"Error Response: {e.response.text}")
            if "404" in str(e):
                error_msg += f"\nEndpoint ID '{self.pod_id}' not found. Please check your RunPod dashboard for the correct endpoint ID."
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error stopping pod: {str(e)}")
            raise

    def get_pod_details(self) -> Dict[str, Any]:
        """Get detailed information about the pod."""
        try:
            url = f"{self.base_url}/pods/{self.pod_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return data
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get pod details: {str(e)}"
            logger.error(error_msg)
            if hasattr(e.response, 'text'):
                logger.error(f"Error Response: {e.response.text}")
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error getting pod details: {str(e)}")
            raise

    def get_ollama_url(self) -> str:
        """Get the Ollama API URL for the pod."""
        return f"https://{self.pod_id}-11434.proxy.runpod.net"

    def get_webui_url(self) -> str:
        """Get the Open WebUI URL for the pod."""
        return f"https://{self.pod_id}-8080.proxy.runpod.net"

    def get_jupyter_url(self) -> str:
        """Get the JupyterLab URL for the pod."""
        return f"https://{self.pod_id}-8888.proxy.runpod.net"

    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            url = f"{self.get_ollama_url()}/api/tags"
            response = requests.get(url)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error checking Ollama status: {str(e)}")
            return False

    def wait_for_pod(self, timeout: int = 300) -> bool:
        """Wait for the pod to be ready, with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_pod_status()
                if status == "RUNNING":
                    # Also check if Ollama is accessible
                    if self.check_ollama_status():
                        logger.info("Pod is running and Ollama is accessible")
                        return True
                    else:
                        logger.info("Pod is running but waiting for Ollama to be ready...")
                elif status in ["FAILED", "TERMINATED"]:
                    logger.error(f"Pod failed to start. Status: {status}")
                    return False
                logger.info(f"Waiting for pod to start... Current status: {status}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error while waiting for pod: {str(e)}")
                return False
        logger.error("Timeout waiting for pod to start")
        return False

# Create and expose the singleton instance
runpod_manager = RunPodManager()

# Export the instance and its methods
__all__ = ['runpod_manager'] 