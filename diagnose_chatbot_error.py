#!/usr/bin/env python3
"""Diagnose chatbot 'No response generated' error"""

import requests
import json
import sys

BACKEND_URL = "https://hackathon1-q4-production.up.railway.app"

def test_endpoint(name, method, endpoint, data=None):
    """Test an endpoint and return response"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        print(f"\n[{name}]")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                body = response.json()
                print(f"  Response: {json.dumps(body, indent=2)}")
                return True, body
            except:
                print(f"  Response: {response.text[:200]}")
                return True, response.text
        else:
            print(f"  Error: {response.text[:200]}")
            return False, response.text
    except Exception as e:
        print(f"\n[{name}] FAILED")
        print(f"  Error: {str(e)}")
        return False, str(e)

print("=" * 70)
print("CHATBOT ERROR DIAGNOSTIC")
print("=" * 70)

# Test 1: Health
print("\n1. Testing health endpoint...")
ok, data = test_endpoint("Health", "GET", "/")

# Test 2: Modes
print("\n2. Testing modes endpoint...")
ok, data = test_endpoint("Modes", "GET", "/api/chatbot/modes")

# Test 3: Stats (this shows variable configuration)
print("\n3. Testing stats endpoint...")
ok, data = test_endpoint("Stats", "GET", "/api/chatbot/stats")

# Test 4: Query (the actual test)
print("\n4. Testing chatbot query...")
query_data = {
    "query": "What is ROS?",
    "mode": "global"
}
ok, data = test_endpoint("Query", "POST", "/api/chatbot/query", query_data)

print("\n" + "=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)
print("\nIf you see:")
print("  - Stats endpoint error about OPENAI_API_KEY → Old code still deployed")
print("  - Stats endpoint shows variables set → New code deployed")
print("  - Query returns empty/null → Check Gemini quota or embedding service")
print("  - Query has database error → DB session not initialized")
print("\nNext steps:")
print("  1. Check Railway is using 002-rag-chatbot branch")
print("  2. Verify environment variables are set on Railway")
print("  3. Check Railway logs for detailed errors")

