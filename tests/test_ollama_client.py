"""
Tests for the Ollama client component.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.components.ollama_client import OllamaClient, OllamaError

@pytest.fixture
def ollama_client():
    """Create an Ollama client instance for testing."""
    return OllamaClient()

def test_init_default_values():
    """Test initialization with default values."""
    client = OllamaClient()
    assert client.base_url == "http://localhost:11434"
    assert client.model == "mistral"

def test_init_custom_values():
    """Test initialization with custom values."""
    client = OllamaClient(base_url="http://custom:11434", model="custom-model")
    assert client.base_url == "http://custom:11434"
    assert client.model == "custom-model"

@patch('requests.post')
def test_generate_response_success(mock_post):
    """Test successful response generation."""
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "Test response",
        "total_tokens": 10,
        "prompt_tokens": 5,
        "completion_tokens": 5
    }
    mock_post.return_value = mock_response
    
    client = OllamaClient()
    result = client.generate_response("Test prompt")
    
    assert result["text"] == "Test response"
    assert result["tokens"] == 10
    assert result["prompt_tokens"] == 5
    assert result["completion_tokens"] == 5

@patch('requests.post')
def test_generate_response_with_context(mock_post):
    """Test response generation with context."""
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "Test response",
        "total_tokens": 10,
        "prompt_tokens": 5,
        "completion_tokens": 5
    }
    mock_post.return_value = mock_response
    
    client = OllamaClient()
    context = ["Context 1", "Context 2"]
    result = client.generate_response("Test prompt", context=context)
    
    # Verify the prompt was prepared correctly
    call_args = mock_post.call_args[1]['json']
    assert "Context 1" in call_args['prompt']
    assert "Context 2" in call_args['prompt']
    assert "Test prompt" in call_args['prompt']

@patch('requests.post')
def test_generate_response_error(mock_post):
    """Test error handling during response generation."""
    mock_post.side_effect = Exception("API Error")
    
    client = OllamaClient()
    with pytest.raises(OllamaError):
        client.generate_response("Test prompt")

@patch('requests.get')
def test_check_model_availability_success(mock_get):
    """Test successful model availability check."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [{"name": "mistral"}]
    }
    mock_get.return_value = mock_response
    
    client = OllamaClient()
    assert client.check_model_availability() is True

@patch('requests.get')
def test_check_model_availability_not_found(mock_get):
    """Test model availability check when model is not found."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [{"name": "other-model"}]
    }
    mock_get.return_value = mock_response
    
    client = OllamaClient()
    assert client.check_model_availability() is False

@patch('requests.get')
def test_check_model_availability_error(mock_get):
    """Test error handling during model availability check."""
    mock_get.side_effect = Exception("API Error")
    
    client = OllamaClient()
    assert client.check_model_availability() is False 