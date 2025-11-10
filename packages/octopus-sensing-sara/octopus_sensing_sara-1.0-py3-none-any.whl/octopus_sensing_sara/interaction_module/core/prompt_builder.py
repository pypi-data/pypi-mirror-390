"""Prompt building system for LLM interactions.

This module provides a unified interface to the modular prompt system.
Individual prompts are stored in the app/prompts/ directory, with each
prompt type having its own folder containing:
- prompt.txt: The actual prompt template
- handler.py: Code to process variables and build the final prompt
"""

import logging
from typing import Optional

from octopus_sensing_sara.models.schemas import Message, UserProfile
from octopus_sensing_sara.prompts.system_prompt import SystemPromptHandler
from octopus_sensing_sara.prompts.summarization_prompt import SummarizationPromptHandler
from octopus_sensing_sara.prompts.extraction_prompt import ExtractionPromptHandler

logger = logging.getLogger(__name__)


class ConversationalPromptBuilder:
    """Builds prompts for conversational AI interactions.

    This class acts as a facade to the modular prompt system, providing
    a simple interface while keeping prompts organized in separate modules.
    """

    def __init__(
        self,
        bot_name: str = "Assistant",
        bot_personality: str = "helpful, friendly, and knowledgeable",
    ):
        """Initialize prompt builder.

        Args:
            bot_name: Name of the bot
            bot_personality: Personality description of the bot
        """
        self.bot_name = bot_name
        self.bot_personality = bot_personality

        # Initialize prompt handlers
        self.system_prompt_handler = SystemPromptHandler(
            bot_name=bot_name,
            bot_personality=bot_personality
        )
        self.summarization_prompt_handler = SummarizationPromptHandler()
        self.extraction_prompt_handler = ExtractionPromptHandler()

        logger.info(f"Initialized ConversationalPromptBuilder for '{bot_name}'")

    def build_system_prompt(self, user_profile: Optional[UserProfile] = None) -> str:
        """Build system prompt with optional user context.

        Args:
            user_profile: Optional user profile for personalization

        Returns:
            Formatted system prompt string

        Example:
            >>> builder = ConversationalPromptBuilder()
            >>> prompt = builder.build_system_prompt(user_profile)
        """
        return self.system_prompt_handler.build(user_profile)

    def build_conversation_prompt(
        self, messages: list[Message], user_profile: Optional[UserProfile] = None
    ) -> list[dict[str, str]]:
        """Build complete conversation prompt for LLM.

        Args:
            messages: List of conversation messages
            user_profile: Optional user profile for context

        Returns:
            List of message dictionaries in LangChain format

        Example:
            >>> builder = ConversationalPromptBuilder()
            >>> messages = [Message(role="user", content="Hello!")]
            >>> prompt = builder.build_conversation_prompt(messages)
            [
                {"role": "system", "content": "You are..."},
                {"role": "user", "content": "Hello!"}
            ]
        """
        # Start with system prompt
        prompt_messages = [
            {"role": "system", "content": self.build_system_prompt(user_profile)}
        ]

        # Add conversation history
        for msg in messages:
            prompt_messages.append({"role": msg.role.value, "content": msg.content})

        logger.debug(f"Built conversation prompt with {len(prompt_messages)} messages")
        return prompt_messages

    def build_summarization_prompt(self, messages: list[Message]) -> str:
        """Build prompt for conversation summarization.

        Args:
            messages: List of conversation messages

        Returns:
            Summarization prompt string

        Example:
            >>> builder = ConversationalPromptBuilder()
            >>> prompt = builder.build_summarization_prompt(messages)
        """
        return self.summarization_prompt_handler.build(messages)

    def build_extraction_prompt(self, message: str, current_facts: list[str]) -> str:
        """Build prompt for extracting user information from a message.

        Args:
            message: User message to analyze
            current_facts: Existing facts about the user

        Returns:
            Extraction prompt string
        """
        return self.extraction_prompt_handler.build(message, current_facts)
