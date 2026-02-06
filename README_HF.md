---
title: ContractIQ - AI Contract Analysis
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.53.1
app_file: app.py
pinned: false
license: mit
---

# 📄 ContractIQ - AI Contract Analysis

**Trustworthy AI-powered contract analysis using RAG with citation-first answers.**

## 🎯 What is ContractIQ?

ContractIQ is a production-grade RAG (Retrieval-Augmented Generation) system specifically designed for analyzing legal contracts. It provides **trustworthy, cited answers** with **zero hallucination tolerance**.

## ✨ Key Features

### 🔒 Trustworthy Answers
- **Citation-First**: Every answer MUST start with "According to [Clause X]..."
- **Hard Refusal**: Refuses to answer when information isn't in the contract
- **Zero Hallucination**: Only uses contract text, never external knowledge

### 🎯 Advanced Retrieval
- **Sub-Clause Chunking**: Fine-grained semantic search at sub-clause level
- **Intent Detection**: Understands query intent using embeddings
- **Semantic Enrichment**: Enhanced embeddings with clause metadata

### 🚀 Production Ready
- **RESTful API**: FastAPI backend with full OpenAPI documentation
- **Error Handling**: Comprehensive validation and error messages
- **API Versioning**: `/api/v1/` endpoints for stability

## 📖 How to Use

### 1. Upload a Contract
- Click "Upload Contract" tab
- Choose a PDF contract file
- Wait for processing (typically 5-30 seconds)

### 2. Ask Questions
- Switch to "Ask Questions" tab
- Type your question (e.g., "What are the termination conditions?")
- Click "Ask" and get a cited answer

### 3. Verify Citations
- Every answer includes [Clause X] citations
- Check sources in the expandable sections
- Verify against original contract pages

## 💡 Example Questions

Try asking:
- "What are the termination conditions?"
- "What law governs this agreement?"
- "How is personal data handled?"
- "What are the payment terms?"
- "What are the liability limits?"

## 🔍 Answer Formats

### Valid Answer (With Citation)
```
According to [Clause 10.2], the termination conditions are as follows:
Either party may by notice in writing terminate this Agreement with
immediate effect if the other party commits a breach...
```

### Refusal (Information Not Found)
```
INSUFFICIENT_INFORMATION: The contract does not specify this.
```

## 🏗️ Architecture

```
Streamlit UI → FastAPI Backend → RAG Pipeline
                    ↓
              ChromaDB Vector Store
                    ↓
              Groq LLM (llama-3.1-8b-instant)
```

### Components

1. **Document Ingestion**
   - PDF parsing with pdfplumber
   - Text cleaning and normalization
   - Sub-clause level chunking

2. **Embedding & Retrieval**
   - sentence-transformers (all-MiniLM-L6-v2)
   - ChromaDB for vector storage
   - Intent-aware similarity boosting

3. **Generation**
   - Groq LLM for fast inference
   - Citation-first prompting
   - Hallucination detection & blocking

## 📊 Performance

- **Latency**: ~0.5-1.5s per query
- **Recall**: High (false refusals eliminated)
- **Precision**: Citation-enforced accuracy
- **Throughput**: Handles multiple concurrent requests

## 🔐 Privacy & Security

- **No Data Retention**: Contracts stored only in your Space
- **Local Processing**: All RAG operations run locally
- **API Key**: Your GROQ_API_KEY is secure in Space Secrets
- **No Training**: Your contracts are NOT used for model training

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Vector DB**: ChromaDB
- **Embeddings**: sentence-transformers
- **LLM**: Groq (llama-3.1-8b-instant)
- **OCR/PDF**: pdfplumber
- **ML**: scikit-learn, numpy

## 📚 API Documentation

### Endpoints

#### Upload Contract
```http
POST /api/v1/upload
Content-Type: multipart/form-data

file: <PDF file>
```

#### Ask Question
```http
POST /api/v1/ask
Content-Type: application/json

{
  "question": "What are the termination conditions?",
  "top_k": 4
}
```

#### Health Check
```http
GET /health
```

See the "API Docs" tab in the app for complete documentation.

## 🎓 Research & Development

### Phase 1: Production API
- ✅ API versioning with `/api/v1`
- ✅ Pydantic request/response schemas
- ✅ Centralized error handling
- ✅ OpenAPI/Swagger documentation

### Phase 2: Trustworthy Answers
- ✅ Citation-first enforcement
- ✅ Hard refusal for missing information
- ✅ Hallucination blocking
- ✅ Multi-layer validation

### Phase 3: Retrieval Quality
- ✅ Sub-clause level chunking
- ✅ Semantic enrichment
- ✅ Intent-aware similarity boosting
- ✅ Debug logging

## ⚠️ Limitations

1. **PDF Only**: Currently supports PDF contracts only
2. **English**: Optimized for English contracts
3. **Text-Based**: Cannot process scanned/image PDFs (OCR not included)
4. **Contract Focus**: Designed for legal contracts, may not work well for other document types
5. **LLM Dependent**: Requires Groq API (free tier available)

## 🔄 Updates

- **v1.0.0** (2024): Initial release with all three phases complete

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 💬 Support

- **Issues**: Report bugs or feature requests
- **Discussions**: Ask questions and share ideas
- **Documentation**: See DEPLOYMENT.md for deployment guide

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude](https://claude.ai) for development
- [Groq](https://groq.com) for fast LLM inference
- [Hugging Face](https://huggingface.co) for hosting
- [Streamlit](https://streamlit.io) for UI
- [FastAPI](https://fastapi.tiangolo.com) for API

---

**Built with ❤️ using RAG** | [GitHub](https://github.com) | [Documentation](DEPLOYMENT.md)
