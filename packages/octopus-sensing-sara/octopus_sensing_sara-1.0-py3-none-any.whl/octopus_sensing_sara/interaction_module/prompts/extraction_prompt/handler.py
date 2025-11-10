"""Handler for user information extraction prompt generation."""

import logging

from .prompt import extraction_template

logger = logging.getLogger(__name__)


class ExtractionPromptHandler:
    """Handles extraction prompt generation."""

    def __init__(self):
        """Initialize extraction prompt handler."""
        self.template = extraction_template

    def build(self, message: str, current_facts: list[str]) -> str:
        """Build prompt for extracting user information from a message.

        Args:
            message: User message to analyze
            current_facts: Existing facts about the user

        Returns:
            Extraction prompt string
        """
        # Format current facts
        current_facts_text = self._format_facts(current_facts)

        # Format prompt using LangChain template
        prompt_value = self.template.format_prompt(
            message=message,
            current_facts=current_facts_text
        )

        # Convert to string format for LLM
        prompt = prompt_value.to_string()

        logger.debug("Built extraction prompt")
        return prompt

    def _format_facts(self, facts: list[str]) -> str:
        """Format current facts for display.

        Args:
            facts: List of current facts

        Returns:
            Formatted facts string
        """
        if not facts:
            return "None"

        return "\n".join(f"- {fact}" for fact in facts)
