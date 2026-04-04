"""
Custom exception handlers for EZOO POS API.

Implements structured error responses following API contracts.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


class EZOOException(Exception):
    """Base exception for EZOO POS."""

    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundException(EZOOException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} {resource_id} not found",
            details={"resource": resource, "id": resource_id},
        )


class ValidationException(EZOOException):
    """Validation error."""

    def __init__(self, message: str, field: str = None, value: any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(code="VALIDATION_ERROR", message=message, details=details)


class ConflictException(EZOOException):
    """Conflict error (e.g., duplicate SKU)."""

    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(code="CONFLICT", message=message, details=details)


class InsufficientStockException(EZOOException):
    """Insufficient stock error."""

    def __init__(self, product_name: str, requested: int, available: int):
        super().__init__(
            code="INSUFFICIENT_STOCK",
            message=f"Insufficient stock for {product_name}: requested {requested}, available {available}",
            details={
                "product_name": product_name,
                "requested": requested,
                "available": available,
            },
        )


class AlreadyReversedException(EZOOException):
    """Sale already reversed error."""

    def __init__(self, sale_id: str):
        super().__init__(
            code="ALREADY_REVERSED",
            message=f"Sale {sale_id} has already been reversed",
            details={"sale_id": sale_id},
        )


async def ezoo_exception_handler(request: Request, exc: EZOOException) -> JSONResponse:
    """Handle EZOO exceptions with structured response."""
    status_code = _get_status_code(exc.code)

    logger.warning(
        f"EZOO Exception: {exc.code} - {exc.message}",
        extra={"details": exc.details, "path": request.url.path},
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(
            {
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(f"Validation error: {errors}", extra={"path": request.url.path})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors},
            }
        },
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity errors."""
    logger.error(f"Integrity error: {str(exc)}", extra={"path": request.url.path})

    # Parse common integrity errors
    error_message = str(exc)
    if "unique constraint" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "code": "CONFLICT",
                    "message": "A resource with this identifier already exists",
                    "details": {},
                }
            },
        )
    elif "foreign key constraint" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "INVALID_REFERENCE",
                    "message": "Referenced resource does not exist",
                    "details": {},
                }
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "A database error occurred",
                    "details": {},
                }
            },
        )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {str(exc)}", extra={"path": request.url.path})

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            }
        },
    )


def _get_status_code(code: str) -> int:
    """Map error codes to HTTP status codes."""
    mapping = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "INSUFFICIENT_STOCK": status.HTTP_400_BAD_REQUEST,
        "ALREADY_REVERSED": status.HTTP_400_BAD_REQUEST,
        "INTERNAL_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    return mapping.get(code, status.HTTP_400_BAD_REQUEST)


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app."""
    from fastapi.exceptions import HTTPException

    app.add_exception_handler(EZOOException, ezoo_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
