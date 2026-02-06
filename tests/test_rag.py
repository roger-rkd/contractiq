from pathlib import Path
import uuid

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.chunking.clause_chunker import clause_chunk
from app.embeddings.embedder import embed_texts
from app.vectorstore.chroma_client import ChromaVectorStore
from app.rag.generator import RAGPipeline

# 1️⃣ Ingest + store clauses
pdf_path = Path("data/contracts/sample.pdf")

docs = load_pdf(pdf_path)
cleaned_docs = [clean_text(d) for d in docs]

chunks = []
for doc in cleaned_docs:
    chunks.extend(clause_chunk(doc))

texts = [c["text"] for c in chunks]
metadatas = [
    {
        "clause_title": c["clause_title"],
        "page_number": c["page_number"],
        "source_file": c["source_file"]
    }
    for c in chunks
]
ids = [str(uuid.uuid4()) for _ in texts]

embeddings = embed_texts(texts)

vector_store = ChromaVectorStore()
vector_store.add_documents(texts, metadatas, ids)

# 2️⃣ Ask a question
rag = RAGPipeline()
question = "What are the termination conditions in this contract?"
response = rag.answer(question)

print("\nANSWER:\n", response["answer"])
print("\nSOURCES:")
for s in response["sources"]:
    print(s)
