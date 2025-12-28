"""
Security middleware for Sukh Mental Health API
Implements JWT validation, rate limiting, request logging, and monitoring
"""

import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import asyncio
from collections import defaultdict, deque

from config import settings


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class SecurityMiddleware:
    """Comprehensive security middleware for API protection"""
    
    def __init__(self):
        self.rate_limiter = EnhancedRateLimiter()
        self.request_logger = RequestLogger()
        self.security_monitor = SecurityMonitor()
    
    async def __call__(self, request: Request, call_next):
        """Main middleware function"""
        start_time = time.time()
        
        try:
            # 1. Log incoming request
            await self.request_logger.log_request(request)
            
            # 2. Validate request size and content type
            await self._validate_request(request)
            
            # 3. Apply rate limiting
            await self.rate_limiter.check_rate_limit(request)
            
            # 4. Validate JWT token for protected routes
            await self._validate_authentication(request)
            
            # 5. Monitor for security threats
            await self.security_monitor.analyze_request(request)
            
            # Process the request
            response = await call_next(request)
            
            # 6. Add security headers
            self._add_security_headers(response)
            
            # 7. Log response
            process_time = time.time() - start_time
            await self.request_logger.log_response(request, response, process_time)
            
            return response
            
        except HTTPException as e:
            # Log security violations
            await self.security_monitor.log_security_event(request, e)
            raise e
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Middleware error: {str(e)}\nFull traceback:\n{error_details}")
            print(f"🚨 MIDDLEWARE ERROR: {str(e)}")
            print(f"🚨 FULL TRACEBACK:\n{error_details}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    async def _validate_request(self, request: Request):
        """Validate request size and content type"""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            max_size = 1024 * 1024  # 1MB
            if int(content_length) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request too large. Maximum size: {max_size} bytes"
                )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            allowed_types = ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"]
            
            if content_type and not any(allowed_type in content_type for allowed_type in allowed_types):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Unsupported content type: {content_type}"
                )
    
    async def _validate_authentication(self, request: Request):
        """Skip authentication - no auth required"""
        # Set default user state for compatibility
        request.state.user = None
        request.state.authenticated = False
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Permitted-Cross-Domain-Policies": "none"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value


