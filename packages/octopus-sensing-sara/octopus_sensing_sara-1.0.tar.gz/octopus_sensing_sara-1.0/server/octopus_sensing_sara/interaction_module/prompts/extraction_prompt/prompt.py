"""Extraction prompt templates using LangChain format."""

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# System prompt for extraction task
EXTRACTION_SYSTEM_PROMPT = """You are an expert at extracting user information from messages.

Extract:
1. Name (if mentioned)
2. Preferences or likes/dislikes
3. Personal information
4. Interests or hobbies

Only extract information that is explicitly stated. Do not make assumptions."""

# Human prompt template with user message and current facts
EXTRACTION_HUMAN_PROMPT = """User message: "{message}"

Current known facts:
{current_facts}

Format your response as JSON:
{{
    "name": "user's name or null",
    "new_facts": ["fact1", "fact2"],
    "preferences": {{"preference_key": "value"}}
}}"""

# Create message prompt templates
extraction_system_prompt = SystemMessagePromptTemplate.from_template(
    template=EXTRACTION_SYSTEM_PROMPT,
)

extraction_human_prompt = HumanMessagePromptTemplate.from_template(
    template=EXTRACTION_HUMAN_PROMPT,
)

# Create complete chat prompt template
extraction_template = ChatPromptTemplate.from_messages(
    messages=[
        extraction_system_prompt,
        extraction_human_prompt,
    ],
)
