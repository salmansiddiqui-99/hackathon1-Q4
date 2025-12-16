"""
FastAPI application entry point for Physical AI Textbook + RAG Chatbot
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from src.config import settings
from src.errors import BaseAPIException
from src.api import chapters, rag, health, chatbot, selected_text

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.get_cors_methods(),
    allow_headers=settings.get_cors_headers(),
)

# Configure logging
logger = logging.getLogger(__name__)

# Application startup state
app_state = {
    "start_time": datetime.utcnow(),
    "uptime_seconds": 0
}

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("=" * 80)
    logger.info("🚀 Physical AI Textbook API starting up...")
    logger.info("=" * 80)
    app_state["start_time"] = datetime.utcnow()

    # Log critical configuration values for debugging
    logger.info("📋 Configuration Check:")
    logger.info(f"  API_TITLE: {settings.API_TITLE}")
    logger.info(f"  API_VERSION: {settings.API_VERSION}")
    logger.info(f"  DEBUG: {settings.DEBUG}")

    logger.info("🗄️  Database Configuration:")
    logger.info(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}..." if settings.DATABASE_URL else "  DATABASE_URL: NOT SET")

    logger.info("🔍 Qdrant Configuration:")
    logger.info(f"  QDRANT_URL: {settings.QDRANT_URL}")
    logger.info(f"  QDRANT_COLLECTION: {settings.QDRANT_COLLECTION}")
    logger.info(f"  QDRANT_VECTOR_SIZE: {settings.QDRANT_VECTOR_SIZE}")
    logger.info(f"  QDRANT_API_KEY: {'SET ✅' if settings.QDRANT_API_KEY else 'NOT SET ❌'}")

    logger.info("🤖 AI Configuration:")
    logger.info(f"  COHERE_API_KEY: {'SET ✅' if settings.COHERE_API_KEY else 'NOT SET ❌'}")
    logger.info(f"  GEMINI_API_KEY: {'SET ✅' if settings.GEMINI_API_KEY else 'NOT SET ❌'}")
    logger.info(f"  GEMINI_MODEL: {settings.GEMINI_MODEL if hasattr(settings, 'GEMINI_MODEL') else 'NOT SET'}")

    logger.info("🎯 RAG Configuration:")
    logger.info(f"  RAG_SIMILARITY_THRESHOLD: {settings.RAG_SIMILARITY_THRESHOLD}")
    logger.info(f"  RAG_TOP_K: {settings.RAG_TOP_K}")

    logger.info("🌐 CORS Configuration:")
    logger.info(f"  CORS_ORIGINS: {settings.get_cors_origins()}")

    try:
        # Validate required configuration
        settings.validate_required_keys()
        logger.info("✅ Configuration validation passed")
    except ValueError as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        logger.error("⚠️  Application may not function correctly!")

    logger.info("=" * 80)
    logger.info("✅ Startup complete")
    logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("🔴 Physical AI Textbook API shutting down...")
    # TODO: Close database connections
    # TODO: Clean up resources
    logger.info("✅ Shutdown complete")

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "status": "ok",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

# Include routers
app.include_router(health.router)
app.include_router(chapters.router)
app.include_router(rag.router)
app.include_router(chatbot.router)
app.include_router(selected_text.router)

# Exception handlers
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle API exceptions"""
    logger.warning(f"API exception: {exc.error} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
