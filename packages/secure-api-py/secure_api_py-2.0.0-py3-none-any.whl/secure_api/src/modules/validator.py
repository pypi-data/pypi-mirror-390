"""Basic validator module for SecureAPI."""

from typing import Dict, List, Any, Optional


class Validator:
    """Basic validator for headers, query params, and body."""
    
    @staticmethod
    def validate_headers(
        headers: Dict[str, str],
        required_keys: List[str],
        match_values: Optional[List[str]] = None
    ) -> None:
        """
        Validate required headers.
        
        Args:
            headers: Request headers
            required_keys: List of required header keys
            match_values: Optional list of allowed values
            
        Raises:
            ValueError: If validation fails
        """
        for key in required_keys:
            if key not in headers or not headers[key]:
                raise ValueError(f'Missing or empty required header: {key}')
            
            if match_values and headers[key] not in match_values:
                raise ValueError(f'Invalid value for header: {key}')
    
    @staticmethod
    def validate_query_params(
        query_params: Dict[str, Any],
        required_keys: List[str]
    ) -> None:
        """
        Validate required query parameters.
        
        Args:
            query_params: Request query parameters
            required_keys: List of required parameter keys
            
        Raises:
            ValueError: If validation fails
        """
        for key in required_keys:
            if key not in query_params or not str(query_params[key]):
                raise ValueError(f'Missing or empty required query parameter: {key}')
    
    @staticmethod
    def validate_body(
        body: Dict[str, Any],
        required_keys: List[str]
    ) -> None:
        """
        Validate the request body against required keys.
        
        Args:
            body: Request body
            required_keys: List of required body keys
            
        Raises:
            ValueError: If validation fails
        """
        for key in required_keys:
            if key not in body or body[key] is None or str(body[key]) == '':
                raise ValueError(f'Missing or empty required body key: {key}')
