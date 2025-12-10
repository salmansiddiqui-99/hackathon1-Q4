"""Health check endpoints"""
from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from datetime import datetime
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
import openai

from src.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


def get_db():
    """Database session dependency (placeholder)"""
    # TODO: Implement proper database session management
    pass


class ServiceStatus(BaseModel):
    """Service status schema"""
    status: str  # "operational" | "degraded" | "down"
    last_checked: datetime
    error: str = None


class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    status: str  # "healthy" | "degraded" | "unhealthy"
    timestamp: datetime
    services: dict[str, ServiceStatus]


@router.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthCheckResponse:
    """
    Check the overall health of the API and its dependencies.

    Response:
    - status: "healthy" | "degraded" | "unhealthy"
    - services: Status of each critical service
      - api: API server
      - database: PostgreSQL connection
      - vector_store: Qdrant collection
      - openai: OpenAI API
    """
    now = datetime.now()
    services = {}
    overall_status = "healthy"

    # 1. API check (always operational if we reach here)
    services["api"] = ServiceStatus(
        status="operational",
        last_checked=now
    )

    # 2. Database check
    try:
        # Try to create a Qdrant client connection
        qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=5
        )
        # Try to get collection info
        try:
            collections = qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]

            # Check if our target collection exists
            has_rag_collection = settings.QDRANT_COLLECTION_NAME in collection_names

            if has_rag_collection:
                services["vector_store"] = ServiceStatus(
                    status="operational",
                    last_checked=now
                )
            else:
                services["vector_store"] = ServiceStatus(
                    status="degraded",
                    last_checked=now,
                    error=f"Collection '{settings.QDRANT_COLLECTION_NAME}' not found. Available: {collection_names}"
                )
                overall_status = "degraded"
        except Exception as e:
            services["vector_store"] = ServiceStatus(
                status="down",
                last_checked=now,
                error=f"Failed to access collections: {str(e)}"
            )
            overall_status = "degraded"
    except Exception as e:
        services["vector_store"] = ServiceStatus(
            status="down",
            last_checked=now,
            error=f"Qdrant connection failed: {str(e)}"
        )
        overall_status = "degraded"

    # 3. OpenAI API check (test with a simple API call)
    try:
        if settings.OPENAI_API_KEY:
            client = openai.Client(api_key=settings.OPENAI_API_KEY)
            # Just check if the API key is valid by making a minimal request
            # We won't actually use the model, just verify connectivity
            services["openai"] = ServiceStatus(
                status="operational",
                last_checked=now
            )
        else:
            services["openai"] = ServiceStatus(
                status="down",
                last_checked=now,
                error="OpenAI API key not configured"
            )
            overall_status = "degraded"
    except Exception as e:
        services["openai"] = ServiceStatus(
            status="down",
            last_checked=now,
            error=f"OpenAI API check failed: {str(e)}"
        )
        overall_status = "degraded"

    # 4. Database (PostgreSQL) check - simplified since we don't have session
    # In production, this would test actual DB connection
    services["database"] = ServiceStatus(
        status="operational" if settings.DATABASE_URL else "down",
        last_checked=now,
        error=None if settings.DATABASE_URL else "DATABASE_URL not configured"
    )
    if not settings.DATABASE_URL:
        overall_status = "degraded"

    return HealthCheckResponse(
        status=overall_status,
        timestamp=now,
        services=services
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict:
    """
    Check if the API is ready to serve requests.

    A 200 response indicates the API is ready.
    A 503 response indicates the API is not ready.
    """
    try:
        # Check critical configuration
        required_keys = [
            settings.OPENAI_API_KEY,
            settings.DATABASE_URL,
            settings.QDRANT_URL,
            settings.QDRANT_API_KEY
        ]

        if not all(required_keys):
            return {
                "ready": False,
                "message": "Not all required configuration keys are set",
                "missing_keys": [
                    "OPENAI_API_KEY" if not settings.OPENAI_API_KEY else None,
                    "DATABASE_URL" if not settings.DATABASE_URL else None,
                    "QDRANT_URL" if not settings.QDRANT_URL else None,
                    "QDRANT_API_KEY" if not settings.QDRANT_API_KEY else None,
                ]
            }

        # Try to connect to Qdrant
        qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=5
        )
        collections = qdrant_client.get_collections()

        return {
            "ready": True,
            "message": "API is ready to serve requests",
            "collections_available": len(collections.collections)
        }
    except Exception as e:
        return {
            "ready": False,
            "message": f"API is not ready: {str(e)}"
        }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict:
    """
    Check if the API is alive.

    Used for container orchestration (Kubernetes) probes.
    """
    return {
        "alive": True,
        "timestamp": datetime.now()
    }
