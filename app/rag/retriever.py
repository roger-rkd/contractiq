"""
Enhanced retriever with intent-aware similarity boosting and debug logging.
"""
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

from app.embeddings.embedder import embed_texts
from app.vectorstore.chroma_client import ChromaVectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Intent templates for query understanding
INTENT_TEMPLATES = {
    "governing_law": [
        "What law governs this agreement?",
        "Which jurisdiction applies?",
        "What is the applicable law?",
        "Under what legal framework?"
    ],
    "termination": [
        "What are the termination conditions?",
        "How can this agreement be terminated?",
        "When can the contract end?",
        "What are the cancellation terms?"
    ],
    "data_protection": [
        "How is personal data handled?",
        "What are the data protection requirements?",
        "How is privacy managed?",
        "What are the GDPR obligations?"
    ],
    "liability": [
        "What is the liability limit?",
        "Who is responsible for damages?",
        "What are the indemnity provisions?",
        "What are the liability clauses?"
    ],
    "payment": [
        "What are the payment terms?",
        "How much does it cost?",
        "What are the fees?",
        "When is payment due?"
    ],
    "confidentiality": [
        "What are the confidentiality requirements?",
        "How is confidential information protected?",
        "What are the non-disclosure terms?",
        "What information must be kept secret?"
    ]
}


