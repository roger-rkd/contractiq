"""Query endpoint for asking questions about contracts"""
import time
from fastapi import APIRouter, status

from app.api.schemas import QueryRequest, QueryResponse, SourceMetadata
from app.api.exceptions import LLMError, NoDocumentsFoundError, VectorDBError
from app.rag.generator import RAGPipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post(
    "/ask",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about the contract",
    description="Query the RAG system with a question about the uploaded contract documents"
)
async def ask_question(request: QueryRequest) -> QueryResponse:
    """
    Ask a question about the contract.

    Args:
        request: QueryRequest with question and optional top_k parameter

    Returns:
        QueryResponse with answer, sources, and latency

    Raises:
        NoDocumentsFoundError: If no documents are found in vector store
        LLMError: If LLM fails to generate response
        VectorDBError: If vector database query fails
    """
    logger.info(f"Received query: {request.question}")

    start_time = time.time()

    try:
        # Initialize RAG pipeline
        rag = RAGPipeline()

        # Get answer from RAG system
        result = rag.answer(request.question)

        latency = round(time.time() - start_time, 3)

        # Check if any sources were found
        if not result.get("sources"):
            raise NoDocumentsFoundError()

        # Convert sources to proper schema
        sources = [
            SourceMetadata(
                clause_title=src.get("clause_title", "Unknown"),
                page_number=src.get("page_number", 0),
                source_file=src.get("source_file", "Unknown")
            )
            for src in result["sources"]
        ]

        response = QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=sources,
            latency_sec=latency
        )

        logger.info(f"Query processed successfully in {latency}s")
        return response

    except NoDocumentsFoundError:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise LLMError(f"Failed to process query: {str(e)}")
