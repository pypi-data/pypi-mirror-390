"""FastAPI dependency injection functions."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from octopus_sensing_sara.core.config import get_settings
from octopus_sensing_sara.core.llm_factory import LLMFactory
from octopus_sensing_sara.core.prompt_builder import ConversationalPromptBuilder
from octopus_sensing_sara.services.conversation_service import ConversationService
from octopus_sensing_sara.services.memory_service import MemoryService
from octopus_sensing_sara.services.user_service import UserService
from octopus_sensing_sara.storage.database import DatabaseManager
from octopus_sensing_sara.storage.repositories import ConversationRepository, UserRepository

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with DatabaseManager.get_session() as session:
        yield session


async def get_conversation_service(
    session: AsyncSession = None,
) -> ConversationService:
    """Get conversation service dependency.

    Creates and configures all required services and dependencies.

    Args:
        session: Optional database session (for testing)

    Returns:
        ConversationService: Configured conversation service

    Raises:
        RuntimeError: If service initialization fails

    Example:
        @app.post("/chat")
        async def chat(
            request: ChatRequest,
            service: ConversationService = Depends(get_conversation_service)
        ):
            return await service.process_message(request)
    """
    try:
        # Get settings
        settings = get_settings()
        logger.debug("Initializing conversation service")

        # Create or use provided session
        if session is None:
            async with DatabaseManager.get_session() as db_session:
                return await _create_service(db_session, settings)
        else:
            return await _create_service(session, settings)

    except Exception as e:
        logger.error(f"Failed to create conversation service: {e}")
        raise RuntimeError(f"Service initialization failed: {e}") from e


async def _create_service(session: AsyncSession, settings) -> ConversationService:
    """Internal helper to create conversation service.

    Args:
        session: Database session
        settings: Application settings

    Returns:
        ConversationService: Configured service
    """
    # Create LLMs
    llm = LLMFactory.create_llm(settings)
    summarization_llm = LLMFactory.create_summarization_llm(settings)

    # Create repositories
    user_repository = UserRepository(session)
    conversation_repository = ConversationRepository(session)

    # Create services
    user_service = UserService(user_repository, llm=None)
    memory_service = MemoryService(user_repository, conversation_repository, settings)
    prompt_builder = ConversationalPromptBuilder(
        bot_name=settings.app_name, bot_personality="helpful, friendly, and knowledgeable"
    )

    # Create conversation service
    conversation_service = ConversationService(
        llm=llm,
        memory_service=memory_service,
        user_service=user_service,
        prompt_builder=prompt_builder,
        summarization_llm=summarization_llm,
        settings=settings,
    )

    logger.debug("Conversation service created successfully")
    return conversation_service


# Singleton services (cached across requests)
_service_cache: dict[str, ConversationService] = {}


async def get_cached_conversation_service() -> ConversationService:
    """Get cached conversation service (singleton pattern).

    This is more efficient for production use as it reuses the same
    service instance across requests.

    Returns:
        ConversationService: Cached conversation service

    Note:
        This creates a new database session for each request but reuses
        the service components (LLMs, memory cache, etc.)
    """
    cache_key = "main_service"

    if cache_key not in _service_cache:
        async with DatabaseManager.get_session() as session:
            settings = get_settings()
            _service_cache[cache_key] = await _create_service(session, settings)
            logger.info("Created and cached conversation service")

    return _service_cache[cache_key]


def clear_service_cache() -> None:
    """Clear the service cache.

    Useful for testing or when configuration changes.
    """
    global _service_cache
    _service_cache.clear()
    logger.info("Service cache cleared")
