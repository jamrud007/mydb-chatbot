"""
Pytest Fixtures
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database.db_connection import DatabaseConnection
from database.user_manager import UserManager
from config import Config
from utils.auth_helper import create_token

@pytest.fixture
def client():
    """FastAPI Test Client"""
    return TestClient(app)

@pytest.fixture
def test_user():
    """Create a test user dictionary"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

@pytest.fixture
def auth_headers(test_user):
    """Create valid auth headers"""
    token = create_token(test_user)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    mock_conn = MagicMock(spec=DatabaseConnection)
    mock_conn.get_connection.return_value = MagicMock()
    return mock_conn

@pytest.fixture
def mock_user_manager(mock_db_connection):
    """Mock user manager"""
    mock_mgr = MagicMock(spec=UserManager)
    mock_mgr.db_connection = mock_db_connection
    return mock_mgr
