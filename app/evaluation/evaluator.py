import time
from typing import Dict, List, Optional

from app.rag.generator import RAGPipeline
from app.evaluation.metrics import (
    measure_latency,
    retrieval_recall,
    detect_hallucination
)


class RAGEvaluator:
    def __init__(self):
        self.rag = RAGPipeline()

    def evaluate(
        self,
        question: str,
        expected_keywords: List[str],
        expect_absent: bool = False
    ) -> Dict:
        """
        expect_absent:
            True  -> clause is NOT expected to exist in the document
            False -> clause SHOULD exist and be retrievable
        """

        start = time.time()

        contexts = self.rag.retriever.retrieve(question)
        result = self.rag.answer(question)
        answer = result["answer"]

        end = time.time()

        latency = measure_latency(start, end)

        # 🔹 FIX: Do not penalize missing clauses
        if expect_absent:
            recall: Optional[float] = None
        else:
            recall = retrieval_recall(contexts, expected_keywords)

        hallucinated = detect_hallucination(answer, contexts)

        return {
            "question": question,
            "answer": answer,
            "latency_sec": latency,
            "retrieval_recall": recall,
            "hallucination_risk": hallucinated,
            "num_contexts": len(contexts)
        }
