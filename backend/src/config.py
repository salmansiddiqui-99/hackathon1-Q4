"""Application configuration and environment loading"""
import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


# Load environment variables
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Server configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "Physical AI Textbook API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Backend API for AI/Spec-Driven Book Creation"
    DEBUG: bool = False

    # Database configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/physical_ai_book"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Qdrant configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "chapter_chunks"
    QDRANT_VECTOR_SIZE: int = 384
    QDRANT_DISTANCE_METRIC: str = "Cosine"

    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_TIMEOUT: int = 30

    # Claude Code / Anthropic configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_CODE_API_KEY: Optional[str] = None
    CLAUDE_CODE_TIMEOUT: int = 60
    CLAUDE_CODE_MAX_RETRIES: int = 3
    CLAUDE_CODE_RETRY_BACKOFF: float = 2.0

    # GitHub configuration
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPO_OWNER: str = "yourname"
    GITHUB_REPO_NAME: str = "physical_ai_book"

    # RAG configuration
    RAG_TOP_K: int = 5
    RAG_TOP_K_CHUNKS: Optional[int] = None  # Alternative name
    RAG_SIMILARITY_THRESHOLD: float = 0.75
    RAG_CONTEXT_MAX_TOKENS: int = 3000
    RAG_MAX_RESPONSE_TOKENS: Optional[int] = None
    RAG_RESPONSE_TOKENS: Optional[int] = None

    # Chapter generation configuration
    CHAPTER_MIN_LENGTH: int = 1000
    CHAPTER_MAX_LENGTH: int = 5000
    CHAPTER_GENERATION_TIMEOUT: int = 300

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # CORS configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_ALLOW_HEADERS: str = "Content-Type,Authorization"

    # Feature flags
    FEATURE_RAG_ENABLED: bool = True
    FEATURE_CHAPTER_GENERATION_ENABLED: bool = True
    FEATURE_TEXT_SELECTION_MODE: Optional[bool] = None
    FEATURE_PERFORMANCE_LOGGING: Optional[bool] = None
    FEATURE_HALLUCINATION_DETECTION: Optional[bool] = None
    FEATURE_STREAMING_RESPONSES: Optional[bool] = None

    # Additional LLM models
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # Chat configuration
    CHAT_LOG_RETENTION_DAYS: Optional[int] = None
    CHAT_MAX_MESSAGES_PER_SESSION: Optional[int] = None

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: Optional[int] = None

    # Collections
    QDRANT_COLLECTION_NAME: Optional[str] = None

    # API Debug
    API_DEBUG: Optional[bool] = None

    # Performance limits
    REQUEST_TIMEOUT: int = 30
    BATCH_SIZE: int = 100
    MAX_RETRIES: int = 3

    model_config = ConfigDict(
        env_file=str(env_file) if env_file.exists() else None,
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )

    def get_cors_origins(self) -> list:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def get_cors_methods(self) -> list:
        """Parse CORS methods from comma-separated string"""
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",")]

    def get_cors_headers(self) -> list:
        """Parse CORS headers from comma-separated string"""
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]

    def validate_required_keys(self) -> None:
        """Validate that all required environment keys are present"""
        required_keys = [
            "GEMINI_API_KEY",
            "QDRANT_URL",
            "DATABASE_URL",
        ]
        missing = []
        for key in required_keys:
            if not getattr(self, key, None):
                missing.append(key)

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file."
            )


# Load settings
settings = Settings()


def get_db():
    """Database session dependency for FastAPI endpoints"""
    # This is a stub for local testing - actual DB setup happens in models
    return None


def configure_logging() -> None:
    """Configure structured logging"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("physical_ai_book")
    logger.setLevel(log_level)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    # Create formatter
    if settings.LOG_FORMAT == "json":
        try:
            import pythonjsonlogger.jsonlogger as jsonlogger
            formatter = jsonlogger.JsonFormatter()
        except ImportError:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Configure logging on module load
logger = configure_logging()
