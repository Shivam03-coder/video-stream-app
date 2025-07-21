# app/middlewares/error_handlers.py
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse 
import logging
from src.utils import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

def ErrorMiddleware(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        logger.error(f"Resource not found: {exc}")
        return JSONResponse(status_code=404, content={"error": "Not found", "message": str(exc)})

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        logger.error(f"Validation error: {exc}")
        return JSONResponse(status_code=400, content={"error": "Validation error", "message": str(exc)})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal server error", "message": "An unexpected error occurred"})
