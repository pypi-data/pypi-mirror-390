"""User profile management service."""

import json
import logging
import re
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from octopus_sensing_sara.models.schemas import UserProfile
from octopus_sensing_sara.storage.repositories import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Manages user profiles and information extraction."""

    def __init__(self, user_repository: UserRepository, llm: BaseChatModel | None = None):
        """Initialize user service.

        Args:
            user_repository: Repository for user operations
            llm: Optional LLM for advanced extraction (not implemented yet)
        """
        self.user_repository = user_repository
        self.llm = llm

    async def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one.

        Args:
            user_id: Unique user identifier

        Returns:
            UserProfile schema object

        Example:
            >>> profile = await service.get_or_create_user_profile("user_123")
        """
        try:
            user_model = await self.user_repository.get_or_create_user(user_id)

            return UserProfile(
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
        except Exception as e:
            logger.error(f"Error getting/creating user profile: {e}")
            raise

    async def update_user_stats(self, user_id: str) -> None:
        """Update user interaction statistics.

        Args:
            user_id: User identifier
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if user:
                from datetime import datetime

                await self.user_repository.update_user(
                    user_id,
                    {
                        "last_interaction": datetime.now(),
                        "total_messages": user.total_messages + 1,
                    },
                )
                logger.debug(f"Updated stats for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
            # Don't raise - stats update is not critical

    async def extract_user_info(
        self, message: str, current_profile: UserProfile
    ) -> dict[str, Any]:
        """Extract user information from message using pattern matching.

        Args:
            message: User message to analyze
            current_profile: Current user profile

        Returns:
            Dictionary with extracted information: {
                "name": str or None,
                "new_facts": list[str],
                "preferences": dict[str, Any]
            }

        Example:
            >>> info = await service.extract_user_info(
            ...     "My name is John and I like Python",
            ...     user_profile
            ... )
            >>> print(info)
            {"name": "John", "new_facts": ["Likes Python"], "preferences": {}}
        """
        extracted = {"name": None, "new_facts": [], "preferences": {}}

        try:
            logger.info(f"🔍 Running pattern matching on user message...")
            # Extract name patterns
            name_patterns = [
                r"my name is (\w+)",
                r"i'm (\w+)",
                r"i am (\w+)",
                r"call me (\w+)",
                r"this is (\w+)",
            ]

            for pattern in name_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    extracted["name"] = match.group(1).capitalize()
                    logger.info(f"✅ Name pattern matched: '{pattern}' -> '{extracted['name']}'")
                    break

            # Extract preferences (likes/dislikes)
            preference_patterns = [
                (r"i like (\w+)", "likes"),
                (r"i love (\w+)", "loves"),
                (r"i prefer (\w+)", "prefers"),
                (r"i enjoy (\w+)", "enjoys"),
                (r"i hate (\w+)", "dislikes"),
                (r"i don't like (\w+)", "dislikes"),
            ]

            for pattern, pref_type in preference_patterns:
                matches = re.finditer(pattern, message.lower())
                for match in matches:
                    item = match.group(1)
                    extracted["new_facts"].append(f"{pref_type.capitalize()} {item}")
                    logger.info(f"✅ Preference pattern matched: '{pattern}' -> '{pref_type} {item}'")

            # Extract common personal information patterns
            personal_patterns = [
                (r"i work as (?:a |an )?(\w+)", "Works as"),
                (r"i'm (?:a |an )?(\w+ (?:engineer|developer|designer|manager|teacher|student))", "Occupation"),
                (r"i live in (\w+)", "Lives in"),
                (r"i'm from (\w+)", "From"),
                (r"i'm (\d+) years old", "Age"),
            ]

            for pattern, fact_type in personal_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    value = match.group(1)
                    extracted["new_facts"].append(f"{fact_type}: {value}")
                    logger.info(f"✅ Personal info pattern matched: '{pattern}' -> '{fact_type}: {value}'")

            # Log extraction summary
            total_extracted = len(extracted["new_facts"]) + (1 if extracted["name"] else 0)
            if total_extracted > 0:
                logger.info(f"📊 Extraction complete: {total_extracted} items found")
                logger.info(f"   Name: {extracted['name'] or 'None'}")
                logger.info(f"   Facts: {extracted['new_facts']}")
            else:
                logger.info(f"ℹ️  No extractable information found in message")

        except Exception as e:
            logger.error(f"❌ Error extracting user info: {e}")
            # Return empty extraction on error

        return extracted

    async def add_key_fact(self, user_id: str, fact: str) -> None:
        """Add a key fact to user profile.

        Args:
            user_id: User identifier
            fact: Fact to add

        Example:
            >>> await service.add_key_fact("user_123", "Enjoys hiking")
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found, cannot add fact")
                return

            # Get current facts
            key_facts = list(user.key_facts) if user.key_facts else []

            # Check if fact already exists (case-insensitive)
            fact_lower = fact.lower()
            if not any(existing.lower() == fact_lower for existing in key_facts):
                key_facts.append(fact)

                # Keep only the 10 most recent facts
                if len(key_facts) > 10:
                    key_facts = key_facts[-10:]

                await self.user_repository.update_user(user_id, {"key_facts": key_facts})
                logger.info(f"Added key fact for user {user_id}: {fact}")
            else:
                logger.debug(f"Fact already exists for user {user_id}: {fact}")

        except Exception as e:
            logger.error(f"Error adding key fact: {e}")
            # Don't raise - fact addition is not critical

    async def update_conversation_summary(self, user_id: str, new_summary: str) -> None:
        """Update user's conversation summary.

        Args:
            user_id: User identifier
            new_summary: New summary text

        Example:
            >>> await service.update_conversation_summary(
            ...     "user_123",
            ...     "User is interested in machine learning and Python"
            ... )
        """
        try:
            await self.user_repository.update_user(
                user_id, {"conversation_summary": new_summary}
            )
            logger.info(f"Updated conversation summary for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating conversation summary: {e}")
            raise

    async def update_preferences(self, user_id: str, preferences: dict[str, Any]) -> None:
        """Update user preferences.

        Args:
            user_id: User identifier
            preferences: Dictionary of preferences to update/add

        Example:
            >>> await service.update_preferences("user_123", {"theme": "dark", "language": "en"})
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found, cannot update preferences")
                return

            # Merge with existing preferences
            current_prefs = dict(user.preferences) if user.preferences else {}
            current_prefs.update(preferences)

            await self.user_repository.update_user(user_id, {"preferences": current_prefs})
            logger.info(f"Updated preferences for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            # Don't raise - preference update is not critical

    async def add_session_summary(
        self, user_id: str, session_id: str, summary: str, message_count: int = 0
    ) -> None:
        """Add a session summary to user profile (keeps max 5 most recent).

        Args:
            user_id: User identifier
            session_id: Session identifier
            summary: Summary of the session
            message_count: Number of messages in the session

        Example:
            >>> await service.add_session_summary(
            ...     "user_123",
            ...     "user_123_20250107_140000",
            ...     "User discussed Python programming best practices",
            ...     12
            ... )
        """
        try:
            from datetime import datetime

            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found, cannot add session summary")
                return

            # Get current session summaries
            session_summaries = list(user.session_summaries) if hasattr(user, 'session_summaries') and user.session_summaries else []

            # Create new session summary
            new_summary = {
                "session_id": session_id,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
                "message_count": message_count,
            }

            # Add to the beginning (most recent first)
            session_summaries.insert(0, new_summary)

            # Keep only the 5 most recent summaries
            session_summaries = session_summaries[:5]

            await self.user_repository.update_user(user_id, {"session_summaries": session_summaries})
            logger.debug(f"Added session summary for {user_id} (total: {len(session_summaries)} summaries)")

        except Exception as e:
            logger.error(f"Error adding session summary: {e}")
            # Don't raise - summary addition is not critical

    async def delete_user(self, user_id: str) -> bool:
        """Delete user profile and all associated data.

        Args:
            user_id: User identifier

        Returns:
            True if deleted, False if not found

        Example:
            >>> deleted = await service.delete_user("user_123")
        """
        try:
            deleted = await self.user_repository.delete_user(user_id)
            if deleted:
                logger.info(f"Deleted user {user_id}")
            else:
                logger.warning(f"User {user_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise
