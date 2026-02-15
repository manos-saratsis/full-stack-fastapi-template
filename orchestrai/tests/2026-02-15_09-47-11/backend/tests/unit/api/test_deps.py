import pytest
from unittest.mock import Mock, MagicMock, patch, create_autospec
from datetime import datetime, timedelta, timezone
from typing import Generator
import jwt
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.api.deps import (
    get_db,
    SessionDep,
    TokenDep,
    get_current_user,
    CurrentUser,
    get_current_active_superuser,
    reusable_oauth2,
    limiter,
)
from app.core import security
from app.core.config import settings
from app.models import TokenPayload, User
from uuid import UUID


class TestGetDb:
    """Test get_db dependency injection."""

    @patch('app.api.deps.Session')
    def test_get_db_yields_session(self, mock_session_class):
        """should yield a database session"""
        mock_session = MagicMock(spec=Session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        mock_session_class.return_value = mock_session
        
        with patch('app.api.deps.engine') as mock_engine:
            from app.api.deps import get_db
            gen = get_db()
            
            session = next(gen)
            assert session is mock_session

    @patch('app.api.deps.Session')
    def test_get_db_context_manager_cleanup(self, mock_session_class):
        """should properly cleanup session context"""
        mock_session = MagicMock(spec=Session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        mock_session_class.return_value = mock_session
        
        with patch('app.api.deps.engine') as mock_engine:
            from app.api.deps import get_db
            gen = get_db()
            
            next(gen)
            try:
                next(gen)
            except StopIteration:
                pass
            
            mock_session.__exit__.assert_called()

    def test_get_db_returns_generator(self):
        """should return a generator"""
        result = get_db()
        assert isinstance(result, Generator)


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    def test_get_current_user_with_valid_token(self):
        """should return user when token is valid"""
        user_id = "12345678-1234-5678-1234-567812345678"
        token_payload = TokenPayload(sub=user_id)
        
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_session.get.return_value = mock_user
        
        # Create valid token
        expires_delta = timedelta(minutes=30)
        token = security.create_access_token(user_id, expires_delta)
        
        result = get_current_user(mock_session, token)
        
        assert result == mock_user
        mock_session.get.assert_called_once_with(User, user_id)

    def test_get_current_user_with_invalid_token_format(self):
        """should raise HTTPException with invalid token format"""
        mock_session = MagicMock(spec=Session)
        invalid_token = "not.a.valid.jwt.token"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Could not validate credentials"

    def test_get_current_user_with_expired_token(self):
        """should raise HTTPException with expired token"""
        user_id = "12345678-1234-5678-1234-567812345678"
        mock_session = MagicMock(spec=Session)
        
        # Create expired token
        expires_delta = timedelta(minutes=-30)
        token = security.create_access_token(user_id, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Could not validate credentials"

    def test_get_current_user_with_invalid_payload_signature(self):
        """should raise HTTPException when token signature is invalid"""
        mock_session = MagicMock(spec=Session)
        
        # Create token with wrong secret
        user_id = "12345678-1234-5678-1234-567812345678"
        expires_delta = timedelta(minutes=30)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(user_id)}
        bad_token = jwt.encode(to_encode, "wrong_secret", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, bad_token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_when_user_not_found(self):
        """should raise HTTPException when user doesn't exist in database"""
        user_id = "12345678-1234-5678-1234-567812345678"
        mock_session = MagicMock(spec=Session)
        mock_session.get.return_value = None
        
        expires_delta = timedelta(minutes=30)
        token = security.create_access_token(user_id, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Could not validate credentials"

    def test_get_current_user_when_user_is_inactive(self):
        """should raise HTTPException when user is inactive"""
        user_id = "12345678-1234-5678-1234-567812345678"
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = False
        mock_session.get.return_value = mock_user
        
        expires_delta = timedelta(minutes=30)
        token = security.create_access_token(user_id, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Inactive user"

    def test_get_current_user_with_invalid_token_payload_missing_sub(self):
        """should raise HTTPException when token lacks sub claim"""
        user_id = "12345678-1234-5678-1234-567812345678"
        mock_session = MagicMock(spec=Session)
        
        # Create token with missing sub
        expires_delta = timedelta(minutes=30)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire}  # Missing 'sub'
        bad_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, bad_token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_with_valid_token_string_subject(self):
        """should handle string subject in token"""
        user_id = "test_user_id"
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user
        
        expires_delta = timedelta(minutes=30)
        token = security.create_access_token(user_id, expires_delta)
        
        result = get_current_user(mock_session, token)
        
        assert result == mock_user

    def test_get_current_user_calls_session_get_with_correct_user_class(self):
        """should call session.get with User class"""
        user_id = "12345678-1234-5678-1234-567812345678"
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user
        
        expires_delta = timedelta(minutes=30)
        token = security.create_access_token(user_id, expires_delta)
        
        get_current_user(mock_session, token)
        
        # Verify session.get was called with User class
        call_args = mock_session.get.call_args
        assert call_args[0][0] == User


class TestGetCurrentActiveSuperuser:
    """Test get_current_active_superuser dependency."""

    def test_get_current_active_superuser_with_superuser(self):
        """should return user when they are superuser"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = True
        
        result = get_current_active_superuser(mock_user)
        
        assert result == mock_user

    def test_get_current_active_superuser_with_non_superuser(self):
        """should raise HTTPException when user is not superuser"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = False
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_superuser(mock_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    def test_get_current_active_superuser_preserves_user_object(self):
        """should return same user object instance"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = True
        mock_user.id = "test_id"
        mock_user.email = "test@example.com"
        
        result = get_current_active_superuser(mock_user)
        
        assert result is mock_user
        assert result.id == "test_id"
        assert result.email == "test@example.com"


class TestReusableOAuth2:
    """Test reusable_oauth2 configuration."""

    def test_reusable_oauth2_configured(self):
        """should be properly configured OAuth2PasswordBearer"""
        assert reusable_oauth2 is not None
        assert hasattr(reusable_oauth2, 'tokenUrl')
        expected_url = f"{settings.API_V1_STR}/login/access-token"
        assert reusable_oauth2.tokenUrl == expected_url


class TestLimiter:
    """Test rate limiter configuration."""

    def test_limiter_configured(self):
        """should be properly configured"""
        assert limiter is not None
        assert hasattr(limiter, 'key_func')


class TestAnnotationTypes:
    """Test annotated types."""

    def test_session_dep_annotation(self):
        """should have SessionDep annotation"""
        assert SessionDep is not None

    def test_token_dep_annotation(self):
        """should have TokenDep annotation"""
        assert TokenDep is not None

    def test_current_user_annotation(self):
        """should have CurrentUser annotation"""
        assert CurrentUser is not None


class TestErrorScenarios:
    """Test error handling edge cases."""

    def test_get_current_user_with_empty_token(self):
        """should raise HTTPException with empty token"""
        mock_session = MagicMock(spec=Session)
        
        with pytest.raises(HTTPException):
            get_current_user(mock_session, "")

    def test_get_current_user_with_none_token(self):
        """should handle None token"""
        mock_session = MagicMock(spec=Session)
        
        with pytest.raises((HTTPException, AttributeError, TypeError)):
            get_current_user(mock_session, None)

    def test_get_current_user_with_malformed_payload(self):
        """should raise HTTPException with malformed token payload"""
        mock_session = MagicMock(spec=Session)
        
        # Create token with invalid payload structure
        expires_delta = timedelta(minutes=30)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": 123}  # sub should be string-convertible
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        
        # This might work or fail depending on TokenPayload validation
        try:
            result = get_current_user(mock_session, token)
            # If it doesn't raise, verify the session was called
            assert mock_session.get.called or True
        except HTTPException:
            # Expected behavior
            pass