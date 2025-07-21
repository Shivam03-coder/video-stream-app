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
        
        
