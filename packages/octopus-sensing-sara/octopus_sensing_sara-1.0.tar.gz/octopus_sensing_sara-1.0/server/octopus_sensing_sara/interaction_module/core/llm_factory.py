"""Factory for creating LLM instances based on provider configuration."""

import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from octopus_sensing_sara.core.config import Settings

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory class for creating LLM instances."""

    @staticmethod
    def create_llm(settings: Settings) -> BaseChatModel:
        """Create an LLM instance based on settings.

        Args:
            settings: Application settings

        Returns:
            BaseChatModel: Configured LLM instance

        Raises:
            ValueError: If provider is unsupported or API key is missing

        Example:
            >>> settings = get_settings()
            >>> llm = LLMFactory.create_llm(settings)
            >>> response = await llm.ainvoke("Hello!")
        """
        provider = settings.llm_provider.lower()

        try:
            if provider == "openai":
                return LLMFactory._create_openai(settings)
            elif provider == "anthropic":
                return LLMFactory._create_anthropic(settings)
            elif provider == "gemini":
                return LLMFactory._create_gemini(settings)
            elif provider == "ollama":
                return LLMFactory._create_ollama(settings)
            else:
                raise ValueError(
                    f"Unsupported LLM provider: {provider}. "
                    f"Supported providers: openai, anthropic, gemini, ollama"
                )
        except Exception as e:
            logger.error(f"Failed to create LLM instance: {e}")
            raise

    @staticmethod
    def create_summarization_llm(settings: Settings) -> BaseChatModel:
        """Create a cheaper/faster LLM for summarization tasks.

        Uses more cost-effective models and lower temperature for consistency.

        Args:
            settings: Application settings

        Returns:
            BaseChatModel: Configured summarization LLM instance

        Raises:
            ValueError: If provider is unsupported or API key is missing
        """
        provider = settings.llm_provider.lower()

        try:
            if provider == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    max_tokens=500,
                    api_key=settings.openai_api_key,
                )
                logger.info("Created OpenAI summarization LLM (gpt-3.5-turbo)")
                return llm

            elif provider == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")

                llm = ChatAnthropic(
                    model="claude-3-haiku-20240307",
                    temperature=0.3,
                    max_tokens=500,
                    api_key=settings.anthropic_api_key,
                )
                logger.info("Created Anthropic summarization LLM (claude-3-haiku)")
                return llm

            elif provider == "gemini":
                if not settings.google_api_key:
                    raise ValueError("GOOGLE_API_KEY is required for Gemini provider")

                llm = ChatGoogleGenerativeAI(
                    model="models/gemini-2.5-flash",
                    temperature=0.3,
                    max_output_tokens=500,
                    google_api_key=settings.google_api_key,
                    convert_system_message_to_human=True,
                )
                logger.info("Created Gemini summarization LLM (models/gemini-2.5-flash)")
                return llm

            elif provider == "ollama":
                llm = ChatOllama(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_model,
                    temperature=0.3,
                )
                logger.info(f"Created Ollama summarization LLM ({settings.ollama_model})")
                return llm

            else:
                raise ValueError(
                    f"Unsupported LLM provider: {provider}. "
                    f"Supported providers: openai, anthropic, gemini, ollama"
                )
        except Exception as e:
            logger.error(f"Failed to create summarization LLM: {e}")
            raise

    @staticmethod
    def _create_openai(settings: Settings) -> ChatOpenAI:
        """Create OpenAI LLM instance.

        Args:
            settings: Application settings

        Returns:
            ChatOpenAI: Configured OpenAI LLM

        Raises:
            ValueError: If API key is missing
        """
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when using OpenAI provider. "
                "Please set it in your .env file."
            )

        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.openai_api_key,
        )
        logger.info(f"Created OpenAI LLM ({settings.llm_model})")
        return llm

    @staticmethod
    def _create_anthropic(settings: Settings) -> ChatAnthropic:
        """Create Anthropic LLM instance.

        Args:
            settings: Application settings

        Returns:
            ChatAnthropic: Configured Anthropic LLM

        Raises:
            ValueError: If API key is missing
        """
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when using Anthropic provider. "
                "Please set it in your .env file."
            )

        llm = ChatAnthropic(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.anthropic_api_key,
        )
        logger.info(f"Created Anthropic LLM ({settings.llm_model})")
        return llm

    @staticmethod
    def _create_gemini(settings: Settings) -> ChatGoogleGenerativeAI:
        """Create Google Gemini LLM instance.

        Args:
            settings: Application settings

        Returns:
            ChatGoogleGenerativeAI: Configured Gemini LLM

        Raises:
            ValueError: If API key is missing
        """
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when using Gemini provider. "
                "Please set it in your .env file."
            )

        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_tokens,
            google_api_key=settings.google_api_key,
            convert_system_message_to_human=True,
        )
        logger.info(f"Created Gemini LLM ({settings.llm_model})")
        return llm

    @staticmethod
    def _create_ollama(settings: Settings) -> ChatOllama:
        """Create Ollama LLM instance.

        Args:
            settings: Application settings

        Returns:
            ChatOllama: Configured Ollama LLM
        """
        llm = ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.llm_temperature,
        )
        logger.info(f"Created Ollama LLM ({settings.ollama_model})")
        return llm
