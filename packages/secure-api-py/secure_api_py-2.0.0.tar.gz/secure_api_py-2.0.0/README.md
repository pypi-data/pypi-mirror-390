# SecureAPI-Py - A Secure RESTful API Framework for Appwrite Functions

**`SecureAPI-Py`** is a lightweight, modular, and secure framework designed for building RESTful APIs in Appwrite Functions using Python. It provides a streamlined development experience with built-in utilities for request handling, validation, authentication, and database interactions.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Core Library](#core-library-secureapi)
  - [Utility Modules](#utility-modules)
  - [Middleware](#middleware)
  - [Real-World Example](#real-world-example)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Core Library**: Simplifies request/response handling, error management, and enhanced logging with pretty-print support.
- **Utility Modules**:
  - **Validator**: Ensures input integrity by validating headers, query parameters, and body content.
  - **Security**: Provides JWT validation and API key verification.
  - **DatabaseManager**: Facilitates CRUD operations on Appwrite databases with flexible database ID management.
- **Enhanced Logging**: Pretty-print JSON/dicts with proper formatting for better debugging.
- **Middleware Support**: Customize request processing with authentication, logging, CORS, and validation middleware.
- **Helper Properties**: Convenient properties for accessing Appwrite Function metadata, user info, and environment variables.
- **Response Types**: Support for all Appwrite Function response types (JSON, text, binary, redirect, empty).
- **Router**: Simple routing system for handling multiple endpoints.

## Installation

To use `SecureAPI-Py` in your Appwrite function, add it to your `requirements.txt` file:

```txt
secure-api-py>=1.0.0
appwrite>=7.0.0
```

Then, install the dependencies:

```bash
pip install -r requirements.txt
```

## Getting Started

### Core Library: `SecureAPI`

#### Usage

The `SecureAPI` class is your entry point to build APIs. It handles request processing and provides utility methods for standardized responses.

#### Example:

```python
from secure_api import SecureAPI

def main(context):
    # Option 1: Initialize with a default database ID
    api = SecureAPI(context, database_id='YOUR_DATABASE_ID')
    
    # Option 2: Initialize without default database ID (flexible approach)
    # api = SecureAPI(context)
    
    if api.context.req.path == '/tasks/create' and api.method == 'POST':
        # Add task creation logic here
        return api.send_success(message='Task created', data=task_doc)
```

### Utility Modules

#### Validator

Ensures your API receives valid input.

```python
from secure_api import Validator

async def input_validator(api):
    Validator.validate_headers(api.headers, ['x-api-key'])
    Validator.validate_query_params(api.query_params, ['type'])
    api.log('Input validation passed.')
```

#### Security

Handle authentication via JWTs or API keys.

```python
from secure_api import Security, auth_middleware

# Use built-in auth middleware
api.use_middleware(auth_middleware)

# Or create custom authentication
async def custom_auth(api):
    headers = api.headers
    
    if 'x-api-key' not in headers or not headers['x-api-key']:
        raise Exception('Missing `x-api-key` header.')
    
    jwt = headers['x-api-key']
    security = Security(api.client)
    
    try:
        is_authenticated = await security.validate_jwt(jwt)
        api.log(f'User authenticated: {is_authenticated}')
    except Exception as e:
        api.error(f'Authentication failed: {e}')
        raise Exception('Invalid or expired token.')
```

#### DatabaseManager

Simplifies CRUD operations for Appwrite collections with flexible database management.

```python
async def create_task(api):
    task_doc = await api.db.create_document(
        collection_id='tasks',
        data=task,
        database_id='YOUR_DATABASE_ID'
    )
    return await api.send_success(message='Task created', data=task_doc)
```

**Key Features:**
- **Flexible Database IDs**: Use different databases dynamically
- **Named Parameters**: Clean, readable function calls
- **Backward Compatibility**: Existing code continues to work via `api.db_helper` (deprecated)

### Enhanced Logging

The improved logging system now properly formats objects and dicts for better debugging:

```python
# Simple logging
api.log('Processing request...')

# Pretty-print JSON objects
api.log_json('User Data', {
    'id': '123',
    'name': 'John Doe',
    'permissions': ['read', 'write'],
})

# Automatic formatting for dicts/lists
api.log({
    'status': 'success',
    'count': 42,
    'items': ['item1', 'item2']
})
# Output will be properly indented JSON
```

### Helper Properties

SecureAPI includes convenient helper properties for common Appwrite Function patterns:

```python
# Request helpers
api.path           # Request path
api.url            # Full URL  
api.host           # Hostname
api.method         # HTTP method

# Authentication helpers
api.user_id         # User ID if authenticated
api.user_jwt        # JWT token if available
api.is_authenticated # Check if user is authenticated

# Function metadata
api.trigger_type    # How function was triggered (http, schedule, event)
api.trigger_event   # Event that triggered the function

# Environment variables with defaults
api.get_env('MY_VAR', default_value='default')
```

### Response Types

Support for all Appwrite Function response types:

```python
# JSON responses
await api.send_success(message='Success', data={...})
await api.send_error(message='Error', status_code=500)

# Other response types
await api.send_empty()                          # 204 No Content
await api.send_text('Plain text', status_code=200)
await api.send_redirect('https://example.com')  # 301 Redirect
await api.send_binary(bytes_data)               # Binary data
```

### Middleware

Middleware functions process requests before hitting route handlers:

#### Built-in Middleware

1. **CORS Middleware**:
```python
from secure_api import cors_middleware

api.use_middleware(cors_middleware(
    origin='*',
    methods='GET, POST, PUT, DELETE, OPTIONS',
    headers='Content-Type, Authorization',
))
```

2. **Logging Request Middleware** (with enhanced formatting):
```python
from secure_api import log_request

api.use_middleware(log_request)  # Now with pretty-print support!
```

3. **Authentication Middleware**:
```python
from secure_api import auth_middleware

api.use_middleware(auth_middleware)
```

4. **Rate Limiting Middleware**:
```python
from secure_api import rate_limit_middleware

api.use_middleware(rate_limit_middleware(
    max_requests=100,
    window_minutes=1
))
```

#### Adding Middleware (Order Matters!)

```python
api.use_middleware(cors_middleware())  # Handle CORS first
api.use_middleware(log_request)        # Then log requests
api.use_middleware(auth_middleware)    # Then check auth
```

### Router

Use the built-in router for handling multiple endpoints:

```python
from secure_api import SecureAPI, Router

async def main(context):
    api = SecureAPI(context, database_id='YOUR_DATABASE_ID')
    router = Router()
    
    # Define routes
    router.get('/tasks', list_tasks)
    router.post('/tasks', create_task)
    router.put('/tasks/:id', update_task)
    router.delete('/tasks/:id', delete_task)
    
    # Execute middleware
    await api.execute_middleware()
    
    # Handle request
    return await router.handle(api)

async def list_tasks(api, params):
    tasks = await api.db.list_documents(collection_id='tasks')
    return await api.send_success(message='Tasks retrieved', data={'tasks': tasks})

async def create_task(api, params):
    api.validate_body({'title': 'required|string', 'description': 'required|string'})
    task = {
        'title': api.body_json['title'],
        'description': api.body_json['description'],
        'completed': False,
    }
    task_doc = await api.db.create_document(collection_id='tasks', data=task)
    return await api.send_success(message='Task created', data=task_doc)

async def update_task(api, params):
    task_id = params['id']
    data = api.body_json
    task_doc = await api.db.update_document(
        collection_id='tasks',
        document_id=task_id,
        data=data
    )
    return await api.send_success(message='Task updated', data=task_doc)

async def delete_task(api, params):
    task_id = params['id']
    await api.db.delete_document(collection_id='tasks', document_id=task_id)
    return await api.send_success(message='Task deleted')
```

### Real-World Example: Task Management System

#### Endpoints

1. **Create Task**: `POST /tasks/create`
2. **List Tasks**: `GET /tasks/get`
3. **Update Task**: `PUT /tasks/update`
4. **Delete Task**: `DELETE /tasks/delete`

#### Example Implementation

```python
from secure_api import SecureAPI, log_request, auth_middleware, Validator

async def main(context):
    # Flexible initialization - can work with or without default database ID
    api = SecureAPI(context)
    
    # Middleware
    api.use_middleware(log_request)
    api.use_middleware(auth_middleware)
    
    # Handle requests
    try:
        await api.execute_middleware()
        path = api.context.req.path
        
        if path == '/tasks/create' and api.method == 'POST':
            return await create_task(api)
        elif path == '/tasks/get' and api.method == 'GET':
            return await list_tasks(api)
        elif path == '/tasks/update' and api.method == 'PUT':
            return await update_task(api)
        elif path == '/tasks/delete' and api.method == 'DELETE':
            return await delete_task(api)
        else:
            return await api.send_error(
                message='Endpoint not found',
                status_code=404,
            )
    except Exception as e:
        api.error(f'Error: {e}')
        return await api.handle_error(e)

async def create_task(api):
    Validator.validate_body(api.body_json, ['title', 'description'])
    task = {
        'title': api.body_json['title'],
        'description': api.body_json['description'],
        'completed': False,
    }
    
    task_doc = await api.db.create_document(
        collection_id='tasks',
        data=task,
        database_id='YOUR_DATABASE_ID'
    )
    return await api.send_success(message='Task created', data=task_doc)

async def list_tasks(api):
    tasks = await api.db.list_documents(
        collection_id='tasks',
        database_id='YOUR_DATABASE_ID'
    )
    return await api.send_success(message='Tasks retrieved', data={'tasks': tasks})
```

## Configuration

Configure your Appwrite function to use `SecureAPI-Py` by setting up the necessary environment variables and dependencies as described in the [Getting Started](#getting-started) section.

## API Reference

### SecureAPI Class

Main class for handling requests and responses.

**Methods:**
- `log(message)` - Log a message
- `error(message)` - Log an error
- `log_json(label, data)` - Log JSON with label
- `send_success(...)` - Send success response
- `send_error(...)` - Send error response
- `send_unauthorized(...)` - Send 401 response
- `send_empty()` - Send 204 response
- `send_redirect(url)` - Send redirect response
- `send_text(text)` - Send text response
- `send_binary(bytes)` - Send binary response
- `validate_body(rules)` - Validate request body
- `handle_error(error)` - Handle errors

**Properties:**
- `method` - HTTP method
- `headers` - Request headers
- `query_params` - Query parameters
- `body_text` - Request body as text
- `body_json` - Request body as JSON
- `path` - Request path
- `url` - Request URL
- `user_id` - Authenticated user ID
- `is_authenticated` - Authentication status

## Contributing

Contributions are welcome! Please submit pull requests or open issues for suggestions.

## License

This package is distributed under the BSD-3-Clause License.
