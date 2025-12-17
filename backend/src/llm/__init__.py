"""
LLM abstraction layer with OpenAI-compatible interface.

This module provides a unified interface for working with different LLM providers
(Gemini, OpenAI) through an adapter pattern. All adapters implement the same
OpenAI-compatible interface, enabling seamless provider switching.

Usage:
    from src.llm import create_llm_adapter, LLMCompletionParams, LLMMessage
    from src.config import settings

    # Create adapter (auto-detects provider from settings)
    adapter = create_llm_adapter(settings)

    # Create completion
    params = LLMCompletionParams(
        messages=[
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content="What is ROS 2?")
        ],
        model="gemini-2.0-flash",
        temperature=0.7,
        stream=True
    )

    # Stream response
    for chunk in adapter.create_completion_stream(params):
        print(chunk.choices[0].delta.get("content", ""), end="")
"""

from .base import (
    BaseLLMAdapter,
    LLMMessage,
    LLMCompletionParams,
    LLMResponse,
    LLMStreamChunk,
    LLMAdapterError,
    LLMProviderError,
    LLMConfigurationError,
)

from .factory import (
    LLMFactory,
    create_llm_adapter,
)

from .adapters.gemini_adapter import GeminiAdapter

# Export main classes and functions
__all__ = [
    # Base interfaces
    "BaseLLMAdapter",
    "LLMMessage",
    "LLMCompletionParams",
    "LLMResponse",
    "LLMStreamChunk",

    # Exceptions
    "LLMAdapterError",
    "LLMProviderError",
    "LLMConfigurationError",

    # Factory
    "LLMFactory",
    "create_llm_adapter",

    # Adapters
    "GeminiAdapter",
]
