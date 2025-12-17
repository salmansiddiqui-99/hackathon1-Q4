"""
Gemini API adapter with OpenAI-compatible interface.

This adapter wraps Google's Gemini API to provide an OpenAI-compatible interface,
enabling seamless switching between LLM providers without changing application code.
"""

import os
import time
import uuid
from typing import Iterator, Optional, List, Dict, Any
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "google-generativeai package is required for GeminiAdapter. "
        "Install it with: pip install google-generativeai"
    )

from ..base import (
    BaseLLMAdapter,
    LLMMessage,
    LLMCompletionParams,
    LLMResponse,
    LLMStreamChunk,
    LLMProviderError,
    LLMConfigurationError
)


class GeminiAdapter(BaseLLMAdapter):
    """
    Adapter for Google Gemini API with OpenAI-compatible interface.

    This adapter handles:
    - Converting OpenAI message format to Gemini format
    - Converting Gemini responses back to OpenAI format
    - Streaming response conversion
    - Tool/function calling translation
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        **kwargs
    ):
        """
        Initialize Gemini adapter.

        Args:
            api_key: Google AI API key
            model: Gemini model name (e.g., "gemini-2.0-flash", "gemini-1.5-pro")
            **kwargs: Additional Gemini-specific configuration
        """
        if not api_key:
            raise LLMConfigurationError("Gemini API key is required")

        self._api_key = api_key
        self._model = model
        self._kwargs = kwargs

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Initialize the model
        try:
            self._client = genai.GenerativeModel(model)
        except Exception as e:
            raise LLMConfigurationError(f"Failed to initialize Gemini model: {e}")

    def create_completion(
        self,
        params: LLMCompletionParams
    ) -> LLMResponse:
        """
        Create a non-streaming completion.

        Args:
            params: Unified completion parameters

        Returns:
            LLMResponse in OpenAI-compatible format
        """
        # Convert messages to Gemini format
        gemini_messages = self._convert_messages_to_gemini(params.messages)

        # Build generation config
        generation_config = self._build_generation_config(params)

        # Convert tools if present
        tools = None
        if params.tools:
            tools = self._convert_tools_to_gemini(params.tools)

        try:
            # Generate content
            response = self._client.generate_content(
                gemini_messages,
                generation_config=generation_config,
                tools=tools,
                stream=False
            )

            # Convert to OpenAI format
            return self._convert_gemini_response_to_openai(response, params.model)

        except Exception as e:
            # Handle quota exceeded errors gracefully (429 Too Many Requests)
            error_message = str(e).lower()
            if "429" in str(getattr(e, 'status_code', '')) or "quota" in error_message or "rate limit" in error_message:
                raise LLMProviderError(
                    "Gemini API quota exceeded. Free tier daily limit reached. Please try again after 24 hours or use a paid API key.",
                    status_code=429
                )

            raise LLMProviderError(
                f"Gemini API error: {str(e)}",
                status_code=getattr(e, 'status_code', None)
            )

    def create_completion_stream(
        self,
        params: LLMCompletionParams
    ) -> Iterator[LLMStreamChunk]:
        """
        Create a streaming completion.

        Args:
            params: Unified completion parameters

        Yields:
            LLMStreamChunk in OpenAI-compatible format
        """
        # Convert messages to Gemini format
        gemini_messages = self._convert_messages_to_gemini(params.messages)

        # Build generation config
        generation_config = self._build_generation_config(params)

        # Convert tools if present
        tools = None
        if params.tools:
            tools = self._convert_tools_to_gemini(params.tools)

        try:
            # Generate streaming content
            response_stream = self._client.generate_content(
                gemini_messages,
                generation_config=generation_config,
                tools=tools,
                stream=True
            )

            # Generate chunk ID (same for all chunks in this stream)
            chunk_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
            created = int(time.time())

            # Convert each chunk to OpenAI format
            for chunk in response_stream:
                yield self._convert_gemini_chunk_to_openai(
                    chunk,
                    chunk_id,
                    created,
                    params.model
                )

        except Exception as e:
            # Handle quota exceeded errors gracefully (429 Too Many Requests)
            # Don't retry - just provide clear error message to user
            error_message = str(e).lower()
            if "429" in str(getattr(e, 'status_code', '')) or "quota" in error_message or "rate limit" in error_message:
                raise LLMProviderError(
                    "Gemini API quota exceeded. Free tier daily limit reached. Please try again after 24 hours or use a paid API key.",
                    status_code=429
                )

            raise LLMProviderError(
                f"Gemini streaming API error: {str(e)}",
                status_code=getattr(e, 'status_code', None)
            )

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for the given text.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        try:
            # Use Gemini's token counting API
            result = self._client.count_tokens(text)
            return result.total_tokens
        except Exception:
            # Fallback: rough estimation (4 chars per token)
            return len(text) // 4

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        return self._model

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"

    # Private helper methods

    def _convert_messages_to_gemini(
        self,
        messages: List[LLMMessage]
    ) -> str:
        """
        Convert OpenAI message format to Gemini format.

        Gemini expects a single string prompt, so we concatenate system + user messages.
        For multi-turn conversations, we'll need to use Gemini's ChatSession API separately.

        Args:
            messages: List of OpenAI-format messages

        Returns:
            Combined prompt string for Gemini
        """
        prompt_parts = []

        for msg in messages:
            role = msg.role
            content = msg.content

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "function" or role == "tool":
                # Handle function/tool results
                name = msg.name or "function"
                prompt_parts.append(f"Function {name} result: {content}")

        # Join with double newlines for clarity
        combined_prompt = "\n\n".join(prompt_parts)

        # Add instruction for assistant to respond
        if messages and messages[-1].role == "user":
            combined_prompt += "\n\nAssistant:"

        return combined_prompt

    def _build_generation_config(
        self,
        params: LLMCompletionParams
    ) -> genai.types.GenerationConfig:
        """
        Build Gemini generation config from unified parameters.

        Args:
            params: Unified completion parameters

        Returns:
            Gemini GenerationConfig object
        """
        config = {
            "temperature": params.temperature,
            "max_output_tokens": params.max_tokens,
        }

        # Map optional parameters
        if params.top_p is not None:
            config["top_p"] = params.top_p

        # Note: Gemini doesn't support frequency_penalty, presence_penalty, or stop sequences
        # in the same way as OpenAI. We'll ignore these for now.

        return genai.types.GenerationConfig(**config)

    def _convert_tools_to_gemini(
        self,
        tools: List[Dict[str, Any]]
    ) -> List[genai.types.Tool]:
        """
        Convert OpenAI tools format to Gemini FunctionDeclarations.

        Args:
            tools: List of OpenAI tool definitions

        Returns:
            List of Gemini Tool objects
        """
        gemini_tools = []

        for tool in tools:
            if tool.get("type") != "function":
                continue

            func = tool.get("function", {})
            name = func.get("name")
            description = func.get("description", "")
            parameters = func.get("parameters", {})

            # Convert JSON schema to Gemini format
            # Gemini uses a similar schema structure, so we can mostly pass it through
            function_declaration = genai.types.FunctionDeclaration(
                name=name,
                description=description,
                parameters=parameters
            )

            gemini_tools.append(genai.types.Tool(
                function_declarations=[function_declaration]
            ))

        return gemini_tools

    def _convert_gemini_response_to_openai(
        self,
        response: Any,
        model: str
    ) -> LLMResponse:
        """
        Convert Gemini response to OpenAI ChatCompletion format.

        Args:
            response: Gemini GenerateContentResponse
            model: Model name to include in response

        Returns:
            LLMResponse in OpenAI format
        """
        # Extract text from response
        try:
            text = response.text
        except Exception:
            # If response.text fails, try to get from candidates
            text = ""
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    text = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])

        # Build OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created = int(time.time())

        # Extract finish reason
        finish_reason = "stop"
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                # Map Gemini finish reasons to OpenAI
                gemini_reason = str(candidate.finish_reason)
                if "MAX_TOKENS" in gemini_reason:
                    finish_reason = "length"
                elif "SAFETY" in gemini_reason:
                    finish_reason = "content_filter"
                elif "STOP" in gemini_reason:
                    finish_reason = "stop"

        # Calculate token usage (approximate)
        prompt_tokens = self.count_tokens(" ".join([msg.content for msg in []]))  # Would need original messages
        completion_tokens = self.count_tokens(text)

        return LLMResponse(
            id=completion_id,
            object="chat.completion",
            created=created,
            model=model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text,
                    },
                    "finish_reason": finish_reason,
                }
            ],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            }
        )

    def _convert_gemini_chunk_to_openai(
        self,
        chunk: Any,
        chunk_id: str,
        created: int,
        model: str
    ) -> LLMStreamChunk:
        """
        Convert Gemini streaming chunk to OpenAI ChatCompletionChunk format.

        Args:
            chunk: Gemini streaming chunk
            chunk_id: Completion ID (same for all chunks)
            created: Unix timestamp
            model: Model name

        Returns:
            LLMStreamChunk in OpenAI format
        """
        # Extract text from chunk
        text = ""
        try:
            if hasattr(chunk, 'text'):
                text = chunk.text
            elif hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    text = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
        except Exception:
            text = ""

        # Determine finish reason (only set on last chunk)
        finish_reason = None
        try:
            if hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    gemini_reason = str(candidate.finish_reason)
                    if "MAX_TOKENS" in gemini_reason:
                        finish_reason = "length"
                    elif "SAFETY" in gemini_reason:
                        finish_reason = "content_filter"
                    elif "STOP" in gemini_reason:
                        finish_reason = "stop"
        except Exception:
            pass

        # Build delta
        delta = {}
        if text:
            delta["content"] = text
        if finish_reason:
            delta["finish_reason"] = finish_reason

        return LLMStreamChunk(
            id=chunk_id,
            object="chat.completion.chunk",
            created=created,
            model=model,
            choices=[
                {
                    "index": 0,
                    "delta": delta,
                    "finish_reason": finish_reason,
                }
            ]
        )
