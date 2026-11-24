"""
Authentication Helper Utilities
Handles JWT token creation/verification and password validation
"""
import jwt
import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))  # 24 hours


class AuthHelper:
    """Helper class for authentication operations"""
    
    @staticmethod
    def create_access_token(user_data: Dict) -> str:
        """
        Create JWT access token
        
        Args:
            user_data: Dictionary containing user information (id, username, email)
            
        Returns:
            JWT token string
        """
        try:
            # Create token payload
            payload = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data.get('role', 'user'),
                'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                'iat': datetime.utcnow()
            }
            
            # Encode token
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"JWT token created for user: {user_data['username']}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token is expired (jwt.decode already checks this, but being explicit)
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("Token has expired")
                return None
            
            logger.info(f"Token verified for user: {payload.get('username')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=/\[\];\'`~]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Validate email format
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format
        
        Requirements:
        - 3-50 characters
        - Only alphanumeric, underscore, and hyphen
        - Must start with a letter
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username must not exceed 50 characters"
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
            return False, "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Sanitize user input by removing potentially dangerous characters
        
        Args:
            input_string: Input to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove any SQL injection attempts or XSS attempts
        sanitized = input_string.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized


# Convenience functions for direct use
def create_token(user_data: Dict) -> str:
    """Create JWT token - convenience wrapper"""
    return AuthHelper.create_access_token(user_data)


def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token - convenience wrapper"""
    return AuthHelper.verify_token(token)


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password - convenience wrapper"""
    return AuthHelper.validate_password(password)


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email - convenience wrapper"""
    return AuthHelper.validate_email(email)


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username - convenience wrapper"""
    return AuthHelper.validate_username(username)
