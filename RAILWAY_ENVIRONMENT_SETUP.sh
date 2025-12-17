#!/bin/bash
# Railway Environment Variables Setup Script
# This script configures all required environment variables on Railway
# Prerequisites: Railway CLI installed and authenticated (railway login)

echo "=============================================================================="
echo "Railway Environment Variables Setup"
echo "=============================================================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "ERROR: Railway CLI is not installed"
    echo "Install from: https://docs.railway.app/cli/install"
    exit 1
fi

echo "Setting up environment variables on Railway..."
echo ""

# Set Database Configuration
echo "[1/11] Setting DATABASE_URL..."
railway variable set DATABASE_URL "postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require"

# Set Qdrant Configuration
echo "[2/11] Setting QDRANT_URL..."
railway variable set QDRANT_URL "https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io"

echo "[3/11] Setting QDRANT_API_KEY..."
railway variable set QDRANT_API_KEY "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM"

echo "[4/11] Setting QDRANT_COLLECTION..."
railway variable set QDRANT_COLLECTION "chapter_chunks"

echo "[5/11] Setting QDRANT_COLLECTION_NAME..."
railway variable set QDRANT_COLLECTION_NAME "aibook"

# Set OpenAI Configuration
echo "[6/11] Setting OPENAI_API_KEY..."
echo "IMPORTANT: Replace 'sk-your_openai_api_key_here' with your actual OpenAI API key"
railway variable set OPENAI_API_KEY "sk-your_openai_api_key_here"

echo "[7/11] Setting OPENAI_MODEL..."
railway variable set OPENAI_MODEL "gpt-4o"

echo "[8/11] Setting OPENAI_EMBEDDING_MODEL..."
railway variable set OPENAI_EMBEDDING_MODEL "text-embedding-3-small"

# Set Gemini Configuration
echo "[9/11] Setting GEMINI_API_KEY..."
railway variable set GEMINI_API_KEY "AIzaSyB-w0Tc9vH_DQl5sEXzZZtcwEKJfWsChpI"

echo "[10/11] Setting GEMINI_MODEL..."
railway variable set GEMINI_MODEL "gemini-2.5-flash"

# Set CORS Configuration
echo "[11/11] Setting CORS_ORIGINS..."
railway variable set CORS_ORIGINS "https://salmansiddiqui-99.github.io"

echo ""
echo "=============================================================================="
echo "Setup Complete!"
echo "=============================================================================="
echo ""
echo "Next Steps:"
echo "1. Update OPENAI_API_KEY with your actual key from:"
echo "   https://platform.openai.com/api-keys"
echo ""
echo "   Run: railway variable set OPENAI_API_KEY 'sk-your-actual-key'"
echo ""
echo "2. Redeploy your service:"
echo "   railway up"
echo ""
echo "3. Verify setup:"
echo "   python test_chatbot_integration.py"
echo ""
echo "=============================================================================="
