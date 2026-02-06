"""
RAG Pipeline with citation enforcement and hallucination blocking.
"""
import re
from typing import Dict, List

from app.utils.groq_client import generate_response
from app.rag.retriever import Retriever
from app.rag.prompt import build_citation_first_prompt
from app.evaluation.metrics import detect_hallucination
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Standard refusal message
REFUSAL_MESSAGE = "INSUFFICIENT_INFORMATION: The contract does not specify this."


class RAGPipeline:
    """
    RAG Pipeline with:
    - Citation-first enforcement
    - Hallucination blocking (not just detection)
    - Hard refusal for unsupported questions
    """

    def __init__(self):
        self.retriever = Retriever()

    def _has_valid_citation(self, answer: str) -> bool:
        """
        Check if the answer starts with a proper citation.

        Valid citation patterns:
        - "According to [Clause X]"
        - "Based on [Clause X]"
        - "As stated in [Clause X]"

        Returns:
            True if answer has valid citation, False otherwise
        """
        citation_patterns = [
            r"^According to \[Clause \d+\]",
            r"^Based on \[Clause \d+\]",
            r"^As stated in \[Clause \d+\]",
        ]

        answer_lower = answer.strip()

        for pattern in citation_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                return True

        return False

    def _is_refusal(self, answer: str) -> bool:
        """
        Check if the answer is a proper refusal.

        Returns:
            True if answer is a refusal, False otherwise
        """
        refusal_patterns = [
            "INSUFFICIENT_INFORMATION",
            "The contract does not specify this",
            "does not specify",
            "not specified in the contract",
        ]

        answer_lower = answer.lower()

        for pattern in refusal_patterns:
            if pattern.lower() in answer_lower:
                return True

        return False

    def _enforce_citation_requirement(self, answer: str) -> str:
        """
        Enforce that answers must have citations or be refusals.

        If an answer lacks both citation and refusal format,
        force it to be a refusal.

        Args:
            answer: The LLM-generated answer

        Returns:
            Original answer if valid, or forced refusal message
        """
        # If it's a refusal, that's acceptable
        if self._is_refusal(answer):
            return REFUSAL_MESSAGE

        # If it has a citation, that's acceptable
        if self._has_valid_citation(answer):
            return answer

        # If it has neither citation nor refusal, FORCE refusal
        logger.warning(
            "LLM response lacks citation and is not a refusal. "
            "Forcing refusal to maintain trustworthiness."
        )
        return REFUSAL_MESSAGE

    def _block_if_hallucinated(
        self,
        answer: str,
        contexts: List[Dict]
    ) -> str:
        """
        Block hallucinated answers with hard refusal.

        Uses semantic similarity to detect if the answer is grounded
        in the retrieved context. If hallucination is detected,
        returns a refusal instead.

        Args:
            answer: The generated answer
            contexts: Retrieved context chunks

        Returns:
            Original answer if grounded, or refusal if hallucinated
        """
        # Skip hallucination check for refusals
        if self._is_refusal(answer):
            return answer

        # Detect hallucination
        is_hallucinated = detect_hallucination(answer, contexts)

        if is_hallucinated:
            logger.warning(
                "Hallucination detected. Blocking answer and returning refusal."
            )
            return REFUSAL_MESSAGE

        return answer

    def answer(self, question: str) -> Dict:
        """
        Generate a trustworthy answer with citation enforcement.

        Process:
        1. Retrieve relevant contexts
        2. Build citation-first prompt
        3. Generate answer from LLM
        4. Enforce citation requirement
        5. Block if hallucinated
        6. Return final answer

        Args:
            question: User's question

        Returns:
            Dict with question, answer, and sources
        """
        logger.info(f"Processing question: {question}")

        # Step 1: Retrieve contexts
        contexts = self.retriever.retrieve(question)

        if not contexts:
            logger.warning("No contexts retrieved. Returning refusal.")
            return {
                "question": question,
                "answer": REFUSAL_MESSAGE,
                "sources": []
            }

        # Step 2: Build citation-first prompt
        messages = build_citation_first_prompt(question, contexts)

        # Step 3: Generate answer
        raw_answer = generate_response(messages)
        logger.info(f"Raw LLM answer: {raw_answer[:100]}...")

        # Step 4: Enforce citation requirement
        answer_with_citation = self._enforce_citation_requirement(raw_answer)

        # Step 5: Block if hallucinated
        final_answer = self._block_if_hallucinated(
            answer_with_citation,
            contexts
        )

        # Log if answer was modified
        if final_answer != raw_answer:
            logger.warning(
                f"Answer was modified from raw LLM output. "
                f"Original: {raw_answer[:50]}... "
                f"Final: {final_answer[:50]}..."
            )

        return {
            "question": question,
            "answer": final_answer,
            "sources": [ctx["metadata"] for ctx in contexts]
        }
