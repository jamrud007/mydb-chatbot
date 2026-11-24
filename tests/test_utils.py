
import pytest
from utils.auth_helper import AuthHelper

def test_validate_password_strength():
    """Test password strength validation"""
    # Weak passwords
    assert AuthHelper.validate_password("short")[0] == False
    assert AuthHelper.validate_password("nouppercase1!")[0] == False
    assert AuthHelper.validate_password("HOLOWERCASE1!")[0] == False
    assert AuthHelper.validate_password("NoDigit!")[0] == False
    assert AuthHelper.validate_password("NoSpecialChar1")[0] == False
    
    # Strong password
    is_valid, msg = AuthHelper.validate_password("StrongP@ssw0rd")
    assert is_valid == True
    assert msg == ""

def test_validate_email_format():
    """Test email format validation"""
    # Invalid emails
    assert AuthHelper.validate_email("invalid-email")[0] == False
    assert AuthHelper.validate_email("user@domain")[0] == False # Missing TLD
    assert AuthHelper.validate_email("@domain.com")[0] == False
    
    # Valid email
    is_valid, msg = AuthHelper.validate_email("user@example.com")
    assert is_valid == True
    assert msg == ""

def test_validate_username_format():
    """Test username format validation"""
    # Invalid usernames
    assert AuthHelper.validate_username("ab")[0] == False # Too short
    assert AuthHelper.validate_username("1startwithnumber")[0] == False
    assert AuthHelper.validate_username("invalid char$")[0] == False
    
    # Valid usernames
    assert AuthHelper.validate_username("valid_user")[0] == True
    assert AuthHelper.validate_username("valid-user-123")[0] == True

def test_sanitize_input():
    """Test input sanitization"""
    # SQL Injection attempt
    input_str = "users; DROP TABLE users; --"
    sanitized = AuthHelper.sanitize_input(input_str)
    assert sanitized == input_str.strip() # The base sanitizer just strips and removes null bytes currently
    
    # Null bytes
    input_with_null = "Hello\x00World"
    assert AuthHelper.sanitize_input(input_with_null) == "HelloWorld"
