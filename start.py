#!/usr/bin/env python3
"""
Unified startup script for Loneliness Combat Engine.

Starts both frontend (Next.js on port 3000) and backend (FastAPI + MCP on port 8000) concurrently.

Usage:
    python start.py              # Start both frontend and backend
    python start.py --backend    # Start backend only
    python start.py --frontend   # Start frontend only
"""

import subprocess
import sys
import os
import signal
import time
import argparse
from pathlib import Path

# ANSI color codes for pretty output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


class ProcessManager:
    """Manages frontend and backend processes."""

    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent.absolute()

    def start_backend(self):
        """Start FastAPI backend server with integrated MCP server."""
        print(f"{CYAN}{BOLD}🚀 Starting Backend (FastAPI + MCP on port 8000)...{RESET}")

        backend_env = os.environ.copy()
        backend_env["PYTHONUNBUFFERED"] = "1"  # Ensure immediate output

        # Use virtual environment Python (required)
        venv_python = self.project_root / "venv" / "bin" / "python"
        
        if not venv_python.exists():
            print(f"{RED}❌ Virtual environment not found at: {venv_python}{RESET}")
            print(f"{YELLOW}Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt{RESET}")
            return None
        
        python_exe = str(venv_python)

        backend_process = subprocess.Popen(
            [
                python_exe,
                "backend/main.py",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ],
            cwd=self.project_root,
            env=backend_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.processes.append(("Backend", backend_process))
        return backend_process

    def start_frontend(self):
        """Start Next.js frontend server."""
        print(f"{CYAN}{BOLD}🎨 Starting Frontend (Next.js on port 3000)...{RESET}")

        frontend_dir = self.project_root / "frontend"

        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print(f"{YELLOW}📦 Installing frontend dependencies...{RESET}")
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if npm_install.returncode != 0:
                print(f"{RED}❌ Failed to install frontend dependencies{RESET}")
                print(npm_install.stderr)
                return None

        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.processes.append(("Frontend", frontend_process))
        return frontend_process

    def stream_output(self, name, process):
        """Stream output from a process with colored labels."""
        colors = {
            "Backend": GREEN,
            "Frontend": CYAN
        }
        color = colors.get(name, RESET)

        try:
            for line in iter(process.stdout.readline, ""):
                if line:
                    print(f"{color}[{name}]{RESET} {line.rstrip()}")
        except Exception as e:
            print(f"{RED}[{name}] Error reading output: {e}{RESET}")

    def cleanup(self, signum=None, frame=None):
        """Cleanup: terminate all processes."""
        print(f"\n{YELLOW}🛑 Shutting down servers...{RESET}")

        for name, process in self.processes:
            try:
                print(f"{YELLOW}   Stopping {name}...{RESET}")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"{RED}   Force killing {name}...{RESET}")
                process.kill()
                process.wait()
            except Exception as e:
                print(f"{RED}   Error stopping {name}: {e}{RESET}")

        print(f"{GREEN}✅ All servers stopped{RESET}")
        sys.exit(0)

    def run(self, start_backend=True, start_frontend=True):
        """Start servers based on arguments and monitor them."""
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        print(f"{BOLD}{CYAN}╔════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║  Loneliness Combat Engine - Start Script  ║{RESET}")
        print(f"{BOLD}{CYAN}╚════════════════════════════════════════════╝{RESET}\n")

        backend = None
        frontend = None
        threads = []

        # Start backend if requested
        if start_backend:
            backend = self.start_backend()
            if not backend:
                print(f"{RED}❌ Failed to start backend{RESET}")
                return
            time.sleep(1)  # Give backend a moment to start

        # Start frontend if requested
        if start_frontend:
            frontend = self.start_frontend()
            if not frontend:
                print(f"{RED}❌ Failed to start frontend{RESET}")
                self.cleanup()
                return

        # Print status based on what's running
        print(f"\n{GREEN}{BOLD}✅ Server(s) started!{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        if start_frontend:
            print(f"{BOLD}🌐 Frontend:{RESET} http://localhost:3000")
        
        if start_backend:
            print(f"{BOLD}⚙️  Backend API:{RESET} http://localhost:8000")
            print(f"{BOLD}🔌 MCP Server:{RESET}  http://localhost:8000/mcp")
            print(f"{BOLD}📚 API Docs:{RESET}    http://localhost:8000/docs")
        
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop server(s){RESET}\n")

        # Stream output from processes
        import threading

        if backend:
            backend_thread = threading.Thread(
                target=self.stream_output,
                args=("Backend", backend),
                daemon=True
            )
            backend_thread.start()
            threads.append(backend_thread)

        if frontend:
            frontend_thread = threading.Thread(
                target=self.stream_output,
                args=("Frontend", frontend),
                daemon=True
            )
            frontend_thread.start()
            threads.append(frontend_thread)

        # Wait for processes to complete or be interrupted
        try:
            # Wait for the first process that was started
            if backend:
                backend.wait()
            elif frontend:
                frontend.wait()
        except KeyboardInterrupt:
            self.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Loneliness Combat Engine - Unified startup script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py              # Start both frontend and backend
  python start.py --backend    # Start backend only
  python start.py --frontend   # Start frontend only
        """
    )
    
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Start backend server only (FastAPI + MCP on port 8000)"
    )
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Start frontend server only (Next.js on port 3000)"
    )
    
    args = parser.parse_args()
    
    # Determine what to start
    start_backend = args.backend or (not args.backend and not args.frontend)
    start_frontend = args.frontend or (not args.backend and not args.frontend)
    
    manager = ProcessManager()

    try:
        manager.run(start_backend=start_backend, start_frontend=start_frontend)
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        manager.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
