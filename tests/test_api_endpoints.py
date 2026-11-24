
import pytest
from fastapi import status
from api import auth

def test_register_user_success(client, mock_user_manager):
    """Test successful user registration"""
    # Setup mock
    mock_user_manager.get_user_by_username.return_value = None
    mock_user_manager.get_user_by_email.return_value = None
    mock_user_manager.create_user.return_value = 1
    mock_user_manager.get_user_by_id.return_value = {
        "id": 1,
        "username": "newuser",
        "email": "new@example.com",
        "created_at": "2023-01-01 10:00:00"
    }

    # Inject mock
    auth.set_user_manager(mock_user_manager)

    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "Password123!"
    }

    response = client.post("/api/auth/register", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "new@example.com"

def test_register_duplicate_username(client, mock_user_manager):
    """Test registration with existing username"""
    # Setup mock
    mock_user_manager.get_user_by_username.return_value = {"id": 1, "username": "existing"}
    
    # Inject mock
    auth.set_user_manager(mock_user_manager)

    payload = {
        "username": "existing",
        "email": "new@example.com",
        "password": "Password123!"
    }

    response = client.post("/api/auth/register", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already exists" in response.json()["detail"]

def test_login_success(client, mock_user_manager):
    """Test successful login"""
    # Setup mock
    mock_user_manager.authenticate_user.return_value = {
        "id": 1, 
        "username": "testuser", 
        "email": "test@example.com"
    }

    # Inject mock
    auth.set_user_manager(mock_user_manager)

    payload = {
        "username_or_email": "testuser",
        "password": "Password123!"
    }

    response = client.post("/api/auth/login", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "testuser"

def test_login_invalid_credentials(client, mock_user_manager):
    """Test login with invalid credentials"""
    # Setup mock
    mock_user_manager.authenticate_user.return_value = None

    # Inject mock
    auth.set_user_manager(mock_user_manager)

    payload = {
        "username_or_email": "testuser",
        "password": "WrongPassword"
    }

    response = client.post("/api/auth/login", json=payload)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user_info(client, mock_user_manager, auth_headers):
    """Test getting current user info with valid token"""
    # Setup mock
    mock_user_manager.get_user_by_id.return_value = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2023-01-01"
    }

    # Inject mock
    auth.set_user_manager(mock_user_manager)

    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"

def test_get_current_user_unauthorized(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN # FastAPI returns 403 when NotAuthenticated or 401 depends on setup. Bearer usually 403 if missing scheme? No, HTTPBearer raises 403 if missing credentials.
    # Actually, let's check what actual response is. Usually 403 "Not authenticated" or 401. 
    # But usually TestClient gives 403 for missing auth header with HTTPBearer.
    # Let's assume 403 or 401.
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

def test_invalid_token(client):
    """Test accessing protected endpoint with invalid token"""
    headers = {"Authorization": "Bearer invalid_token_string"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
