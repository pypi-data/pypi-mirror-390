"""
Data models for the Halfred API.
Compatible with OpenAI SDK response format.
"""

from typing import Optional, Dict, Any, List


class Model:
    """Represents a model object compatible with OpenAI SDK."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.object = data.get("object", "model")
        self.created = data.get("created")
        self.owned_by = data.get("owned_by", "")
        # Store all other fields as attributes
        for key, value in data.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<Model {self.id}>"


class ModelsListResponse:
    """Response object for models list endpoint, compatible with OpenAI SDK."""
    
    def __init__(self, data: Dict[str, Any]):
        models_data = data.get("data", [])
        self.data = [Model(model) for model in models_data] if models_data else []
        self.object = data.get("object", "list")
        # Store all other fields as attributes
        for key, value in data.items():
            if key != "data" and not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<ModelsListResponse object={self.object} data={len(self.data)} models>"


class Message:
    """Represents a message in a chat completion."""
    
    def __init__(self, data: Dict[str, Any]):
        self.role = data.get("role", "")
        # Preserve None if content is None, otherwise default to empty string
        self.content = data.get("content") if "content" in data else ""
        # Store all other fields as attributes
        for key, value in data.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<Message role={self.role}>"


class Choice:
    """Represents a choice in a chat completion."""
    
    def __init__(self, data: Dict[str, Any]):
        self.index = data.get("index", 0)
        message_data = data.get("message", {})
        self.message = Message(message_data) if message_data else None
        self.finish_reason = data.get("finish_reason")
        # Store all other fields as attributes
        for key, value in data.items():
            if key not in ("message",) and not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<Choice index={self.index} finish_reason={self.finish_reason}>"


class Usage:
    """Represents token usage information."""
    
    def __init__(self, data: Dict[str, Any]):
        self.prompt_tokens = data.get("prompt_tokens", 0)
        self.completion_tokens = data.get("completion_tokens", 0)
        self.total_tokens = data.get("total_tokens", 0)
        # Store all other fields as attributes
        for key, value in data.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<Usage prompt={self.prompt_tokens} completion={self.completion_tokens} total={self.total_tokens}>"


class ChatCompletion:
    """Response object for chat completions, compatible with OpenAI SDK."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.object = data.get("object", "chat.completion")
        self.created = data.get("created", 0)
        self.model = data.get("model", "")
        
        # Parse choices
        choices_data = data.get("choices", [])
        self.choices = [Choice(choice) for choice in choices_data] if choices_data else []
        
        # Parse usage
        usage_data = data.get("usage")
        self.usage = Usage(usage_data) if usage_data else None
        
        # Store all other fields as attributes (for custom fields like provider, profile)
        for key, value in data.items():
            if key not in ("choices", "usage") and not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<ChatCompletion id={self.id} model={self.model}>"

