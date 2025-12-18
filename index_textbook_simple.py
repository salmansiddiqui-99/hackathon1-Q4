#!/usr/bin/env python3
"""
Simple Textbook Indexing - Memory Efficient Version

Processes files one at a time to avoid memory issues.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List
import time

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv("backend/.env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TEXTBOOK_DIR = Path("textbook/docs")

def chunk_text(text: str, chunk_size: int = 300) -> List[str]:
    """Split text into chunks efficiently."""
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1  # +1 for newline

        if current_size + line_size > chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_size = 0

        if line.strip():  # Skip empty lines
            current_chunk.append(line)
            current_size += line_size

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return [c.strip() for c in chunks if c.strip()]

def main():
    logger.info("=" * 70)
    logger.info("TEXTBOOK INDEXING - MEMORY EFFICIENT")
    logger.info("=" * 70)

    # Validate
    if not all([QDRANT_URL, QDRANT_API_KEY, COHERE_API_KEY]):
        logger.error("Missing environment variables")
        return False

    logger.info(f"✓ Qdrant URL: {QDRANT_URL[:50]}...")
    logger.info(f"✓ Cohere API Key: {COHERE_API_KEY[:20]}...")

    # Initialize clients
    try:
        cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        logger.info("✓ Clients initialized")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        return False

    # Create collection
    collection_name = "chapter_chunks"
    try:
        qdrant_client.get_collection(collection_name)
        logger.info(f"✓ Collection '{collection_name}' already exists")
    except:
        logger.info(f"Creating collection '{collection_name}'...")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
        logger.info("✓ Collection created")

    # Find markdown files
    md_files = sorted(list(TEXTBOOK_DIR.rglob("*.md")))
    logger.info(f"\nFound {len(md_files)} markdown files")

    # Process each file
    total_points = 0
    chunk_id = 1

    for file_path in md_files:
        try:
            logger.info(f"\nProcessing: {file_path.name}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                logger.info("  (empty file, skipping)")
                continue

            # Chunk the content
            chunks = chunk_text(content, chunk_size=300)
            logger.info(f"  Created {len(chunks)} chunks")

            # Generate embeddings with rate limit handling
            embeddings_list = None
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries and embeddings_list is None:
                try:
                    logger.info(f"  Generating embeddings...")
                    response = cohere_client.embed(
                        model="embed-english-v3.0",
                        input_type="search_document",
                        texts=chunks
                    )
                    # Extract float embeddings from response object
                    embeddings_list = response.embeddings.float if hasattr(response.embeddings, 'float') else response.embeddings
                    logger.info(f"  ✓ Generated {len(embeddings_list)} embeddings")
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str or "rate limit" in error_str or "trial token" in error_str:
                        retry_count += 1
                        wait_time = min(2 ** retry_count, 60)  # Exponential backoff, max 60 seconds
                        logger.warning(f"  ⚠ Rate limited. Retrying in {wait_time}s (attempt {retry_count}/{max_retries})...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"  ✗ Embedding failed: {e}")
                        break

            if embeddings_list is None:
                logger.error(f"  ✗ Failed to generate embeddings after {max_retries} attempts")
                continue

            # Prepare points
            points = []
            for chunk, embedding in zip(chunks, embeddings_list):
                point = PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload={
                        "text": chunk[:500],  # Store first 500 chars in payload
                        "source": str(file_path.relative_to(TEXTBOOK_DIR)),
                    }
                )
                points.append(point)
                chunk_id += 1

            # Upload to Qdrant
            try:
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                logger.info(f"  ✓ Uploaded {len(points)} points")
                total_points += len(points)
            except Exception as e:
                logger.error(f"  ✗ Upload failed: {e}")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"  Error processing {file_path.name}: {e}")
            continue

    # Final stats
    logger.info("\n" + "=" * 70)
    logger.info("INDEXING COMPLETE")
    logger.info("=" * 70)

    try:
        collection_info = qdrant_client.get_collection(collection_name)
        logger.info(f"✓ Total points indexed: {collection_info.points_count}")
        logger.info(f"✓ Vector dimension: {collection_info.config.params.vectors.size}")
        logger.info("\n✓ Textbook is now indexed and searchable!")
        logger.info("✓ Test the chatbot: https://hackathon1-q4-production.up.railway.app/api/chatbot/query")
        return True
    except Exception as e:
        logger.error(f"Failed to verify: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nIndexing cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        sys.exit(1)
