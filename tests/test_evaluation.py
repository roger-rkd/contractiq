from pathlib import Path
import uuid

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.chunking.clause_chunker import clause_chunk
from app.embeddings.embedder import embed_texts
from app.vectorstore.chroma_client import ChromaVectorStore

from app.evaluation.evaluator import RAGEvaluator
from app.evaluation.test_cases import TEST_CASES

# 🔹 STEP 1: Ingest contract BEFORE evaluation
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

# 🔹 STEP 2: Run evaluation
evaluator = RAGEvaluator()

for case in TEST_CASES:
    result = evaluator.evaluate(
        question=case["question"],
        expected_keywords=case["expected_keywords"],
        expect_absent=case["expect_absent"]
    )

    print("\nQUESTION:", result["question"])
    print("ANSWER:", result["answer"])
    print("Latency (s):", result["latency_sec"])
    print("Retrieval Recall:", result["retrieval_recall"])
    print("Hallucination Risk:", result["hallucination_risk"])
