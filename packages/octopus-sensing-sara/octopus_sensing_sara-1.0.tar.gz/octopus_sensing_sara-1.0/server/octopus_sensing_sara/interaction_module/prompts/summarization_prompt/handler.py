"""Handler for conversation summarization prompt generation."""

import logging

from octopus_sensing_sara.models.schemas import Message
from .prompt import summarization_template

logger = logging.getLogger(__name__)


class SummarizationPromptHandler:
    """Handles summarization prompt generation."""

    def __init__(self):
        """Initialize summarization prompt handler."""
        self.template = summarization_template

    def build(self, messages: list[Message]) -> str:
        """Build prompt for conversation summarization.

        Args:
            messages: List of conversation messages

        Returns:
            Summarization prompt string
        """
        # Format conversation history
        conversation_text = self._format_messages(messages)

        # Format prompt using LangChain template
        prompt_value = self.template.format_prompt(conversation_text=conversation_text)

        # Convert to string format for LLM
        prompt = prompt_value.to_string()

        logger.debug(f"Built summarization prompt for {len(messages)} messages")
        return prompt

    def _format_messages(self, messages: list[Message]) -> str:
        """Format messages for summarization.

        Args:
            messages: List of messages

        Returns:
            Formatted conversation string
        """
        formatted = []
        for msg in messages:
            role = msg.role.value.capitalize()
            content = msg.content
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)
