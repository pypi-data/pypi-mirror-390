"""Basic example of using SecureAPI."""

from secure_api import SecureAPI, log_request


async def main(context):
    """
    Basic example showing core SecureAPI features.
    
    Args:
        context: Appwrite function context
    """
    # Initialize SecureAPI
    api = SecureAPI(context, database_id='YOUR_DATABASE_ID')
    
    # Add middleware
    api.use_middleware(log_request)
    
    try:
        # Execute middleware
        await api.execute_middleware()
        
        # Handle different HTTP methods
        if api.method == 'GET':
            return await api.send_success(
                message='Hello from SecureAPI!',
                data={
                    'path': api.path,
                    'method': api.method,
                    'authenticated': api.is_authenticated
                }
            )
        
        elif api.method == 'POST':
            # Access request body
            body = api.body_json
            
            return await api.send_success(
                message='Data received',
                data={'received': body}
            )
        
        else:
            return await api.send_error(
                message=f'Method {api.method} not supported',
                status_code=405
            )
    
    except Exception as e:
        api.error(f'Error occurred: {e}')
        return await api.handle_error(e)
