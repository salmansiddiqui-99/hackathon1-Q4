"""Health check endpoints"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["health"])


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
    # TODO: Implement actual health checks
    # - Test database connection
    # - Test Qdrant connectivity
    # - Test OpenAI API
    now = datetime.now()
    return HealthCheckResponse(
        status="degraded",
        timestamp=now,
        services={
            "api": ServiceStatus(
                status="operational",
                last_checked=now
            ),
            "database": ServiceStatus(
                status="down",
                last_checked=now,
                error="Not connected"
            ),
            "vector_store": ServiceStatus(
                status="down",
                last_checked=now,
                error="Qdrant not reachable"
            ),
            "openai": ServiceStatus(
                status="down",
                last_checked=now,
                error="API key not configured"
            )
        }
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict:
    """
    Check if the API is ready to serve requests.

    A 200 response indicates the API is ready.
    A 503 response indicates the API is not ready.
    """
    # TODO: Check if all critical services are ready
    return {
        "ready": False,
        "message": "Services not yet configured"
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
