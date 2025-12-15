#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Verification Script
Run this AFTER you add variables to Railway and click Redeploy
Checks if all variables are properly set
"""

import requests
import time
import sys
from datetime import datetime

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BACKEND_URL = "https://hackathon1-q4-production.up.railway.app"

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}\n")

def check_endpoint(name, url):
    """Check a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] {name} - HTTP 200")
            return True, response.json() if response.text else None
        else:
            print(f"[FAIL] {name} - HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"[FAIL] {name} - {str(e)[:50]}")
        return False, None

def main():
    print_header("Quick Verification After Setup")
    print("Running checks to verify variables are set...\n")

    # Check health
    print("1. Checking health endpoint...")
    health_ok, health_data = check_endpoint("Health", f"{BACKEND_URL}/")

    # Check modes
    print("\n2. Checking chatbot modes...")
    modes_ok, modes_data = check_endpoint("Modes", f"{BACKEND_URL}/api/chatbot/modes")
    if modes_ok and modes_data:
        print(f"   Found modes: {', '.join(modes_data)}")

    # Check stats (critical - shows if variables are set)
    print("\n3. Checking stats (variable configuration)...")
    stats_ok, stats_data = check_endpoint("Stats", f"{BACKEND_URL}/api/chatbot/stats")

    if stats_ok and stats_data:
        if "error" in stats_data:
            print(f"   ERROR: {stats_data['error']}")
            print("\n   Variable still missing! Check which one:")
            error_msg = stats_data.get('error', '')
            if 'OPENAI_API_KEY' in error_msg:
                print("   -> OPENAI_API_KEY not set on Railway")
            elif 'DATABASE_URL' in error_msg:
                print("   -> DATABASE_URL not set on Railway")
            elif 'QDRANT' in error_msg:
                print("   -> QDRANT_URL or QDRANT_API_KEY not set")
            stats_ok = False
        else:
            print(f"   Chunks indexed: {stats_data.get('total_chunks_indexed', 'N/A')}")
            print(f"   Chapters: {stats_data.get('total_chapters', 'N/A')}")
            stats_ok = True

    # Summary
    print_header("Verification Results")

    if health_ok and modes_ok and stats_ok:
        print("[SUCCESS] All variables are set!")
        print("\nYour chatbot is fully configured.")
        print("Next: Run python test_chatbot_integration.py")
        return True
    else:
        print("[NEEDS ATTENTION] Some checks failed")
        if not stats_ok:
            print("\nMissing variable detected!")
            print("Steps:")
            print("  1. Go to Railway dashboard")
            print("  2. Check Variables tab")
            print("  3. Verify all 4 variables are there")
            print("  4. Redeploy if you made changes")
            print("  5. Wait 2-3 minutes")
            print("  6. Run this script again")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled")
        sys.exit(1)
