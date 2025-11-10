"""API route handlers."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from octopus_sensing_sara.api.dependencies import get_db_session
from octopus_sensing_sara.core.config import get_settings
from octopus_sensing_sara.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationSummary,
    DeleteResponse,
    HealthResponse,
    Message,
    UserProfile,
)
from octopus_sensing_sara.services.conversation_service import ConversationService
from octopus_sensing_sara.services.memory_service import MemoryService
from octopus_sensing_sara.services.user_service import UserService
from octopus_sensing_sara.storage.repositories import ConversationRepository, UserRepository

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse: System health status

    Example:
        GET /health
        Response: {"status": "healthy", "timestamp": "2024-01-01T12:00:00", "version": "1.0.0"}
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy", timestamp=datetime.now(), version=settings.app_version
    )


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest, session: AsyncSession = Depends(get_db_session)
) -> ChatResponse:
    """Process a chat message.

    Args:
        request: Chat request with user message
        session: Database session

    Returns:
        ChatResponse: Assistant's response

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors

    Example:
        POST /chat
        Body: {
            "user_id": "user123",
            "message": "Hello, how are you?"
        }
        Response: {
            "session_id": "user123_20240101_120000",
            "message": "I'm doing well, thank you!",
            "timestamp": "2024-01-01T12:00:01"
        }
    """
    try:
        # Import here to avoid circular imports
        from octopus_sensing_sara.api.dependencies import _create_service

        settings = get_settings()
        conversation_service = await _create_service(session, settings)

        # Process the message
        response = await conversation_service.process_message(request)

        logger.info(
            f"Chat successful: user={request.user_id}, session={response.session_id}"
        )
        return response

    except ValueError as e:
        logger.warning(f"Validation error in chat: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again.",
        )


@router.get("/user/{user_id}/profile", response_model=UserProfile, tags=["Users"])
async def get_user_profile(
    user_id: str, session: AsyncSession = Depends(get_db_session)
) -> UserProfile:
    """Get user profile.

    Args:
        user_id: User identifier
        session: Database session

    Returns:
        UserProfile: User profile data

    Raises:
        HTTPException: 404 if user not found

    Example:
        GET /user/user123/profile
        Response: {
            "user_id": "user123",
            "name": "John Doe",
            "preferences": {},
            "conversation_summary": "...",
            "key_facts": ["Likes Python"],
            ...
        }
    """
    try:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)

        user_profile = await user_service.get_or_create_user_profile(user_id)

        logger.info(f"Retrieved profile for user {user_id}")
        return user_profile

    except Exception as e:
        logger.error(f"Error getting user profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.delete("/user/{user_id}/profile", response_model=DeleteResponse, tags=["Users"])
async def delete_user_profile(
    user_id: str, session: AsyncSession = Depends(get_db_session)
) -> DeleteResponse:
    """Delete user profile and all associated data.

    Args:
        user_id: User identifier
        session: Database session

    Returns:
        DeleteResponse: Deletion confirmation

    Raises:
        HTTPException: 404 if user not found

    Example:
        DELETE /user/user123/profile
        Response: {
            "message": "User user123 deleted successfully",
            "timestamp": "2024-01-01T12:00:00"
        }
    """
    try:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)

        deleted = await user_service.delete_user(user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
            )

        logger.info(f"Deleted user {user_id}")
        return DeleteResponse(
            message=f"User {user_id} deleted successfully", timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user profile",
        )


@router.get("/conversation/{session_id}", response_model=list[Message], tags=["Conversations"])
async def get_conversation(
    session_id: str, session: AsyncSession = Depends(get_db_session)
) -> list[Message]:
    """Get conversation history.

    Args:
        session_id: Session identifier
        session: Database session

    Returns:
        List of messages in the conversation

    Raises:
        HTTPException: 404 if conversation not found

    Example:
        GET /conversation/user123_20240101_120000
        Response: [
            {
                "role": "user",
                "content": "Hello!",
                "timestamp": "2024-01-01T12:00:00"
            },
            {
                "role": "assistant",
                "content": "Hi there!",
                "timestamp": "2024-01-01T12:00:01"
            }
        ]
    """
    try:
        conversation_repository = ConversationRepository(session)

        # Get conversation
        conversation = await conversation_repository.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {session_id} not found",
            )

        # Get recent messages (or all)
        messages = await conversation_repository.get_recent_messages(
            session_id, limit=1000
        )  # Large limit to get all

        logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
        return messages

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation",
        )


@router.post(
    "/conversation/{session_id}/close", tags=["Conversations"]
)
async def close_session(
    session_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Close a session and create a summary.

    This endpoint should be called when a user finishes a conversation session.
    It will:
    1. Summarize all messages in the session
    2. Extract and save key facts
    3. Store the summary for future sessions (max 5 recent summaries kept)

    Args:
        session_id: Session identifier
        user_id: User identifier
        session: Database session

    Returns:
        Dictionary with summary information

    Example:
        POST /conversation/user123_20250107_140000/close?user_id=user123
        Response: {
            "success": true,
            "summary": "User discussed Python programming...",
            "message_count": 12,
            "session_id": "user123_20250107_140000"
        }
    """
    try:
        from octopus_sensing_sara.api.dependencies import _create_service

        settings = get_settings()
        conversation_service = await _create_service(session, settings)

        # Summarize and close the session
        result = await conversation_service.summarize_and_close_session(user_id, session_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to close session"),
            )

        logger.info(f"Closed session {session_id} for user {user_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close session",
        )


