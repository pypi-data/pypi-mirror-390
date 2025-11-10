"""API error classes for SecureAPI."""

from typing import Dict, List, Optional, Any


class ApiError(Exception):
    """Base class for all API errors."""
    
    def __init__(self, message: str, status_code: int, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert error to JSON-serializable dictionary."""
        result = {
            'status': 'error',
            'error': self.__class__.__name__,
            'message': self.message,
            'statusCode': self.status_code,
        }
        if self.details:
            result['details'] = self.details
        return result
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class ValidationError(ApiError):
    """Validation error for invalid input."""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, List[str]]] = None):
        details = {'fieldErrors': field_errors} if field_errors else None
        super().__init__(message, 400, details)
        self.field_errors = field_errors


class AuthenticationError(ApiError):
    """Authentication error."""
    
    def __init__(self, message: str):
        super().__init__(message, 401)


class AuthorizationError(ApiError):
    """Authorization error (user authenticated but not authorized)."""
    
    def __init__(self, message: str):
        super().__init__(message, 403)


class NotFoundError(ApiError):
    """Resource not found error."""
    
    def __init__(self, message: str):
        super().__init__(message, 404)


class RateLimitError(ApiError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str, retry_after_seconds: Optional[int] = None):
        details = {'retryAfter': retry_after_seconds} if retry_after_seconds else None
        super().__init__(message, 429, details)
        self.retry_after_seconds = retry_after_seconds


class DatabaseError(ApiError):
    """Database operation error."""
    
    def __init__(self, message: str):
        super().__init__(message, 500)


class ExternalServiceError(ApiError):
    """External service error."""
    
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code)


class ServerError(ApiError):
    """Server error."""
    
    def __init__(self, message: str):
        super().__init__(message, 500)
