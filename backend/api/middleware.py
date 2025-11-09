"""
Middleware for FastAPI application.
"""

import time
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core import get_settings

settings = get_settings()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        start_time = time.time()

        # Log request
        print(f"[{request.method}] {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response time
        process_time = time.time() - start_time
        print(f"Completed in {process_time:.2f}s - Status: {response.status_code}")

        response.headers["X-Process-Time"] = str(process_time)

        return response


def setup_cors(app):
    """
    Set up CORS middleware for the application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
