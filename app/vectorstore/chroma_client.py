import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaVectorStore:
    def __init__(self, collection_name: str = "contracts"):
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=str(settings.VECTOR_DB_DIR),
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(self, texts: List[str], metadatas: List[Dict], ids: List[str]):
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Stored {len(texts)} documents in vector DB")

    def similarity_search(self, query_embedding: List[float], top_k: int = 5):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
