"""
LLM provider factory for creating adapters based on configuration.

This factory enables runtime switching between different LLM providers
(Gemini, OpenAI) through configuration settings.
"""

from typing import Optional, Dict, Any
import logging

from .base import BaseLLMAdapter, LLMConfigurationError
from .adapters.gemini_adapter import GeminiAdapter
from .adapters.openrouter_adapter import OpenRouterAdapter

# OpenAI adapter will be implemented later
# from .adapters.openai_adapter import OpenAIAdapter

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LLM adapters based on configuration.

    This factory abstracts provider selection, allowing runtime switching
    between different LLM providers without changing application code.
    """

    # Model mapping: OpenAI model names → Gemini equivalents
    MODEL_MAPPING: Dict[str, str] = {
        "gpt-4": "gemini-2.0-flash-thinking",
        "gpt-4-turbo": "gemini-2.0-flash-thinking",
        "gpt-4o": "gemini-2.0-flash",
        "gpt-3.5-turbo": "gemini-1.5-flash",
        "gpt-3.5-turbo-16k": "gemini-1.5-flash",
    }

    @staticmethod
    def create_from_settings(settings: Any) -> BaseLLMAdapter:
        """
        Create an LLM adapter from application settings.

        IMPORTANT: OpenRouter is the REQUIRED provider. Other providers are not supported.

        Args:
            settings: Application settings object with LLM configuration

        Returns:
            Configured OpenRouter LLM adapter instance

        Raises:
            LLMConfigurationError: If OpenRouter is not properly configured
        """
        provider = getattr(settings, "LLM_PROVIDER", "openrouter").lower()

        logger.info(f"Creating LLM adapter with provider: {provider}")

        # Only OpenRouter is supported
        if provider in ["openrouter", "auto"]:
            # For "auto", detect and use OpenRouter
            if provider == "auto":
                provider = LLMFactory._auto_detect_provider(settings)
                logger.info(f"Auto-detected provider: {provider}")

            return LLMFactory.create_openrouter_adapter(settings)
        else:
            raise LLMConfigurationError(
                f"Unsupported LLM provider: {provider}. "
                f"Only 'openrouter' is supported. "
                f"Please set LLM_PROVIDER='openrouter' and configure OPENROUTER_API_KEY."
            )

    @staticmethod
    def create_openrouter_adapter(settings: Any) -> BaseLLMAdapter:
        """
        Create an OpenRouter adapter from settings.

        Args:
            settings: Application settings with OPENROUTER_API_KEY and OPENROUTER_MODEL

        Returns:
            Configured OpenRouterAdapter instance

        Raises:
            LLMConfigurationError: If OpenRouter configuration is missing
        """
        api_key = getattr(settings, "OPENROUTER_API_KEY", None)
        if not api_key:
            raise LLMConfigurationError(
                "OPENROUTER_API_KEY is required for OpenRouter provider. "
                "Set it in your .env file or environment variables."
            )

        # Get model name, with fallback
        model = getattr(settings, "OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")
        base_url = getattr(settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        # Get optional configuration
        temperature = getattr(settings, "OPENAI_TEMPERATURE", 0.7)
        max_tokens = getattr(settings, "OPENAI_MAX_TOKENS", 2000)

        logger.info(
            f"Creating OpenRouterAdapter with model={model}, "
            f"temperature={temperature}, max_tokens={max_tokens}"
        )

        return OpenRouterAdapter(
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )

    @staticmethod
    def create_gemini_adapter(settings: Any) -> BaseLLMAdapter:
        """
        Create a Gemini adapter from settings.

        Args:
            settings: Application settings with GEMINI_API_KEY and GEMINI_MODEL

        Returns:
            Configured GeminiAdapter instance

        Raises:
            LLMConfigurationError: If Gemini configuration is missing
        """
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise LLMConfigurationError(
                "GEMINI_API_KEY is required for Gemini provider. "
                "Set it in your .env file or environment variables."
            )

        # Get model name, with fallback
        model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")

        # Get optional configuration
        temperature = getattr(settings, "OPENAI_TEMPERATURE", 0.7)
        max_tokens = getattr(settings, "OPENAI_MAX_TOKENS", 2000)

        logger.info(
            f"Creating GeminiAdapter with model={model}, "
            f"temperature={temperature}, max_tokens={max_tokens}"
        )

        return GeminiAdapter(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    @staticmethod
    def create_openai_adapter(settings: Any) -> BaseLLMAdapter:
        """
        Create an OpenAI adapter from settings.

        Args:
            settings: Application settings with OPENAI_API_KEY and OPENAI_MODEL

        Returns:
            Configured OpenAIAdapter instance

        Raises:
            LLMConfigurationError: If OpenAI configuration is missing
            NotImplementedError: OpenAI adapter not yet implemented
        """
        # TODO: Implement OpenAIAdapter
        raise NotImplementedError(
            "OpenAI adapter is not yet implemented. "
            "Use 'gemini' provider for now."
        )

        # Future implementation:
        # api_key = getattr(settings, "OPENAI_API_KEY", None)
        # if not api_key:
        #     raise LLMConfigurationError("OPENAI_API_KEY is required for OpenAI provider")
        #
        # model = getattr(settings, "OPENAI_MODEL", "gpt-4o")
        # return OpenAIAdapter(api_key=api_key, model=model)

    @staticmethod
    def create_adapter(
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMAdapter:
        """
        Create an LLM adapter with explicit parameters.

        This is a lower-level method for creating adapters when you have
        explicit configuration values instead of a settings object.

        Args:
            provider: Provider name ("gemini" or "openai")
            api_key: API key for the provider
            model: Optional model name (uses provider default if None)
            **kwargs: Additional provider-specific configuration

        Returns:
            Configured LLM adapter instance

        Raises:
            LLMConfigurationError: If configuration is invalid
        """
        provider = provider.lower()

        if provider == "gemini":
            model = model or "gemini-2.0-flash"
            return GeminiAdapter(api_key=api_key, model=model, **kwargs)
        elif provider == "openai":
            raise NotImplementedError("OpenAI adapter not yet implemented")
        else:
            raise LLMConfigurationError(
                f"Unknown provider: {provider}. Supported: 'gemini', 'openai'"
            )

    @staticmethod
    def map_openai_model_to_gemini(openai_model: str) -> str:
        """
        Map OpenAI model name to equivalent Gemini model.

        This enables drop-in compatibility where code uses OpenAI model names
        but needs to run on Gemini backend.

        Args:
            openai_model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")

        Returns:
            Equivalent Gemini model name

        Example:
            >>> LLMFactory.map_openai_model_to_gemini("gpt-4")
            "gemini-2.0-flash-thinking"
        """
        return LLMFactory.MODEL_MAPPING.get(
            openai_model,
            "gemini-2.0-flash"  # Default fallback
        )

    @staticmethod
    def _auto_detect_provider(settings: Any) -> str:
        """
        Auto-detect the LLM provider based on available API keys.

        OpenRouter is the REQUIRED and only supported provider.
        This method ensures we use OpenRouter for all LLM operations.

        Raises:
            LLMConfigurationError: If OpenRouter is not configured
        """
        openrouter_key = getattr(settings, "OPENROUTER_API_KEY", None)
        if openrouter_key:
            logger.info("Using OpenRouter as LLM provider")
            return "openrouter"

        raise LLMConfigurationError(
            "OPENROUTER_API_KEY is required and not configured. "
            "Please set OPENROUTER_API_KEY in your environment variables or .env file. "
            "Get your API key from: https://openrouter.ai/"
        )

    @staticmethod
    def _old_auto_detect_provider(settings: Any) -> str:
        """
        Auto-detect which provider to use based on available API keys.

        Priority order:
        1. Gemini (if GEMINI_API_KEY is set)
        2. OpenAI (if OPENAI_API_KEY is set)

        Args:
            settings: Application settings object

        Returns:
            Provider name ("gemini" or "openai")

        Raises:
            LLMConfigurationError: If no API keys are configured
        """
        gemini_key = getattr(settings, "GEMINI_API_KEY", None)
        openai_key = getattr(settings, "OPENAI_API_KEY", None)

        # Prefer Gemini (current primary provider)
        if gemini_key:
            logger.info("Auto-detected Gemini API key, using 'gemini' provider")
            return "gemini"
        elif openai_key:
            logger.info("Auto-detected OpenAI API key, using 'openai' provider")
            return "openai"
        else:
            raise LLMConfigurationError(
                "No LLM provider configured. "
                "Set either GEMINI_API_KEY or OPENAI_API_KEY in your environment."
            )

    @staticmethod
    def get_available_providers(settings: Any) -> list[str]:
        """
        Get list of available providers based on configured API keys.

        Currently, only OpenRouter is supported.

        Args:
            settings: Application settings object

        Returns:
            List of available provider names (only 'openrouter' if configured)
        """
        providers = []

        if getattr(settings, "OPENROUTER_API_KEY", None):
            providers.append("openrouter")

        return providers


# Convenience function for quick adapter creation
def create_llm_adapter(settings: Any) -> BaseLLMAdapter:
    """
    Convenience function to create an LLM adapter from settings.

    This is a shortcut for LLMFactory.create_from_settings(settings).

    Args:
        settings: Application settings object

    Returns:
        Configured LLM adapter instance
    """
    return LLMFactory.create_from_settings(settings)
