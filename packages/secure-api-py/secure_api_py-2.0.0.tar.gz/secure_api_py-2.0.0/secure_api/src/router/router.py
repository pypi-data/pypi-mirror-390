"""Router module for handling HTTP routes in Appwrite Functions."""

from typing import Callable, Awaitable, Dict, List, Optional, Tuple
import re


# Type definition for route handler functions
RouteHandler = Callable[['SecureAPI', Dict[str, str]], Awaitable]


class Router:
    """A simple router for handling HTTP routes in Appwrite Functions."""
    
    def __init__(self):
        """Initialize Router."""
        self._routes: List['Route'] = []
        self._named_routes: Dict[str, RouteHandler] = {}
    
    def route(
        self,
        method: str,
        path: str,
        handler: RouteHandler,
        name: Optional[str] = None
    ) -> None:
        """
        Add a route to the router.
        
        Args:
            method: HTTP method
            path: Route path (can include :param for parameters)
            handler: Handler function
            name: Optional route name
        """
        self._routes.append(Route(method, path, handler))
        if name:
            self._named_routes[name] = handler
    
    def get(self, path: str, handler: RouteHandler, name: Optional[str] = None) -> None:
        """Add a GET route."""
        self.route('GET', path, handler, name)
    
    def post(self, path: str, handler: RouteHandler, name: Optional[str] = None) -> None:
        """Add a POST route."""
        self.route('POST', path, handler, name)
    
    def put(self, path: str, handler: RouteHandler, name: Optional[str] = None) -> None:
        """Add a PUT route."""
        self.route('PUT', path, handler, name)
    
    def patch(self, path: str, handler: RouteHandler, name: Optional[str] = None) -> None:
        """Add a PATCH route."""
        self.route('PATCH', path, handler, name)
    
    def delete(self, path: str, handler: RouteHandler, name: Optional[str] = None) -> None:
        """Add a DELETE route."""
        self.route('DELETE', path, handler, name)
    
    async def handle(self, api: 'SecureAPI'):
        """
        Handle an incoming request.
        
        Args:
            api: SecureAPI instance
            
        Returns:
            Response from handler or 404 error
        """
        method = api.method
        path = api.path
        
        for route in self._routes:
            match = route.match(method, path)
            if match:
                # Add route params to context
                if match.params:
                    api.set_context('routeParams', match.params)
                
                # Execute handler with timing
                api.start_timer('route_handler')
                try:
                    result = await route.handler(api, match.params)
                    api.end_timer('route_handler')
                    return result
                except Exception as e:
                    api.end_timer('route_handler')
                    raise
        
        # No route matched
        return await api.send_error(
            message=f'Route not found: {method} {path}',
            status_code=404
        )
    
    def get_named_route(self, name: str) -> Optional[RouteHandler]:
        """
        Get a named route handler.
        
        Args:
            name: Route name
            
        Returns:
            Handler function or None
        """
        return self._named_routes.get(name)
    
    def list_routes(self) -> List[str]:
        """
        List all registered routes.
        
        Returns:
            List of route strings
        """
        return [f'{r.method} {r.path}' for r in self._routes]


class Route:
    """Represents a single route."""
    
    def __init__(self, method: str, path: str, handler: RouteHandler):
        """
        Initialize Route.
        
        Args:
            method: HTTP method
            path: Route path
            handler: Handler function
        """
        self.method = method
        self.path = path
        self.handler = handler
        self._segments = path.split('/')
        self._param_indices: List[int] = []
        self._param_names: List[str] = []
        
        # Identify parameter segments
        for i, segment in enumerate(self._segments):
            if segment.startswith(':'):
                self._param_indices.append(i)
                self._param_names.append(segment[1:])
    
    def match(self, method: str, path: str) -> Optional['RouteMatch']:
        """
        Check if this route matches the given method and path.
        
        Args:
            method: HTTP method
            path: Request path
            
        Returns:
            RouteMatch if matched, None otherwise
        """
        # Check method
        if self.method != method and self.method != '*':
            return None
        
        # Split the incoming path
        path_segments = path.split('/')
        
        # Check segment count
        if len(path_segments) != len(self._segments):
            return None
        
        # Extract parameters and check static segments
        params: Dict[str, str] = {}
        
        for i, segment in enumerate(self._segments):
            if i in self._param_indices:
                # This is a parameter segment
                param_index = self._param_indices.index(i)
                params[self._param_names[param_index]] = path_segments[i]
            else:
                # This is a static segment, must match exactly
                if segment != path_segments[i]:
                    return None
        
        return RouteMatch(params)


class RouteMatch:
    """Result of a successful route match."""
    
    def __init__(self, params: Dict[str, str]):
        """
        Initialize RouteMatch.
        
        Args:
            params: Route parameters
        """
        self.params = params
