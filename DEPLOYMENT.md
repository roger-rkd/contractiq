# ContractIQ - Hugging Face Spaces Deployment Guide

## Overview

ContractIQ is deployed as a **single Hugging Face Space** that runs both:
- **Streamlit UI** (frontend)
- **FastAPI Backend** (API server)

## Architecture

```
Hugging Face Space
│
├── app.py (Streamlit entrypoint)
│   ├── Starts FastAPI in background thread
│   ├── Waits for API readiness
│   └── Renders UI
│
├── FastAPI Server (localhost:8000)
│   ├── POST /api/v1/upload
│   ├── POST /api/v1/ask
│   └── GET /health
│
└── ChromaDB (local persistence)
    └── data/chroma_db/
```

## Files Structure

```
contractiq-rag/
├── app.py                  # Main entrypoint for HF Spaces
├── .huggingface/
│   └── space.yaml          # Space configuration
├── requirements.txt        # Python dependencies
├── app/                    # Application code
│   ├── api/               # FastAPI routes
│   ├── rag/               # RAG pipeline
│   ├── chunking/          # Document chunking
│   ├── embeddings/        # Embedding generation
│   ├── vectorstore/       # ChromaDB client
│   └── ...
├── data/                   # Persistent data
│   ├── chroma_db/         # Vector database
│   └── contracts/         # Uploaded PDFs
└── tests/                  # Test suites
```

## Deployment Steps

### 1. Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - **Space name:** `contractiq-rag` (or your choice)
   - **License:** MIT
   - **SDK:** Streamlit
   - **Hardware:** CPU Basic (free tier works)

### 2. Add GROQ_API_KEY Secret

1. Go to Space Settings → Secrets
2. Add secret:
   - **Name:** `GROQ_API_KEY`
   - **Value:** Your Groq API key from https://console.groq.com

### 3. Push Code to Space

#### Option A: Git Clone and Push

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/contractiq-rag
cd contractiq-rag

# Copy ContractIQ files
cp -r /path/to/contractiq-rag/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### Option B: Web Upload

1. Use the "Files" tab in your Space
2. Upload these files:
   - `app.py`
   - `.huggingface/space.yaml`
   - `requirements.txt`
   - `app/` directory (all contents)
3. Commit changes

### 4. Monitor Build

1. Watch the "Logs" tab for build progress
2. Wait for "Running" status
3. Access your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/contractiq-rag`

## Configuration

### Environment Variables

Set in Space Settings → Secrets:

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM inference |

### ChromaDB Persistence

ChromaDB data is stored in `data/chroma_db/` and persists across Space restarts (as long as you have persistent storage enabled).

**Note:** Free tier Spaces may not have persistent storage. Consider upgrading to persistent storage if you want uploaded contracts to persist.

### Resource Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB

**Recommended:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB

**Free Tier:** Works but may be slow during peak usage.

## Testing Deployment

### 1. Test Health Check

```bash
curl https://YOUR_USERNAME-contractiq-rag.hf.space/health
```

Expected response:
```json
{
  "status": "ok",
  "app": "ContractIQ",
  "version": "1.0.0"
}
```

### 2. Test UI

1. Open Space URL in browser
2. Upload a sample PDF contract
3. Ask a question
4. Verify answer has citations

### 3. Test API Endpoints

```bash
# Upload contract
curl -X POST https://YOUR_USERNAME-contractiq-rag.hf.space/api/v1/upload \
  -F "file=@contract.pdf"

