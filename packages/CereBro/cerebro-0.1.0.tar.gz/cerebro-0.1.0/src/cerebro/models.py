"""Data models for the application."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message model."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSession(BaseModel):
    """Chat session model."""
    id: str
    name: str
    model: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: Optional[str] = None


class OllamaModel(BaseModel):
    """Ollama model information."""
    name: str
    size: int
    digest: str
    modified_at: datetime
    details: Optional[dict] = None


class SiteModel(BaseModel):
    """Model available on Ollama site."""
    name: str
    description: str
    tags: List[str] = Field(default_factory=list)