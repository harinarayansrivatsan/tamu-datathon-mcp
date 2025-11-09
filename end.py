#!/usr/bin/env python3
"""
Shutdown script for Loneliness Combat Engine.

Stops services running on ports 3000 (frontend) and 8000 (backend).
"""

import subprocess
import sys
import platform
import argparse

# ANSI color codes for pretty output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def find_process_on_port(port):
    """Find process ID running on a specific port."""
    system = platform.system()
    
    try:
        if system == "Darwin" or system == "Linux":
            # Use lsof on macOS/Linux
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True
            )
            pids = result.stdout.strip().split('\n')
            return [pid for pid in pids if pid]
        
        elif system == "Windows":
            # Use netstat on Windows
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            pids = []
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if parts:
                        pids.append(parts[-1])
            return pids
        
    except Exception as e:
        print(f"{RED}Error finding process on port {port}: {e}{RESET}")
        return []
    
    return []


def kill_process(pid):
    """Kill a process by PID."""
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", pid], check=True)
        else:
            subprocess.run(["kill", "-9", pid], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        print(f"{RED}Error killing process {pid}: {e}{RESET}")
        return False


def stop_service(port, name):
    """Stop service running on specified port."""
    print(f"{CYAN}Looking for {name} on port {port}...{RESET}")
    
    pids = find_process_on_port(port)
    
    if not pids:
        print(f"{YELLOW}  No process found on port {port}{RESET}")
        return False
    
    success = True
    for pid in pids:
        print(f"{YELLOW}  Found PID {pid}, stopping...{RESET}")
        if kill_process(pid):
            print(f"{GREEN}  ✅ Stopped process {pid}{RESET}")
        else:
            print(f"{RED}  ❌ Failed to stop process {pid}{RESET}")
            success = False
    
    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Loneliness Combat Engine - Shutdown script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python end.py              # Stop both frontend and backend
  python end.py --backend    # Stop backend only (port 8000)
  python end.py --frontend   # Stop frontend only (port 3000)
        """
    )
    
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Stop backend server only (port 8000)"
    )
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Stop frontend server only (port 3000)"
    )
    
    args = parser.parse_args()
    
    # Determine what to stop
    stop_backend = args.backend or (not args.backend and not args.frontend)
    stop_frontend = args.frontend or (not args.backend and not args.frontend)
    
    print(f"{BOLD}{CYAN}╔════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║  Loneliness Combat Engine - End Script    ║{RESET}")
    print(f"{BOLD}{CYAN}╚════════════════════════════════════════════╝{RESET}\n")
    
    stopped_any = False
    
    if stop_frontend:
        if stop_service(3000, "Frontend (Next.js)"):
            stopped_any = True
    
    if stop_backend:
        if stop_service(8000, "Backend (FastAPI + MCP)"):
            stopped_any = True
    
    print()
    if stopped_any:
        print(f"{GREEN}{BOLD}✅ Service(s) stopped successfully!{RESET}")
    else:
        print(f"{YELLOW}{BOLD}ℹ️  No services were running{RESET}")
    
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        sys.exit(1)