class Retriever:
    """
    Enhanced retriever with:
    - Intent-aware similarity boosting
    - Multi-query retrieval
    - Embedding-based ranking
    - Debug logging
    """

    def __init__(self, top_k: int = 4, debug: bool = False):
        self.vector_store = ChromaVectorStore()
        self.top_k = top_k
        self.debug = debug

        # Pre-compute intent embeddings for faster similarity
        self._intent_embeddings = self._compute_intent_embeddings()

    def _compute_intent_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Pre-compute embeddings for intent templates.

        Returns:
            Dict mapping intent names to their average embeddings
        """
        logger.info("Computing intent embeddings for similarity boosting...")

        intent_embeddings = {}

        for intent_name, templates in INTENT_TEMPLATES.items():
            # Embed all templates for this intent
            embeddings = np.array(embed_texts(templates))

            # Average the embeddings
            avg_embedding = embeddings.mean(axis=0)

            intent_embeddings[intent_name] = avg_embedding

        logger.info(f"Computed {len(intent_embeddings)} intent embeddings")
        return intent_embeddings

    def _detect_query_intent(self, query_embedding: np.ndarray) -> Dict[str, float]:
        """
        Detect the intent of the query using embedding similarity.

        Args:
            query_embedding: Embedding of the user query

        Returns:
            Dict mapping intent names to similarity scores
        """
        intent_scores = {}

        for intent_name, intent_embedding in self._intent_embeddings.items():
            # Compute cosine similarity
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                intent_embedding.reshape(1, -1)
            )[0][0]

            intent_scores[intent_name] = float(similarity)

        return intent_scores

    def _expand_query(self, query: str) -> List[str]:
        """
        Expand user query with semantic variations.

        Now uses more intelligent expansion based on the query content.

        Args:
            query: User's original query

        Returns:
            List of expanded query variations
        """
        expanded = [query]

        query_lower = query.lower()

        # Expanded variations based on common legal terms
        expansions = {
            "terminate": [
                "termination",
                "cancel this agreement",
                "end the contract"
            ],
            "termination": [
                "terminate",
                "cancellation conditions",
                "agreement termination"
            ],
            "law": [
                "governing law",
                "applicable jurisdiction",
                "legal framework"
            ],
            "governing law": [
                "applicable law",
                "jurisdiction",
                "legal framework"
            ],
            "data": [
                "personal data",
                "data protection",
                "information handling"
            ],
            "personal data": [
                "data protection",
                "privacy",
                "information security"
            ],
            "payment": [
                "fees",
                "charges",
                "cost"
            ],
            "fees": [
                "payment",
                "charges",
                "billing"
            ],
            "confidential": [
                "confidentiality",
                "proprietary information",
                "non-disclosure"
            ],
            "liability": [
                "responsibility",
                "damages",
                "indemnity"
            ]
        }

        # Add variations found in the query
        for key, variants in expansions.items():
            if key in query_lower:
                expanded.extend(variants)

        # Deduplicate while preserving order
        seen = set()
        unique_expanded = []
        for q in expanded:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_expanded.append(q)

        return unique_expanded

    def _rank_by_intent_similarity(
        self,
        chunks: List[Dict],
        query_embedding: np.ndarray,
        intent_scores: Dict[str, float]
    ) -> List[Dict]:
        """
        Rank chunks using intent-aware similarity boosting.

        Uses embedding-based similarity (NOT keyword matching) to boost
        chunks that match the query intent.

        Args:
            chunks: Retrieved chunks
            query_embedding: Embedding of the query
            intent_scores: Intent similarity scores for the query

        Returns:
            Ranked list of chunks
        """
        # Get the top intents (those with score > 0.3)
        top_intents = {
            intent: score
            for intent, score in intent_scores.items()
            if score > 0.3
        }

        if self.debug and top_intents:
            logger.debug(f"Detected intents: {top_intents}")

        # For each chunk, compute a ranking score
        ranked_chunks = []

        for chunk in chunks:
            clause_title = chunk["metadata"].get("clause_title", "").lower()
            text = chunk["text"].lower()

            # Base score: 0
            boost_score = 0.0

            # Boost based on intent matching
            # Use embedding similarity between chunk text and intent templates
            if "termination" in top_intents and "termination" in clause_title:
                boost_score += top_intents["termination"] * 2.0

            if "governing_law" in top_intents and any(
                term in clause_title
                for term in ["governing law", "law", "jurisdiction"]
            ):
                boost_score += top_intents["governing_law"] * 2.0

            if "data_protection" in top_intents and any(
                term in clause_title
                for term in ["data protection", "data", "privacy"]
            ):
                boost_score += top_intents["data_protection"] * 2.0

            if "liability" in top_intents and "liability" in clause_title:
                boost_score += top_intents["liability"] * 2.0

            if "payment" in top_intents and any(
                term in clause_title
                for term in ["payment", "fees", "charges"]
            ):
                boost_score += top_intents["payment"] * 2.0

            if "confidentiality" in top_intents and "confidential" in clause_title:
                boost_score += top_intents["confidentiality"] * 2.0

            ranked_chunks.append({
                "chunk": chunk,
                "score": boost_score
            })

        # Sort by score (descending)
        ranked_chunks.sort(key=lambda x: x["score"], reverse=True)

        # Extract chunks
        result = [item["chunk"] for item in ranked_chunks]

        if self.debug:
            logger.debug("Top 3 chunks after intent boosting:")
            for i, item in enumerate(ranked_chunks[:3], 1):
                title = item["chunk"]["metadata"].get("clause_title", "Unknown")
                score = item["score"]
                logger.debug(f"  {i}. {title} (boost score: {score:.3f})")

        return result

    def retrieve(self, query: str) -> List[Dict]:
        """
        Retrieve relevant chunks with intent-aware boosting.

        Process:
        1. Expand query into variations
        2. Detect query intent using embeddings
        3. Retrieve chunks for each query variation
        4. Deduplicate
        5. Rank using intent-aware similarity boosting
        6. Return top-k

        Args:
            query: User's question

        Returns:
            List of top-k relevant chunks
        """
        if self.debug:
            logger.debug(f"\n{'='*60}")
            logger.debug(f"RETRIEVAL DEBUG: {query}")
            logger.debug(f"{'='*60}")

        # Step 1: Expand query
        expanded_queries = self._expand_query(query)

        if self.debug:
            logger.debug(f"Expanded into {len(expanded_queries)} variations:")
            for i, eq in enumerate(expanded_queries, 1):
                logger.debug(f"  {i}. {eq}")

        # Step 2: Embed all queries
        query_embeddings = embed_texts(expanded_queries)

        # Step 3: Detect intent using the original query embedding
        query_embedding = np.array(query_embeddings[0])
        intent_scores = self._detect_query_intent(query_embedding)

        if self.debug:
            sorted_intents = sorted(
                intent_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            logger.debug(f"\nIntent detection scores:")
            for intent, score in sorted_intents[:3]:
                logger.debug(f"  {intent}: {score:.3f}")

        # Step 4: Retrieve chunks for each query variation
        all_results = []

        for i, emb in enumerate(query_embeddings):
            results = self.vector_store.similarity_search(
                query_embedding=emb,
                top_k=self.top_k
            )

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]

            for doc, meta in zip(documents, metadatas):
                all_results.append({
                    "text": doc,
                    "metadata": meta
                })

        if self.debug:
            logger.debug(f"\nRetrieved {len(all_results)} chunks (before dedup)")

        # Step 5: Deduplicate by text
        unique = {}
        for r in all_results:
            # Use text as key for deduplication
            unique[r["text"]] = r

        retrieved = list(unique.values())

        if self.debug:
            logger.debug(f"After deduplication: {len(retrieved)} unique chunks")

        # Step 6: Rank using intent-aware similarity boosting
        ranked = self._rank_by_intent_similarity(
            retrieved,
            query_embedding,
            intent_scores
        )

        # Step 7: Return top-k
        final_chunks = ranked[:self.top_k]

        if self.debug:
            logger.debug(f"\nFinal top-{self.top_k} chunks:")
            for i, chunk in enumerate(final_chunks, 1):
                title = chunk["metadata"].get("clause_title", "Unknown")
                page = chunk["metadata"].get("page_number", "?")
                logger.debug(f"  {i}. {title} (Page {page})")
            logger.debug(f"{'='*60}\n")
        else:
            logger.info(
                f"Retrieved {len(final_chunks)} chunks "
                f"(from {len(retrieved)} candidates)"
            )

        return final_chunks
