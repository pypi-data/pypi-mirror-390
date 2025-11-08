"""
Halfred Python SDK

A Python SDK for consuming the Halfred service API.
"""

__version__ = "0.1.0"

from halfred.client import Halfred
from halfred.exceptions import HalfredError, HalfredAPIError, HalfredAuthenticationError

__all__ = [
    "Halfred",
    "HalfredError",
    "HalfredAPIError",
    "HalfredAuthenticationError",
    "__version__",
]

