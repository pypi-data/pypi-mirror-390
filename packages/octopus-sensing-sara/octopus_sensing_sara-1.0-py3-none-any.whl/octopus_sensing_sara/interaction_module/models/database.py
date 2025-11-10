"""SQLAlchemy database models for SQLite."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class UserProfileModel(Base):
    """User profile table storing user information and conversation summary."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    conversation_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    key_facts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    session_summaries: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False,
        comment="List of recent session summaries (max 5), each with: session_id, summary, timestamp"
    )
    first_interaction: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_interaction: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship to conversations
    conversations: Mapped[list["ConversationHistoryModel"]] = relationship(
        "ConversationHistoryModel", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of UserProfile."""
        return (
            f"<UserProfile(user_id={self.user_id!r}, name={self.name!r}, "
            f"total_messages={self.total_messages})>"
        )


class ConversationHistoryModel(Base):
    """Conversation history table storing message exchanges."""

    __tablename__ = "conversation_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False
    )
    messages: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship to user
    user: Mapped[UserProfileModel] = relationship("UserProfileModel", back_populates="conversations")

    # Indexes for performance
    __table_args__ = (Index("ix_conversation_user_id", "user_id"),)

    def __repr__(self) -> str:
        """String representation of ConversationHistory."""
        return (
            f"<ConversationHistory(session_id={self.session_id!r}, user_id={self.user_id!r}, "
            f"messages_count={len(self.messages)})>"
        )
