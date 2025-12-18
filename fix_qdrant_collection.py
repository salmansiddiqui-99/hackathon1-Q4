#!/usr/bin/env python3
"""
Fix Qdrant collection vector dimensions from 384 to 1024
"""
import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

if __name__ == "__main__":
    # Fix Windows encoding
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    load_dotenv("backend/.env")

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "chapter_chunks"

    logger.info("=" * 70)
    logger.info("FIXING QDRANT COLLECTION VECTOR DIMENSIONS")
    logger.info("=" * 70)

    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        logger.info(f"✓ Connected to Qdrant at {QDRANT_URL}")

        # Check existing collection
        try:
            collection_info = client.get_collection(COLLECTION_NAME)
            current_dims = collection_info.config.params.vectors.size
            logger.info(f"Current collection dimensions: {current_dims}")

            if current_dims == 1024:
                logger.info("✓ Collection already has correct 1024 dimensions. No fix needed.")
                sys.exit(0)

            logger.info(f"Deleting collection with {current_dims} dimensions...")
            client.delete_collection(COLLECTION_NAME)
            logger.info("✓ Collection deleted")
        except Exception as e:
            logger.info(f"Collection doesn't exist or error checking: {e}")

        # Create new collection with 1024 dimensions
        logger.info(f"Creating new collection '{COLLECTION_NAME}' with 1024 dimensions...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE
            ),
        )
        logger.info("✓ Collection created successfully with 1024 dimensions")

        # Verify
        collection_info = client.get_collection(COLLECTION_NAME)
        logger.info(f"✓ Verified: {collection_info.config.params.vectors.size} dimensions")
        logger.info("=" * 70)
        logger.info("Ready for re-indexing!")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Failed to fix collection: {e}")
        sys.exit(1)
