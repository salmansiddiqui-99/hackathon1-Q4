"""Custom exceptions and error handling"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail response schema"""
    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None


class BaseAPIException(HTTPException):
    """Base exception for all API errors"""
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.details = details
        super().__init__(
            status_code=status_code,
            detail=ErrorDetail(
                error=error,
                message=message,
                status_code=status_code,
                details=details
            ).dict()
        )


class ValidationError(BaseAPIException):
    """Raised when validation fails"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="VALIDATION_ERROR",
            message=message,
            details=details
        )


class NotFoundError(BaseAPIException):
    """Raised when resource is not found"""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="NOT_FOUND",
            message=f"{resource} with id {resource_id} not found"
        )


class ConflictError(BaseAPIException):
    """Raised when resource already exists"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="CONFLICT",
            message=message,
            details=details
        )


class UnauthorizedError(BaseAPIException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
            message=message
        )


class ForbiddenError(BaseAPIException):
    """Raised when user lacks permission"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="FORBIDDEN",
            message=message
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error="RATE_LIMIT_EXCEEDED",
            message=message
        )


class InternalServerError(BaseAPIException):
    """Raised when unexpected error occurs"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="INTERNAL_SERVER_ERROR",
            message=message,
            details=details
        )


class ExternalServiceError(BaseAPIException):
    """Raised when external service fails"""
    def __init__(self, service: str, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error="EXTERNAL_SERVICE_ERROR",
            message=f"{service} error: {message}",
            details=details
        )


class QdrantError(ExternalServiceError):
    """Raised when Qdrant operations fail"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(service="Qdrant", message=message, details=details)


class DatabaseError(ExternalServiceError):
    """Raised when database operations fail"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(service="Database", message=message, details=details)


class OpenAIError(ExternalServiceError):
    """Raised when OpenAI API calls fail"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(service="OpenAI", message=message, details=details)
