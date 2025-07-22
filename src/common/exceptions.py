from fastapi import HTTPException


# --- 4xx Client Errors ---


class ValidationError(HTTPException):
    """Invalid input or data validation failure."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(status_code=422, detail=message)


class BadRequestError(HTTPException):
    """Generic bad request."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(status_code=400, detail=message)


class NotFoundError(HTTPException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id=None):
        message = (
            f"{resource} not found"
            if resource_id is None
            else f"{resource} with id {resource_id} not found"
        )
        super().__init__(status_code=404, detail=message)


class UnauthorizedError(HTTPException):
    """Authentication failure."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)


class ForbiddenError(HTTPException):
    """Authorization failure."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(status_code=403, detail=message)


# --- 5xx Server Errors ---


class InternalServerError(HTTPException):
    """Generic server-side error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(status_code=500, detail=message)


class DatabaseError(HTTPException):
    """Database-related errors."""

    def __init__(self, message: str = "Database error"):
        super().__init__(status_code=500, detail=message)
