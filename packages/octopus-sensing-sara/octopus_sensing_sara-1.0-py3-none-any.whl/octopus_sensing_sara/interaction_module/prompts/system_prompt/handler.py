"""Handler for system prompt generation."""

import logging
from typing import Optional

from octopus_sensing_sara.models.schemas import UserProfile
from .prompt import SYSTEM_PROMPT, USER_CONTEXT_TEMPLATE

logger = logging.getLogger(__name__)


class SystemPromptHandler:
    """Handles system prompt generation with user context."""

    def __init__(self, bot_name: str = "Assistant", bot_personality: str = "helpful, friendly, and knowledgeable"):
        """Initialize system prompt handler.

        Args:
            bot_name: Name of the bot
            bot_personality: Personality description of the bot
        """
        self.bot_name = bot_name
        self.bot_personality = bot_personality

    def build(self, user_profile: Optional[UserProfile] = None) -> str:
        """Build system prompt with optional user context.

        Args:
            user_profile: Optional user profile for personalization

        Returns:
            Formatted system prompt string
        """
        # Format base prompt with bot details
        prompt = SYSTEM_PROMPT.format(
            bot_name=self.bot_name,
            bot_personality=self.bot_personality
        )

        # Add user context if available
        if user_profile:
            user_context = self._build_user_context(user_profile)
            if user_context:
                prompt += USER_CONTEXT_TEMPLATE.format(user_context=user_context)

        logger.debug(f"Built system prompt for bot: {self.bot_name}")
        return prompt

    def _build_user_context(self, user_profile: UserProfile) -> str:
        """Build user context section of the prompt.

        Args:
            user_profile: User profile information

        Returns:
            Formatted user context string
        """
        context_parts = []

        # Add user name
        if user_profile.name:
            context_parts.append(f"- The user's name is {user_profile.name}")

        # Add key facts
        if user_profile.key_facts:
            context_parts.append("- Key facts about the user:")
            for fact in user_profile.key_facts[:10]:  # Limit to 10 most recent facts
                context_parts.append(f"  * {fact}")

        # Add preferences
        if user_profile.preferences:
            context_parts.append("- User preferences:")
            for key, value in user_profile.preferences.items():
                context_parts.append(f"  * {key}: {value}")

        # Add recent session summaries (most important for continuity!)
        if hasattr(user_profile, 'session_summaries') and user_profile.session_summaries:
            context_parts.append("- Recent conversation sessions:")
            for i, session in enumerate(user_profile.session_summaries[:5], 1):
                summary = session.get('summary', '')
                msg_count = session.get('message_count', 0)
                context_parts.append(f"  Session {i}: {summary} ({msg_count} messages)")

        # Add overall conversation summary (if exists)
        if user_profile.conversation_summary:
            context_parts.append(f"- Overall history: {user_profile.conversation_summary}")

        # Only return if we have content
        if context_parts:
            return "\n".join(context_parts)
        return ""
