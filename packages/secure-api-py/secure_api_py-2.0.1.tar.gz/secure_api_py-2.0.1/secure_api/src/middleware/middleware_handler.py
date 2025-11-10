"""Middleware handler for SecureAPI."""

from typing import Callable, List, Awaitable


# Type definition for middleware functions
Middleware = Callable[['SecureAPI'], Awaitable[None]]


class MiddlewareHandler:
    """Handler for managing and executing middleware."""
    
    def __init__(self):
        """Initialize MiddlewareHandler."""
        self._middlewares: List[Middleware] = []
    
    def use(self, middleware: Middleware) -> None:
        """
        Add a middleware to the pipeline.
        
        Args:
            middleware: Middleware function to add
        """
        self._middlewares.append(middleware)
    
    async def execute(self, api: 'SecureAPI') -> None:
        """
        Execute all middlewares in sequence.
        
        Args:
            api: SecureAPI instance
        """
        for middleware in self._middlewares:
            await middleware(api)
