"""
Main FastAPI application for Loneliness Combat Engine.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.routing import Mount

from backend.api.middleware import LoggingMiddleware, setup_cors
from backend.api.routes import router
from backend.core import get_settings
from backend.models import init_db
from backend.mcp_server.server import mcp_server

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting Loneliness Combat Engine API...")
    print(f"📊 Environment: {settings.environment}")
    print(f"🗄️  Database: {settings.database_url}")

    # Initialize database
    init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("👋 Shutting down Loneliness Combat Engine API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered loneliness detection and intervention system",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Setup middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(router)

# Mount MCP server at /mcp endpoint
# This makes the MCP server accessible via HTTP at http://localhost:8000/mcp
app.mount("/mcp", mcp_server.streamable_http_app())


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI-powered loneliness detection and intervention system",
        "docs": "/docs" if settings.debug else "disabled",
        "health": "/api/v1/health",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions."""
    print(f"❌ Unhandled exception: {exc}")

    if settings.debug:
        import traceback

        traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.debug else None},
    )


if __name__ == "__main__":
    import argparse
    import sys

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Loneliness Combat Engine API")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["http", "stdio"],
        default="http",
        help="Run mode: http (FastAPI server) or stdio (MCP server for Claude Desktop)",
    )
    args = parser.parse_args()

    if args.mode == "stdio":
        # Run MCP server in stdio mode for Claude Desktop
        print("🔌 Starting MCP server in stdio mode...", file=sys.stderr)
        mcp_server.run()
    else:
        # Run FastAPI server in HTTP mode
        import uvicorn

        uvicorn.run(
            "main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
        )
