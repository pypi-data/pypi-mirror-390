"""
Data models for the Halfred API.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class APIResponse:
    """
    Base response model for API responses.
    
    This can be extended with specific response models as needed.
    """
    data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIResponse":
        """Create an APIResponse from a dictionary."""
        return cls(
            data=data.get("data"),
            status=data.get("status"),
            message=data.get("message")
        )

