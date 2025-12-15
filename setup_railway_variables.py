#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Environment Variables Setup Script
This script helps configure Railway environment variables either via:
1. Railway CLI (if installed)
2. Manual instructions
3. Environment variable validation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}[ERROR] {text}{RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}[WARN] {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{BLUE}[INFO] {text}{RESET}")

# Railway environment variables to set
RAILWAY_VARIABLES = {
    # Database Configuration
    "DATABASE_URL": {
        "value": "postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require",
        "description": "PostgreSQL database connection (Neon)",
        "required": True,
        "secret": True
    },

    # Qdrant Vector Database
    "QDRANT_URL": {
        "value": "https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io",
        "description": "Qdrant Cloud vector database URL",
        "required": True,
        "secret": False
    },
    "QDRANT_API_KEY": {
        "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM",
        "description": "Qdrant Cloud API authentication key",
        "required": True,
        "secret": True
    },
    "QDRANT_COLLECTION": {
        "value": "chapter_chunks",
        "description": "Qdrant collection name",
        "required": False,
        "secret": False
    },

    # OpenAI Configuration
    "OPENAI_API_KEY": {
        "value": "sk-your_openai_api_key_here",  # PLACEHOLDER
        "description": "OpenAI API key (get from https://platform.openai.com/api-keys)",
        "required": True,
        "secret": True,
        "placeholder": True
    },
    "OPENAI_MODEL": {
        "value": "gpt-4o",
        "description": "OpenAI model for LLM responses",
        "required": False,
        "secret": False
    },
    "OPENAI_EMBEDDING_MODEL": {
        "value": "text-embedding-3-small",
        "description": "OpenAI model for embeddings",
        "required": False,
        "secret": False
    },

    # Gemini Configuration (alternative)
    "GEMINI_API_KEY": {
        "value": "AIzaSyB-w0Tc9vH_DQl5sEXzZZtcwEKJfWsChpI",
        "description": "Google Gemini API key",
        "required": False,
        "secret": True
    },

    # CORS Configuration
    "CORS_ORIGINS": {
        "value": "https://salmansiddiqui-99.github.io",
        "description": "Allowed frontend CORS origins",
        "required": True,
        "secret": False
    },

    # RAG Configuration
    "RAG_TOP_K": {
        "value": "5",
        "description": "Number of chunks to retrieve",
        "required": False,
        "secret": False
    },
    "RAG_SIMILARITY_THRESHOLD": {
        "value": "0.75",
        "description": "Minimum similarity score for chunks",
        "required": False,
        "secret": False
    },
}

def check_railway_cli() -> bool:
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(
            ["railway", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def validate_local_env_file() -> Dict[str, str]:
    """Load and validate local .env file"""
    env_path = Path("backend/.env")

    if not env_path.exists():
        print_error(f"No .env file found at {env_path}")
        return {}

    env_vars = {}
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
    except Exception as e:
        print_error(f"Failed to read .env file: {e}")
        return {}

    return env_vars

def check_environment_variables() -> Dict[str, Tuple[bool, str]]:
    """Check which environment variables are set locally"""
    print_header("Checking Local Environment Variables")

    status = {}
    local_env = validate_local_env_file()

    print(f"\nChecking {len(RAILWAY_VARIABLES)} required variables...\n")

    for var_name, config in RAILWAY_VARIABLES.items():
        is_set = var_name in local_env
        is_placeholder = config.get("placeholder", False)

        if is_set and not is_placeholder:
            value = local_env[var_name]
            # Mask sensitive values
            if config.get("secret"):
                display_value = value[:20] + "..." if len(value) > 20 else value
            else:
                display_value = value

            print_success(f"{var_name} = {display_value}")
            status[var_name] = (True, value)
        elif is_set and is_placeholder:
            print_warning(f"{var_name} = [PLACEHOLDER - needs real value]")
            status[var_name] = (False, "")
        else:
            if config.get("required"):
                print_error(f"{var_name} = [MISSING]")
            else:
                print_warning(f"{var_name} = [not set]")
            status[var_name] = (False, "")

    return status

def setup_via_railway_cli():
    """Set up variables using Railway CLI"""
    print_header("Setting Up Variables via Railway CLI")

    if not check_railway_cli():
        print_error("Railway CLI not installed")
        print_info("Install from: https://docs.railway.app/cli/install")
        return False

    print_info("Railway CLI found - starting setup\n")

    # First, authenticate
    print_info("Make sure you're logged in to Railway...")
    result = subprocess.run(
        ["railway", "whoami"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print_error("Not authenticated with Railway CLI")
        print_info("Run: railway login")
        return False

    print_success(f"Authenticated: {result.stdout.strip()}\n")

    # Load local env
    local_env = validate_local_env_file()

    # Set each variable
    success_count = 0
    for var_name, config in RAILWAY_VARIABLES.items():
        if var_name in local_env:
            value = local_env[var_name]

            # Skip placeholder values
            if config.get("placeholder"):
                print_warning(f"Skipping {var_name} - placeholder value detected")
                continue

            print_info(f"Setting {var_name}...")

            try:
                result = subprocess.run(
                    ["railway", "variable", "set", var_name, value],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print_success(f"Set {var_name}")
                    success_count += 1
                else:
                    print_error(f"Failed to set {var_name}: {result.stderr}")
            except Exception as e:
                print_error(f"Error setting {var_name}: {e}")

    print(f"\n{BOLD}Setup complete: {success_count} variables set{RESET}")
    return True

def generate_manual_setup_instructions():
    """Generate manual setup instructions"""
    print_header("Manual Setup Instructions")

    print(f"{BOLD}1. Go to Railway Dashboard:{RESET}")
    print("   https://railway.app/")
    print("   → Log in")
    print("   → Select project 'hackathon1-Q4'")
    print("   → Click on your backend service")
    print("   → Go to 'Variables' tab\n")

    print(f"{BOLD}2. Add the following variables:{RESET}\n")

    local_env = validate_local_env_file()

    for i, (var_name, config) in enumerate(RAILWAY_VARIABLES.items(), 1):
        if config.get("required") and var_name not in local_env:
            value = local_env.get(var_name, config.get("value", ""))

            if config.get("placeholder"):
                print(f"{i}. {YELLOW}{var_name}{RESET}")
                print(f"   Description: {config['description']}")
                print(f"   Value: {YELLOW}[Get from {config['description']}]{RESET}\n")
            else:
                print(f"{i}. {var_name}")
                print(f"   Description: {config['description']}")
                if config.get("secret"):
                    display_value = value[:30] + "..." if len(value) > 30 else value
                    print(f"   Value: {display_value}\n")
                else:
                    print(f"   Value: {value}\n")

    print(f"{BOLD}3. After adding variables:{RESET}")
    print("   → Click 'Redeploy' button")
    print("   → Wait for deployment to complete (green checkmark)")
    print("   → Check logs for any errors\n")

    print(f"{BOLD}4. Verify setup:{RESET}")
    print("   python test_chatbot_integration.py")
    print("   → All 9 tests should PASS ✓\n")

def generate_curl_tests():
    """Generate curl test commands"""
    print_header("Testing with curl")

    base_url = "https://hackathon1-q4-production.up.railway.app"

    tests = [
        ("Health Check", f"curl {base_url}/"),
        ("Modes", f"curl {base_url}/api/chatbot/modes"),
        ("Stats", f"curl {base_url}/api/chatbot/stats"),
        ("Query", f"curl -X POST {base_url}/api/chatbot/query -H 'Content-Type: application/json' -d '{{\"query_text\": \"What is robotics?\"}}'"),
    ]

    for i, (name, cmd) in enumerate(tests, 1):
        print(f"{i}. {name}:")
        print(f"   {cmd}\n")

def main():
    """Main entry point"""
    print_header("Railway Environment Variables Setup Tool")

    # Check environment
    has_railway_cli = check_railway_cli()

    print(f"Railway CLI: {GREEN if has_railway_cli else RED}{'installed' if has_railway_cli else 'not installed'}{RESET}")
    print(f"Setup Mode: {GREEN if has_railway_cli else YELLOW}{'automated' if has_railway_cli else 'manual'}{RESET}\n")

    # Check local variables
    env_status = check_environment_variables()

    # Count status
    set_count = sum(1 for is_set, _ in env_status.values() if is_set)
    total_count = len([v for v in RAILWAY_VARIABLES.values() if v.get("required")])

    print(f"\n{BOLD}Status: {set_count}/{total_count} required variables found locally{RESET}\n")

    # Offer setup options
    if has_railway_cli:
        print(f"{BOLD}Available setup methods:{RESET}")
        print("1. Automated (via Railway CLI)")
        print("2. Manual (via Railway Dashboard)")

        choice = input("\nChoose setup method (1 or 2): ").strip()

        if choice == "1":
            setup_via_railway_cli()
        else:
            generate_manual_setup_instructions()
    else:
        print(f"{BOLD}Using manual setup method{RESET}\n")
        generate_manual_setup_instructions()

    # Show test commands
    generate_curl_tests()

    print(f"{BOLD}Next Steps:{RESET}")
    print("1. Complete the setup above")
    print("2. Run: python test_chatbot_integration.py")
    print("3. All tests should PASS ✓")
    print("4. Test from frontend: https://salmansiddiqui-99.github.io\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Setup cancelled{RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
