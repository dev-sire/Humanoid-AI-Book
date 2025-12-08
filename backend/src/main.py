"""
FastAPI application entry point.

Main application with CORS middleware, route registration, and lifespan events.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import health, chat, sessions, debug
from src.config import settings
from src.services.conversation import ConversationService
from src.services.vector_store import VectorStoreService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Initialize database tables
        - Verify Qdrant collection exists

    Shutdown:
        - Cleanup resources
    """
    # Startup
    logger.info("Starting RAG chatbot backend...")

    try:
        # Initialize database
        conversation_service = ConversationService()
        await conversation_service.create_tables()
        logger.info("Database initialized")

        # Ensure Qdrant collection exists
        vector_store = VectorStoreService()
        await vector_store.ensure_collection_exists()
        logger.info("Vector store initialized")

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

    logger.info("Backend startup complete")

    yield

    # Shutdown
    logger.info("Shutting down backend...")


# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for Physical AI & Humanoid Robotics documentation chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def home():
    return {"status": "backend running"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured for origins: {settings.cors_origins_list}")


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# Register routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(debug.router, prefix="/api", tags=["debug"])

logger.info("Routes registered")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
