"""
LLM provider adapters.

This module contains adapter implementations for different LLM providers.
All adapters implement the BaseLLMAdapter interface defined in llm.base.
"""

from .gemini_adapter import GeminiAdapter

# Future: from .openai_adapter import OpenAIAdapter

__all__ = [
    "GeminiAdapter",
]
