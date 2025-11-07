"""
Main client for interacting with the Halfred API.
Compatible with OpenAI API standard.
"""

import requests
from typing import Optional, Dict, Any, List
from halfred.exceptions import HalfredAPIError, HalfredAuthenticationError


class Models:
    """Models API endpoint."""
    
    def __init__(self, client: "HalfredClient"):
        self._client = client
    
    def list(self) -> Dict[str, Any]:
        """
        List all available models.
        
        Returns:
            Dictionary containing a 'data' key with a list of models
            
        Raises:
            HalfredAPIError: If the API returns an error
            HalfredAuthenticationError: If authentication fails
        """
        return self._client._request("GET", "/v1/models")


class Completions:
    """Chat completions API endpoint."""
    
    def __init__(self, client: "HalfredClient"):
        self._client = client
    
    def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        stream: Optional[bool] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            model: The model to use for the completion
            messages: A list of message objects with 'role' and 'content' keys
            temperature: Sampling temperature (0-2). Defaults to 1.
            max_tokens: Maximum number of tokens to generate
            max_completion_tokens: Maximum number of completion tokens
            response_format: Response format specification (e.g., {"type": "json_object"})
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary containing the completion response
            
        Raises:
            HalfredAPIError: If the API returns an error
            HalfredAuthenticationError: If authentication fails
        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        if stream is not None:
            payload["stream"] = stream
        
        # Add any additional kwargs
        payload.update(kwargs)
        
        return self._client._request("POST", "/v1/chat/completions", json=payload)


class Chat:
    """Chat API namespace."""
    
    def __init__(self, client: "HalfredClient"):
        self.completions = Completions(client)


class HalfredClient:
    """
    Client for interacting with the Halfred API.
    Compatible with OpenAI API standard.
    
    Args:
        api_key: Your Halfred API key
        base_url: Base URL for the API (defaults to production)
        timeout: Request timeout in seconds (default: 30)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://api.halfred.com"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"halfred-python-sdk/{__import__('halfred').__version__}"
        })
        
        # Initialize API namespaces
        self.models = Models(self)
        self.chat = Chat(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., '/v1/models')
            params: URL parameters
            data: Form data
            json: JSON payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            HalfredAPIError: If the API returns an error
            HalfredAuthenticationError: If authentication fails
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise HalfredAuthenticationError(
                    "Authentication failed. Please check your API key.",
                    response=response
                )
            
            # Handle other errors
            if not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message") or error_data.get("error", {}).get("message", response.text)
                except ValueError:
                    error_message = response.text
                
                raise HalfredAPIError(
                    f"API request failed: {error_message}",
                    status_code=response.status_code,
                    response=response
                )
            
            # Return JSON response
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            raise HalfredAPIError(f"Request failed: {str(e)}")
