#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Deployment Monitor
Monitors backend deployment after variables are added
Checks for successful startup and configuration validation
"""

import requests
import time
import sys
from datetime import datetime
from typing import Tuple, Optional

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BACKEND_URL = "https://hackathon1-q4-production.up.railway.app"
HEALTH_ENDPOINT = f"{BACKEND_URL}/"
MODES_ENDPOINT = f"{BACKEND_URL}/api/chatbot/modes"
STATS_ENDPOINT = f"{BACKEND_URL}/api/chatbot/stats"
MAX_WAIT_TIME = 600  # 10 minutes
CHECK_INTERVAL = 5   # 5 seconds between checks

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_status(symbol: str, message: str, detail: str = ""):
    """Print status message"""
    if symbol == "[OK]":
        color = GREEN
    elif symbol == "[FAIL]":
        color = RED
    elif symbol == "[WAIT]":
        color = YELLOW
    else:
        color = BLUE

    output = f"{color}{symbol}{RESET} {message}"
    if detail:
        output += f" ({detail})"
    print(output)

def check_health() -> Tuple[bool, Optional[dict]]:
    """Check if backend is responding to health checks"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, None
    except requests.exceptions.ConnectionError:
        return False, None
    except requests.exceptions.Timeout:
        return False, None
    except Exception as e:
        return False, None

def check_modes() -> Tuple[bool, Optional[list]]:
    """Check if chatbot modes endpoint is working"""
    try:
        response = requests.get(MODES_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, None
    except Exception:
        return False, None

def check_stats() -> Tuple[bool, Optional[dict]]:
    """Check if RAG stats endpoint is working (requires all variables)"""
    try:
        response = requests.get(STATS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Check if it's an error response
            if "error" not in data:
                return True, data
            else:
                return False, data
        else:
            return False, None
    except Exception:
        return False, None

def check_variable_errors(data: Optional[dict]) -> Optional[str]:
    """Check if response indicates missing variables"""
    if not data or not isinstance(data, dict):
        return None

    error_msg = data.get("error", "")

    if "OPENAI_API_KEY" in error_msg:
        return "OPENAI_API_KEY"
    elif "DATABASE_URL" in error_msg:
        return "DATABASE_URL"
    elif "QDRANT" in error_msg:
        return "QDRANT_URL or QDRANT_API_KEY"

    return None

def monitor_deployment():
    """Main deployment monitoring function"""
    print_header("Railway Deployment Monitor")

    print(f"{BLUE}Monitoring backend deployment...{RESET}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Max wait time: {MAX_WAIT_TIME} seconds (~10 minutes)")
    print(f"Check interval: {CHECK_INTERVAL} seconds\n")

    start_time = time.time()
    attempt = 0

    # Phase 1: Wait for backend to come online
    print_header("PHASE 1: Waiting for Backend to Come Online")

    while time.time() - start_time < MAX_WAIT_TIME:
        attempt += 1
        elapsed = int(time.time() - start_time)

        health_ok, health_data = check_health()

        if health_ok:
            service_name = health_data.get("service", "Unknown")
            version = health_data.get("version", "Unknown")
            print_status("[OK]", f"Backend is online!", f"{service_name} v{version}")
            break
        else:
            print_status("[WAIT]", f"Waiting for backend ({elapsed}s, attempt {attempt})...", "Not responding yet")
            time.sleep(CHECK_INTERVAL)
    else:
        print_status("[FAIL]", "Backend did not come online within timeout", "Check Railway logs")
        return False

    # Phase 2: Check basic endpoints
    print_header("PHASE 2: Checking Basic Endpoints")

    # Health check
    health_ok, health_data = check_health()
    if health_ok:
        print_status("[OK]", "Health endpoint", f"Status: {health_data.get('status')}")
    else:
        print_status("[FAIL]", "Health endpoint", "Not responding")
        return False

    # Modes endpoint
    modes_ok, modes_data = check_modes()
    if modes_ok:
        print_status("[OK]", "Chatbot modes endpoint", f"Found {len(modes_data)} modes")
        for i, mode in enumerate(modes_data, 1):
            print(f"         {i}. {mode}")
    else:
        print_status("[FAIL]", "Chatbot modes endpoint", "Not responding")

    # Phase 3: Check variable configuration
    print_header("PHASE 3: Checking Variable Configuration")

    stats_ok, stats_data = check_stats()

    if stats_ok:
        print_status("[OK]", "RAG stats endpoint", "All variables configured!")
        if isinstance(stats_data, dict):
            print(f"         Total chunks: {stats_data.get('total_chunks_indexed', 'N/A')}")
            print(f"         Total chapters: {stats_data.get('total_chapters', 'N/A')}")
            print(f"         Vectors indexed: {stats_data.get('vectors_indexed', 'N/A')}")
    else:
        missing_var = check_variable_errors(stats_data)
        if missing_var:
            print_status("[FAIL]", "RAG stats endpoint", f"Missing variable: {missing_var}")
            print(f"\n{RED}ERROR: One or more required variables are missing on Railway:{RESET}")
            if isinstance(stats_data, dict):
                error_detail = stats_data.get("error", "Unknown error")
                print(f"  {error_detail}")
            return False
        else:
            print_status("[FAIL]", "RAG stats endpoint", "Not responding")

    # Phase 4: Test full chatbot query
    print_header("PHASE 4: Testing Chatbot Query Endpoint")

    try:
        query_payload = {"query_text": "What is robotics?"}
        response = requests.post(
            f"{BACKEND_URL}/api/chatbot/query",
            json=query_payload,
            timeout=10
        )

        if response.status_code == 200:
            print_status("[OK]", "Chatbot query endpoint", "Responding")
            # Check if we can parse the response
            if "application/x-ndjson" in response.headers.get("content-type", ""):
                print_status("[OK]", "Response format", "Streaming (NDJSON)")
            else:
                print_status("[OK]", "Response format", response.headers.get("content-type", "Unknown"))
        else:
            print_status("[FAIL]", "Chatbot query endpoint", f"HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print_status("[FAIL]", "Chatbot query endpoint", "Request timeout")
    except Exception as e:
        print_status("[FAIL]", "Chatbot query endpoint", str(e))

    # Summary
    print_header("DEPLOYMENT MONITORING COMPLETE")

    if stats_ok:
        print(f"{GREEN}SUCCESS! All systems operational{RESET}")
        print(f"\nYour chatbot backend is ready!")
        print(f"Next: Run python test_chatbot_integration.py")
        return True
    else:
        print(f"{YELLOW}WARNING: Some endpoints not fully ready{RESET}")
        print(f"\nYour backend is online but may need more configuration.")
        print(f"Check Railway logs for any error messages.")
        return False

def main():
    """Main entry point"""
    try:
        print(f"\n{BOLD}Railway Deployment Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")

        success = monitor_deployment()

        print(f"\n{BOLD}{'='*70}{RESET}")
        if success:
            print(f"{GREEN}Deployment Status: SUCCESSFUL{RESET}")
            print(f"Your chatbot backend is ready to use!")
            print(f"\nNext steps:")
            print(f"  1. Run: python test_chatbot_integration.py")
            print(f"  2. Expected: All 9 tests should PASS")
            print(f"  3. Test frontend: https://salmansiddiqui-99.github.io")
        else:
            print(f"{RED}Deployment Status: NEEDS ATTENTION{RESET}")
            print(f"Check Railway logs and verify all variables are set.")
            print(f"Re-run this script after fixing issues.")
        print(f"{BOLD}{'='*70}{RESET}\n")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Monitoring interrupted by user{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