class EnhancedRateLimiter:
    """Enhanced rate limiter with per-user and per-IP limits"""
    
    def __init__(self):
        self.ip_requests: Dict[str, deque] = defaultdict(deque)
        self.user_requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self, request: Request):
        """Check and enforce rate limits"""
        try:
            from config import settings
            client_ip = self._get_client_ip(request)
            
            # Skip rate limiting for localhost in development
            if settings.is_development() and client_ip in ["127.0.0.1", "localhost", "::1"]:
                return
        except Exception as e:
            logger.warning(f"Config import error in rate limiter: {e}")
            # Continue with default behavior if config fails
            client_ip = self._get_client_ip(request)
        
        # Check if IP is temporarily blocked
        if await self._is_ip_blocked(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="IP temporarily blocked due to excessive requests"
            )
        
        # Apply IP-based rate limiting (more restrictive)
        await self._check_ip_rate_limit(client_ip, request)
        
        # Apply user-based rate limiting (if authenticated)
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'uid', None) or getattr(request.state.user, 'sub', None)
            if user_id:
                await self._check_user_rate_limit(user_id, request)
    
    async def _check_ip_rate_limit(self, ip: str, request: Request):
        """Check IP-based rate limits"""
        try:
            from config import settings
            is_dev = settings.is_development()
        except Exception as e:
            logger.warning(f"Config import error: {e}")
            is_dev = True  # Default to development mode if config fails
        
        # More relaxed limits for development
        if is_dev:
            endpoint_limits = {
                "/auth/": (50, 300),     # 50 requests per 5 minutes for auth (dev)
                "/chat": (200, 60),      # 200 requests per minute for chat (dev)
                "default": (1000, 60)    # 1000 requests per minute for other endpoints (dev)
            }
        else:
            # Production limits
            endpoint_limits = {
                "/auth/": (5, 300),      # 5 requests per 5 minutes for auth
                "/chat": (20, 60),       # 20 requests per minute for chat
                "default": (100, 60)     # 100 requests per minute for other endpoints
            }
        
        # Determine rate limit based on endpoint
        max_requests, window_seconds = endpoint_limits.get("default")
        for endpoint, limits in endpoint_limits.items():
            if endpoint in request.url.path:
                max_requests, window_seconds = limits
                break
        
        if not await self._is_allowed(f"ip:{ip}", max_requests, window_seconds, self.ip_requests):
            # Block IP temporarily if too many violations
            await self._maybe_block_ip(ip)
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for IP. Max {max_requests} requests per {window_seconds} seconds",
                headers=self._get_rate_limit_headers(f"ip:{ip}", max_requests, window_seconds)
            )
    
    async def _check_user_rate_limit(self, user_id: str, request: Request):
        """Check user-based rate limits"""
        try:
            from config import settings
            is_dev = settings.is_development()
        except Exception as e:
            logger.warning(f"Config import error: {e}")
            is_dev = True  # Default to development mode if config fails
        
        # More generous limits for authenticated users
        if is_dev:
            endpoint_limits = {
                "/chat": (300, 60),      # 300 requests per minute for chat (dev)
                "default": (2000, 60)    # 2000 requests per minute for other endpoints (dev)
            }
        else:
            # Production limits
            endpoint_limits = {
                "/chat": (30, 60),       # 30 requests per minute for chat
                "default": (200, 60)     # 200 requests per minute for other endpoints
            }
        
        max_requests, window_seconds = endpoint_limits.get("default")
        for endpoint, limits in endpoint_limits.items():
            if endpoint in request.url.path:
                max_requests, window_seconds = limits
                break
        
        if not await self._is_allowed(f"user:{user_id}", max_requests, window_seconds, self.user_requests):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for user. Max {max_requests} requests per {window_seconds} seconds",
                headers=self._get_rate_limit_headers(f"user:{user_id}", max_requests, window_seconds)
            )
    
    async def _is_allowed(self, identifier: str, max_requests: int, window_seconds: int, request_store: Dict) -> bool:
        """Check if request is allowed based on rate limits"""
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Get request history
            request_times = request_store[identifier]
            
            # Remove old requests
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Check if under limit
            if len(request_times) >= max_requests:
                return False
            
            # Add current request
            request_times.append(now)
            return True
    
    async def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                # Unblock expired IPs
                del self.blocked_ips[ip]
        return False
    
    async def _maybe_block_ip(self, ip: str):
        """Temporarily block IP if too many violations"""
        # Block for 15 minutes after rate limit violation
        self.blocked_ips[ip] = time.time() + 900
        logger.warning(f"Temporarily blocked IP {ip} due to rate limit violations")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, handling proxy headers"""
        # Check for forwarded IP (from load balancer/proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit_headers(self, identifier: str, max_requests: int, window_seconds: int) -> Dict[str, str]:
        """Get rate limit headers for response"""
        return {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Window": str(window_seconds),
            "X-RateLimit-Remaining": "0",
            "Retry-After": str(window_seconds)
        }


class RequestLogger:
    """Enhanced request logging for monitoring and debugging"""
    
    def __init__(self):
        self.logger = logging.getLogger("sukh.requests")
        self.logger.setLevel(logging.INFO)
    
    async def log_request(self, request: Request):
        """Log incoming request details"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "content_length": request.headers.get("content-length"),
            "content_type": request.headers.get("content-type")
        }
        
        self.logger.info(f"REQUEST: {json.dumps(log_data)}")
    
    async def log_response(self, request: Request, response: Response, process_time: float):
        """Log response details"""
        client_ip = self._get_client_ip(request)
        user_id = None
        
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'uid', None) or getattr(request.state.user, 'sub', None)
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "client_ip": client_ip,
            "user_id": user_id
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            self.logger.error(f"RESPONSE: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            self.logger.warning(f"RESPONSE: {json.dumps(log_data)}")
        else:
            self.logger.info(f"RESPONSE: {json.dumps(log_data)}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class SecurityMonitor:
    """Monitor for security threats and suspicious activity"""
    
    def __init__(self):
        self.logger = logging.getLogger("sukh.security")
        self.logger.setLevel(logging.WARNING)
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',  # XSS attempts
            r'union.*select',            # SQL injection
            r'drop.*table',              # SQL injection
            r'exec.*\(',                 # Code injection
            r'eval.*\(',                 # Code injection
        ]
    
    async def analyze_request(self, request: Request):
        """Analyze request for security threats"""
        # Check for suspicious patterns in URL
        path = request.url.path.lower()
        query = str(request.query_params).lower()
        
        for pattern in self.suspicious_patterns:
            import re
            if re.search(pattern, path + query, re.IGNORECASE):
                await self._log_security_threat(request, f"Suspicious pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Malicious request detected"
                )
        
        # Check for excessive header size
        total_header_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if total_header_size > 8192:  # 8KB limit
            await self._log_security_threat(request, "Excessive header size")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request headers too large"
            )
    
    async def log_security_event(self, request: Request, exception: HTTPException):
        """Log security-related events"""
        if exception.status_code in [401, 403, 429]:
            client_ip = self._get_client_ip(request)
            
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "security_violation",
                "status_code": exception.status_code,
                "detail": exception.detail,
                "client_ip": client_ip,
                "path": request.url.path,
                "method": request.method,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
            
            self.logger.warning(f"SECURITY_EVENT: {json.dumps(event_data)}")
    
    async def _log_security_threat(self, request: Request, threat_type: str):
        """Log detected security threats"""
        client_ip = self._get_client_ip(request)
        
        threat_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "threat_type": threat_type,
            "client_ip": client_ip,
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "query_params": str(request.query_params)
        }
        
        self.logger.error(f"SECURITY_THREAT: {json.dumps(threat_data)}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# Global middleware instance
security_middleware = SecurityMiddleware()