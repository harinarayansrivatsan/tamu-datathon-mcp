"""
Entry point for Loneliness Combat Engine backend.

Runs the FastAPI server with integrated MCP server mounted at /mcp endpoint.
"""

import sys
import os
import argparse

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core import get_settings

settings = get_settings()


def main():
    """Main entry point for the backend application."""
    parser = argparse.ArgumentParser(description="Loneliness Combat Engine Backend")
    parser.add_argument(
        "--host",
        default=settings.api_host,
        help="Host to bind to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help="Port to bind to",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.debug,
        help="Enable auto-reload",
    )

    args = parser.parse_args()

    # Run FastAPI server with integrated MCP server
    print("🚀 Starting FastAPI server with integrated MCP server...")
    print(f"� API available at: http://{args.host}:{args.port}")
    print(f"🔌 MCP server available at: http://{args.host}:{args.port}/mcp")

    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
