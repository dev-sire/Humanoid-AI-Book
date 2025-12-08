"""
Chat domain models.

Pydantic models for chat requests, responses, messages, and sessions.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual message in a conversation."""

    message_id: UUID = Field(description="Unique message identifier")
    session_id: UUID = Field(description="Session this message belongs to")
    role: str = Field(description="Message sender role: 'user' or 'assistant'")
    content: str = Field(description="Message text content")
    selected_text: Optional[str] = Field(
        default=None, description="Optional user-selected page text"
    )
    context_used: Optional[dict] = Field(
        default=None, description="Retrieved chunks used for answer (assistant only)"
    )
    created_at: datetime = Field(description="Message creation timestamp")

    model_config = {"from_attributes": True}


class ChatSession(BaseModel):
    """Conversation session between user and chatbot."""

    session_id: UUID = Field(description="Unique session identifier")
    created_at: datetime = Field(description="Session creation timestamp")
    last_activity_at: datetime = Field(description="Last activity timestamp")

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    """Request payload for chat endpoint."""

    message: str = Field(
        min_length=1, max_length=1000, description="User message (1-1000 characters)"
    )
    session_id: Optional[str] = Field(
        default=None, description="Optional existing session ID (UUID)"
    )
    selected_text: Optional[str] = Field(
        default=None, min_length=1, max_length=1000, description="Optional selected page text"
    )


class Source(BaseModel):
    """Source citation for chatbot response."""

    title: str = Field(description="Page/section title")
    file_path: str = Field(description="File path relative to docs/")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score (0-1)")
    excerpt: str = Field(max_length=500, description="Text excerpt from source")


class ChatResponse(BaseModel):
    """Response payload for chat endpoint."""

    session_id: str = Field(description="Session ID (UUID)")
    message: str = Field(description="Assistant response message")
    sources: list[Source] = Field(default_factory=list, description="Source citations")
    timestamp: datetime = Field(description="Response timestamp")


class SessionHistoryResponse(BaseModel):
    """Response payload for session history endpoint."""

    session_id: str = Field(description="Session ID (UUID)")
    messages: list[ChatMessage] = Field(description="Chronological message history")
