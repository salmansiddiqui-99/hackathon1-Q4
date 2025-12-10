"""Chatbot service for generating RAG-based responses using Claude/OpenAI"""
import logging
from typing import List, AsyncGenerator, Iterator
import openai

from src.config import settings
from src.models.rag import RetrievedChunkData, ResponseStatus

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for generating context-aware responses using LLMs"""

    def __init__(self):
        """Initialize chatbot service with OpenAI client"""
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

    def generate_response(
        self,
        query_text: str,
        chunks: List[RetrievedChunkData],
        stream: bool = True
    ) -> Iterator[str]:
        """
        Generate a response using retrieved chunks as context.

        The response is strictly constrained to use only the provided context.
        If no relevant context is found, the chatbot will decline to answer.

        Args:
            query_text: The user's question
            chunks: List of retrieved content chunks to use as context
            stream: Whether to stream tokens or return full response

        Yields:
            Token strings (if stream=True) or single response string (if stream=False)

        Raises:
            ValueError: If context is insufficient or generation fails
        """
        # Build context from chunks
        context = self._build_context(chunks)

        if not context.strip():
            logger.warning(f"No context available for query: {query_text}")
            yield "I cannot answer this based on the available content."
            return

        # Build the prompt
        system_prompt = (
            "You are a helpful AI assistant for a Physical AI & Humanoid Robotics textbook. "
            "Your role is to answer student questions using ONLY the provided context. "
            "Do not use your general knowledge or training data. "
            "If the context does not contain sufficient information to answer the question, "
            "respond with: 'I cannot answer this based on the available content.'"
        )

        user_message = f"""Context from the textbook:
{context}

---

Student Question: {query_text}

Please answer the student's question using ONLY the provided context above.
If the context doesn't contain relevant information, say you cannot answer based on available content."""

        try:
            if stream:
                # Stream response
                with self.openai_client.messages.stream(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                ) as stream_response:
                    for text in stream_response.text_stream:
                        yield text
            else:
                # Generate full response at once
                response = self.openai_client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                yield response.content[0].text

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Failed to generate response: {str(e)}")
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise ValueError(f"Response generation failed: {str(e)}")

    def _build_context(self, chunks: List[RetrievedChunkData]) -> str:
        """
        Build a context string from retrieved chunks.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Formatted context string for the prompt
        """
        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk.section_title} (Similarity: {chunk.similarity_score:.2f})]"
                f"\n{chunk.text}\n"
            )

        return "\n".join(context_parts)

    def validate_response_contains_context(
        self,
        response_text: str,
        chunks: List[RetrievedChunkData]
    ) -> bool:
        """
        Simple heuristic check that response relates to provided context.

        This is a basic validation to ensure the response isn't purely from general knowledge.
        A more sophisticated approach would use embedding similarity.

        Args:
            response_text: Generated response text
            chunks: Chunks used for context

        Returns:
            True if response appears to use the context, False otherwise
        """
        if not chunks or not response_text:
            return False

        # Extract key terms from chunks (simple keyword approach)
        context_keywords = set()
        for chunk in chunks:
            # Get first few significant words from each chunk
            words = chunk.text.lower().split()
            for word in words[:20]:  # First 20 words per chunk
                if len(word) > 4:  # Skip short words
                    context_keywords.add(word.strip(".,;:!?"))

        # Check if response uses context keywords
        response_lower = response_text.lower()
        keyword_matches = sum(1 for kw in context_keywords if kw in response_lower)

        # Need at least some keyword overlap to consider it context-based
        return keyword_matches > 0

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses a simple heuristic: ~1 token per 4 characters (approximation for GPT models).

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Simple approximation: 1 token ~ 4 characters
        return len(text) // 4

    def check_context_sufficiency(
        self,
        chunks: List[RetrievedChunkData],
        min_similarity: float = 0.75
    ) -> tuple[bool, str]:
        """
        Check if retrieved context is sufficient to answer a question.

        Args:
            chunks: Retrieved chunks
            min_similarity: Minimum similarity score to consider relevant

        Returns:
            Tuple of (is_sufficient, reason_if_not)
        """
        if not chunks:
            return False, "No context chunks retrieved"

        # Check if we have at least some relevant chunks
        relevant_chunks = [c for c in chunks if c.similarity_score >= min_similarity]

        if not relevant_chunks:
            return False, f"No chunks with similarity > {min_similarity}"

        # Check total context size
        total_tokens = sum(self.count_tokens(c.text) for c in relevant_chunks)
        if total_tokens < 100:
            return False, f"Retrieved context too small ({total_tokens} tokens)"

        return True, "Context sufficient"
