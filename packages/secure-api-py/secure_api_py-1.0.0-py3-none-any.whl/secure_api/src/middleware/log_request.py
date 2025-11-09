"""Request logging middleware for SecureAPI."""

import json


async def log_request(api: 'SecureAPI') -> None:
    """
    Middleware that logs request information with pretty formatting.
    
    Args:
        api: SecureAPI instance
    """
    api.log('========== REQUEST LOG ==========')
    api.log(f'Method: {api.method}')
    api.log(f'Path: {api.context.req.path}')
    
    # Log headers with proper formatting
    api.log_json('Headers', api.headers)
    
    # Log query parameters with proper formatting
    if api.query_params:
        api.log_json('Query Parameters', api.query_params)
    
    # Log body - try to parse as JSON for pretty printing
    if api.body_text:
        try:
            body_json = api.body_json
            if body_json:
                api.log_json('Request Body (JSON)', body_json)
            else:
                api.log(f'Request Body (Text): {api.body_text}')
        except Exception:
            api.log(f'Request Body (Raw): {api.body_text}')
    
    api.log('=================================')
