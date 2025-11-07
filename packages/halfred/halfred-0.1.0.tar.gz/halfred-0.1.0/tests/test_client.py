"""
Tests for the HalfredClient.
"""

import pytest
from unittest.mock import Mock, patch
from halfred import HalfredClient, HalfredAPIError, HalfredAuthenticationError


def test_client_initialization():
    """Test that the client initializes correctly."""
    client = HalfredClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.halfred.com"
    assert client.timeout == 30
    assert client.models is not None
    assert client.chat is not None
    assert client.chat.completions is not None


def test_client_custom_base_url():
    """Test client with custom base URL."""
    client = HalfredClient(api_key="test-key", base_url="https://custom.api.com")
    assert client.base_url == "https://custom.api.com"


def test_client_authentication_header():
    """Test that the client sets the correct authentication header."""
    client = HalfredClient(api_key="test-key")
    assert "Authorization" in client.session.headers
    assert client.session.headers["Authorization"] == "Bearer test-key"


@patch("halfred.client.requests.Session.request")
def test_models_list(mock_request):
    """Test listing models."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {
        "data": [
            {"id": "gpt-4", "object": "model"},
            {"id": "gpt-3.5-turbo", "object": "model"}
        ]
    }
    mock_response.content = b'{"data": [{"id": "gpt-4"}]}'
    mock_request.return_value = mock_response
    
    client = HalfredClient(api_key="test-key")
    result = client.models.list()
    
    assert "data" in result
    assert len(result["data"]) == 2
    mock_request.assert_called_once()
    # Verify the endpoint
    call_args = mock_request.call_args
    assert call_args[1]["method"] == "GET"
    assert "/v1/models" in call_args[1]["url"]


@patch("halfred.client.requests.Session.request")
def test_chat_completions_create(mock_request):
    """Test creating a chat completion."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
    mock_response.content = b'{"id": "chatcmpl-123"}'
    mock_request.return_value = mock_response
    
    client = HalfredClient(api_key="test-key")
    result = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Hello!"}
        ]
    )
    
    assert result["id"] == "chatcmpl-123"
    assert "choices" in result
    mock_request.assert_called_once()
    # Verify the endpoint and payload
    call_args = mock_request.call_args
    assert call_args[1]["method"] == "POST"
    assert "/v1/chat/completions" in call_args[1]["url"]
    assert call_args[1]["json"]["model"] == "gpt-4"
    assert call_args[1]["json"]["messages"][0]["role"] == "user"
    assert call_args[1]["json"]["messages"][0]["content"] == "Hello!"


@patch("halfred.client.requests.Session.request")
def test_chat_completions_with_parameters(mock_request):
    """Test creating a chat completion with additional parameters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "choices": []
    }
    mock_response.content = b'{"id": "chatcmpl-123"}'
    mock_request.return_value = mock_response
    
    client = HalfredClient(api_key="test-key")
    client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test"}],
        temperature=0.7,
        max_tokens=100,
        max_completion_tokens=50
    )
    
    call_args = mock_request.call_args
    payload = call_args[1]["json"]
    assert payload["temperature"] == 0.7
    assert payload["max_tokens"] == 100
    assert payload["max_completion_tokens"] == 50


@patch("halfred.client.requests.Session.request")
def test_chat_completions_with_response_format(mock_request):
    """Test creating a chat completion with response_format parameter."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "choices": []
    }
    mock_response.content = b'{"id": "chatcmpl-123"}'
    mock_request.return_value = mock_response
    
    client = HalfredClient(api_key="test-key")
    client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test"}],
        response_format={"type": "json_object"}
    )
    
    call_args = mock_request.call_args
    payload = call_args[1]["json"]
    assert payload["response_format"] == {"type": "json_object"}


@patch("halfred.client.requests.Session.request")
def test_authentication_error(mock_request):
    """Test authentication error handling."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.ok = False
    mock_request.return_value = mock_response
    
    client = HalfredClient(api_key="test-key")
    
    with pytest.raises(HalfredAuthenticationError):
        client.models.list()


@patch("halfred.client.requests.Session.request")
def test_api_error(mock_request):
    """Test API error handling."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.ok = False
    mock_response.json.return_value = {
        "error": {
            "message": "Invalid model",
            "type": "invalid_request_error"
        }
    }
    mock_response.text = "Bad request"
    mock_request.return_value = mock_response
    
    client = HalfredClient(api_key="test-key")
    
    with pytest.raises(HalfredAPIError) as exc_info:
        client.chat.completions.create(
            model="invalid-model",
            messages=[{"role": "user", "content": "Test"}]
        )
    
    assert exc_info.value.status_code == 400
