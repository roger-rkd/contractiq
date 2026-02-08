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

**Upload a contract. Ask a question. Get a cited, verified answer or an honest refusal.**

</div>

---

## The Problem

Let's be real: nobody enjoys reading a 50-page legal contract word by word. But that's exactly what lawyers, procurement teams, and business owners have to do every single day just to find one termination clause or a liability cap buried somewhere on page 37.

And here's the frustrating part. When you try using AI chatbots to speed things up, they actually make it worse:

- They **hallucinate**: confidently telling you about terms that don't even exist in the document
- They **skip citations**: giving you answers with absolutely no way to verify where they got that from
- They **paraphrase too loosely**: subtly changing the legal language, which in a contract can mean something completely different

The bottom line? There was no lightweight, trustworthy tool that could guarantee every answer comes straight from the document itself. So we built one.

---

## The Solution

ContractIQ is a RAG (Retrieval-Augmented Generation) system that lets you upload a PDF contract and ask questions in plain English. But here's what makes it different from just throwing your contract at ChatGPT:

- **Every answer is cited**: responses always start with `According to [Clause X]...` so you know exactly where to look
- **Strictly grounded**: answers come only from your uploaded document, never from the LLM's training data
- **Hallucination blocking built in**: a post-generation verification layer actually checks whether the answer is semantically grounded in the retrieved context. If it's not? The answer gets rejected entirely and replaced with an honest refusal
- **Clean bullet-point formatting**: no walls of text, just structured, scannable answers

> The philosophy here is simple: **refuse rather than fabricate.** If the contract doesn't say it, ContractIQ won't make it up.

---

## How It Works

ContractIQ runs on a **6-stage pipeline**, and each stage has a very specific job:

```
PDF Upload --> Clause-Aware --> Embedding & --> Intent-Aware --> Citation-First --> Post-Generation
               Chunking         Storage          Retrieval        Generation        Verification
```

### Stage 1: PDF Ingestion
The uploaded PDF gets parsed page by page using `pdfplumber`. Nothing fancy here, just clean text extraction while keeping track of which page each piece of text came from.

### Stage 2: Clause-Aware Chunking
This is where things get interesting. Instead of blindly chopping the document into fixed-size chunks (which almost always cuts clauses in half), ContractIQ uses a custom clause-aware chunker that actually understands contract structure:
- It detects clause headings using regex patterns (things like `10.2 TERMINATION`)
- It maps each clause to a legal category: Termination, Liability, Payment, Data Protection, and so on
- Long clauses get split further into sub-clauses for finer granularity
- Each chunk is enriched with semantic metadata: the clause title, number, and relevant keywords get prepended to the text before embedding

### Stage 3: Embedding & Storage
Each enriched chunk gets converted into a vector using the `all-MiniLM-L6-v2` sentence-transformer model and stored in ChromaDB for fast similarity search later.

### Stage 4: Intent-Aware Retrieval
When you ask a question, the retriever doesn't just do a simple similarity search. It goes through a multi-step process:
- **Query expansion**: your question gets expanded with semantic variations. So "termination" also searches for "cancellation", "end the contract", and similar phrases
- **Intent detection**: the system figures out what type of legal question you're asking by comparing your query embedding against pre-computed intent template embeddings
- **Multi-query retrieval**: candidate chunks are pulled from ChromaDB for each query variation
- **Intent-aware re-ranking**: chunks whose clause title matches the detected intent get a relevance boost, so the most relevant clauses float to the top

### Stage 5: Citation-First Generation
The top-k retrieved chunks are assembled into a strict prompt and sent to Groq's Llama 3.1 8B model. The prompt is very opinionated about formatting:
- Every answer must begin with `According to [Clause X]...`
- Information must be presented as bullet points
- No paraphrasing beyond what's directly stated in the contract
- If the information isn't there, the model must refuse

