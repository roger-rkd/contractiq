"""Main FastAPI application"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api import query, upload
from app.api.schemas import HealthResponse
from app.api.exceptions import ContractIQException
from app.api.exception_handlers import (
    contractiq_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade RAG API for contract analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(ContractIQException, contractiq_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(query.router)
app.include_router(upload.router)


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Health check",
    description="Check if the API is running and healthy"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with status and application info
    """
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version="1.0.0"
    )


# Root endpoint (redirects to docs)
@app.get(
    "/",
    include_in_schema=False
)
async def root():
    """Root endpoint - redirects to API documentation"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/api/docs",
        "health": "/health"
    }
