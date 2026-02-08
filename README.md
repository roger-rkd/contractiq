---
title: ContractIQ - AI Contract Analysis
emoji: "\U0001F4C4"
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.53.1"
python_version: "3.11"
app_file: streamlit_app.py
pinned: false
license: mit
tags:
  - rag
  - legal
  - contract-analysis
  - nlp
  - llm
  - fastapi
  - streamlit
  - citation
  - hallucination-detection
---

<div align="center">

# ContractIQ

### AI-Powered Legal Contract Analysis with Citation Enforcement & Hallucination Blocking

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace%20Spaces-blue?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/dubey-codes/ContractIQ)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Upload a contract. Ask a question. Get a cited, verified answer — or an honest refusal.**

</div>

---

## The Problem

Legal contracts are dense, lengthy documents filled with nested clauses, cross-references, and domain-specific language. Reviewing a 50-page service agreement to find a specific termination condition, liability cap, or data protection obligation is painfully time-consuming.

Generic AI chatbots make this worse:
- They **hallucinate** — confidently stating terms that don't exist in the document
- They **omit citations** — giving answers with no way to verify the source
- They **paraphrase loosely** — drifting from the actual legal language, which can change the meaning entirely

**There is no lightweight, trustworthy tool that guarantees every answer is grounded strictly in the document's own text.**

---

## The Solution

ContractIQ is a RAG (Retrieval-Augmented Generation) system that lets you upload a PDF contract and ask natural-language questions. Every answer is:

- **Cited** — responses begin with `According to [Clause X]...` pointing to the exact source
- **Grounded** — answers are drawn exclusively from the uploaded document, never from the LLM's training data
- **Hallucination-blocked** — a post-generation verification layer checks semantic similarity between the answer and retrieved context; if the answer isn't grounded, it's rejected and replaced with an explicit refusal
- **Bullet-formatted** — answers are structured as bullet points for easy reading

> ContractIQ follows a **"refuse rather than fabricate"** philosophy. If the contract doesn't contain the answer, it says so.

---

## How It Works

ContractIQ operates as a **6-stage pipeline**:

```
PDF Upload --> Clause-Aware --> Embedding & --> Intent-Aware --> Citation-First --> Post-Generation
               Chunking         Storage          Retrieval        Generation        Verification
```

### Stage 1: PDF Ingestion
The uploaded PDF is parsed page-by-page using `pdfplumber`, extracting raw text while preserving page boundaries.

### Stage 2: Clause-Aware Chunking
Unlike naive fixed-size chunking, ContractIQ uses a custom clause-aware chunker:
- Detects clause headings via regex patterns (e.g., `10.2 TERMINATION`)
- Maps clauses to legal categories (Termination, Liability, Payment, Data Protection, etc.)
- Splits long clauses into sub-clauses for finer granularity
- Enriches each chunk with semantic metadata — clause title, number, and keywords

### Stage 3: Embedding & Storage
Each enriched chunk is embedded using `all-MiniLM-L6-v2` sentence-transformer and stored in ChromaDB for fast similarity search.

### Stage 4: Intent-Aware Retrieval
When a question is asked, the retriever:
- **Expands** the query with semantic variations (e.g., "termination" also searches "cancellation", "end the contract")
- **Detects intent** via cosine similarity against pre-computed intent template embeddings
- **Retrieves** candidate chunks from ChromaDB for each query variation
- **Re-ranks** using intent-aware similarity boosting — chunks whose clause title matches the detected intent get a relevance boost

### Stage 5: Citation-First Generation
Top-k chunks are assembled into a strict citation-first prompt sent to the LLM. The prompt enforces:
- Every answer must begin with `According to [Clause X]...`
- Bullet-point formatting for readability
- No paraphrasing beyond what is directly stated
- Hard refusal if information isn't found

### Stage 6: Post-Generation Verification
Before returning the answer, two checks run:
1. **Citation enforcement** — if the response lacks a citation and isn't a refusal, it's forcibly replaced with a refusal
2. **Hallucination blocking** — the answer is embedded and compared against retrieved context via cosine similarity; if grounding similarity falls below the threshold, the answer is blocked

---

## Project Structure

```
contractiq-rag/
├── streamlit_app.py              # Streamlit frontend + FastAPI launcher
├── requirements.txt              # Python dependencies
├── app/
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Settings (Pydantic)
│   ├── api/
│   │   ├── upload.py             # POST /api/v1/upload
│   │   ├── query.py              # POST /api/v1/ask
│   │   ├── schemas.py            # Request/Response models
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── exception_handlers.py # Error handlers
│   ├── ingestion/
│   │   ├── pdf_loader.py         # PDF text extraction
│   │   └── text_cleaner.py       # Text preprocessing
│   ├── chunking/
│   │   └── clause_chunker.py     # Clause-aware chunking + enrichment
│   ├── embeddings/
│   │   └── embedder.py           # Sentence-transformer embeddings
│   ├── vectorstore/
│   │   └── chroma_client.py      # ChromaDB vector store
│   ├── rag/
│   │   ├── retriever.py          # Intent-aware retrieval
│   │   ├── prompt.py             # Citation-first prompt template
│   │   └── generator.py          # RAG pipeline + hallucination blocking
│   ├── evaluation/
│   │   ├── metrics.py            # Retrieval recall + hallucination detection
│   │   ├── evaluator.py          # Evaluation runner
│   │   └── test_cases.py         # Evaluation test cases
│   └── utils/
│       ├── groq_client.py        # Groq LLM client
│       └── logger.py             # Logging setup
└── data/
    └── contracts/                # Uploaded PDFs (gitignored)
```