@router.delete(
    "/conversation/{session_id}", response_model=DeleteResponse, tags=["Conversations"]
)
async def delete_conversation(
    session_id: str, session: AsyncSession = Depends(get_db_session)
) -> DeleteResponse:
    """Delete a conversation.

    Args:
        session_id: Session identifier
        session: Database session

    Returns:
        DeleteResponse: Deletion confirmation

    Raises:
        HTTPException: 404 if conversation not found

    Example:
        DELETE /conversation/user123_20240101_120000
        Response: {
            "message": "Conversation deleted successfully",
            "timestamp": "2024-01-01T12:00:00"
        }
    """
    try:
        conversation_repository = ConversationRepository(session)
        settings = get_settings()

        # Create memory service to clear from cache
        user_repository = UserRepository(session)
        memory_service = MemoryService(user_repository, conversation_repository, settings)

        # Clear from both cache and database
        deleted = await memory_service.clear_session(session_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {session_id} not found",
            )

        logger.info(f"Deleted conversation {session_id}")
        return DeleteResponse(
            message="Conversation deleted successfully", timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )


@router.get("/user/{user_id}/conversations", response_model=ConversationListResponse, tags=["Conversations"])
async def get_user_conversations(
    user_id: str,
    limit: int = 50,
    session: AsyncSession = Depends(get_db_session)
) -> ConversationListResponse:
    """Get all conversations for a user.

    Args:
        user_id: User identifier
        limit: Maximum number of conversations to return (default: 50)
        session: Database session

    Returns:
        ConversationListResponse: List of user's conversations

    Example:
        GET /user/user123/conversations?limit=20
        Response: {
            "conversations": [...],
            "total": 20
        }
    """
    try:
        conversation_repository = ConversationRepository(session)

        # Get all conversations for the user
        conversations = await conversation_repository.get_user_conversations(user_id, limit)

        # Build conversation summaries
        summaries = []
        for conv in conversations:
            # Get first user message as title
            title = "New Conversation"
            last_message_preview = ""
            message_count = len(conv.messages)

            if conv.messages:
                # Find first user message for title
                for msg in conv.messages:
                    if msg.get("role") == "user":
                        # Use first 50 chars of first user message as title
                        content = msg.get("content", "")
                        title = content[:50] + ("..." if len(content) > 50 else "")
                        break

                # Get last message for preview
                last_msg = conv.messages[-1]
                last_message_preview = last_msg.get("content", "")[:100]
                if len(last_msg.get("content", "")) > 100:
                    last_message_preview += "..."

            summary = ConversationSummary(
                session_id=conv.session_id,
                user_id=conv.user_id,
                title=title,
                message_count=message_count,
                last_message_preview=last_message_preview,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
            summaries.append(summary)

        logger.info(f"Retrieved {len(summaries)} conversations for user {user_id}")
        return ConversationListResponse(
            conversations=summaries,
            total=len(summaries)
        )

    except Exception as e:
        logger.error(f"Error getting conversations for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        )
