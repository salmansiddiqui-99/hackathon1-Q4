"""
FastAPI application entry point for Physical AI Textbook + RAG Chatbot
"""

# CRITICAL: Print at module load time to ensure visibility in Railway logs
print("=" * 80)
print("📦 MAIN MODULE LOADING - This should appear in Railway logs!")
print("=" * 80)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from src.config import settings
from src.errors import BaseAPIException
from src.api import chapters, rag, health, chatbot, selected_text

# Print config immediately after import (module-level)
print("=" * 80)
print("🔍 MODULE-LEVEL CONFIG CHECK (runs before startup event):")
print("=" * 80)
print(f"QDRANT_COLLECTION: {settings.QDRANT_COLLECTION}")
print(f"QDRANT_VECTOR_SIZE: {settings.QDRANT_VECTOR_SIZE}")
print(f"RAG_SIMILARITY_THRESHOLD: {settings.RAG_SIMILARITY_THRESHOLD}")
print(f"COHERE_API_KEY: {'SET ✅' if settings.COHERE_API_KEY else 'NOT SET ❌'}")
print(f"GEMINI_API_KEY: {'SET ✅' if settings.GEMINI_API_KEY else 'NOT SET ❌'}")
print(f"QDRANT_API_KEY: {'SET ✅' if settings.QDRANT_API_KEY else 'NOT SET ❌'}")
print(f"RAG_TOP_K: {settings.RAG_TOP_K}")
print("=" * 80)

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
    # Use print() to ensure logs appear even if logging is misconfigured
    print("=" * 80)
    print("🚀 Physical AI Textbook API starting up...")
    print("=" * 80)

    logger.info("=" * 80)
    logger.info("🚀 Physical AI Textbook API starting up...")
    logger.info("=" * 80)
    app_state["start_time"] = datetime.utcnow()

    # Log critical configuration values for debugging
    config_info = f"""
📋 Configuration Check:
  API_TITLE: {settings.API_TITLE}
  API_VERSION: {settings.API_VERSION}
  DEBUG: {settings.DEBUG}

🗄️  Database Configuration:
  DATABASE_URL: {settings.DATABASE_URL[:50] + '...' if settings.DATABASE_URL else 'NOT SET'}

🔍 Qdrant Configuration:
  QDRANT_URL: {settings.QDRANT_URL}
  QDRANT_COLLECTION: {settings.QDRANT_COLLECTION}
  QDRANT_VECTOR_SIZE: {settings.QDRANT_VECTOR_SIZE}
  QDRANT_API_KEY: {'SET ✅' if settings.QDRANT_API_KEY else 'NOT SET ❌'}

🤖 AI Configuration:
  COHERE_API_KEY: {'SET ✅' if settings.COHERE_API_KEY else 'NOT SET ❌'}
  GEMINI_API_KEY: {'SET ✅' if settings.GEMINI_API_KEY else 'NOT SET ❌'}
  GEMINI_MODEL: {settings.GEMINI_MODEL if hasattr(settings, 'GEMINI_MODEL') else 'NOT SET'}

🎯 RAG Configuration:
  RAG_SIMILARITY_THRESHOLD: {settings.RAG_SIMILARITY_THRESHOLD}
  RAG_TOP_K: {settings.RAG_TOP_K}

🌐 CORS Configuration:
  CORS_ORIGINS: {settings.get_cors_origins()}
"""

    # Print to stdout (will always show in Railway logs)
    print(config_info)
    # Also log normally
    logger.info(config_info)

    try:
        # Validate required configuration
        settings.validate_required_keys()
        print("✅ Configuration validation passed")
        logger.info("✅ Configuration validation passed")
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
        print("⚠️  Application may not function correctly!")
        logger.error(f"❌ Configuration validation failed: {e}")
        logger.error("⚠️  Application may not function correctly!")

    print("=" * 80)
    print("✅ Startup complete")
    print("=" * 80)
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
