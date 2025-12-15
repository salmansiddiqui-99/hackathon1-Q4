#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test script for chatbot integration with Railway variables
Tests: CORS, Database, Qdrant, Gemini/OpenAI, RAG pipeline
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Environment variables for testing
RAILWAY_BACKEND_URL = os.getenv("RAILWAY_BACKEND_URL", "https://hackathon1-q4-production.up.railway.app")
FRONTEND_URL = "https://salmansiddiqui-99.github.io"
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://salmansiddiqui-99.github.io")

# Test results tracking
test_results = {
    "timestamp": datetime.utcnow().isoformat(),
    "backend_url": RAILWAY_BACKEND_URL,
    "frontend_url": FRONTEND_URL,
    "tests": {}
}


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(test_name: str, status: str, details: str = ""):
    """Print test result"""
    emoji = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    print(f"{emoji} {test_name}: {status}")
    if details:
        print(f"   -> {details}")


def test_environment_variables() -> bool:
    """Test that all required environment variables are set"""
    print_header("ENVIRONMENT VARIABLES TEST")

    required_vars = {
        "DATABASE_URL": DATABASE_URL,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "QDRANT_API_KEY": QDRANT_API_KEY,
        "QDRANT_URL": QDRANT_URL,
        "CORS_ORIGINS": CORS_ORIGINS,
    }

    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # Mask sensitive values
            display_value = var_value[:20] + "..." if len(str(var_value)) > 20 else var_value
            print_test(f"  {var_name}", "PASS", f"Value: {display_value}")
        else:
            print_test(f"  {var_name}", "FAIL", "Not set")
            all_set = False

    test_results["tests"]["environment_variables"] = "PASS" if all_set else "FAIL"
    return all_set


