"""
Custom exceptions for the Halfred SDK.
"""

from typing import Optional
import requests


class HalfredError(Exception):
    """Base exception for all Halfred SDK errors."""
    pass


class HalfredAPIError(HalfredError):
    """
    Exception raised when an API request fails.
    
    Args:
        message: Error message
        status_code: HTTP status code (if available)
        response: Response object (if available)
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[requests.Response] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HalfredAuthenticationError(HalfredAPIError):
    """
    Exception raised when authentication fails.
    
    This is a subclass of HalfredAPIError for convenience.
    """
    pass

