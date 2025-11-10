"""Summarization prompt templates using LangChain format."""

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# System prompt for summarization task
SUMMARIZATION_SYSTEM_PROMPT = """Analyze the following conversation and provide a structured summary.

Please provide:
1. A concise summary of the conversation (max 200 words)
2. Key facts about the user (preferences, interests, personal information)
3. Main topics discussed

Focus on extracting actionable information that will help personalize future interactions."""

# Human prompt template with conversation
SUMMARIZATION_HUMAN_PROMPT = """Conversation:
{conversation_text}

Format your response as JSON:
{{
    "summary": "Brief summary of the conversation",
    "key_facts": ["fact1", "fact2", "fact3"],
    "topics": ["topic1", "topic2", "topic3"]
}}"""

# Create message prompt templates
summarization_system_prompt = SystemMessagePromptTemplate.from_template(
    template=SUMMARIZATION_SYSTEM_PROMPT,
)

summarization_human_prompt = HumanMessagePromptTemplate.from_template(
    template=SUMMARIZATION_HUMAN_PROMPT,
)

# Create complete chat prompt template
summarization_template = ChatPromptTemplate.from_messages(
    messages=[
        summarization_system_prompt,
        summarization_human_prompt,
    ],
)
