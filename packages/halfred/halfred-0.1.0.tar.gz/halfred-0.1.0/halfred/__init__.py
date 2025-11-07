"""
Halfred Python SDK

A Python SDK for consuming the Halfred service API.
"""

__version__ = "0.1.0"

from halfred.client import HalfredClient
from halfred.exceptions import HalfredError, HalfredAPIError, HalfredAuthenticationError

__all__ = [
    "HalfredClient",
    "HalfredError",
    "HalfredAPIError",
    "HalfredAuthenticationError",
    "__version__",
]

