import pytest
from unittest.mock import Mock, MagicMock, patch, create_autospec
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.api.deps import (
    get_db,
    get_current_user,
    get_current_active_superuser,
    SessionDep,
    TokenDep,
    reusable_oauth2,
    limiter,
)
from app.models import User, TokenPayload
from app.core.config import settings
from app.core import security


class TestGetDb:
    """Tests for get_db dependency function"""

    @patch("app.api.deps.engine")
    @patch("app.api.deps.Session")
    def test_get_db_yields_session(self, mock_session_class, mock_engine):
        """Should yield a Session object"""
        mock_session_instance = MagicMock()
        mock_session_class.return_value.__enter__ = MagicMock(
            return_value=mock_session_instance
        )
        mock_session_class.return_value.__exit__ = MagicMock(return_value=None)

        generator = get_db()
        session = next(generator)

        assert session == mock_session_instance
        mock_session_class.assert_called_once_with(mock_engine)

    @patch("app.api.deps.engine")
    @patch("app.api.deps.Session")
    def test_get_db_context_manager_cleanup(self, mock_session_class, mock_engine):
        """Should properly cleanup session after use"""
        mock_session_instance = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_session_instance)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_session_class.return_value = mock_context_manager

        generator = get_db()
        session = next(generator)

        try:
            generator.send(None)
        except StopIteration:
            pass

        mock_context_manager.__exit__.assert_called()

    @patch("app.api.deps.engine")
    @patch("app.api.deps.Session")
    def test_get_db_is_generator(self, mock_session_class, mock_engine):
        """Should be a generator function"""
        mock_session_instance = MagicMock()
        mock_session_class.return_value.__enter__ = MagicMock(
            return_value=mock_session_instance
        )
        mock_session_class.return_value.__exit__ = MagicMock(return_value=None)

        result = get_db()

        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


class TestGetCurrentUser:
    """Tests for get_current_user dependency function"""

    def test_get_current_user_with_valid_token(self):
        """Should return user when token is valid"""
        # Create a valid token
        user_id = 1
        expires_delta = pytest.duration(hours=1)
        token = security.create_access_token(user_id, timedelta(hours=1))

        # Create mock session and user
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        result = get_current_user(mock_session, token)

        assert result == mock_user
        mock_session.get.assert_called_once_with(User, str(user_id))

    def test_get_current_user_with_invalid_token(self):
        """Should raise HTTPException when token is invalid"""
        invalid_token = "invalid.token.here"
        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, invalid_token)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_get_current_user_with_expired_token(self):
        """Should raise HTTPException when token is expired"""
        # Create an expired token
        user_id = 1
        token = security.create_access_token(user_id, timedelta(hours=-1))

        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_with_malformed_jwt(self):
        """Should raise HTTPException with malformed JWT"""
        malformed_token = "not.a.valid.jwt"
        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, malformed_token)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_user_not_found(self):
        """Should raise HTTPException when user doesn't exist"""
        user_id = 999
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_get_current_user_user_is_inactive(self):
        """Should raise HTTPException when user is inactive"""
        user_id = 1
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = False
        mock_session.get.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)

    def test_get_current_user_validation_error_on_token_payload(self):
        """Should raise HTTPException when token payload fails validation"""
        # Create token with invalid payload structure
        import jwt
        invalid_payload = {"exp": 9999999999, "invalid_field": "value"}
        token = jwt.encode(invalid_payload, settings.SECRET_KEY, algorithm="HS256")

        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_session, token)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_checks_is_active_before_returning(self):
        """Should check is_active status before returning user"""
        user_id = 1
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        result = get_current_user(mock_session, token)

        assert result.is_active is True

    def test_get_current_user_with_numeric_subject(self):
        """Should handle numeric user IDs"""
        user_id = 42
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        result = get_current_user(mock_session, token)

        assert result == mock_user
        mock_session.get.assert_called_once_with(User, "42")

    def test_get_current_user_with_string_subject(self):
        """Should handle string user IDs"""
        user_id = "user-uuid-123"
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        result = get_current_user(mock_session, token)

        assert result == mock_user
        mock_session.get.assert_called_once_with(User, user_id)