def test_health_endpoint() -> bool:
    """Test the health check endpoint"""
    print_header("HEALTH CHECK TEST")

    try:
        health_url = f"{RAILWAY_BACKEND_URL}/"
        print(f"Testing: {health_url}")

        response = requests.get(health_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_test("Health Endpoint", "PASS", f"Status: {data.get('status')}")
            test_results["tests"]["health_endpoint"] = "PASS"
            test_results["tests"]["health_data"] = data
            return True
        else:
            print_test("Health Endpoint", "FAIL", f"HTTP {response.status_code}")
            test_results["tests"]["health_endpoint"] = "FAIL"
            return False

    except requests.exceptions.ConnectionError:
        print_test("Health Endpoint", "FAIL", "Connection error - backend may be offline")
        test_results["tests"]["health_endpoint"] = "FAIL"
        return False
    except Exception as e:
        print_test("Health Endpoint", "FAIL", str(e))
        test_results["tests"]["health_endpoint"] = "FAIL"
        return False


def test_cors_configuration() -> bool:
    """Test CORS headers from frontend origin"""
    print_header("CORS CONFIGURATION TEST")

    try:
        cors_test_url = f"{RAILWAY_BACKEND_URL}/api/chatbot/modes"
        print(f"Testing CORS from: {FRONTEND_URL}")
        print(f"Endpoint: {cors_test_url}")

        headers = {
            "Origin": FRONTEND_URL,
            "Access-Control-Request-Method": "GET"
        }

        response = requests.options(cors_test_url, headers=headers, timeout=10)

        # Check for CORS headers
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        cors_methods = response.headers.get("Access-Control-Allow-Methods")
        cors_credentials = response.headers.get("Access-Control-Allow-Credentials")

        if cors_origin == FRONTEND_URL or cors_origin == "*":
            print_test("CORS Allow-Origin", "PASS", f"Allows: {cors_origin}")
        else:
            print_test("CORS Allow-Origin", "FAIL", f"Got: {cors_origin}")
            return False

        if cors_methods:
            print_test("CORS Allow-Methods", "PASS", f"Methods: {cors_methods}")
        else:
            print_test("CORS Allow-Methods", "WARN", "No methods header")

        test_results["tests"]["cors_configuration"] = "PASS"
        return True

    except Exception as e:
        print_test("CORS Configuration", "FAIL", str(e))
        test_results["tests"]["cors_configuration"] = "FAIL"
        return False


def test_qdrant_connectivity() -> bool:
    """Test Qdrant vector database connectivity"""
    print_header("QDRANT CONNECTIVITY TEST")

    try:
        from qdrant_client import QdrantClient

        print(f"Connecting to: {QDRANT_URL}")
        print(f"Using API key: {QDRANT_API_KEY[:20]}..." if QDRANT_API_KEY else "No API key")

        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

        # Try to get collections
        collections = client.get_collections()
        print_test("Qdrant Connection", "PASS", f"Connected successfully")
        print_test("Collections", "PASS", f"Found {len(collections.collections)} collections")

        # List collections
        for i, collection in enumerate(collections.collections[:5], 1):
            print(f"   └─ Collection {i}: {collection.name}")

        test_results["tests"]["qdrant_connectivity"] = "PASS"
        test_results["tests"]["qdrant_collections"] = [c.name for c in collections.collections]
        return True

    except ImportError:
        print_test("Qdrant Import", "FAIL", "qdrant-client not installed")
        test_results["tests"]["qdrant_connectivity"] = "FAIL"
        return False
    except Exception as e:
        print_test("Qdrant Connection", "FAIL", str(e))
        test_results["tests"]["qdrant_connectivity"] = "FAIL"
        return False


def test_database_connectivity() -> bool:
    """Test PostgreSQL database connectivity"""
    print_header("DATABASE CONNECTIVITY TEST")

    try:
        from sqlalchemy import create_engine, text

        if not DATABASE_URL:
            print_test("Database URL", "FAIL", "DATABASE_URL not set")
            test_results["tests"]["database_connectivity"] = "FAIL"
            return False

        # Create engine
        print(f"Connecting to PostgreSQL...")
        engine = create_engine(DATABASE_URL, echo=False)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print_test("Database Connection", "PASS", "Connected to PostgreSQL")

            # Get schema info
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            print_test("Tables", "PASS", f"Found {len(tables)} tables")

            for table in tables[:10]:
                print(f"   └─ {table}")

        test_results["tests"]["database_connectivity"] = "PASS"
        test_results["tests"]["database_tables"] = tables
        return True

    except ImportError:
        print_test("SQLAlchemy Import", "FAIL", "sqlalchemy not installed")
        test_results["tests"]["database_connectivity"] = "FAIL"
        return False
    except Exception as e:
        print_test("Database Connection", "FAIL", str(e))
        test_results["tests"]["database_connectivity"] = "FAIL"
        return False


def test_gemini_api() -> bool:
    """Test Gemini API connectivity"""
    print_header("GEMINI API TEST")

    try:
        import google.generativeai as genai

        if not GEMINI_API_KEY:
            print_test("Gemini API Key", "FAIL", "GEMINI_API_KEY not set")
            test_results["tests"]["gemini_api"] = "FAIL"
            return False

        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)

        # Test with simple query
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello, how are you?", stream=False)

        if response and response.text:
            print_test("Gemini Connection", "PASS", "API responded successfully")
            print_test("Response", "PASS", f"Got response: {response.text[:50]}...")
            test_results["tests"]["gemini_api"] = "PASS"
            return True
        else:
            print_test("Gemini Response", "FAIL", "No response from API")
            test_results["tests"]["gemini_api"] = "FAIL"
            return False

    except ImportError:
        print_test("Google Generative AI", "FAIL", "google-generativeai not installed")
        test_results["tests"]["gemini_api"] = "FAIL"
        return False
    except Exception as e:
        print_test("Gemini API", "FAIL", str(e))
        test_results["tests"]["gemini_api"] = "FAIL"
        return False


def test_chatbot_modes_endpoint() -> bool:
    """Test the chatbot modes endpoint"""
    print_header("CHATBOT MODES ENDPOINT TEST")

    try:
        modes_url = f"{RAILWAY_BACKEND_URL}/api/chatbot/modes"
        print(f"Testing: {modes_url}")

        response = requests.get(modes_url, timeout=10)

        if response.status_code == 200:
            modes = response.json()
            print_test("Modes Endpoint", "PASS", f"Found {len(modes)} modes")
            for mode in modes:
                print(f"   └─ {mode}")
            test_results["tests"]["chatbot_modes"] = "PASS"
            test_results["tests"]["modes_data"] = modes
            return True
        else:
            print_test("Modes Endpoint", "FAIL", f"HTTP {response.status_code}")
            test_results["tests"]["chatbot_modes"] = "FAIL"
            return False

    except Exception as e:
        print_test("Chatbot Modes", "FAIL", str(e))
        test_results["tests"]["chatbot_modes"] = "FAIL"
        return False


