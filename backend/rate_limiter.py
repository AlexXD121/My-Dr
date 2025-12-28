import time
from typing import Dict, Optional
from fastapi import HTTPException, Request, status
from collections import defaultdict, deque
import asyncio


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store request timestamps for each IP/user
        self.requests: Dict[str, deque] = defaultdict(deque)
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def is_allowed(
        self, 
        identifier: str, 
        max_requests: int = 60, 
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is allowed based on rate limits
        
        Args:
            identifier: IP address or user ID
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False otherwise
        """
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Get request history for this identifier
            request_times = self.requests[identifier]
            
            # Remove old requests outside the window
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Check if under limit
            if len(request_times) >= max_requests:
                return False
            
            # Add current request
            request_times.append(now)
            return True
    
    async def get_remaining_requests(
        self, 
        identifier: str, 
        max_requests: int = 60, 
        window_seconds: int = 60
    ) -> int:
        """Get number of remaining requests in current window"""
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds
            
            request_times = self.requests[identifier]
            
            # Remove old requests
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            return max(0, max_requests - len(request_times))
    
    async def get_reset_time(
        self, 
        identifier: str, 
        window_seconds: int = 60
    ) -> Optional[float]:
        """Get timestamp when rate limit resets"""
        async with self._lock:
            request_times = self.requests[identifier]
            if request_times:
                return request_times[0] + window_seconds
            return None


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(
    request: Request,
    max_requests: int = 60,
    window_seconds: int = 60,
    per_user: bool = False
):
    """
    Rate limiting middleware
    
    Args:
        request: FastAPI request object
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        per_user: If True, limit per authenticated user, otherwise per IP
    """
    # Get identifier (IP or user ID)
    if per_user and hasattr(request.state, 'user'):
        identifier = f"user:{request.state.user.uid}"
    else:
        # Get client IP (handle proxy headers)
        client_ip = request.headers.get("X-Forwarded-For")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        identifier = f"ip:{client_ip}"
    
    # Check rate limit
    if not await rate_limiter.is_allowed(identifier, max_requests, window_seconds):
        # Get reset time for headers
        reset_time = await rate_limiter.get_reset_time(identifier, window_seconds)
        
        headers = {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(reset_time)) if reset_time else str(int(time.time() + window_seconds))
        }
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers=headers
        )
    
    # Add rate limit headers to response
    remaining = await rate_limiter.get_remaining_requests(identifier, max_requests, window_seconds)
    reset_time = await rate_limiter.get_reset_time(identifier, window_seconds)
    
    # Store rate limit info in request state for response headers
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(reset_time)) if reset_time else str(int(time.time() + window_seconds))
    }


# Decorator for applying rate limits to specific endpoints
def rate_limit(max_requests: int = 60, window_seconds: int = 60, per_user: bool = False):
    """
    Decorator to apply rate limiting to FastAPI endpoints
    
    Usage:
        @app.post("/api/chat")
        @rate_limit(max_requests=10, window_seconds=60, per_user=True)
        async def chat_endpoint():
            pass
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            await rate_limit_middleware(request, max_requests, window_seconds, per_user)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator