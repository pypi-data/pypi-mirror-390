"""Advanced example with router, middleware, and validation."""

from secure_api import (
    SecureAPI,
    Router,
    log_request,
    auth_middleware,
    cors_middleware,
    rate_limit_middleware,
    Validator,
    ValidationError
)


async def main(context):
    """
    Advanced example showing router, middleware, and validation.
    
    Args:
        context: Appwrite function context
    """
    # Initialize SecureAPI with database
    api = SecureAPI(context, database_id='YOUR_DATABASE_ID')
    
    # Add middleware (order matters!)
    api.use_middleware(cors_middleware(origin='*'))
    api.use_middleware(log_request)
    api.use_middleware(rate_limit_middleware(max_requests=100, window_minutes=1))
    # Uncomment to enable authentication
    # api.use_middleware(auth_middleware)
    
    # Create router
    router = Router()
    
    # Define routes
    router.get('/tasks', list_tasks, name='list_tasks')
    router.post('/tasks', create_task, name='create_task')
    router.get('/tasks/:id', get_task, name='get_task')
    router.put('/tasks/:id', update_task, name='update_task')
    router.delete('/tasks/:id', delete_task, name='delete_task')
    
    try:
        # Execute middleware
        await api.execute_middleware()
        
        # Handle request with router
        return await router.handle(api)
    
    except ValidationError as e:
        api.error(f'Validation error: {e}')
        return await api.handle_error(e)
    
    except Exception as e:
        api.error(f'Error occurred: {e}')
        return await api.handle_error(e)


async def list_tasks(api, params):
    """List all tasks."""
    api.start_timer('list_tasks')
    
    try:
        # Get query parameters
        limit = api.query_params.get('limit', 10)
        
        # List documents from database
        tasks = await api.db.list_documents(
            collection_id='tasks',
            queries=[f'limit({limit})']
        )
        
        api.end_timer('list_tasks')
        
        return await api.send_success(
            message='Tasks retrieved successfully',
            data={
                'tasks': tasks.get('documents', []),
                'total': tasks.get('total', 0)
            }
        )
    
    except Exception as e:
        api.end_timer('list_tasks')
        raise


async def create_task(api, params):
    """Create a new task."""
    api.start_timer('create_task')
    
    try:
        # Validate request body
        api.validate_body({
            'title': 'required|string|min:3|max:100',
            'description': 'required|string|min:10',
            'priority': 'in:low,medium,high',
            'due_date': 'string'  # Optional field
        })
        
        # Create task data
        task_data = {
            'title': api.body_json['title'],
            'description': api.body_json['description'],
            'priority': api.body_json.get('priority', 'medium'),
            'completed': False,
            'created_at': api.body_json.get('created_at'),
            'due_date': api.body_json.get('due_date')
        }
        
        # Create document
        task = await api.db.create_document(
            collection_id='tasks',
            data=task_data
        )
        
        api.end_timer('create_task')
        api.log(f'Task created: {task.get("$id")}')
        
        return await api.send_success(
            message='Task created successfully',
            data={'task': task},
            status_code=201
        )
    
    except Exception as e:
        api.end_timer('create_task')
        raise


async def get_task(api, params):
    """Get a specific task by ID."""
    task_id = params['id']
    
    try:
        task = await api.db.get_document(
            collection_id='tasks',
            document_id=task_id
        )
        
        return await api.send_success(
            message='Task retrieved successfully',
            data={'task': task}
        )
    
    except Exception as e:
        api.error(f'Task not found: {task_id}')
        return await api.send_error(
            message=f'Task with ID {task_id} not found',
            status_code=404
        )


async def update_task(api, params):
    """Update a task."""
    task_id = params['id']
    
    try:
        # Validate at least one field is provided
        if not api.body_json:
            raise ValidationError('No update data provided')
        
        # Update document
        task = await api.db.update_document(
            collection_id='tasks',
            document_id=task_id,
            data=api.body_json
        )
        
        api.log(f'Task updated: {task_id}')
        
        return await api.send_success(
            message='Task updated successfully',
            data={'task': task}
        )
    
    except Exception as e:
        api.error(f'Failed to update task: {task_id}')
        raise


async def delete_task(api, params):
    """Delete a task."""
    task_id = params['id']
    
    try:
        await api.db.delete_document(
            collection_id='tasks',
            document_id=task_id
        )
        
        api.log(f'Task deleted: {task_id}')
        
        return await api.send_success(
            message='Task deleted successfully',
            data={'deleted_id': task_id}
        )
    
    except Exception as e:
        api.error(f'Failed to delete task: {task_id}')
        raise