### Stage 6: Post-Generation Verification
Here's the safety net. Before the answer reaches you, two verification checks run:
1. **Citation enforcement**: if the LLM's response doesn't have a proper citation and isn't a refusal, it gets forcibly replaced with a refusal message. No exceptions
2. **Hallucination blocking**: the answer is embedded and compared against the retrieved context using cosine similarity. If the grounding score falls below 0.6, the answer is blocked entirely

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
| **Frontend** | Streamlit | Interactive UI for uploading contracts and asking questions |
| **Backend API** | FastAPI | RESTful API powering the `/upload` and `/ask` endpoints |
| **PDF Parsing** | pdfplumber | Page-by-page text extraction from PDF contracts |
| **Chunking** | Custom clause chunker | Clause-aware splitting with semantic enrichment |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) | Converts text into vectors for semantic search |
| **Vector Database** | ChromaDB | Stores and retrieves document chunks by similarity |
| **LLM** | Groq (`llama-3.1-8b-instant`) | Fast inference for generating cited answers |
| **Hallucination Detection** | scikit-learn (cosine similarity) | Verifies that answers are actually grounded in the source |
| **Deployment** | Hugging Face Spaces | Cloud hosting with Streamlit SDK |

---

## API Reference

ContractIQ isn't just a UI. It also exposes a full REST API, so you can integrate it into your own workflows.

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
# This launches both the Streamlit UI and the FastAPI backend in one go
streamlit run streamlit_app.py
```

Once it's running, the Streamlit UI will be at `http://localhost:8501` and the FastAPI docs at `http://localhost:8000/api/docs`.

---

## Deployment

ContractIQ is deployed on **Hugging Face Spaces** using the Streamlit SDK. The `streamlit_app.py` entry point spins up a FastAPI server in a background thread and runs the Streamlit frontend, all in a single process.

Want to deploy your own instance? Here's how:
1. Create a new Space on [Hugging Face](https://huggingface.co/new-space) with **Streamlit** SDK
2. Add your `GROQ_API_KEY` as a Space secret
3. Push the repository to the Space, and you're good to go

---

## Limitations

Being honest about what this can't do (yet):

- **PDF only**: it currently handles PDF contracts. Word docs, scanned images, and OCR are not supported
- **One document at a time**: you can't upload multiple contracts and ask comparative questions across them
- **Clause detection relies on regex**: if a contract has unusual heading formats, some clauses might get lumped under "GENERAL"
- **Tables lose their structure**: pricing schedules, SLA matrices, and other tabular data get flattened into plain text
- **English only**: the embedding model, intent templates, and prompts are all built for English-language contracts
- **No persistence on free tier**: since ChromaDB runs in-memory, uploaded contracts don't survive container restarts
- **Free-tier rate limits**: cold starts on Hugging Face take a few minutes, and Groq's free plan has API rate limits

---

## Key Learnings

Building this taught us a few things the hard way:

- **Prompt engineering alone won't save you.** Even with a carefully crafted citation-first prompt, the LLM still occasionally ignored instructions and produced uncited answers. That's exactly why post-generation verification exists: it's not a nice-to-have, it's essential.
- **Chunking strategy matters way more than model choice.** We spent a lot of time trying different LLMs, but the single biggest improvement came from switching to clause-aware chunking with semantic enrichment. Get the retrieval right, and even a small model produces great answers.
- **Query expansion is a surprisingly cheap win.** A user asking "What are the termination conditions?" would miss chunks that say "cancellation" or "end the contract." Adding semantic query expansion fixed this with almost zero overhead.
- **Pure embedding similarity isn't always enough.** Sometimes irrelevant clauses scored higher in raw cosine similarity than the correct ones. Adding intent detection and clause-title boosting reliably fixed the ranking.
- **Users trust honesty over confidence.** A system that says "the contract doesn't specify this" earns far more trust than one that confidently makes something up. Hard refusal is a feature, not a limitation.

---

## Future Scope

There's a lot more we'd love to build on top of this:

- **Multi-format support**: handle Word documents, scanned contracts via OCR, and HTML agreements
- **Multi-document analysis**: upload several contracts and ask comparative questions like "Which one has a longer notice period?"
- **Table extraction**: properly parse and preserve structured data like pricing schedules and SLA tables
- **Conversational memory**: let users ask follow-up questions like "What about for the second party?" without re-stating the full context
- **Fine-tuned embeddings**: train the embedding model on legal contract data for even better domain-specific retrieval
- **Confidence scoring**: show a reliability score alongside each answer so users can gauge how well-grounded it is
- **Clause-level summarization**: automatically generate a structured summary of the entire contract (key dates, parties, obligations, risks) right after upload
- **Multilingual support**: extend to contracts written in other languages using multilingual embedding models

---

<div align="center">

**Built by [Rohit Kumar Dubey](https://github.com/roger-rkd)**

FastAPI  ·  Streamlit  ·  ChromaDB  ·  sentence-transformers  ·  Groq LLM  ·  pdfplumber

</div>
