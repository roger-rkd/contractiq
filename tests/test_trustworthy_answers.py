"""
Test script for Phase 2: Trustworthy Answers

This test verifies:
1. Citation-first enforcement
2. Hard refusal for unsupported questions
3. Hallucination blocking
"""
from pathlib import Path
import uuid
import re

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.chunking.clause_chunker import clause_chunk
from app.embeddings.embedder import embed_texts
from app.vectorstore.chroma_client import ChromaVectorStore
from app.rag.generator import RAGPipeline, REFUSAL_MESSAGE


def setup_test_data():
    """Load and ingest the sample contract"""
    print("Setting up test data...")

    pdf_path = Path("data/contracts/sample.pdf")
    if not pdf_path.exists():
        print(f"ERROR: Sample PDF not found at {pdf_path}")
        return False

    # Load and process
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

    # Embed and store
    embeddings = embed_texts(texts)
    vector_store = ChromaVectorStore()
    vector_store.add_documents(texts, metadatas, ids)

    print(f"[OK] Loaded {len(chunks)} chunks from {len(docs)} pages\n")
    return True


def has_citation(answer: str) -> bool:
    """Check if answer has proper citation format"""
    citation_patterns = [
        r"According to \[Clause \d+\]",
        r"Based on \[Clause \d+\]",
        r"As stated in \[Clause \d+\]",
    ]

    for pattern in citation_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            return True

    return False


def is_refusal(answer: str) -> bool:
    """Check if answer is a refusal"""
    return "INSUFFICIENT_INFORMATION" in answer


def test_supported_question():
    """Test that supported questions get cited answers"""
    print("=" * 70)
    print("TEST 1: Supported Question (Should have citation)")
    print("=" * 70)

    rag = RAGPipeline()
    question = "What are the termination conditions?"

    result = rag.answer(question)
    answer = result["answer"]

    print(f"\nQuestion: {question}")
    print(f"Answer: {answer[:200]}...")
    print(f"Sources: {len(result['sources'])} clauses")

    # Checks
    checks = []

    # Check 1: Not a refusal
    not_refusal = not is_refusal(answer)
    checks.append(("Not a refusal", not_refusal))
    if not_refusal:
        print("[OK] Not a refusal")
    else:
        print("[FAIL] FAIL: Should not be refused")

    # Check 2: Has citation
    has_cite = has_citation(answer)
    checks.append(("Has citation", has_cite))
    if has_cite:
        print("[OK] Has proper citation format")
    else:
        print("[FAIL] FAIL: Missing citation")

    # Check 3: Has sources
    has_sources = len(result['sources']) > 0
    checks.append(("Has sources", has_sources))
    if has_sources:
        print(f"[OK] Has {len(result['sources'])} source(s)")
    else:
        print("[FAIL] FAIL: No sources")

    passed = all(check[1] for check in checks)
    print(f"\nTest 1: {'PASSED' if passed else 'FAILED'}")
    return passed


def test_unsupported_question():
    """Test that unsupported questions get refused"""
    print("\n" + "=" * 70)
    print("TEST 2: Unsupported Question (Should refuse)")
    print("=" * 70)

    rag = RAGPipeline()
    question = "What law governs this agreement?"

    result = rag.answer(question)
    answer = result["answer"]

    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")

    # Check: Must be a refusal
    is_refused = is_refusal(answer)

    if is_refused:
        print("[OK] Properly refused (contract doesn't specify this)")
    else:
        print("[FAIL] FAIL: Should have been refused")
        print(f"  Got: {answer}")

    print(f"\nTest 2: {'PASSED' if is_refused else 'FAILED'}")
    return is_refused


def test_another_unsupported_question():
    """Test another unsupported question"""
    print("\n" + "=" * 70)
    print("TEST 3: Another Unsupported Question (Should refuse)")
    print("=" * 70)

    rag = RAGPipeline()
    question = "How is personal data handled?"

    result = rag.answer(question)
    answer = result["answer"]

    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")

    # Check: Must be a refusal
    is_refused = is_refusal(answer)

    if is_refused:
        print("[OK] Properly refused (contract doesn't specify this)")
    else:
        print("[FAIL] FAIL: Should have been refused")
        print(f"  Got: {answer}")

    print(f"\nTest 3: {'PASSED' if is_refused else 'FAILED'}")
    return is_refused


def test_citation_format():
    """Test that citations follow the required format"""
    print("\n" + "=" * 70)
    print("TEST 4: Citation Format Verification")
    print("=" * 70)

    rag = RAGPipeline()

    # Test multiple questions that should be answerable
    questions = [
        "What are the termination conditions?",
        "What happens if there is a breach?",
    ]

    all_passed = True

    for i, question in enumerate(questions, 1):
        print(f"\n  {i}. Testing: {question}")

        result = rag.answer(question)
        answer = result["answer"]

        # Skip refusals
        if is_refusal(answer):
            print(f"     → Refused (OK, question might not be answerable)")
            continue

        # Check citation format
        has_cite = has_citation(answer)

        if has_cite:
            print(f"     [OK] Has citation")
        else:
            print(f"     [FAIL] FAIL: Missing citation")
            print(f"       Answer: {answer[:100]}...")
            all_passed = False

    print(f"\nTest 4: {'PASSED' if all_passed else 'FAILED'}")
    return all_passed


def test_no_hallucination():
    """Test that hallucinated content is blocked"""
    print("\n" + "=" * 70)
    print("TEST 5: Hallucination Blocking")
    print("=" * 70)

    rag = RAGPipeline()

    # Ask a question that might tempt hallucination
    question = "What are the payment terms and conditions?"

    result = rag.answer(question)
    answer = result["answer"]

    print(f"\nQuestion: {question}")
    print(f"Answer: {answer[:200]}...")

    # If answered, must have citation
    # If not in contract, must be refused
    if is_refusal(answer):
        print("[OK] Refused (information not in contract)")
        passed = True
    elif has_citation(answer):
        print("[OK] Answered with citation (information found)")
        passed = True
    else:
        print("[FAIL] FAIL: Answer without citation (hallucination not blocked)")
        passed = False

    print(f"\nTest 5: {'PASSED' if passed else 'FAILED'}")
    return passed


def main():
    """Run all trustworthy answer tests"""
    print("\n")
    print("#" * 70)
    print("#" + " " * 68 + "#")
    print("#  PHASE 2: TRUSTWORTHY ANSWERS - TEST SUITE" + " " * 23 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    print("\n")

    # Setup
    if not setup_test_data():
        print("ERROR: Failed to set up test data")
        return 1

    # Run tests
    results = []

    results.append(("Supported Question (Citation)", test_supported_question()))
    results.append(("Unsupported Question (Refusal)", test_unsupported_question()))
    results.append(("Another Unsupported Question", test_another_unsupported_question()))
    results.append(("Citation Format", test_citation_format()))
    results.append(("Hallucination Blocking", test_no_hallucination()))

    # Summary
    print("\n")
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "[OK]" if passed else "[FAIL]"
        print(f"{symbol} {name}: {status}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed_count}/{total} tests passed")

    if all(p for _, p in results):
        print("\n🎉 ALL TESTS PASSED - Trustworthy answers are working!")
    else:
        print("\nWARNING:  SOME TESTS FAILED - Review the output above")

    print("=" * 70)
    print("\n")

    return 0 if all(p for _, p in results) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
