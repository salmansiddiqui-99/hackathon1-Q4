# Indexing Textbook Content into Qdrant

## Overview

This guide explains how to index your textbook content into Qdrant so the chatbot can retrieve and answer questions about it.

**Status:**
- ✅ Backend API: Operational
- ✅ Gemini LLM: Configured
- ✅ Cohere Embeddings: Configured
- ✅ Qdrant Vector DB: Connected
- ❌ Textbook Content: NOT INDEXED (this is what we're fixing)

---

## What Happens During Indexing

1. **Read**: All markdown files from `textbook/docs/` are read
2. **Chunk**: Content is split into semantic chunks (500 chars with 100 char overlap)
3. **Embed**: Each chunk is converted to a 1024-dimensional vector using Cohere
4. **Store**: Vectors are stored in Qdrant for semantic search
5. **Verify**: System confirms successful indexing

**Example:**
```
Your textbook (Markdown)
  ↓
Split into chunks (semantic boundaries)
  ↓
Convert to vectors (Cohere embeddings)
  ↓
Store in Qdrant (searchable database)
  ↓
Chatbot retrieves relevant chunks for questions
```

---

## Prerequisites

Before indexing, make sure you have:

✅ **Environment Variables Set (Already Done)**
- `QDRANT_URL`: Qdrant cloud endpoint
- `QDRANT_API_KEY`: Qdrant API key
- `COHERE_API_KEY`: Cohere API key for embeddings

✅ **Textbook Content**
- Location: `textbook/docs/`
- Format: Markdown files (.md)
- Automatically discovers all files recursively

---

## Quick Start (4 Steps)

### Step 1: Run the Indexing Script

```bash
cd C:\Users\haroon traders\Desktop\projects\hackathon1-Q4

python index_textbook_to_qdrant.py
```

**Expected output:**
```
======================================================================
                    TEXTBOOK INDEXING TO QDRANT
======================================================================

Validating environment
✓ QDRANT_URL: https://...
✓ QDRANT_API_KEY: eyJhbGc...
✓ COHERE_API_KEY: UqLzBN...
✓ TEXTBOOK_DIR: textbook/docs

Reading markdown files
Found 20 markdown files
Successfully read 20 files

Chunking documents
Created 500 chunks from 20 documents
Total characters: 250,000
Average chunk length: 500 characters

Generating embeddings
Processing batch 1/5...
Processing batch 2/5...
Processing batch 3/5...
Processing batch 4/5...
Processing batch 5/5...
Successfully generated 500 embeddings

Uploading to Qdrant
✓ Uploaded 500/500 chunks
```

**Time Required:** 3-10 minutes depending on textbook size and Cohere API speed

### Step 2: Wait for Completion

The script will:
- Show progress updates every batch
- Report any errors encountered
- Provide final statistics when complete

### Step 3: Verify Success

At the end, you'll see:
```
✓ Indexing successful!
  Ready to answer questions about 500 content chunks
```

### Step 4: Test the Chatbot

Run a test query:

```bash
python << 'EOF'
import requests

response = requests.post(
    "https://hackathon1-q4-production.up.railway.app/api/chatbot/query",
    json={"query_text": "What is ROS 2?", "mode": "global"},
    timeout=15
)

result = response.json()
print(f"Success: {result['success']}")
if result['success']:
    print(f"Response: {result['data']['response']}")
else:
    print(f"Error: {result['error']}")
EOF
```

**Expected Success Result:**
```
Success: True
Response: ROS 2 is... [answer from your textbook]
```

---

## Detailed Workflow

### What the Script Does

**1. Environment Validation**
```
✓ Checks all required API keys are set
✓ Verifies textbook directory exists
✓ Confirms Qdrant and Cohere connectivity
```

**2. File Reading**
```
Reads: textbook/docs/
  → textbook/docs/index.md
  → textbook/docs/intro.md
  → textbook/docs/module1/01-ros2-basics.md
  → textbook/docs/module1/02-humanoid-control.md
  → ... (all markdown files)
```

**3. Text Chunking**
```
Original: "ROS 2 is a robotics middleware... [long text]"
  ↓
Chunk 1: "ROS 2 is a robotics middleware..." (500 chars)
Chunk 2: "middleware that provides..." (500 chars, 100 char overlap)
Chunk 3: "provides communication between..." (500 chars)
```

**4. Embedding Generation**
```
Chunk 1: "ROS 2 is..."
  → [0.123, -0.456, 0.789, ..., 0.234] (1024 dimensions)

Chunk 2: "middleware that..."
  → [0.234, -0.567, 0.890, ..., 0.345] (1024 dimensions)
```

**5. Qdrant Upload**
```
Point 1: {
  id: 1,
  vector: [0.123, -0.456, ...],
  payload: {
    text: "ROS 2 is...",
    source: "module1/01-ros2-basics.md",
    chapter: "module1"
  }
}
```

**6. Verification**
```
Collection: chapter_chunks
  Total points: 500
  Vectors: 1024 dimensions
Status: ✓ Ready for queries
```

---

## How the Chatbot Uses Indexed Content

Once indexed, here's what happens when you ask a question:

```
User: "What is ROS 2?"
  ↓
Embedding: Convert question to vector (Cohere)
  ↓
Search: Find similar chunks in Qdrant (semantic search)
  ↓
Retrieve: Get top 5 most relevant chunks
  ↓
Generate: Use Gemini to answer based on chunks
  ↓
Response: "ROS 2 is a robotics middleware that..."
```

---

## Troubleshooting

### Issue: Script hangs on "Generating embeddings"

**Cause:** Cohere API is slow or quota-limited
**Solution:**
1. Wait - Cohere embedding may take time
2. Check quota at: https://dashboard.cohere.com
3. If quota exceeded, wait for reset (usually 1 minute)

### Issue: "Connection refused" to Qdrant

**Cause:** Qdrant is unreachable
**Solution:**
1. Verify `QDRANT_URL` in `.env`
2. Check Qdrant Cloud is running: https://dashboard.qdrant.io
3. Verify `QDRANT_API_KEY` is correct

### Issue: "Cannot answer: No context chunks retrieved"

**Cause:** Content not indexed yet
**Solution:**
1. Run indexing script
2. Wait for completion
3. Verify with `python index_textbook_to_qdrant.py`

### Issue: Permission denied errors

**Cause:** File access issues
**Solution:**
1. Close other applications using the files
2. Run command prompt as Administrator
3. Check file permissions on `textbook/docs/`

### Issue: "Cohere API Key not set"

**Cause:** Environment variables not loaded
**Solution:**
1. Verify `backend/.env` has `COHERE_API_KEY`
2. Restart terminal/IDE
3. Check: `echo %COHERE_API_KEY%` (Windows)

---

## Advanced Options

### Custom Chunk Size

Edit the script to change chunk size:

```python
CHUNK_SIZE = 1000  # Larger chunks (default: 500)
CHUNK_OVERLAP = 200  # More overlap (default: 100)
```

**Recommendations:**
- Smaller chunks (300-500): Better for dense technical content
- Larger chunks (1000-2000): Better for narrative content
- More overlap (150-200): Better for boundary-relevant questions

### Filtering Files

Only index specific chapters:

```python
# In index_textbook_to_qdrant.py
md_files = list(TEXTBOOK_DIR.rglob("module1/*.md"))  # Only module1
```

### Batch Size

Adjust embedding batch size for speed vs. memory:

```python
batch_size = 50   # Faster, less memory
batch_size = 200  # Slower, more parallel
```

---

## Monitoring

### Check Indexing Progress

While the script runs, you can check Qdrant status:

```bash
python << 'EOF'
import requests
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

headers = {"api-key": QDRANT_API_KEY}
response = requests.get(
    f"{QDRANT_URL}/collections/chapter_chunks",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Points indexed: {data['result']['points_count']}")
else:
    print("Collection not yet created")
EOF
```

### Check Chatbot Status After Indexing

```bash
python << 'EOF'
import requests

# Check stats
response = requests.get(
    "https://hackathon1-q4-production.up.railway.app/api/chatbot/stats",
    timeout=10
)
stats = response.json()

print(f"Chunks indexed: {stats['total_chunks_indexed']}")
print(f"Vectors in Qdrant: {stats['vectors_indexed']}")
print(f"Embedding model: {stats['embedding_model']}")
EOF
```

---

## Performance Notes

**Indexing Speed:**
- Reading files: ~1 second per file
- Chunking: ~0.1 seconds per file
- Embedding: ~1 minute per 100 chunks (depends on Cohere)
- Upload: ~1 second per 100 chunks
- **Total:** 3-10 minutes for typical textbook

**Query Speed (After Indexing):**
- Embedding query: 1-2 seconds
- Search in Qdrant: <100ms
- Generate response: 2-5 seconds
- **Total:** 3-8 seconds per question

**Storage:**
- Each 1024-dim vector: ~4KB in memory
- 500 chunks: ~2MB in Qdrant
- Scales linearly

---

## Success Checklist

- [ ] Run `python index_textbook_to_qdrant.py`
- [ ] Wait for completion (3-10 minutes)
- [ ] See "✓ Indexing successful!" message
- [ ] Verify Qdrant shows points indexed
- [ ] Test chatbot with sample question
- [ ] Chatbot returns answer from textbook
- [ ] Share textbook knowledge with others!

---

## Next Steps

After indexing:

1. **Test Different Questions:**
   ```
   "What is ROS 2?"
   "How do humanoids move?"
   "What is URDF?"
   "Explain Gazebo simulation"
   ```

2. **Share the Chatbot:**
   - Frontend: https://salmansiddiqui-99.github.io
   - Backend: https://hackathon1-q4-production.up.railway.app

3. **Monitor Performance:**
   - Check response times
   - Review answer quality
   - Adjust chunk size if needed

4. **Add More Content:**
   - Add more markdown files to `textbook/docs/`
   - Re-run indexing script
   - New content is automatically indexed

---

## Summary

**Before Indexing:**
- ❌ Chatbot: "Cannot answer: No context chunks retrieved"
- Qdrant: 0 vectors indexed
- System: Ready but empty

**After Indexing:**
- ✅ Chatbot: Answers questions about textbook
- Qdrant: 500+ vectors indexed
- System: Fully operational RAG chatbot

**Ready to index? Run:**
```bash
python index_textbook_to_qdrant.py
```

**Questions?** Check the troubleshooting section above!
