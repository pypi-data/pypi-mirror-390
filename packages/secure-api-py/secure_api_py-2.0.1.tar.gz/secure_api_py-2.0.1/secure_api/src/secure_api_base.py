"""Core SecureAPI class for building RESTful APIs in Appwrite Functions."""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from appwrite.client import Client
from .modules.database import DatabaseManager
from .middleware.middleware_handler import MiddlewareHandler, Middleware
from .errors.api_errors import ApiError
from .modules.enhanced_validator import EnhancedValidator


class SecureAPI:
    """Core API class for handling requests and responses in Appwrite Functions."""
    
    def __init__(self, context, database_id: Optional[str] = None):
        """
        Initialize SecureAPI.
        
        Args:
            context: Appwrite function context
            database_id: Optional default database ID
        """
        self.context = context
        self.database_id = database_id
        
        # Initialize Appwrite client
        self.client = Client()
        self.client.set_endpoint(os.environ.get('APPWRITE_FUNCTION_API_ENDPOINT', ''))
        self.client.set_project(os.environ.get('APPWRITE_FUNCTION_PROJECT_ID', ''))
        
        # Set API key from headers if available
        if 'x-appwrite-key' in self.headers:
            self.client.set_key(self.headers['x-appwrite-key'])
        
        # Initialize database manager
        self.db = DatabaseManager(self.client, database_id)
        
        # Initialize middleware handler
        self._middleware_handler = MiddlewareHandler()
        
        # Request context storage
        self._context_data: Dict[str, Any] = {}
        
        # Body JSON override
        self._body_json_override: Optional[Dict[str, Any]] = None
        
        # Performance timers
        self._timers: Dict[str, datetime] = {}
        self._timer_results: Dict[str, timedelta] = {}
    
    @property
    def db_helper(self) -> Optional[DatabaseManager]:
        """Backward compatibility getter for dbHelper."""
        return self.db if self.database_id else None
    
    def use_middleware(self, middleware: Middleware) -> None:
        """
        Add middleware to the pipeline.
        
        Args:
            middleware: Middleware function
        """
        self._middleware_handler.use(middleware)
    
    async def execute_middleware(self) -> None:
        """Execute all registered middleware."""
        await self._middleware_handler.execute(self)
    
    def log(self, message: Any) -> None:
        """
        Log a standard message to the console with proper formatting.
        
        Args:
            message: Message to log
        """
        if isinstance(message, (dict, list)):
            # Pretty print JSON objects/arrays
            formatted = self._format_json(message)
            self.context.log(formatted)
        elif isinstance(message, str):
            self.context.log(message)
        else:
            self.context.log(str(message))
    
    def error(self, error_message: Any) -> None:
        """
        Log an error to the console with proper formatting.
        
        Args:
            error_message: Error message to log
        """
        if isinstance(error_message, (dict, list)):
            # Pretty print JSON objects/arrays
            formatted = self._format_json(error_message)
            self.context.error(formatted)
        elif isinstance(error_message, str):
            self.context.error(error_message)
        else:
            self.context.error(str(error_message))
    
    def log_json(self, label: str, data: Any) -> None:
        """
        Log a JSON object with pretty formatting.
        
        Args:
            label: Label for the log entry
            data: Data to log
        """
        self.context.log(f'\n{label}:')
        if isinstance(data, (dict, list)):
            self.context.log(self._format_json(data))
        else:
            self.context.log(f'  {data}')
        self.context.log('')
    
    def _format_json(self, data: Any) -> str:
        """
        Helper method to format JSON with proper indentation.
        
        Args:
            data: Data to format
            
        Returns:
            Formatted JSON string
        """
        try:
            return json.dumps(data, indent=2)
        except Exception:
            return str(data)
    
    @property
    def method(self) -> str:
        """Parse the request method."""
        return self.context.req.method
    
    @property
    def headers(self) -> Dict[str, str]:
        """Parse headers from the request."""
        return dict(self.context.req.headers)
    
    @property
    def query_params(self) -> Dict[str, Any]:
        """Parse query parameters."""
        return self.context.req.query
    
    @property
    def body_text(self) -> str:
        """Parse the request body as text."""
        return self.context.req.body_text
    
    @property
    def body_json(self) -> Dict[str, Any]:
        """Parse the request body as JSON."""
        # Return override if set
        if self._body_json_override is not None:
            return self._body_json_override

        try:
            # Try Appwrite's built-in body_json property first
            if hasattr(self.context.req, 'body_json'):
                body_json = self.context.req.body_json
                if body_json is not None:
                    return body_json

            # Fall back to parsing body_text as JSON
            body_text = self.context.req.body_text
            if body_text:
                return json.loads(body_text)

            return {}
        except (json.JSONDecodeError, AttributeError, ValueError):
            # Return empty dict if JSON parsing fails
            return {}
    
    @body_json.setter
    def body_json(self, value: Dict[str, Any]) -> None:
        """Set the body JSON (overrides the context body)."""
        self._body_json_override = value
    
    async def send_success(
        self,
        status_code: int = 200,
        use_code_as_status: bool = False,
        message: str = 'Success',
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Send a success response.
        
        Args:
            status_code: HTTP status code
            use_code_as_status: Use status code as status field
            message: Success message
            data: Optional response data
            
        Returns:
            Response
        """
        return self.context.res.json({
            'status': status_code if use_code_as_status else 'success',
            'message': message,
            'data': data
        }, status_code)
    
    async def send_error(
        self,
        status_code: int = 500,
        use_code_as_status: bool = False,
        message: str = 'An error occurred'
    ):
        """
        Send an error response.
        
        Args:
            status_code: HTTP status code
            use_code_as_status: Use status code as status field
            message: Error message
            
        Returns:
            Response
        """
        return self.context.res.json({
            'status': status_code if use_code_as_status else 'error',
            'message': message
        }, status_code)
    
    async def send_unauthorized(
        self,
        use_code_as_status: bool = False,
        message: str = 'Unauthorized'
    ):
        """
        Send an unauthorized response.
        
        Args:
            use_code_as_status: Use status code as status field
            message: Error message
            
        Returns:
            Response
        """
        return await self.send_error(
            message=message,
            status_code=401,
            use_code_as_status=use_code_as_status
        )
    
    async def send_empty(self):
        """Send an empty response (204 No Content)."""
        return self.context.res.empty()
    
    async def send_redirect(self, url: str, status_code: int = 301):
        """
        Send a redirect response.
        
        Args:
            url: Redirect URL
            status_code: HTTP status code
            
        Returns:
            Response
        """
        return self.context.res.redirect(url, status_code)
    
    async def send_text(
        self,
        text: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Send a text response.
        
        Args:
            text: Text content
            status_code: HTTP status code
            headers: Optional headers
            
        Returns:
            Response
        """
        return self.context.res.text(text, status_code, headers or {})
    
    async def send_binary(
        self,
        bytes_data: bytes,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Send a binary response.
        
        Args:
            bytes_data: Binary data
            status_code: HTTP status code
            headers: Optional headers
            
        Returns:
            Response
        """
        return self.context.res.binary(bytes_data, status_code, headers or {})
    
    def get_env(self, key: str, default_value: Optional[str] = None) -> str:
        """
        Get an environment variable with optional default value.
        
        Args:
            key: Environment variable key
            default_value: Optional default value
            
        Returns:
            Environment variable value or default
        """
        return os.environ.get(key, default_value or '')
    
    def is_triggered_by(self, trigger_type: str) -> bool:
        """
        Check if the function was triggered by a specific trigger type.
        
        Args:
            trigger_type: Trigger type to check
            
        Returns:
            True if triggered by the specified type
        """
        return self.headers.get('x-appwrite-trigger') == trigger_type
    
    @property
    def user_id(self) -> Optional[str]:
        """Get the user ID if the function was invoked by an authenticated user."""
        return self.headers.get('x-appwrite-user-id')
    
    @property
    def user_jwt(self) -> Optional[str]:
        """Get the JWT token if available."""
        return self.headers.get('x-appwrite-user-jwt')
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the request is from an authenticated user."""
        user_id = self.user_id
        return user_id is not None and user_id != ''
    
    @property
    def trigger_type(self) -> Optional[str]:
        """Get the function execution trigger type (http, schedule, event)."""
        return self.headers.get('x-appwrite-trigger')
    
    @property
    def trigger_event(self) -> Optional[str]:
        """Get the event that triggered the function (if triggered by event)."""
        return self.headers.get('x-appwrite-event')
    
    @property
    def path(self) -> str:
        """Get request path."""
        return self.context.req.path
    
    @property
    def url(self) -> str:
        """Get request URL."""
        return self.context.req.url
    
    @property
    def host(self) -> str:
        """Get request host."""
        return self.context.req.host
    
    # ===== REQUEST CONTEXT STORAGE =====
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Set a value in the request context.
        
        Args:
            key: Context key
            value: Context value
        """
        self._context_data[key] = value
    
    def get_context(self, key: str) -> Any:
        """
        Get a value from the request context.
        
        Args:
            key: Context key
            
        Returns:
            Context value or None
        """
        return self._context_data.get(key)
    
    def has_context(self, key: str) -> bool:
        """
        Check if a context key exists.
        
        Args:
            key: Context key
            
        Returns:
            True if key exists
        """
        return key in self._context_data
    
    def clear_context(self) -> None:
        """Clear all context data."""
        self._context_data.clear()
    
    @property
    def context_data(self) -> Dict[str, Any]:
        """Get all context data (read-only)."""
        return dict(self._context_data)
    
    # ===== PERFORMANCE MONITORING =====
    
    def start_timer(self, name: str) -> None:
        """
        Start a performance timer.
        
        Args:
            name: Timer name
        """
        self._timers[name] = datetime.now()
    
    def end_timer(self, name: str) -> Optional[timedelta]:
        """
        End a performance timer and log the duration.
        
        Args:
            name: Timer name
            
        Returns:
            Duration or None if timer wasn't started
        """
        start_time = self._timers.get(name)
        if start_time is None:
            self.log(f'Timer "{name}" was not started')
            return None
        
        duration = datetime.now() - start_time
        self._timer_results[name] = duration
        del self._timers[name]
        
        self.log(f'Performance: {name} took {duration.total_seconds() * 1000:.2f}ms')
        return duration
    
    def get_timer_result(self, name: str) -> Optional[timedelta]:
        """
        Get the duration of a completed timer.
        
        Args:
            name: Timer name
            
        Returns:
            Duration or None
        """
        return self._timer_results.get(name)
    
    @property
    def timer_results(self) -> Dict[str, timedelta]:
        """Get all timer results (read-only)."""
        return dict(self._timer_results)
    
    def log_timer_summary(self) -> None:
        """Log a summary of all timers."""
        if not self._timer_results:
            self.log('No timers recorded')
            return
        
        self.log('===== Performance Summary =====')
        for name, duration in self._timer_results.items():
            self.log(f'{name}: {duration.total_seconds() * 1000:.2f}ms')
        
        total = sum((d.total_seconds() for d in self._timer_results.values()), 0.0)
        self.log(f'Total: {total * 1000:.2f}ms')
        self.log('==============================')
    
    # ===== VALIDATION HELPERS =====
    
    def validate_body(self, rules: Dict[str, str]) -> None:
        """
        Validate request body with validation rules.
        
        Args:
            rules: Dictionary of field names to rule strings
        """
        EnhancedValidator.validate_body(self.body_json, rules)
    
    def validate_custom(self, validators: Dict[str, Any]) -> None:
        """
        Validate with custom validators.
        
        Args:
            validators: Dictionary of field names to validator functions
        """
        EnhancedValidator.validate_custom(self.body_json, validators)
    
    # ===== ERROR HANDLING =====
    
    async def handle_error(self, error: Exception):
        """
        Handle API errors and return appropriate response.
        
        Args:
            error: Exception to handle
            
        Returns:
            Error response
        """
        if isinstance(error, ApiError):
            # Log the error
            self.error(f'{error.__class__.__name__}: {error.message}')
            
            # Return error response with proper status code
            return self.context.res.json(error.to_json(), error.status_code)
        
        # For unknown errors, log and return generic error
        self.error(f'Unhandled error: {error}')
        return await self.send_error(message='An unexpected error occurred')
