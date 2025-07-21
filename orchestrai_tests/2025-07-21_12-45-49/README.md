# OrchestrAI Test Results for full-stack-fastapi-template

Generated on: 2025-07-21T12:45:50.740Z

## Test Strategy

I'll generate comprehensive unit tests for all supported technologies found in this full-stack FastAPI template repository. Based on the analysis, I need to create tests for Python (backend), TypeScript (frontend), and JavaScript files.

## PYTHON TESTS

=== FILE: backend/tests/test_deps.py ===
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.core.config import settings
from app.models import User
from app.core import security
import jwt


class TestGetDB:
    def test_get_db_yields_session(self):
        """Test that get_db yields a database session."""
        db_generator = deps.get_db()
        db_session = next(db_generator)
        assert isinstance(db_session, Session)
        
    def test_get_db_closes_session(self):
        """Test that get_db properly closes the session."""
        with patch('app.api.deps.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            
            db_generator = deps.get_db()
            next(db_generator)
            
            try:
                next(db_generator)
            except StopIteration:
                pass
                
            mock_session.close.assert_called_once()


class TestGetCurrentUser:
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def valid_token(self):
        return "valid_jwt_token"
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        return user

    def test_get_current_user_success(self, mock_db, valid_token, mock_user):
        """Test successful user retrieval with valid token."""
        with patch('app.core.security.decode_token') as mock_decode, \
             patch('app.crud.user.get') as mock_get_user:
            
            mock_decode.return_value = {"sub": "1"}
            mock_get_user.return_value = mock_user
            
            result = deps.get_current_user(db=mock_db, token=valid_token)
            
            assert result == mock_user
            mock_decode.assert_called_once_with(valid_token)
            mock_get_user.assert_called_once_with(mock_db, id=1)

    def test_get_current_user_invalid_token(self, mock_db):
        """Test user retrieval with invalid token."""
        with patch('app.core.security.decode_token') as mock_decode:
            mock_decode.side_effect = jwt.PyJWTError()
            
            with pytest.raises(HTTPException) as exc_info:
                deps.get_current_user(db=mock_db, token="invalid_token")
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_not_found(self, mock_db, valid_token):
        """Test user retrieval when user doesn't exist."""
        with patch('app.core.security.decode_token') as mock_decode, \
             patch('app.crud.user.get') as mock_get_user:
            
            mock_decode.return_value = {"sub": "999"}
            mock_get_user.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                deps.get_current_user(db=mock_db, token=valid_token)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_current_user_inactive(self, mock_db, valid_token):
        """Test user retrieval with inactive user."""
        inactive_user = Mock(spec=User)
        inactive_user.is_active = False
        
        with patch('app.core.security.decode_token') as mock_decode, \
             patch('app.crud.user.get') as mock_get_user:
            
            mock_decode.return_value = {"sub": "1"}
            mock_get_user.return_value = inactive_user
            
            with pytest.raises(HTTPException) as exc_info:
                deps.get_current_user(db=mock_db, token=valid_token)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetCurrentActiveUser:
    def test_get_current_active_user_success(self):
        """Test getting active user."""
        mock_user = Mock(spec=User)
        mock_user.is_active = True
        
        result = deps.get_current_active_user(current_user=mock_user)
        assert result == mock_user

    def test_get_current_active_user_inactive(self):
        """Test getting inactive user raises exception."""
        mock_user = Mock(spec=User)
        mock_user.is_active = False
        
        with pytest.raises(HTTPException) as exc_info:
            deps.get_current_active_user(current_user=mock_user)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestGetCurrentActiveSuperuser:
    def test_get_current_active_superuser_success(self):
        """Test getting active superuser."""
        mock_user = Mock(spec=User)
        mock_user.is_active = True
        mock_user.is_superuser = True
        
        result = deps.get_current_active_superuser(current_user=mock_user)
        assert result == mock_user

    def test_get_current_active_superuser_not_superuser(self):
        """Test getting non-superuser raises exception."""
        mock_user = Mock(spec=User)
        mock_user.is_active = True
        mock_user.is_superuser = False
        
        with pytest.raises(HTTPException) as exc_info:
            deps.get_current_active_superuser(current_user=mock_user)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
```
=== END FILE ===

=== FILE: backend/tests/test_routes_items.py ===
```python
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.api.routes.items import router
from app.models import User, Item
from app.schemas import ItemCreate, ItemUpdate
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestItemsRoutes:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def mock_superuser(self):
        user = Mock(spec=User)
        user.id = 1
        user.email = "admin@example.com"
        user.is_active = True
        user.is_superuser = True
        return user
    
    @pytest.fixture
    def mock_item(self):
        item = Mock(spec=Item)
        item.id = 1
        item.title = "Test Item"
        item.description = "Test Description"
        item.owner_id = 1
        return item

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.get_multi')
    def test_read_items_success(self, mock_get_multi, mock_get_user, mock_get_db, mock_user, mock_db):
        """Test successful retrieval of items."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_get_multi.return_value = []
        
        response = client.get("/items/", headers={"Authorization": "Bearer token"})
        
        assert response.status_code == status.HTTP_200_OK
        mock_get_multi.assert_called_once()

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.create_with_owner')
    def test_create_item_success(self, mock_create, mock_get_user, mock_get_db, mock_user, mock_db, mock_item):
        """Test successful item creation."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_create.return_value = mock_item
        
        item_data = {
            "title": "New Item",
            "description": "New Description"
        }
        
        response = client.post(
            "/items/",
            json=item_data,
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_create.assert_called_once()

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.get')
    def test_read_item_success(self, mock_get, mock_get_user, mock_get_db, mock_user, mock_db, mock_item):
        """Test successful retrieval of single item."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_get.return_value = mock_item
        
        response = client.get("/items/1", headers={"Authorization": "Bearer token"})
        
        assert response.status_code == status.HTTP_200_OK
        mock_get.assert_called_once_with(mock_db, id=1)

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.get')
    def test_read_item_not_found(self, mock_get, mock_get_user, mock_get_db, mock_user, mock_db):
        """Test item not found."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_get.return_value = None
        
        response = client.get("/items/999", headers={"Authorization": "Bearer token"})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.get')
    @patch('app.crud.item.update')
    def test_update_item_success(self, mock_update, mock_get, mock_get_user, mock_get_db, mock_user, mock_db, mock_item):
        """Test successful item update."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_get.return_value = mock_item
        mock_update.return_value = mock_item
        
        update_data = {
            "title": "Updated Item",
            "description": "Updated Description"
        }
        
        response = client.put(
            "/items/1",
            json=update_data,
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_update.assert_called_once()

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.get')
    @patch('app.crud.item.remove')
    def test_delete_item_success(self, mock_remove, mock_get, mock_get_user, mock_get_db, mock_user, mock_db, mock_item):
        """Test successful item deletion."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_get.return_value = mock_item
        mock_remove.return_value = mock_item
        
        response = client.delete("/items/1", headers={"Authorization": "Bearer token"})
        
        assert response.status_code == status.HTTP_200_OK
        mock_remove.assert_called_once_with(mock_db, id=1)

    @patch('app.api.deps.get_db')
    @patch('app.api.deps.get_current_active_user')
    @patch('app.crud.item.get')
    def test_update_item_permission_denied(self, mock_get, mock_get_user, mock_get_db, mock_user, mock_db):
        """Test item update with insufficient permissions."""
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        
        # Item owned by different user
        other_item = Mock(spec=Item)
        other_item.id = 1
        other_item.owner_id = 999
        mock_get.return_value = other_item
        
        update_data = {"title": "Updated Item"}
        
        response = client.put(
            "/items/1",
            json=update_data,
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
```
=== END FILE ===

=== FILE: backend/tests/test_routes_login.py ===
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