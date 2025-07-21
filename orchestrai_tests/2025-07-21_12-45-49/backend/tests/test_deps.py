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