---

## Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Frontend** | Streamlit | Interactive UI — file upload, question input, answer display |
| **Backend API** | FastAPI | RESTful API with `/upload` and `/ask` endpoints |
| **PDF Parsing** | pdfplumber | Page-by-page text extraction from PDF contracts |
| **Chunking** | Custom clause chunker | Clause-aware splitting with semantic enrichment |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) | Text-to-vector conversion for semantic search |
| **Vector Database** | ChromaDB | Storage and similarity search for document chunks |
| **LLM** | Groq (`llama-3.1-8b-instant`) | Fast inference for answer generation |
| **Hallucination Detection** | scikit-learn (cosine similarity) | Embedding-based grounding verification |
| **Deployment** | Hugging Face Spaces | Cloud hosting with Streamlit SDK |

---

## API Reference

ContractIQ exposes a full REST API alongside the Streamlit UI.

### Health Check
```http
GET /health
```
```json
{
  "status": "ok",
  "app": "ContractIQ",
  "version": "1.0.0"
}
```

### Upload Contract
```http
POST /api/v1/upload
Content-Type: multipart/form-data
```
| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `file` | PDF | Yes | The contract PDF to analyze |
| `description` | string | No | Optional description |

**Response** `201 Created`:
```json
{
  "message": "Contract uploaded and processed successfully",
  "filename": "service-agreement.pdf",
  "chunks_created": 45,
  "pages_processed": 12
}
```

### Ask Question
```http
POST /api/v1/ask
Content-Type: application/json
```
```json
{
  "question": "What are the termination conditions?",
  "top_k": 4
}
```

**Response** `200 OK`:
```json
{
  "question": "What are the termination conditions?",
  "answer": "According to [Clause 2], the Company may terminate this Agreement if:\n- The Client fails to make payment...\n- The Client commits a persistent breach...",
  "sources": [
    {
      "clause_title": "TERMINATION",
      "page_number": 8,
      "source_file": "service-agreement.pdf"
    }
  ],
  "latency_sec": 2.41
}
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- A [Groq API key](https://console.groq.com) (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/roger-rkd/contractiq.git
cd contractiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running Locally

```bash
# Start the application (launches both Streamlit UI and FastAPI backend)
streamlit run streamlit_app.py
```

The Streamlit UI will be available at `http://localhost:8501` and the FastAPI backend at `http://localhost:8000/api/docs`.

---

## Deployment

ContractIQ is deployed on **Hugging Face Spaces** with the Streamlit SDK. The `streamlit_app.py` entry point launches a background FastAPI server thread and the Streamlit frontend in a single process.

To deploy your own instance:
1. Create a new Space on [Hugging Face](https://huggingface.co/new-space) with **Streamlit** SDK
2. Add your `GROQ_API_KEY` as a Space secret
3. Push the repository to the Space

---

## Limitations

- **PDF-only** — no support for Word, scanned images, or OCR
- **Single document** — analyzes one contract at a time; no multi-document comparison
- **Regex-based clause detection** — contracts with non-standard formatting may have clauses mis-classified
- **No table extraction** — tabular data (pricing schedules, SLA matrices) loses structure
- **English-only** — embeddings, intent templates, and prompts are tuned for English
- **In-memory vector store** — uploaded contracts don't survive container restarts on free tier
- **Free-tier constraints** — cold starts take several minutes; Groq has rate limits

---

## Key Learnings

- **Prompt engineering alone is not enough** — even with meticulous citation-first prompts, the LLM occasionally ignores instructions. Post-generation verification is essential, not optional.
- **Chunking strategy matters more than model choice** — clause-aware chunking with semantic enrichment dramatically outperformed naive fixed-size chunking.
- **Query expansion is a cheap win** — expanding "termination" to also search "cancellation" and "end the contract" significantly improved retrieval recall.
- **Intent-aware retrieval beats raw similarity** — boosting chunks whose clause title matches the detected query intent consistently surfaced the right clauses.
- **"Refuse rather than fabricate" builds trust** — users trust a system that says "the contract doesn't specify this" far more than one that confidently fabricates an answer.

---

## Future Scope

- **Multi-format support** — Word documents, scanned contracts via OCR
- **Multi-document analysis** — comparative questions across contracts
- **Table extraction** — preserve structured data like pricing schedules
- **Conversational memory** — follow-up questions without re-stating context
- **Fine-tuned embeddings** — domain-specific model trained on legal data
- **Confidence scoring** — display reliability scores alongside answers
- **Clause-level summarization** — auto-generated structured summaries on upload
- **Multilingual support** — extend to non-English contracts

---

## License

This project is licensed under the MIT License.

---

<div align="center">

**Built by [Rohit Kumar Dubey](https://github.com/roger-rkd)**

FastAPI  ·  Streamlit  ·  ChromaDB  ·  sentence-transformers  ·  Groq LLM  ·  pdfplumber

</div>
