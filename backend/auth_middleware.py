"""
Firebase Authentication Middleware for FastAPI
Handles JWT token validation and user context injection
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps

from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy.orm import Session

from database import get_db
from models import User

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials"""
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        print("✅ Firebase Admin SDK already initialized")
        return True
    except ValueError:
        # Firebase not initialized, initialize it
        try:
            # Try to get service account from environment variable
            service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            
            if service_account_json:
                # Parse JSON from environment variable
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK initialized with service account")
                return True
            else:
                # Try to load from file
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase Admin SDK initialized with service account file")
                    return True
                else:
                    # For development, initialize with project ID only
                    project_id = os.getenv('FIREBASE_PROJECT_ID', 'mydoc-e3824')
                    firebase_admin.initialize_app(options={'projectId': project_id})
                    print(f"✅ Firebase Admin SDK initialized with project ID: {project_id}")
                    print("⚠️ Note: Service account not configured. Some features may be limited.")
                    return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Firebase Admin SDK: {e}")
            print("⚠️ Authentication features will be disabled")
            return False

# Initialize Firebase on module import
FIREBASE_INITIALIZED = initialize_firebase()

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

class AuthenticationError(Exception):
    """Custom authentication error"""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticatedUser:
    """Represents an authenticated user"""
    def __init__(self, firebase_uid: str, email: str, email_verified: bool, 
                 display_name: Optional[str] = None, photo_url: Optional[str] = None,
                 custom_claims: Optional[Dict[str, Any]] = None):
        self.firebase_uid = firebase_uid
        self.email = email
        self.email_verified = email_verified
        self.display_name = display_name
        self.photo_url = photo_url
        self.custom_claims = custom_claims or {}
        self.is_admin = custom_claims.get('admin', False) if custom_claims else False
        self.roles = custom_claims.get('roles', []) if custom_claims else []

async def verify_firebase_token(token: str) -> AuthenticatedUser:
    """
    Verify Firebase ID token and return user information
    """
    if not FIREBASE_INITIALIZED:
        raise AuthenticationError("Firebase authentication not available", 503)
    
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)
        
        # Extract user information
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        email_verified = decoded_token.get('email_verified', False)
        display_name = decoded_token.get('name')
        photo_url = decoded_token.get('picture')
        
        # Get custom claims
        custom_claims = decoded_token.get('custom_claims', {})
        
        if not email:
            raise AuthenticationError("Email not found in token")
        
        return AuthenticatedUser(
            firebase_uid=firebase_uid,
            email=email,
            email_verified=email_verified,
            display_name=display_name,
            photo_url=photo_url,
            custom_claims=custom_claims
        )
        
    except auth.InvalidIdTokenError:
        raise AuthenticationError("Invalid authentication token")
    except auth.ExpiredIdTokenError:
        raise AuthenticationError("Authentication token has expired")
    except auth.RevokedIdTokenError:
        raise AuthenticationError("Authentication token has been revoked")
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        raise AuthenticationError("Authentication failed")

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from database
    Returns None if no authentication provided (for optional auth)
    """
    if not credentials:
        return None
    
    try:
        # Verify Firebase token
        auth_user = await verify_firebase_token(credentials.credentials)
        
        # Get or create user in database
        user = db.query(User).filter(User.firebase_uid == auth_user.firebase_uid).first()
        
        if not user:
            # Create new user
            user = User(
                firebase_uid=auth_user.firebase_uid,
                email=auth_user.email,
                display_name=auth_user.display_name,
                email_verified=auth_user.email_verified,
                photo_url=auth_user.photo_url,
                is_active=True,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created new user: {user.email}")
        else:
            # Update last login and user info
            user.last_login = datetime.utcnow()
            user.email_verified = auth_user.email_verified
            if auth_user.display_name:
                user.display_name = auth_user.display_name
            if auth_user.photo_url:
                user.photo_url = auth_user.photo_url
            db.commit()
        
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        print(f"❌ User retrieval error: {e}")
        raise AuthenticationError("Failed to retrieve user information")

async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Require authentication - raises HTTPException if not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = await get_current_user(credentials, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_verified_email(
    user: User = Depends(require_auth)
) -> User:
    """
    Require authenticated user with verified email
    """
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return user

async def require_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Require admin authentication
    """
    user = await require_auth(credentials, db)
    
    try:
        # Verify admin status from Firebase custom claims
        auth_user = await verify_firebase_token(credentials.credentials)
        if not auth_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

def optional_auth(func):
    """
    Decorator for endpoints that support optional authentication
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract current_user from kwargs if present
        current_user = kwargs.get('current_user')
        
        # If no user provided, continue without authentication
        if current_user is None:
            kwargs['current_user'] = None
        
        return await func(*args, **kwargs)
    
    return wrapper

class RateLimiter:
    """
    Simple rate limiter for authenticated users
    """
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = timedelta(minutes=15)
        self.last_cleanup = datetime.utcnow()
    
    def is_allowed(self, user_id: str, max_requests: int = 100, window_minutes: int = 15) -> bool:
        """
        Check if user is within rate limit
        """
        now = datetime.utcnow()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(now, window_minutes)
            self.last_cleanup = now
        
        # Get user's request history
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        user_requests = self.requests[user_id]
        
        # Remove old requests outside the window
        window_start = now - timedelta(minutes=window_minutes)
        user_requests[:] = [req_time for req_time in user_requests if req_time > window_start]
        
        # Check if under limit
        if len(user_requests) >= max_requests:
            return False
        
        # Add current request
        user_requests.append(now)
        return True
    
    def _cleanup_old_entries(self, now: datetime, window_minutes: int):
        """Clean up old rate limit entries"""
        window_start = now - timedelta(minutes=window_minutes)
        
        for user_id in list(self.requests.keys()):
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id] 
                if req_time > window_start
            ]
            
            # Remove empty entries
            if not self.requests[user_id]:
                del self.requests[user_id]

# Global rate limiter instance
rate_limiter = RateLimiter()

async def check_rate_limit(
    request: Request,
    user: Optional[User] = Depends(get_current_user)
):
    """
    Check rate limit for authenticated users
    """
    if user:
        user_id = user.firebase_uid
        if not rate_limiter.is_allowed(user_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
    
    return True

# Middleware for request logging and security
async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware for logging and security
    """
    start_time = datetime.utcnow()
    
    # Log request
    print(f"🔐 {request.method} {request.url.path} - {request.client.host if request.client else 'unknown'}")
    
    # Add security headers
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Log response time
    duration = (datetime.utcnow() - start_time).total_seconds()
    print(f"✅ {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    return response

# Helper functions for custom claims management
async def set_user_claims(firebase_uid: str, claims: Dict[str, Any]):
    """
    Set custom claims for a user (admin only)
    """
    if not FIREBASE_INITIALIZED:
        raise AuthenticationError("Firebase authentication not available", 503)
    
    try:
        auth.set_custom_user_claims(firebase_uid, claims)
        print(f"✅ Set custom claims for user {firebase_uid}: {claims}")
    except Exception as e:
        print(f"❌ Failed to set custom claims: {e}")
        raise AuthenticationError("Failed to set user permissions")

async def revoke_user_tokens(firebase_uid: str):
    """
    Revoke all tokens for a user (admin only)
    """
    if not FIREBASE_INITIALIZED:
        raise AuthenticationError("Firebase authentication not available", 503)
    
    try:
        auth.revoke_refresh_tokens(firebase_uid)
        print(f"✅ Revoked tokens for user {firebase_uid}")
    except Exception as e:
        print(f"❌ Failed to revoke tokens: {e}")
        raise AuthenticationError("Failed to revoke user tokens")