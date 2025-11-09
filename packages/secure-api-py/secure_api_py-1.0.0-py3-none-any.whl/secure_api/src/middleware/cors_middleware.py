"""CORS middleware for SecureAPI."""

from typing import Optional


def cors_middleware(
    origin: str = '*',
    methods: str = 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
    headers: str = 'Content-Type, Authorization, X-Requested-With',
    credentials: str = 'true'
):
    """
    Create a CORS middleware with customizable options.
    
    Args:
        origin: Allowed origin
        methods: Allowed HTTP methods
        headers: Allowed headers
        credentials: Allow credentials
        
    Returns:
        Middleware function
    """
    async def middleware(api: 'SecureAPI') -> None:
        """CORS middleware function."""
        # Handle preflight OPTIONS request
        if api.method == 'OPTIONS':
            return api.context.res.text('', 204, {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': methods,
                'Access-Control-Allow-Headers': headers,
                'Access-Control-Allow-Credentials': credentials,
                'Access-Control-Max-Age': '86400',  # Cache preflight for 24 hours
            })
        
        # For other requests, CORS headers are handled by Appwrite Functions
        # This is mainly for documentation purposes
    
    return middleware
