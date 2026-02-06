from sentence_transformers import SentenceTransformer
from typing import List
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load once (important for performance)
model = SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of texts into embeddings.
    """
    logger.info(f"Embedding {len(texts)} texts")
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()
