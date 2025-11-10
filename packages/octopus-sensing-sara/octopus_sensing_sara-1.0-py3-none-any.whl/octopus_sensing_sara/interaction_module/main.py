"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from octopus_sensing_sara.api.routes import router
from octopus_sensing_sara.core.config import get_settings
from octopus_sensing_sara.storage.database import DatabaseManager

# Configure logging - Clean format without file paths and timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

# Suppress verbose SQLAlchemy and Uvicorn logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    settings = get_settings()

    try:
        # Initialize database
        await DatabaseManager.init_db()
        logger.info("Database initialized successfully")

        # Validate API keys based on provider
        if settings.llm_provider == "openai" and not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - chat functionality will fail")
        elif settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set - chat functionality will fail")

        logger.info(f"Using LLM provider: {settings.llm_provider}")
        logger.info(f"Application {settings.app_name} v{settings.app_version} started")

    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        await DatabaseManager.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)


def create_application() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A conversational chatbot with short-term and long-term memory",
        lifespan=lifespan,
        debug=settings.debug,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router)

    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle validation errors."""
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc), "type": "validation_error"},
        )

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        """Handle not found errors."""
        logger.warning(f"Key error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Resource not found: {exc}", "type": "not_found"},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        """Handle generic errors."""
        logger.error(f"Unhandled error: {exc}", exc_info=True)

        # Include error details in development mode
        detail = str(exc) if settings.debug else "Internal server error"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": detail, "type": "server_error"},
        )

    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info("FastAPI application configured")
    return app


# Create application instance
app = create_application()
