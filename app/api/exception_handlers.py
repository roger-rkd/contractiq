"""Exception handlers for the API"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.exceptions import ContractIQException
from app.api.schemas import ErrorResponse, ErrorDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def contractiq_exception_handler(
    request: Request,
    exc: ContractIQException
) -> JSONResponse:
    """Handle custom ContractIQ exceptions"""
    logger.error(f"ContractIQ error: {exc.message}", exc_info=True)

    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        detail=exc.message
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")

    errors = [
        ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"]
        )
        for error in exc.errors()
    ]

    error_response = ErrorResponse(
        error="ValidationError",
        detail="Request validation failed",
        errors=errors
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    error_response = ErrorResponse(
        error="InternalServerError",
        detail="An unexpected error occurred. Please try again later."
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )
