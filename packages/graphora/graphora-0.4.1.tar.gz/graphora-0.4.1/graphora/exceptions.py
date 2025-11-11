"""
Graphora Exceptions

Custom exceptions for the Graphora client library.
"""

class GraphoraError(Exception):
    """Base exception for all Graphora errors."""
    pass


class GraphoraClientError(GraphoraError):
    """Exception raised for client-side errors."""
    pass


class GraphoraAPIError(GraphoraError):
    """Exception raised for API errors."""
    
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)
