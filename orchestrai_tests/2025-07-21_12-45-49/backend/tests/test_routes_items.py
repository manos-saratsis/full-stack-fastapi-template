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