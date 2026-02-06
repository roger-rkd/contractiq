"""Upload endpoint for ingesting contract PDFs"""
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, status, Form
from typing import Optional

from app.api.schemas import UploadResponse
from app.api.exceptions import (
    EmptyUploadError,
    UnsupportedFileTypeError,
    DocumentProcessingError,
    VectorDBError
)
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.chunking.clause_chunker import clause_chunk
from app.embeddings.embedder import embed_texts
from app.vectorstore.chroma_client import ChromaVectorStore
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["upload"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a contract PDF",
    description="Upload a PDF contract for processing and ingestion into the vector database"
)
async def upload_contract(
    file: UploadFile = File(..., description="PDF file to upload"),
    description: Optional[str] = Form(None, description="Optional description of the contract")
) -> UploadResponse:
    """
    Upload and process a contract PDF.

    Args:
        file: The PDF file to upload
        description: Optional description of the contract

    Returns:
        UploadResponse with processing details

    Raises:
        EmptyUploadError: If no file is provided
        UnsupportedFileTypeError: If file is not a PDF
        DocumentProcessingError: If document processing fails
        VectorDBError: If vector database ingestion fails
    """
    logger.info(f"Received upload request for file: {file.filename}")

    # Validate file exists
    if not file or not file.filename:
        raise EmptyUploadError()

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise UnsupportedFileTypeError(
            f"File type '{file.filename.split('.')[-1]}' not supported. Only PDF files are allowed."
        )

    # Ensure contracts directory exists
    settings.CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    file_path = settings.CONTRACT_DIR / file.filename
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)

        logger.info(f"Saved file to {file_path}")

    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}", exc_info=True)
        raise DocumentProcessingError(f"Failed to save file: {str(e)}")

    # Process the PDF
    try:
        # Load PDF
        docs = load_pdf(file_path)
        pages_processed = len(docs)

        if not docs:
            raise DocumentProcessingError("No pages could be extracted from the PDF")

        # Clean text
        cleaned_docs = [clean_text(d) for d in docs]

        # Chunk into clauses
        chunks = []
        for doc in cleaned_docs:
            chunks.extend(clause_chunk(doc))

        if not chunks:
            raise DocumentProcessingError("No valid clauses could be extracted from the document")

        logger.info(f"Created {len(chunks)} chunks from {pages_processed} pages")

    except DocumentProcessingError:
        raise
    except Exception as e:
        logger.error(f"Failed to process document: {str(e)}", exc_info=True)
        raise DocumentProcessingError(f"Failed to process document: {str(e)}")

    # Ingest into vector database
    try:
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

        # Create embeddings
        embeddings = embed_texts(texts)

        # Store in vector DB
        vector_store = ChromaVectorStore()
        vector_store.add_documents(texts, metadatas, ids)

        logger.info(f"Successfully ingested {len(chunks)} chunks into vector database")

    except Exception as e:
        logger.error(f"Failed to ingest into vector database: {str(e)}", exc_info=True)
        raise VectorDBError(f"Failed to ingest into vector database: {str(e)}")

    return UploadResponse(
        message="Contract uploaded and processed successfully",
        filename=file.filename,
        chunks_created=len(chunks),
        pages_processed=pages_processed
    )
