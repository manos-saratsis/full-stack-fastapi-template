```python
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.api.routes.login import router
from app.models import User
from app.core.security import create_access_token
from fastapi import FastAPI
from datetime import timedelta

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestLoginRoutes:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        user.hashed_password = "hashed_password"
        return user

    @patch('app.api.deps.get_db')
    @patch('app.crud.user.authenticate')
    @patch('app.core.security.create_access_token')
    def test_login_success(self, mock_create_token, mock_authenticate, mock_get_db, mock_user, mock_db):
        """Test successful login."""
        mock_get_db.return_value = mock_db
        mock_authenticate.return_value = mock_user
        mock_create_token.return_value = "access_token"
        
        login_data = {
            "username": "test@example.com",
            "password": "testpassword"
        }
        
        response = client.post("/login/access-token", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        mock_