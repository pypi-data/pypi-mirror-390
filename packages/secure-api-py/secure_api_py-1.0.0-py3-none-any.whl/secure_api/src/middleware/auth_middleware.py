"""Authentication middleware for SecureAPI."""

import os
from appwrite.client import Client
from ..modules.security import Security


async def auth_middleware(api: 'SecureAPI') -> None:
    """
    Authentication middleware that validates JWT tokens.
    
    Args:
        api: SecureAPI instance
        
    Raises:
        Exception: If authentication fails
    """
    headers = api.headers
    
    if 'x-appwrite-user-jwt' not in headers or not headers['x-appwrite-user-jwt']:
        raise Exception('Missing `x-appwrite-user-jwt` header.')
    
    jwt = headers['x-appwrite-user-jwt']
    
    client = Client()
    client.set_endpoint(os.environ.get('APPWRITE_FUNCTION_API_ENDPOINT', ''))
    client.set_project(os.environ.get('APPWRITE_FUNCTION_PROJECT_ID', ''))
    client.set_jwt(jwt)
    
    security = Security(client)
    
    try:
        is_valid = await security.validate_jwt(jwt)
        api.log(f'Authentication successful: {is_valid}')
    except Exception as e:
        api.error(f'Authentication failed: {e}')
        raise Exception('Invalid or expired token.')
