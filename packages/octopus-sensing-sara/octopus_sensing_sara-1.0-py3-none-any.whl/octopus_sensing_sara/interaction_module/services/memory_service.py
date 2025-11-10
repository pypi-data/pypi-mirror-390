"""Memory management service using LangChain."""

import logging
from datetime import datetime

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from octopus_sensing_sara.core.config import Settings
from octopus_sensing_sara.models.schemas import Message, MessageRole, UserProfile
from octopus_sensing_sara.storage.repositories import ConversationRepository, UserRepository

logger = logging.getLogger(__name__)


class MemoryService:
    """Manages conversation memory using LangChain and database persistence."""

    def __init__(
        self,
        user_repository: UserRepository,
        conversation_repository: ConversationRepository,
        settings: Settings,
    ):
        """Initialize memory service.

        Args:
            user_repository: Repository for user operations
            conversation_repository: Repository for conversation operations
            settings: Application settings
        """
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
        self.settings = settings
        self._memory_cache: dict[str, ConversationBufferWindowMemory] = {}

    def get_or_create_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Get or create LangChain memory for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationBufferWindowMemory instance

        Example:
            >>> memory = service.get_or_create_memory("session_123")
            >>> memory.chat_memory.add_user_message("Hello!")
        """
        # Check cache first
        if session_id in self._memory_cache:
            logger.debug(f"Using cached memory for session {session_id}")
            return self._memory_cache[session_id]

        # Create new memory with window size from settings
        memory = ConversationBufferWindowMemory(
            k=self.settings.short_term_memory_window,
            return_messages=True,
            memory_key="chat_history",
        )

        # Cache it
        self._memory_cache[session_id] = memory
        logger.info(f"Created new memory for session {session_id}")

        return memory

    async def load_memory_from_db(
        self, session_id: str, memory: ConversationBufferWindowMemory
    ) -> None:
        """Load existing messages from database into LangChain memory.

        Args:
            session_id: Unique session identifier
            memory: LangChain memory instance to populate
        """
        try:
            # Get recent messages from database
            messages = await self.conversation_repository.get_recent_messages(
                session_id, limit=self.settings.short_term_memory_window
            )

            # Add messages to LangChain memory
            for msg in messages:
                if msg.role == MessageRole.USER:
                    memory.chat_memory.add_message(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    memory.chat_memory.add_message(AIMessage(content=msg.content))
                elif msg.role == MessageRole.SYSTEM:
                    memory.chat_memory.add_message(SystemMessage(content=msg.content))

            logger.info(f"Loaded {len(messages)} messages into memory for session {session_id}")
        except Exception as e:
            logger.error(f"Error loading memory from database: {e}")
            # Don't raise - we can continue with empty memory

    async def save_interaction(
        self, session_id: str, user_id: str, user_msg: Message, assistant_msg: Message
    ) -> None:
        """Save a conversation interaction to database and memory.

        Args:
            session_id: Unique session identifier
            user_id: User identifier
            user_msg: User's message
            assistant_msg: Assistant's response

        Example:
            >>> await service.save_interaction(
            ...     "session_123",
            ...     "user_456",
            ...     Message(role=MessageRole.USER, content="Hello"),
            ...     Message(role=MessageRole.ASSISTANT, content="Hi there!")
            ... )
        """
        try:
            # Save to long-term database
            conversation = await self.conversation_repository.get_conversation(session_id)
            if not conversation:
                conversation = await self.conversation_repository.create_conversation(
                    session_id, user_id
                )

            # Save messages to database
            await self.conversation_repository.append_message(session_id, user_msg)
            await self.conversation_repository.append_message(session_id, assistant_msg)

            # Update short-term memory
            memory = self.get_or_create_memory(session_id)
            memory.chat_memory.add_user_message(user_msg.content)
            memory.chat_memory.add_ai_message(assistant_msg.content)

            # Update user stats
            await self._update_user_stats(user_id)
        except Exception as e:
            logger.error(f"│  ✗ Error saving interaction: {e}")
            raise

    async def _update_user_stats(self, user_id: str) -> None:
        """Update user statistics.

        Args:
            user_id: User identifier
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if user:
                await self.user_repository.update_user(
                    user_id,
                    {
                        "last_interaction": datetime.now(),
                        "total_messages": user.total_messages + 2,  # +2 for user and assistant
                    },
                )
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
            # Don't raise - stats update failure shouldn't break the flow

    async def get_conversation_context(
        self, user_id: str, session_id: str
    ) -> tuple[UserProfile | None, list[Message]]:
        """Get conversation context including user profile and recent messages.

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Tuple of (user_profile, recent_messages)

        Example:
            >>> profile, messages = await service.get_conversation_context("user_123", "session_456")
        """
        try:
            # Get user profile with session summaries
            user_model = await self.user_repository.get_user_by_id(user_id)
            user_profile = None
            if user_model:
                user_profile = UserProfile(
                    user_id=user_model.user_id,
                    name=user_model.name,
                    preferences=user_model.preferences,
                    conversation_summary=user_model.conversation_summary,
                    key_facts=user_model.key_facts,
                    session_summaries=user_model.session_summaries if hasattr(user_model, 'session_summaries') else [],
                    first_interaction=user_model.first_interaction,
                    last_interaction=user_model.last_interaction,
                    total_messages=user_model.total_messages,
                )
                if user_profile.session_summaries:
                    for i, sess in enumerate(user_profile.session_summaries[:3], 1):
                        summary_preview = sess.get('summary', '')[:60]
                        logger.debug(f"│     Session {i}: {summary_preview}...")

            # Get recent messages from current session only
            memory = self.get_or_create_memory(session_id)

            # Load from database if memory is empty
            if not memory.chat_memory.messages:
                await self.load_memory_from_db(session_id, memory)

            # Convert LangChain messages to our Message schema
            messages = []
            for msg in memory.chat_memory.messages:
                if isinstance(msg, HumanMessage):
                    role = MessageRole.USER
                elif isinstance(msg, AIMessage):
                    role = MessageRole.ASSISTANT
                elif isinstance(msg, SystemMessage):
                    role = MessageRole.SYSTEM
                else:
                    continue

                messages.append(
                    Message(
                        role=role,
                        content=msg.content,
                        timestamp=datetime.now(),  # Use current time as LangChain doesn't store timestamps
                    )
                )

            return user_profile, messages

        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            raise

    def clear_memory(self, session_id: str) -> None:
        """Clear memory for a session.

        Args:
            session_id: Session identifier to clear

        Example:
            >>> service.clear_memory("session_123")
        """
        if session_id in self._memory_cache:
            del self._memory_cache[session_id]
            logger.info(f"Cleared memory cache for session {session_id}")

    async def clear_session(self, session_id: str) -> bool:
        """Clear session from both memory and database.

        Args:
            session_id: Session identifier to clear

        Returns:
            True if session was deleted, False if not found
        """
        try:
            # Clear from cache
            self.clear_memory(session_id)

            # Delete from database
            deleted = await self.conversation_repository.delete_conversation(session_id)

            if deleted:
                logger.info(f"Cleared session {session_id} from memory and database")
            return deleted
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            raise

    def get_memory_stats(self) -> dict[str, int]:
        """Get statistics about cached memories.

        Returns:
            Dictionary with memory statistics
        """
        return {
            "cached_sessions": len(self._memory_cache),
            "total_messages": sum(
                len(mem.chat_memory.messages) for mem in self._memory_cache.values()
            ),
        }
