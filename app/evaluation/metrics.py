import time
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.embeddings.embedder import embed_texts
from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# Latency
# =========================
def measure_latency(start_time: float, end_time: float) -> float:
    """
    Measure latency in seconds.
    """
    return round(end_time - start_time, 3)


# =========================
# Embedding-based Recall
# =========================
def retrieval_recall(
    retrieved_chunks: List[dict],
    expected_concepts: List[str],
    similarity_threshold: float = 0.65,
) -> float:
    """
    Embedding-based retrieval recall.

    Measures whether retrieved chunks semantically
    cover the expected concepts (NO keyword matching).
    """

    if not expected_concepts:
        return 1.0

    if not retrieved_chunks:
        return 0.0

    retrieved_texts = [chunk["text"] for chunk in retrieved_chunks]

    retrieved_embeddings = np.array(embed_texts(retrieved_texts))
    expected_embeddings = np.array(embed_texts(expected_concepts))

    similarity_matrix = cosine_similarity(
        expected_embeddings, retrieved_embeddings
    )

    covered = 0
    for i, concept in enumerate(expected_concepts):
        max_sim = similarity_matrix[i].max()

        logger.debug(
            f"Concept '{concept}' max similarity: {max_sim:.3f}"
        )

        if max_sim >= similarity_threshold:
            covered += 1

    recall = covered / len(expected_concepts)
    return round(recall, 3)


# =========================
# Hallucination Detection
# =========================
def detect_hallucination(
    answer: str,
    retrieved_chunks: List[dict],
    similarity_threshold: float = 0.6,
) -> bool:
    """
    Embedding-based hallucination detection.

    Flags hallucination if the answer is NOT
    semantically grounded in retrieved content.
    """

    if not retrieved_chunks:
        return True

    retrieved_texts = [chunk["text"] for chunk in retrieved_chunks]

    retrieved_embeddings = np.array(embed_texts(retrieved_texts))
    answer_embedding = np.array(embed_texts([answer]))

    similarities = cosine_similarity(
        answer_embedding, retrieved_embeddings
    )[0]

    max_similarity = similarities.max()

    logger.debug(
        f"Answer grounding similarity: {max_similarity:.3f}"
    )

    return max_similarity < similarity_threshold
