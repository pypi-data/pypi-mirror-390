"""SecureAPI - A Secure RESTful API Framework for Appwrite Functions (Python)."""

from .src.secure_api_base import SecureAPI
from .src.middleware.middleware_handler import Middleware
from .src.middleware.auth_middleware import auth_middleware
from .src.middleware.cors_middleware import cors_middleware
from .src.middleware.rate_limit import rate_limit_middleware
from .src.middleware.log_request import log_request
from .src.modules.database import DatabaseManager, BatchResult, BatchError
from .src.modules.security import Security
from .src.modules.validator import Validator
from .src.modules.enhanced_validator import EnhancedValidator
from .src.router.router import Router, RouteHandler
from .src.errors.api_errors import (
    ApiError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    DatabaseError,
    ExternalServiceError,
    ServerError
)

__version__ = '1.0.0'

__all__ = [
    'SecureAPI',
    'Middleware',
    'auth_middleware',
    'cors_middleware',
    'rate_limit_middleware',
    'log_request',
    'DatabaseManager',
    'BatchResult',
    'BatchError',
    'Security',
    'Validator',
    'EnhancedValidator',
    'Router',
    'RouteHandler',
    'ApiError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'RateLimitError',
    'DatabaseError',
    'ExternalServiceError',
    'ServerError',
]
