"""Pydantic models for API validation and serialization."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class MessageRole(str, Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Message model for chat conversations."""

    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., min_length=1, description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate and clean message content."""
        # Strip whitespace
        v = v.strip()
        if not v:
            raise ValueError("Message content cannot be empty or only whitespace")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "Hello, how are you?",
                    "timestamp": "2024-01-01T12:00:00",
                    "metadata": {},
                }
            ]
        }
    }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    user_id: str = Field(..., min_length=1, description="Unique user identifier")
    session_id: str | None = Field(default=None, description="Optional session identifier")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("user_id", "message")
    @classmethod
    def validate_string_fields(cls, v: str) -> str:
        """Validate and clean string fields."""
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty or only whitespace")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user123",
                    "session_id": "session456",
                    "message": "What's the weather like today?",
                    "metadata": {},
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Assistant response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "session456",
                    "message": "The weather is sunny today!",
                    "timestamp": "2024-01-01T12:00:01",
                    "metadata": {},
                }
            ]
        }
    }


class SessionSummary(BaseModel):
    """Individual session summary model."""

    session_id: str = Field(..., description="Session identifier")
    summary: str = Field(..., description="Summary of the session")
    timestamp: datetime = Field(..., description="When the session ended")
    message_count: int = Field(default=0, description="Number of messages in the session")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user123_20250107_140000",
                    "summary": "User discussed their interest in Python programming and asked about best practices",
                    "timestamp": "2025-01-07T14:30:00",
                    "message_count": 12,
                }
            ]
        }
    }


class UserProfile(BaseModel):
    """User profile model."""

    user_id: str = Field(..., description="Unique user identifier")
    name: str | None = Field(default=None, description="User's name")
    preferences: dict[str, Any] = Field(default_factory=dict, description="User preferences")
    conversation_summary: str = Field(default="", description="Summary of past conversations")
    key_facts: list[str] = Field(default_factory=list, description="Key facts about the user")
    session_summaries: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Recent session summaries (max 5 most recent)"
    )
    first_interaction: datetime = Field(..., description="Timestamp of first interaction")
    last_interaction: datetime = Field(..., description="Timestamp of last interaction")
    total_messages: int = Field(default=0, description="Total number of messages")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user123",
                    "name": "John Doe",
                    "preferences": {"language": "en", "theme": "dark"},
                    "conversation_summary": "User is interested in AI and technology",
                    "key_facts": ["Works as a software engineer", "Enjoys hiking"],
                    "first_interaction": "2024-01-01T10:00:00",
                    "last_interaction": "2024-01-01T12:00:00",
                    "total_messages": 42,
                }
            ]
        }
    }


class ConversationSummary(BaseModel):
    """Conversation summary model."""

    summary: str = Field(..., description="Summary of the conversation")
    key_facts: list[str] = Field(default_factory=list, description="Key facts extracted")
    topics: list[str] = Field(default_factory=list, description="Main topics discussed")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Discussion about machine learning and its applications",
                    "key_facts": ["User is learning Python", "Interested in neural networks"],
                    "topics": ["machine learning", "python", "neural networks"],
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="Application version")


class DeleteResponse(BaseModel):
    """Generic delete response model."""

    message: str = Field(..., description="Deletion confirmation message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Deletion timestamp")


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""

    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Conversation title (first user message or generated)")
    message_count: int = Field(..., description="Number of messages in conversation")
    last_message_preview: str = Field(..., description="Preview of the last message")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user123_20240101_120000",
                    "user_id": "user123",
                    "title": "Discussion about Python",
                    "message_count": 12,
                    "last_message_preview": "That's a great point about...",
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T14:30:00",
                }
            ]
        }
    }


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""

    conversations: list[ConversationSummary] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversations": [
                        {
                            "session_id": "user123_20240101_120000",
                            "user_id": "user123",
                            "title": "Getting Started",
                            "message_count": 5,
                            "last_message_preview": "Thanks for the help!",
                            "created_at": "2024-01-01T12:00:00",
                            "updated_at": "2024-01-01T12:30:00",
                        }
                    ],
                    "total": 1,
                }
            ]
        }
    }
