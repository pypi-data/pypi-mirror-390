"""Rate limiting middleware for SecureAPI."""

from datetime import datetime, timedelta
from typing import Dict, Optional
from ..errors.api_errors import RateLimitError


class RateLimitEntry:
    """Rate limit entry for tracking requests."""
    
    def __init__(self, window_start: datetime, count: int):
        self.window_start = window_start
        self.count = count


def rate_limit_middleware(
    max_requests: int = 100,
    window_minutes: int = 1,
    key_extractor: Optional[str] = None
):
    """
    Create a rate limiting middleware.
    
    Args:
        max_requests: Maximum requests allowed in the window
        window_minutes: Time window in minutes
        key_extractor: Optional custom key for rate limiting
        
    Returns:
        Middleware function
    """
    # In-memory storage for rate limit tracking
    store: Dict[str, RateLimitEntry] = {}
    
    def get_key(api: 'SecureAPI', custom_extractor: Optional[str]) -> str:
        """Extract a key to identify the client."""
        if custom_extractor:
            return custom_extractor
        
        # Try to use user ID if authenticated
        if api.is_authenticated and api.user_id:
            return f'user:{api.user_id}'
        
        # Try to use IP address from headers
        ip = (api.headers.get('x-forwarded-for') or
              api.headers.get('x-real-ip') or
              api.headers.get('remote-addr') or
              'unknown')
        
        return f'ip:{ip}'
    
    def cleanup_old_entries(store: Dict[str, RateLimitEntry], window_minutes: int) -> None:
        """Clean up old entries to prevent memory leak."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=window_minutes * 2)
        
        keys_to_remove = [
            key for key, entry in store.items()
            if entry.window_start < cutoff
        ]
        for key in keys_to_remove:
            del store[key]
    
    async def middleware(api: 'SecureAPI') -> None:
        """Rate limiting middleware function."""
        # Generate a key for this client
        key = get_key(api, key_extractor)
        
        # Get or create rate limit entry
        now = datetime.now()
        entry = store.get(key)
        
        if entry is None or (now - entry.window_start).total_seconds() >= window_minutes * 60:
            # Create new window
            entry = RateLimitEntry(window_start=now, count=1)
            store[key] = entry
            
            # Clean up old entries
            cleanup_old_entries(store, window_minutes)
        else:
            # Increment count in current window
            entry.count += 1
            
            # Check if limit exceeded
            if entry.count > max_requests:
                reset_time = entry.window_start + timedelta(minutes=window_minutes)
                seconds_until_reset = int((reset_time - now).total_seconds())
                
                raise RateLimitError(
                    f'Rate limit exceeded. Max {max_requests} requests per {window_minutes} minute(s)',
                    retry_after_seconds=max(seconds_until_reset, 1)
                )
        
        # Add rate limit headers to context
        api.set_context('rateLimit', {
            'limit': max_requests,
            'remaining': max_requests - entry.count,
            'reset': int((entry.window_start + timedelta(minutes=window_minutes)).timestamp() * 1000)
        })
    
    return middleware
