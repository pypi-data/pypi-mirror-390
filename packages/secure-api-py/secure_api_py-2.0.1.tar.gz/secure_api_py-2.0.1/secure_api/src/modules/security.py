"""Security module for JWT and API key validation."""

from appwrite.client import Client
from appwrite.services.account import Account


class Security:
    """Security utilities for JWT validation and API key verification."""
    
    def __init__(self, client: Client):
        """
        Initialize Security.
        
        Args:
            client: Appwrite client instance
        """
        self.client = client
    
    async def validate_jwt(self, jwt: str) -> bool:
        """
        Validate the JWT token and retrieve user details.
        
        Args:
            jwt: JWT token to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If JWT is invalid or expired
        """
        account = Account(self.client)
        try:
            await account.get()
            return True
        except Exception as e:
            raise ValueError(f'Invalid or expired JWT token: {e}')
    
    @staticmethod
    def validate_api_key(provided_key: str, expected_key: str) -> None:
        """
        Validate the API key.
        
        Args:
            provided_key: API key provided in request
            expected_key: Expected API key
            
        Raises:
            ValueError: If API key is invalid
        """
        if provided_key != expected_key:
            raise ValueError('Invalid API key.')
