"""
Authentication API Endpoints
Handles user login, registration, and token verification
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
import os

from utils.auth_helper import (
    create_token,
    verify_token,
    validate_password,
    validate_email,
    validate_username,
    validate_username,
    AuthHelper
)
from utils.email_sender import EmailSender
import random

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


# Pydantic Models
class RegisterRequest(BaseModel):
    """User registration request model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")


class LoginRequest(BaseModel):
    """User login request model"""
    username_or_email: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class VerifyOtpRequest(BaseModel):
    """OTP Verification Request"""
    email: EmailStr
    otp: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User information response model"""
    id: int
    username: str
    email: str
    created_at: Optional[str] = None
    last_login: Optional[str] = None


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool


# Dependency to get user_manager (will be injected by main.py)
user_manager = None


def set_user_manager(um):
    """Set the user manager instance"""
    global user_manager
    user_manager = um


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    When AUTH_BYPASS=True in env, returns a guest user without token validation.
    """
    import os
    if os.getenv("AUTH_BYPASS", "False").lower() == "true":
        return {"user_id": 0, "username": "guest", "email": "guest@local"}

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


# Auth Endpoints

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """
    Register a new user
    
    Args:
        request: Registration request with username, email, password
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If validation fails or user already exists
    """
    if not user_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User manager not initialized"
        )
    
    # Sanitize inputs
    username = AuthHelper.sanitize_input(request.username)
    email = AuthHelper.sanitize_input(request.email)
    
    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Validate email
    is_valid, error = validate_email(email)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Validate password
    is_valid, error = validate_password(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Check if username already exists
    existing_user = user_manager.get_user_by_username(username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_user = user_manager.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Enforce Gmail
    if not email.endswith('@gmail.com'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is restricted to @gmail.com addresses only."
        )

    # Generate OTP
    otp_code = str(random.randint(100000, 999999))
    
    # Create user with OTP
    user_id = user_manager.create_user(username, email, request.password, verification_code=otp_code)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Get created user
    user = user_manager.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user"
        )
    
    # Send Verification Email (Async in production, sync here for simplicity or use BackgroundTasks)
    # Ideally use fastapi.BackgroundTasks
    email_sent = EmailSender.send_verification_email(email, otp_code)
    
    if not email_sent:
        logger.error(f"Failed to send OTP to {email}")
        # CRITICAL: Rollback - Delete the user since they can't verify
        user_manager.delete_user(user_id)
        logger.warning(f"Rolled back user creation for {username} due to email failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please check your email address or try again later."
        )
    
    logger.info(f"User registered successfully: {username}, Email sent: {email_sent}")
    
    # Return response - BUT DO NOT login yet. Require OTP.
    # We return a specific structure telling frontend to go to OTP page
    return {
        "access_token": "", # No token yet 
        "token_type": "bearer",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "message": "Registration successful. Please check your email for OTP."
        }
    }


def _load_admin_users() -> list:
    """Load admin users from local JSON file (not Oracle)."""
    import json
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'admin_users.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f).get('admins', [])
    except Exception:
        return []


def _authenticate_admin(username_or_email: str, password: str) -> dict | None:
    """Check credentials against local admin_users.json. Returns admin dict or None."""
    import bcrypt
    for admin in _load_admin_users():
        if admin['username'] == username_or_email or admin['email'] == username_or_email:
            try:
                if bcrypt.checkpw(password.encode(), admin['hashed_password'].encode()):
                    return {
                        'id': 0,
                        'username': admin['username'],
                        'email': admin['email'],
                        'role': 'admin'
                    }
            except Exception:
                pass
    return None


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Login user and return JWT token.
    Admin credentials are verified against local config/admin_users.json.
    Regular users are authenticated against the database.
    """
    # Sanitize input
    username_or_email = AuthHelper.sanitize_input(request.username_or_email)

    # 1. Check admin JSON first (independent of Oracle)
    admin = _authenticate_admin(username_or_email, request.password)
    if admin:
        token = create_token(admin)
        logger.info(f"Admin logged in: {admin['username']}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": admin['id'],
                "username": admin['username'],
                "email": admin['email'],
                "role": "admin"
            }
        }

    # 2. Fall back to database auth (Oracle / MySQL)
    if not user_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User manager not initialized"
        )

    user = user_manager.authenticate_user(username_or_email, request.password)

    if isinstance(user, dict) and user.get('error') == 'not_verified':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email.",
            headers={"X-Email-Not-Verified": "true"}
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Regular user — no role field in DB, default to 'user'
    user.setdefault('role', 'user')
    token = create_token(user)

    logger.info(f"User logged in successfully: {username_or_email}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user.get('role', 'user')
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Args:
        current_user: Current user from JWT token (injected by dependency)
        
    Returns:
        User information
    """
    if not user_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User manager not initialized"
        )
    
    user = user_manager.get_user_by_id(current_user['user_id'])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/verify-token", response_model=MessageResponse)
def verify_user_token(current_user: dict = Depends(get_current_user)):
    """
    Verify if token is valid
    
    Args:
        current_user: Current user from JWT token (injected by dependency)
        
    Returns:
        Success message
    """
    return {
        "message": "Token is valid",
        "success": True
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh JWT token (create new token with extended expiry)
    
    Args:
        current_user: Current user from JWT token (injected by dependency)
        
    Returns:
        New JWT token
    """
    if not user_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User manager not initialized"
        )
    
    # Get fresh user data
    user = user_manager.get_user_by_id(current_user['user_id'])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new token
    new_token = create_token(user)
    
    logger.info(f"Token refreshed for user: {user['username']}")
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email']
        }
    }


@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(request: VerifyOtpRequest):
    """
    Verify OTP code
    """
    if not user_manager:
        raise HTTPException(status_code=500, detail="User manager not initialized")
        
    is_valid = user_manager.verify_user_email(request.email, request.otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code"
        )
        
    return {"success": True, "message": "Email verified successfully. You can now login."}
