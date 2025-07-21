import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class ValidationError(Exception):
    """Exception raised when validation fails."""

    def __init__(self, detail: str = "Validation failed"):
        self.detail = detail


class DatabaseConnectionError(Exception):
    """Raised when a database connection fails."""

    def __init__(self, detail: str = "Failed to connect to the database"):
        self.detail = detail


class RecordAlreadyExistsError(Exception):
    """Raised when a record already exists in the database."""

    def __init__(self, detail: str = "Record already exists"):
        self.detail = detail


class QueryExecutionError(Exception):
    """Raised when a database query fails to execute properly."""

    def __init__(self, detail: str = "Database query execution failed"):
        self.detail = detail