def test_chatbot_stats_endpoint() -> bool:
    """Test the RAG stats endpoint"""
    print_header("RAG STATS ENDPOINT TEST")

    try:
        stats_url = f"{RAILWAY_BACKEND_URL}/api/chatbot/stats"
        print(f"Testing: {stats_url}")

        response = requests.get(stats_url, timeout=10)

        if response.status_code == 200:
            stats = response.json()
            if "error" not in stats:
                print_test("Stats Endpoint", "PASS", "Retrieved statistics")
                print(f"   └─ Total chunks: {stats.get('total_chunks_indexed', 'N/A')}")
                print(f"   └─ Total chapters: {stats.get('total_chapters', 'N/A')}")
                print(f"   └─ Vectors indexed: {stats.get('vectors_indexed', 'N/A')}")
                test_results["tests"]["chatbot_stats"] = "PASS"
                test_results["tests"]["stats_data"] = stats
                return True
            else:
                print_test("Stats Endpoint", "FAIL", f"Error: {stats.get('error')}")
                test_results["tests"]["chatbot_stats"] = "FAIL"
                return False
        else:
            print_test("Stats Endpoint", "FAIL", f"HTTP {response.status_code}")
            test_results["tests"]["chatbot_stats"] = "FAIL"
            return False

    except Exception as e:
        print_test("RAG Stats", "FAIL", str(e))
        test_results["tests"]["chatbot_stats"] = "FAIL"
        return False


def test_chatbot_query() -> bool:
    """Test the chatbot query endpoint with a simple question"""
    print_header("CHATBOT QUERY TEST")

    try:
        query_url = f"{RAILWAY_BACKEND_URL}/api/chatbot/query"
        print(f"Testing: {query_url}")

        payload = {
            "query_text": "What is physical AI and robotics?",
            "chapter_id": None,
            "selected_text": None
        }

        print(f"Query: {payload['query_text']}")

        response = requests.post(query_url, json=payload, timeout=30)

        if response.status_code == 200:
            # Handle streaming response
            if "application/x-ndjson" in response.headers.get("content-type", ""):
                print_test("Query Endpoint", "PASS", "Received streaming response")

                # Parse NDJSON response
                tokens = []
                metadata = None
                for line in response.text.strip().split("\n"):
                    if line:
                        data = json.loads(line)
                        if data["type"] == "token":
                            tokens.append(data["data"])
                        elif data["type"] == "metadata":
                            metadata = data["data"]

                response_text = "".join(tokens)
                print(f"   └─ Response tokens: {len(tokens)}")
                print(f"   └─ Response preview: {response_text[:100]}...")

                if metadata:
                    print(f"   └─ Chunks used: {metadata.get('chunks_used', 'N/A')}")
                    print(f"   └─ Confident: {metadata.get('is_confident', 'N/A')}")

                test_results["tests"]["chatbot_query"] = "PASS"
                test_results["tests"]["query_data"] = {
                    "response_length": len(response_text),
                    "tokens_count": len(tokens),
                    "metadata": metadata
                }
                return True
            else:
                data = response.json()
                if data.get("success"):
                    print_test("Query Endpoint", "PASS", "Query processed successfully")
                    test_results["tests"]["chatbot_query"] = "PASS"
                    return True
                else:
                    print_test("Query Endpoint", "FAIL", f"Error: {data.get('error')}")
                    test_results["tests"]["chatbot_query"] = "FAIL"
                    return False
        else:
            print_test("Query Endpoint", "FAIL", f"HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            test_results["tests"]["chatbot_query"] = "FAIL"
            return False

    except Exception as e:
        print_test("Chatbot Query", "FAIL", str(e))
        test_results["tests"]["chatbot_query"] = "FAIL"
        return False


def generate_report():
    """Generate a test report"""
    print_header("TEST SUMMARY REPORT")

    passed = sum(1 for v in test_results["tests"].values() if v == "PASS")
    failed = sum(1 for v in test_results["tests"].values() if v == "FAIL")
    total = passed + failed

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")

    # Save report to file
    report_file = "test_report.json"
    with open(report_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"Report saved to: {report_file}")

    return passed == total


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CHATBOT INTEGRATION TEST SUITE")
    print("Testing Railway Deployment Configuration")
    print("=" * 70)

    # Run tests in order
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Health Check", test_health_endpoint),
        ("CORS Configuration", test_cors_configuration),
        ("Qdrant Connectivity", test_qdrant_connectivity),
        ("Database Connectivity", test_database_connectivity),
        ("Gemini API", test_gemini_api),
        ("Chatbot Modes", test_chatbot_modes_endpoint),
        ("RAG Stats", test_chatbot_stats_endpoint),
        ("Chatbot Query", test_chatbot_query),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_test(test_name, "ERROR", str(e))
            results[test_name] = False

    # Generate report
    all_passed = generate_report()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