# Ask question
curl -X POST https://YOUR_USERNAME-contractiq-rag.hf.space/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the termination conditions?"}'
```

## Troubleshooting

### Space Won't Start

**Symptom:** Space shows "Error" status

**Solutions:**
1. Check build logs for errors
2. Verify all files uploaded correctly
3. Check `requirements.txt` for syntax errors
4. Ensure GROQ_API_KEY is set

### API Not Responding

**Symptom:** UI shows "Failed to start API server"

**Solutions:**
1. Check if `uvicorn` is installed
2. Verify port 8000 is not blocked
3. Wait longer (30 seconds) for API startup
4. Check Space logs for FastAPI errors

### Out of Memory

**Symptom:** Space crashes or runs slowly

**Solutions:**
1. Upgrade to better hardware tier
2. Reduce `top_k` parameter (fewer chunks)
3. Clear ChromaDB data: `rm -rf data/chroma_db/`
4. Use smaller embedding model (if customized)

### ChromaDB Errors

**Symptom:** "Collection not found" or similar

**Solutions:**
1. Delete `data/chroma_db/` directory
2. Restart Space
3. Re-upload contracts
4. Check file permissions

## Monitoring

### Space Metrics

Monitor in Space Settings → Analytics:
- **Uptime:** Target 99%+
- **Latency:** Target < 5s per query
- **Memory Usage:** Target < 4GB
- **API Requests:** Track usage patterns

### Logging

View logs in Space → Logs tab:
```
2024-01-01 12:00:00 | INFO | Starting ContractIQ API...
2024-01-01 12:00:01 | INFO | Computing intent embeddings...
2024-01-01 12:00:02 | INFO | API ready on http://127.0.0.1:8000
```

## Updating Deployment

### Code Updates

```bash
# Make changes locally
git pull
# ... edit files ...
git add .
git commit -m "Update: description"
git push
```

Space will automatically rebuild and redeploy.

### Dependency Updates

Update `requirements.txt`:
```bash
# Update specific package
pip install --upgrade sentence-transformers
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push
```

## Performance Optimization

### 1. Caching

Consider adding Streamlit caching:
```python
@st.cache_resource
def get_rag_pipeline():
    return RAGPipeline()
```

### 2. Async Processing

For better concurrency, consider using async/await in FastAPI endpoints.

### 3. Rate Limiting

Add rate limiting to prevent abuse:
```python
from fastapi import Depends
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
```

## Security Considerations

### 1. API Key Protection

- **Never** commit API keys to git
- Always use Space Secrets
- Rotate keys periodically

### 2. Input Validation

Already implemented:
- File type validation (PDF only)
- Question length limits (1-500 chars)
- Error handling for malicious inputs

### 3. Rate Limiting

Consider adding:
- Per-user rate limits
- CORS restrictions
- Request size limits

## Cost Considerations

### Free Tier

- **Cost:** $0
- **Limits:**
  - 2 CPU cores
  - 16GB RAM
  - No GPU
  - No persistent storage
  - May sleep after inactivity

### Paid Tiers

- **CPU Basic:** $0/month (legacy grandfathered)
- **CPU Upgrade:** $5-10/month
- **GPU T4:** $0.60/hour
- **Persistent Storage:** $5/month for 50GB

**Recommendation:** Start with free tier, upgrade if needed.

## Backup and Recovery

### Backup ChromaDB

```bash
# Download ChromaDB data
huggingface-cli download YOUR_USERNAME/contractiq-rag data/chroma_db/
```

### Restore

```bash
# Upload ChromaDB data
huggingface-cli upload YOUR_USERNAME/contractiq-rag data/chroma_db/
```

## Support

### Resources

- **HF Docs:** https://huggingface.co/docs/hub/spaces
- **Issues:** Report at your GitHub repo
- **Community:** HF Community forums

### Common Issues

See [Troubleshooting](#troubleshooting) section above.

## Next Steps

After deployment:

1. ✅ Test all features
2. ✅ Upload sample contracts
3. ✅ Share Space URL with users
4. ✅ Monitor usage and performance
5. ✅ Collect user feedback
6. ✅ Iterate and improve

## Appendix: Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GROQ_API_KEY=your_key_here

# Run Streamlit app
streamlit run app.py
```

Access at: http://localhost:8501
