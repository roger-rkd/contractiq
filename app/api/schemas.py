from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========================
# Request Models
# ========================

class QueryRequest(BaseModel):
    """Request model for querying the RAG system"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The question to ask about the contract",
        examples=["What are the termination conditions?"]
    )
    top_k: Optional[int] = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve"
    )


class UploadRequest(BaseModel):
    """Metadata for uploaded contract"""
    filename: str = Field(..., description="Name of the uploaded file")
    description: Optional[str] = Field(None, description="Optional description of the contract")


# ========================
# Response Models
# ========================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="ok", description="Service status")
    app: str = Field(..., description="Application name")
    version: str = Field(default="1.0.0", description="API version")


class SourceMetadata(BaseModel):
    """Metadata about a source chunk"""
    clause_title: str = Field(..., description="Title of the clause")
    page_number: int = Field(..., description="Page number in the document")
    source_file: str = Field(..., description="Name of the source file")


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    question: str = Field(..., description="The question that was asked")
    answer: str = Field(..., description="Generated answer from the RAG system")
    sources: List[SourceMetadata] = Field(
        default_factory=list,
        description="Source chunks used to generate the answer"
    )
    latency_sec: Optional[float] = Field(None, description="Query latency in seconds")


class UploadResponse(BaseModel):
    """Response model for successful upload"""
    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Name of the uploaded file")
    chunks_created: int = Field(..., description="Number of chunks created from the document")
    pages_processed: int = Field(..., description="Number of pages processed")


class ErrorDetail(BaseModel):
    """Detailed error information"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    errors: Optional[List[ErrorDetail]] = Field(None, description="List of validation errors")