class TestGetCurrentActiveSuperuser:
    """Tests for get_current_active_superuser dependency function"""

    def test_get_current_active_superuser_with_superuser(self):
        """Should return user when user is superuser"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = True

        result = get_current_active_superuser(mock_user)

        assert result == mock_user

    def test_get_current_active_superuser_with_non_superuser(self):
        """Should raise HTTPException when user is not superuser"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_superuser(mock_user)

        assert exc_info.value.status_code == 403
        assert "doesn't have enough privileges" in str(exc_info.value.detail)

    def test_get_current_active_superuser_checks_is_superuser_flag(self):
        """Should specifically check is_superuser attribute"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = True

        result = get_current_active_superuser(mock_user)

        assert result.is_superuser is True

    def test_get_current_active_superuser_error_message_content(self):
        """Should return correct error message for non-superuser"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_superuser(mock_user)

        assert "enough privileges" in exc_info.value.detail.lower()

    def test_get_current_active_superuser_does_not_modify_user(self):
        """Should not modify the user object"""
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = True
        original_user = mock_user

        result = get_current_active_superuser(mock_user)

        assert result is original_user


class TestReusableOAuth2:
    """Tests for reusable_oauth2 OAuth2PasswordBearer configuration"""

    def test_reusable_oauth2_token_url_configured(self):
        """Should have tokenUrl configured"""
        assert reusable_oauth2.tokenUrl is not None

    def test_reusable_oauth2_token_url_includes_api_v1_str(self):
        """Should include API_V1_STR in tokenUrl"""
        assert settings.API_V1_STR in reusable_oauth2.tokenUrl

    def test_reusable_oauth2_token_url_includes_login_endpoint(self):
        """Should include login/access-token endpoint"""
        assert "login/access-token" in reusable_oauth2.tokenUrl

    def test_reusable_oauth2_is_oauth2_password_bearer(self):
        """Should be instance of OAuth2PasswordBearer"""
        from fastapi.security import OAuth2PasswordBearer
        assert isinstance(reusable_oauth2, OAuth2PasswordBearer)


class TestLimiter:
    """Tests for limiter configuration"""

    def test_limiter_is_configured(self):
        """Should have limiter configured"""
        assert limiter is not None

    def test_limiter_has_key_func(self):
        """Should have key function set"""
        assert hasattr(limiter, "key_func")

    def test_limiter_uses_get_remote_address(self):
        """Should use get_remote_address as key function"""
        from slowapi.util import get_remote_address
        assert limiter.key_func == get_remote_address


class TestSessionDepAnnotation:
    """Tests for SessionDep type annotation"""

    def test_session_dep_is_annotated(self):
        """Should be an Annotated type"""
        from typing import get_args, get_origin
        assert get_origin(SessionDep) is not None


class TestTokenDepAnnotation:
    """Tests for TokenDep type annotation"""

    def test_token_dep_is_annotated(self):
        """Should be an Annotated type"""
        from typing import get_args, get_origin
        assert get_origin(TokenDep) is not None


class TestDepsIntegration:
    """Integration tests for dependency functions"""

    def test_get_current_user_then_get_current_active_superuser_flow(self):
        """Should work together in dependency chain"""
        user_id = 1
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_user.is_superuser = True
        mock_session.get.return_value = mock_user

        current_user = get_current_user(mock_session, token)
        result = get_current_active_superuser(current_user)

        assert result == mock_user

    def test_get_current_user_then_get_current_active_superuser_non_superuser(self):
        """Should fail at superuser check if user is not superuser"""
        user_id = 1
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_session.get.return_value = mock_user

        current_user = get_current_user(mock_session, token)

        with pytest.raises(HTTPException):
            get_current_active_superuser(current_user)


# Additional edge case tests
class TestGetCurrentUserEdgeCases:
    """Edge case tests for get_current_user"""

    def test_get_current_user_with_very_large_user_id(self):
        """Should handle very large user IDs"""
        user_id = 9999999999
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        result = get_current_user(mock_session, token)

        assert result == mock_user

    def test_get_current_user_with_special_characters_in_user_id(self):
        """Should handle special characters in user ID"""
        user_id = "user@domain.com"
        token = security.create_access_token(user_id, timedelta(hours=1))

        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        result = get_current_user(mock_session, token)

        assert result == mock_user

    def test_get_current_user_with_empty_token_string(self):
        """Should handle empty token string"""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException):
            get_current_user(mock_session, "")

    def test_get_current_user_with_only_dots_token(self):
        """Should handle token with only dots"""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException):
            get_current_user(mock_session, "...")

    def test_get_current_user_with_wrong_algorithm_token(self):
        """Should reject token signed with wrong algorithm"""
        import jwt
        payload = {"sub": "1", "exp": 9999999999}
        # Sign with different algorithm or key
        token = jwt.encode(payload, "wrong-key", algorithm="HS256")

        mock_session = MagicMock(spec=Session)

        with pytest.raises(HTTPException):
            get_current_user(mock_session, token)