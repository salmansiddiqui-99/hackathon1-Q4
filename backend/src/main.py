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
    logger.info("✅ Physical AI Textbook API starting up...")
    app_state["start_time"] = datetime.utcnow()

    try:
        # Validate required configuration
        settings.validate_required_keys()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"⚠️ Configuration warning: {e}")

    logger.info("✅ Startup complete")

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
