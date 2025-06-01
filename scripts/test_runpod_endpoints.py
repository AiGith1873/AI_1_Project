import os
import requests
import json
from dotenv import load_dotenv
import time
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.config.settings import DeploymentConfig

def test_ollama_connection(base_url):
    """Test basic Ollama connectivity and model availability."""
    print(f"\n=== Testing Ollama at {base_url} ===")
    
    # Get model name from settings
    config = DeploymentConfig.get_active_config()
    model_name = config["model_name"]
    print(f"Using model: {model_name}")
    
    # 1. Test basic connectivity
    try:
        print("\n1. Testing basic connectivity...")
        response = requests.get(f"{base_url}/api/tags")
        response.raise_for_status()
        print("✅ Basic connectivity successful")
    except Exception as e:
        print(f"❌ Basic connectivity failed: {str(e)}")
        return False

    # 2. Check available models
    try:
        print("\n2. Checking available models...")
        response = requests.get(f"{base_url}/api/tags")
        models = response.json()
        print(f"Available models: {json.dumps(models, indent=2)}")
        
        if not models.get("models"):
            print(f"No models found. Pulling {model_name}...")
            pull_response = requests.post(
                f"{base_url}/api/pull",
                json={"name": model_name, "insecure": True}
            )
            pull_response.raise_for_status()
            print("✅ Model pull initiated")
            time.sleep(5)  # Wait a bit for the pull to start
        else:
            print("✅ Models found")
    except Exception as e:
        print(f"❌ Model check failed: {str(e)}")
        return False

    # 3. Test simple prompt
    try:
        print("\n3. Testing simple prompt...")
        prompt = "Say hello in one word."
        print(f"Prompt: {prompt}")
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        print("✅ Prompt test successful")
        return True
    except Exception as e:
        print(f"❌ Prompt test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error response: {e.response.text}")
        return False

def main():
    """Main test function."""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from settings
    config = DeploymentConfig.get_active_config()
    base_url = config["base_url"]
    
    if not base_url:
        print("❌ Base URL not found in configuration")
        return
    
    print(f"Using Ollama URL: {base_url}")
    
    # Run the tests
    if test_ollama_connection(base_url):
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 