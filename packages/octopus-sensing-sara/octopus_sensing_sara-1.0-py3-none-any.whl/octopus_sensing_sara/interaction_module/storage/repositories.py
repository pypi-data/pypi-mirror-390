"""Repository classes for database operations."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from octopus_sensing_sara.models.database import ConversationHistoryModel, UserProfileModel
from octopus_sensing_sara.models.schemas import Message, UserProfile

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user profile operations."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository.

        Args:
            session: Async database session
        """
        self.session = session

    async def get_user_by_id(self, user_id: str) -> UserProfileModel | None:
        """Get user profile by user ID.

        Args:
            user_id: Unique user identifier

        Returns:
            UserProfileModel if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(UserProfileModel).where(UserProfileModel.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise

    async def create_user(self, user_profile: UserProfile) -> UserProfileModel:
        """Create a new user profile.

        Args:
            user_profile: UserProfile schema object

        Returns:
            Created UserProfileModel instance
        """
        try:
            user_model = UserProfileModel(
                user_id=user_profile.user_id,
                name=user_profile.name,
                preferences=user_profile.preferences,
                conversation_summary=user_profile.conversation_summary,
                key_facts=user_profile.key_facts,
                first_interaction=user_profile.first_interaction,
                last_interaction=user_profile.last_interaction,
                total_messages=user_profile.total_messages,
            )
            self.session.add(user_model)
            await self.session.flush()
            await self.session.refresh(user_model)
            logger.info(f"Created user profile: {user_profile.user_id}")
            return user_model
        except Exception as e:
            logger.error(f"Error creating user {user_profile.user_id}: {e}")
            raise

    async def update_user(self, user_id: str, updates: dict[str, Any]) -> UserProfileModel:
        """Update user profile.

        Args:
            user_id: Unique user identifier
            updates: Dictionary of field updates

        Returns:
            Updated UserProfileModel instance

        Raises:
            ValueError: If user not found
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                    # Flag JSON fields as modified
                    if key in ['key_facts', 'preferences']:
                        attributes.flag_modified(user, key)

            await self.session.flush()
            await self.session.refresh(user)
            logger.info(f"Updated user {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def get_or_create_user(self, user_id: str) -> UserProfileModel:
        """Get existing user or create new one.

        Args:
            user_id: Unique user identifier

        Returns:
            UserProfileModel instance
        """
        user = await self.get_user_by_id(user_id)
        if user:
            return user

        # Create new user with defaults
        now = datetime.now(timezone.utc)
        new_user_profile = UserProfile(
            user_id=user_id,
            name=None,
            preferences={},
            conversation_summary="",
            key_facts=[],
            first_interaction=now,
            last_interaction=now,
            total_messages=0,
        )
        return await self.create_user(new_user_profile)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user profile.

        Args:
            user_id: Unique user identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.session.execute(
                delete(UserProfileModel).where(UserProfileModel.user_id == user_id)
            )
            await self.session.flush()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted user {user_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise


class ConversationRepository:
    """Repository for conversation history operations."""

    def __init__(self, session: AsyncSession):
        """Initialize conversation repository.

        Args:
            session: Async database session
        """
        self.session = session

    async def get_conversation(self, session_id: str) -> ConversationHistoryModel | None:
        """Get conversation by session ID.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationHistoryModel if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(ConversationHistoryModel).where(
                    ConversationHistoryModel.session_id == session_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching conversation {session_id}: {e}")
            raise

    async def create_conversation(
        self, session_id: str, user_id: str
    ) -> ConversationHistoryModel:
        """Create a new conversation.

        Args:
            session_id: Unique session identifier
            user_id: User identifier

        Returns:
            Created ConversationHistoryModel instance
        """
        try:
            conversation = ConversationHistoryModel(
                session_id=session_id, user_id=user_id, messages=[]
            )
            self.session.add(conversation)
            await self.session.flush()
            await self.session.refresh(conversation)
            logger.info(f"Created conversation {session_id} for user {user_id}")
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation {session_id}: {e}")
            raise

    async def append_message(self, session_id: str, message: Message) -> None:
        """Append a message to conversation.

        Args:
            session_id: Unique session identifier
            message: Message to append

        Raises:
            ValueError: If conversation not found
        """
        try:
            conversation = await self.get_conversation(session_id)
            if not conversation:
                raise ValueError(f"Conversation {session_id} not found")

            message_dict = {
                "role": message.role.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "metadata": message.metadata,
            }
            conversation.messages.append(message_dict)
            # Force SQLAlchemy to detect the JSON field change
            attributes.flag_modified(conversation, "messages")
            self.session.add(conversation)
            await self.session.flush()
            logger.debug(f"Appended message to conversation {session_id}")
        except Exception as e:
            logger.error(f"Error appending message to {session_id}: {e}")
            raise

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> list[Message]:
        """Get recent messages from conversation.

        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to return

        Returns:
            List of Message objects
        """
        try:
            conversation = await self.get_conversation(session_id)
            if not conversation:
                return []

            messages = conversation.messages[-limit:]
            return [
                Message(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                    metadata=msg.get("metadata", {}),
                )
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error getting recent messages from {session_id}: {e}")
            raise

    async def update_conversation(self, session_id: str, messages: list[Message]) -> None:
        """Update conversation with new messages.

        Args:
            session_id: Unique session identifier
            messages: List of messages to set

        Raises:
            ValueError: If conversation not found
        """
        try:
            conversation = await self.get_conversation(session_id)
            if not conversation:
                raise ValueError(f"Conversation {session_id} not found")

            conversation.messages = [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                }
                for msg in messages
            ]
            self.session.add(conversation)
            await self.session.flush()
            logger.info(f"Updated conversation {session_id}")
        except Exception as e:
            logger.error(f"Error updating conversation {session_id}: {e}")
            raise

    async def get_user_conversations(self, user_id: str, limit: int = 50) -> list[ConversationHistoryModel]:
        """Get all conversations for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return

        Returns:
            List of ConversationHistoryModel objects, ordered by most recent first
        """
        try:
            result = await self.session.execute(
                select(ConversationHistoryModel)
                .where(ConversationHistoryModel.user_id == user_id)
                .order_by(ConversationHistoryModel.updated_at.desc())
                .limit(limit)
            )
            conversations = result.scalars().all()
            logger.debug(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return list(conversations)
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            raise

    async def delete_conversation(self, session_id: str) -> bool:
        """Delete conversation.

        Args:
            session_id: Unique session identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.session.execute(
                delete(ConversationHistoryModel).where(
                    ConversationHistoryModel.session_id == session_id
                )
            )
            await self.session.flush()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted conversation {session_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting conversation {session_id}: {e}")
            raise

    async def get_user_recent_messages(self, user_id: str, limit: int = 10, exclude_session: str | None = None) -> list[Message]:
        """Get recent messages from all user's conversations (cross-session).

        Args:
            user_id: User identifier
            limit: Maximum number of messages to return
            exclude_session: Optional session ID to exclude (e.g., current session)

        Returns:
            List of Message objects from most recent conversations, ordered chronologically
        """
        try:
            # Get user's recent conversations
            conversations = await self.get_user_conversations(user_id, limit=5)

            # Collect all messages
            all_messages = []
            for conv in conversations:
                # Skip if this is the excluded session
                if exclude_session and conv.session_id == exclude_session:
                    continue

                for msg in conv.messages:
                    all_messages.append({
                        'message': Message(
                            role=msg["role"],
                            content=msg["content"],
                            timestamp=datetime.fromisoformat(msg["timestamp"]),
                            metadata=msg.get("metadata", {}),
                        ),
                        'timestamp': datetime.fromisoformat(msg["timestamp"])
                    })

            # Sort by timestamp (most recent first) and take the limit
            all_messages.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_messages = [item['message'] for item in all_messages[:limit]]

            # Return in chronological order (oldest first, as expected for conversation context)
            recent_messages.reverse()

            logger.debug(f"Retrieved {len(recent_messages)} recent messages across user {user_id}'s sessions")
            return recent_messages

        except Exception as e:
            logger.error(f"Error getting user recent messages for {user_id}: {e}")
            raise

    async def delete_old_conversations(self, days: int = 30) -> int:
        """Delete conversations older than specified days.

        Args:
            days: Number of days threshold

        Returns:
            Number of conversations deleted
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            result = await self.session.execute(
                delete(ConversationHistoryModel).where(
                    ConversationHistoryModel.updated_at < cutoff_date
                )
            )
            await self.session.flush()
            count = result.rowcount
            logger.info(f"Deleted {count} conversations older than {days} days")
            return count
        except Exception as e:
            logger.error(f"Error deleting old conversations: {e}")
            raise
