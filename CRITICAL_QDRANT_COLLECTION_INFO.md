# CRITICAL: Qdrant Collection Configuration

## Current Situation

You have TWO collections in Qdrant:

| Collection | Points | Vector Dim | Status | Has Your Data? |
|------------|--------|-----------|--------|---------------|
| `aibook` | 0 | 384 | Empty | ❌ NO |
| `chapter_chunks` | 1,612 | 1024 | **ACTIVE** | ✅ YES |

## Testing Results

**Using `chapter_chunks`:**
```
Query: "What is ROS 2?"
Result: 5 chunks retrieved
Score: 0.724
Status: WORKS ✅
```

**Using `aibook`:**
```
Query: "What is ROS 2?"
Result: 0 chunks retrieved
Error: Vector dimension mismatch (expected 384, got 1024)
Status: BROKEN ❌
```

## Explanation

The `aibook` collection was created with the OLD embedding model that produces 384-dimensional vectors.

The `chapter_chunks` collection was created with Cohere (1024-dimensional vectors) and has your 1,612 indexed textbook chunks.

## Solution

**USE `chapter_chunks` collection - it has all your data!**

## Required Environment Variable

When you add variables to Railway Dashboard, use:

```
QDRANT_COLLECTION=chapter_chunks
```

**NOT** `QDRANT_COLLECTION=aibook` (which is empty)

## Complete Railway Variables

When adding to Railway Dashboard, use:

```
COHERE_API_KEY=UqLzBN1vOpjdW2iFkmjolDu9iG2S9cius17msG63
QDRANT_COLLECTION=chapter_chunks
QDRANT_VECTOR_SIZE=1024
RAG_SIMILARITY_THRESHOLD=0.5
RAG_TOP_K=5
```

## What Happened

1. Initially, `aibook` collection was created with 384-dim vectors
2. The indexing script created `chapter_chunks` with 1024-dim vectors
3. Your 1,612 textbook chunks are in `chapter_chunks`
4. The old `aibook` collection is now obsolete

## Next Steps

1. Go to Railway Dashboard
2. Add the variables above (using `QDRANT_COLLECTION=chapter_chunks`)
3. Railway auto-redeploys
4. Chatbot retrieves chunks from the correct collection
5. Everything works!

## If You Want to Use `aibook`

If you specifically need to use the `aibook` collection for some reason, you would need to:
1. Delete the old `aibook` collection
2. Re-index your textbook into a new `aibook` collection with 1024-dim vectors
3. Update RAG configuration

But this is NOT NECESSARY - just use `chapter_chunks`!
