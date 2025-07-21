# app/middlewares/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from src.utils.error_utils import (
    DatabaseConnectionError,
    NotFoundError,
    QueryExecutionError,
    RecordAlreadyExistsError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        logger.warning(f"Resource not found: {exc.detail}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Not Found",
                "message": exc.detail,
                "code": 404,
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation error: {exc.detail}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Validation Error",
                "message": exc.detail,
                "code": 400,
            },
        )

    @app.exception_handler(DatabaseConnectionError)
    async def db_connection_handler(request: Request, exc: DatabaseConnectionError):
        logger.error(f"Database connection error: {exc.detail}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Service Unavailable",
                "message": exc.detail,
                "code": 503,
            },
        )

    @app.exception_handler(RecordAlreadyExistsError)
    async def record_exists_handler(request: Request, exc: RecordAlreadyExistsError):
        logger.warning(f"Record exists: {exc.detail}")
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": "Conflict",
                "message": exc.detail,
                "code": 409,
            },
        )

    @app.exception_handler(QueryExecutionError)
    async def query_error_handler(request: Request, exc: QueryExecutionError):
        logger.error(f"Query execution error: {exc.detail}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Server Error",
                "message": exc.detail,
                "code": 500,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "code": 500,
            },
        )
