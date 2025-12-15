#!/usr/bin/env python3
"""
Index Textbook Content into Qdrant Vector Database

This script:
1. Reads all markdown files from the textbook directory
2. Splits them into chunks for better semantic search
3. Generates embeddings using Cohere
4. Stores embeddings in Qdrant
5. Tracks progress and provides detailed feedback

Usage:
    python index_textbook_to_qdrant.py

Environment Variables Required:
    - QDRANT_URL: Qdrant cloud endpoint
    - QDRANT_API_KEY: Qdrant API key
    - COHERE_API_KEY: Cohere API key for embeddings
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import time

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

# Load environment variables
load_dotenv("backend/.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TEXTBOOK_DIR = Path("textbook/docs")
COLLECTION_NAME = "chapter_chunks"
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 100  # Characters overlap between chunks
EMBEDDING_MODEL = "embed-english-v3.0"
EMBEDDING_DIMS = 1024


def validate_environment():
    """Validate all required environment variables are set."""
    logger.info("=" * 70)
    logger.info("VALIDATING ENVIRONMENT")
    logger.info("=" * 70)

    missing = []
    if not QDRANT_URL:
        missing.append("QDRANT_URL")
    if not QDRANT_API_KEY:
        missing.append("QDRANT_API_KEY")
    if not COHERE_API_KEY:
        missing.append("COHERE_API_KEY")
    if not TEXTBOOK_DIR.exists():
        missing.append(f"TEXTBOOK_DIR ({TEXTBOOK_DIR})")

    if missing:
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        return False

    logger.info(f"✓ QDRANT_URL: {QDRANT_URL[:50]}...")
    logger.info(f"✓ QDRANT_API_KEY: {QDRANT_API_KEY[:20]}...")
    logger.info(f"✓ COHERE_API_KEY: {COHERE_API_KEY[:20]}...")
    logger.info(f"✓ TEXTBOOK_DIR: {TEXTBOOK_DIR}")
    return True


def read_markdown_files() -> Dict[str, str]:
    """Read all markdown files from textbook directory."""
    logger.info("\n" + "=" * 70)
    logger.info("READING MARKDOWN FILES")
    logger.info("=" * 70)

    documents = {}
    md_files = list(TEXTBOOK_DIR.rglob("*.md"))

    logger.info(f"Found {len(md_files)} markdown files")

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                rel_path = md_file.relative_to(TEXTBOOK_DIR)
                documents[str(rel_path)] = content
                logger.debug(f"  ✓ {rel_path} ({len(content)} chars)")
        except Exception as e:
            logger.warning(f"  ✗ Failed to read {md_file}: {e}")

    logger.info(f"\nSuccessfully read {len(documents)} files")
    return documents


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.7:  # At least 70% of chunk
                end = start + last_period + 1

        chunks.append(text[start:end].strip())
        start = end - overlap

    return [c for c in chunks if c]  # Filter empty chunks


def create_chunks(documents: Dict[str, str]) -> List[Dict]:
    """Create chunks from documents with metadata."""
    logger.info("\n" + "=" * 70)
    logger.info("CHUNKING DOCUMENTS")
    logger.info("=" * 70)

    all_chunks = []
    chunk_id = 0

    for file_path, content in documents.items():
        chunks = chunk_text(content)

        for chunk_text_content in chunks:
            chunk_id += 1
            all_chunks.append({
                "id": chunk_id,
                "text": chunk_text_content,
                "source": file_path,
                "chapter": file_path.split('/')[0] if '/' in file_path else 'intro',
                "length": len(chunk_text_content)
            })

    logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")

    # Show statistics
    total_chars = sum(c["length"] for c in all_chunks)
    avg_length = total_chars / len(all_chunks) if all_chunks else 0
    logger.info(f"Total characters: {total_chars:,}")
    logger.info(f"Average chunk length: {avg_length:.0f} characters")

    return all_chunks


def generate_embeddings(chunks: List[Dict]) -> List[Dict]:
    """Generate embeddings for chunks using Cohere."""
    logger.info("\n" + "=" * 70)
    logger.info("GENERATING EMBEDDINGS")
    logger.info("=" * 70)

    try:
        cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Cohere client: {e}")
        return []

    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    logger.info("(This may take a few minutes)")

    # Batch embeddings for efficiency
    batch_size = 100
    embeddings_data = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]

        try:
            logger.info(f"  Processing batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}...")

            response = cohere_client.embed(
                model=EMBEDDING_MODEL,
                input_type="search_document",
                texts=texts
            )

            for chunk, embedding in zip(batch, response.embeddings):
                chunk["embedding"] = embedding
                embeddings_data.append(chunk)

            # Rate limiting
            if i + batch_size < len(chunks):
                time.sleep(1)

        except Exception as e:
            logger.error(f"  ✗ Failed to embed batch: {e}")
            logger.info("  Retrying...")
            time.sleep(5)

    logger.info(f"\nSuccessfully generated {len(embeddings_data)} embeddings")
    return embeddings_data


def initialize_qdrant_collection(client: QdrantClient) -> bool:
    """Create or verify Qdrant collection."""
    logger.info("\n" + "=" * 70)
    logger.info("INITIALIZING QDRANT COLLECTION")
    logger.info("=" * 70)

    try:
        # Check if collection exists
        try:
            collection_info = client.get_collection(COLLECTION_NAME)
            logger.info(f"Collection '{COLLECTION_NAME}' already exists")
            logger.info(f"  Points: {collection_info.points_count}")
            logger.info(f"  Vectors: {collection_info.config.params.vectors.size} dimensions")

            # Delete and recreate if dimensions don't match
            if collection_info.config.params.vectors.size != EMBEDDING_DIMS:
                logger.info(f"  Dimension mismatch: {collection_info.config.params.vectors.size} != {EMBEDDING_DIMS}")
                logger.info("  Deleting and recreating collection...")
                client.delete_collection(COLLECTION_NAME)
                raise Exception("Recreating...")
            else:
                return True

        except Exception as e:
            if "Recreating" not in str(e):
                logger.info(f"Creating new collection '{COLLECTION_NAME}'...")

            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMS,
                    distance=Distance.COSINE
                ),
            )
            logger.info(f"✓ Collection created successfully")
            return True

    except Exception as e:
        logger.error(f"Failed to initialize collection: {e}")
        return False


def upload_to_qdrant(client: QdrantClient, chunks: List[Dict]) -> int:
    """Upload chunks and embeddings to Qdrant."""
    logger.info("\n" + "=" * 70)
    logger.info("UPLOADING TO QDRANT")
    logger.info("=" * 70)

    if not chunks:
        logger.error("No chunks to upload")
        return 0

    logger.info(f"Uploading {len(chunks)} chunks to Qdrant...")

    # Prepare points for Qdrant
    points = []
    for chunk in chunks:
        point = PointStruct(
            id=chunk["id"],
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "source": chunk["source"],
                "chapter": chunk["chapter"],
                "length": chunk["length"],
            }
        )
        points.append(point)

    # Upload in batches
    batch_size = 100
    uploaded = 0

    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]

        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            uploaded += len(batch)
            logger.info(f"  ✓ Uploaded {uploaded}/{len(points)} chunks")
        except Exception as e:
            logger.error(f"  ✗ Failed to upload batch: {e}")

    logger.info(f"\n✓ Successfully uploaded {uploaded} chunks to Qdrant")
    return uploaded


def verify_indexing(client: QdrantClient) -> bool:
    """Verify that indexing was successful."""
    logger.info("\n" + "=" * 70)
    logger.info("VERIFYING INDEXING")
    logger.info("=" * 70)

    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        logger.info(f"Collection: {COLLECTION_NAME}")
        logger.info(f"  Total points: {collection_info.points_count}")
        logger.info(f"  Vectors: {collection_info.config.params.vectors.size} dimensions")

        if collection_info.points_count > 0:
            logger.info("\n✓ Indexing successful!")
            logger.info(f"  Ready to answer questions about {collection_info.points_count} content chunks")
            return True
        else:
            logger.warning("✗ No points in collection")
            return False

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


def main():
    """Main indexing workflow."""
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " TEXTBOOK INDEXING TO QDRANT ".center(68) + "║")
    logger.info("╚" + "=" * 68 + "╝")
    logger.info("\n")

    start_time = time.time()

    # Step 1: Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        return False

    # Step 2: Read markdown files
    documents = read_markdown_files()
    if not documents:
        logger.error("No markdown files found")
        return False

    # Step 3: Create chunks
    chunks = create_chunks(documents)
    if not chunks:
        logger.error("Failed to create chunks")
        return False

    # Step 4: Generate embeddings
    embeddings_data = generate_embeddings(chunks)
    if not embeddings_data:
        logger.error("Failed to generate embeddings")
        return False

    # Step 5: Connect to Qdrant
    logger.info("\n" + "=" * 70)
    logger.info("CONNECTING TO QDRANT")
    logger.info("=" * 70)

    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        logger.info(f"✓ Connected to Qdrant at {QDRANT_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return False

    # Step 6: Initialize collection
    if not initialize_qdrant_collection(client):
        logger.error("Failed to initialize collection")
        return False

    # Step 7: Upload to Qdrant
    uploaded = upload_to_qdrant(client, embeddings_data)
    if uploaded == 0:
        logger.error("Failed to upload data to Qdrant")
        return False

    # Step 8: Verify
    if not verify_indexing(client):
        logger.error("Indexing verification failed")
        return False

    # Summary
    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("INDEXING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"\n✓ Successfully indexed textbook content")
    logger.info(f"  Documents: {len(documents)}")
    logger.info(f"  Chunks: {len(chunks)}")
    logger.info(f"  Uploaded: {uploaded}")
    logger.info(f"  Time: {elapsed:.1f} seconds")
    logger.info(f"\n✓ Chatbot is now ready to answer questions!")
    logger.info(f"  Test at: https://hackathon1-q4-production.up.railway.app/api/chatbot/query")

    return True


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
