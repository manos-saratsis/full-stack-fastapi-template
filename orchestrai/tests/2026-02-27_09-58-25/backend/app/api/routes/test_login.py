import pytest
from datetime import timedelta
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.routes.login import router, limiter, login_access_token, test_token, recover_password, reset_password, recover_password_html_content
from app.models import Message, NewPassword, Token, UserPublic
from app.core.config import settings


class TestLoginAccessToken:
    """Test suite for login_access_token endpoint"""

    def test_login_access_token_success(self):
        """Should return access token when credentials are valid"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        
        mock_form_data = Mock(spec=OAuth2PasswordRequestForm)
        mock_form_data.username = "test@example.com"
        mock_form_data.password = "password123"
        
        with patch("app.api.routes.login.crud.authenticate", return_value=mock_user):
            with patch("app.api.routes.login.security.create_access_token", return_value="test_token"):
                # Act
                result = login_access_token(mock_request, mock_session, mock_form_data)
        
        # Assert
        assert isinstance(result, Token)
        assert result.access_token == "test_token"

    def test_login_access_token_invalid_credentials(self):
        """Should raise HTTPException when credentials are invalid"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        
        mock_form_data = Mock(spec=OAuth2PasswordRequestForm)
        mock_form_data.username = "test@example.com"
        mock_form_data.password = "wrongpassword"
        
        with patch("app.api.routes.login.crud.authenticate", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login_access_token(mock_request, mock_session, mock_form_data)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Incorrect email or password"

    def test_login_access_token_inactive_user(self):
        """Should raise HTTPException when user is inactive"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = False
        
        mock_form_data = Mock(spec=OAuth2PasswordRequestForm)
        mock_form_data.username = "test@example.com"
        mock_form_data.password = "password123"
        
        with patch("app.api.routes.login.crud.authenticate", return_value=mock_user):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login_access_token(mock_request, mock_session, mock_form_data)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Inactive user"

    def test_login_access_token_expiration_config(self):
        """Should use configured token expiration time"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        
        mock_form_data = Mock(spec=OAuth2PasswordRequestForm)
        mock_form_data.username = "test@example.com"
        mock_form_data.password = "password123"
        
        with patch("app.api.routes.login.crud.authenticate", return_value=mock_user):
            with patch("app.api.routes.login.security.create_access_token", return_value="test_token") as mock_create_token:
                # Act
                result = login_access_token(mock_request, mock_session, mock_form_data)
        
        # Assert
        expected_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        mock_create_token.assert_called_once_with(1, expires_delta=expected_expiry)


class TestTestToken:
    """Test suite for test_token endpoint"""

    def test_test_token_returns_current_user(self):
        """Should return current user when token is valid"""
        # Arrange
        mock_user = Mock(spec=UserPublic)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        
        # Act
        result = test_token(mock_user)
        
        # Assert
        assert result == mock_user

    def test_test_token_with_different_user_data(self):
        """Should return user object with all properties intact"""
        # Arrange
        mock_user = Mock(spec=UserPublic)
        mock_user.id = 42
        mock_user.email = "different@example.com"
        mock_user.full_name = "Test User"
        mock_user.is_active = True
        
        # Act
        result = test_token(mock_user)
        
        # Assert
        assert result.id == 42
        assert result.email == "different@example.com"
        assert result.full_name == "Test User"
        assert result.is_active is True


class TestRecoverPassword:
    """Test suite for recover_password endpoint"""

    def test_recover_password_success(self):
        """Should send password recovery email and return success message"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        email_to = "test@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
            with patch("app.api.routes.login.generate_password_reset_token", return_value="reset_token"):
                with patch("app.api.routes.login.generate_reset_password_email") as mock_email_gen:
                    mock_email_data = Mock()
                    mock_email_data.subject = "Password Reset"
                    mock_email_data.html_content = "<html>Reset</html>"
                    mock_email_gen.return_value = mock_email_data
                    
                    with patch("app.api.routes.login.send_email") as mock_send:
                        # Act
                        result = recover_password(mock_request, email_to, mock_session)
        
        # Assert
        assert isinstance(result, Message)
        assert result.message == "Password recovery email sent"
        mock_send.assert_called_once_with(
            email_to="test@example.com",
            subject="Password Reset",
            html_content="<html>Reset</html>"
        )

    def test_recover_password_user_not_found(self):
        """Should raise HTTPException when user does not exist"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        email_to = "nonexistent@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                recover_password(mock_request, email_to, mock_session)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "The user with this email does not exist in the system."

    def test_recover_password_email_generation(self):
        """Should generate reset token with correct email"""
        # Arrange
        mock_session = MagicMock()
        mock_request = MagicMock(spec=Request)
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        email_to = "test@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
            with patch("app.api.routes.login.generate_password_reset_token", return_value="reset_token") as mock_token_gen:
                with patch("app.api.routes.login.generate_reset_password_email") as mock_email_gen:
                    mock_email_data = Mock()
                    mock_email_data.subject = "Password Reset"
                    mock_email_data.html_content = "<html>Reset</html>"
                    mock_email_gen.return_value = mock_email_data
                    
                    with patch("app.api.routes.login.send_email"):
                        # Act
                        recover_password(mock_request, email_to, mock_session)
        
        # Assert
        mock_token_gen.assert_called_once_with(email=email_to)
        mock_email_gen.assert_called_once_with(
            email_to="test@example.com",
            email=email_to,
            token="reset_token"
        )


class TestResetPassword:
    """Test suite for reset_password endpoint"""

    def test_reset_password_success(self):
        """Should reset password and return success message"""
        # Arrange
        mock_session = MagicMock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.hashed_password = "old_hash"
        
        body = NewPassword(token="valid_token", new_password="newpassword123")
        
        with patch("app.api.routes.login.verify_password_reset_token", return_value="test@example.com"):
            with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
                with patch("app.api.routes.login.get_password_hash", return_value="new_hash"):
                    # Act
                    result = reset_password(mock_session, body)
        
        # Assert
        assert isinstance(result, Message)
        assert result.message == "Password updated successfully"
        assert mock_user.hashed_password == "new_hash"
        mock_session.add.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()

    def test_reset_password_invalid_token(self):
        """Should raise HTTPException when token is invalid"""
        # Arrange
        mock_session = MagicMock()
        body = NewPassword(token="invalid_token", new_password="newpassword123")
        
        with patch("app.api.routes.login.verify_password_reset_token", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                reset_password(mock_session, body)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Invalid token"

    def test_reset_password_user_not_found(self):
        """Should raise HTTPException when user does not exist"""
        # Arrange
        mock_session = MagicMock()
        body = NewPassword(token="valid_token", new_password="newpassword123")
        
        with patch("app.api.routes.login.verify_password_reset_token", return_value="test@example.com"):
            with patch("app.api.routes.login.crud.get_user_by_email", return_value=None):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    reset_password(mock_session, body)
                
                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "The user with this email does not exist in the system."

    def test_reset_password_inactive_user(self):
        """Should raise HTTPException when user is inactive"""
        # Arrange
        mock_session = MagicMock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.is_active = False
        
        body = NewPassword(token="valid_token", new_password="newpassword123")
        
        with patch("app.api.routes.login.verify_password_reset_token", return_value="test@example.com"):
            with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    reset_password(mock_session, body)
                
                assert exc_info.value.status_code == 400
                assert exc_info.value.detail == "Inactive user"

    def test_reset_password_updates_database(self):
        """Should call session methods to update user in database"""
        # Arrange
        mock_session = MagicMock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.hashed_password = "old_hash"
        
        body = NewPassword(token="valid_token", new_password="newpassword123")
        
        with patch("app.api.routes.login.verify_password_reset_token", return_value="test@example.com"):
            with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
                with patch("app.api.routes.login.get_password_hash", return_value="new_hash"):
                    # Act
                    reset_password(mock_session, body)
        
        # Assert
        mock_session.add.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()


class TestRecoverPasswordHtmlContent:
    """Test suite for recover_password_html_content endpoint"""

    def test_recover_password_html_content_success(self):
        """Should return HTML content for password recovery"""
        # Arrange
        mock_session = MagicMock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        email = "test@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
            with patch("app.api.routes.login.generate_password_reset_token", return_value="reset_token"):
                with patch("app.api.routes.login.generate_reset_password_email") as mock_email_gen:
                    mock_email_data = Mock()
                    mock_email_data.subject = "Password Reset"
                    mock_email_data.html_content = "<html><body>Reset Password</body></html>"
                    mock_email_gen.return_value = mock_email_data
                    
                    # Act
                    result = recover_password_html_content(email, mock_session)
        
        # Assert
        assert result.body == b"<html><body>Reset Password</body></html>"
        assert result.headers["subject:"] == "Password Reset"

    def test_recover_password_html_content_user_not_found(self):
        """Should raise HTTPException when user does not exist"""
        # Arrange
        mock_session = MagicMock()
        email = "nonexistent@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                recover_password_html_content(email, mock_session)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "The user with this username does not exist in the system."

    def test_recover_password_html_content_token_generation(self):
        """Should generate reset token with correct email"""
        # Arrange
        mock_session = MagicMock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        email = "test@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
            with patch("app.api.routes.login.generate_password_reset_token", return_value="reset_token") as mock_token_gen:
                with patch("app.api.routes.login.generate_reset_password_email") as mock_email_gen:
                    mock_email_data = Mock()
                    mock_email_data.subject = "Password Reset"
                    mock_email_data.html_content = "<html></html>"
                    mock_email_gen.return_value = mock_email_data
                    
                    # Act
                    recover_password_html_content(email, mock_session)
        
        # Assert
        mock_token_gen.assert_called_once_with(email=email)
        mock_email_gen.assert_called_once_with(
            email_to="test@example.com",
            email=email,
            token="reset_token"
        )

    def test_recover_password_html_content_different_email(self):
        """Should work with different email addresses"""
        # Arrange
        mock_session = MagicMock()
        mock_user = Mock()
        mock_user.email = "different@example.com"
        
        email = "different@example.com"
        
        with patch("app.api.routes.login.crud.get_user_by_email", return_value=mock_user):
            with patch("app.api.routes.login.generate_password_reset_token", return_value="reset_token"):
                with patch("app.api.routes.login.generate_reset_password_email") as mock_email_gen:
                    mock_email_data = Mock()
                    mock_email_data.subject = "Reset"
                    mock_email_data.html_content = "<html>Reset</html>"
                    mock_email_gen.return_value = mock_email_data
                    
                    # Act
                    result = recover_password_html_content(email, mock_session)
        
        # Assert
        assert result.body == b"<html>Reset</html>"


class TestRouterConfiguration:
    """Test suite for router configuration"""

    def test_router_has_correct_tags(self):
        """Should configure router with login tag"""
        # Assert
        assert "login" in router.tags

    def test_login_endpoint_exists(self):
        """Should have /login/access-token endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/login/access-token" in endpoint_paths

    def test_test_token_endpoint_exists(self):
        """Should have /login/test-token endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/login/test-token" in endpoint_paths

    def test_recover_password_endpoint_exists(self):
        """Should have /password-recovery/{email} endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/password-recovery/{email}" in endpoint_paths

    def test_reset_password_endpoint_exists(self):
        """Should have /reset-password/ endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/reset-password/" in endpoint_paths

    def test_recover_password_html_endpoint_exists(self):
        """Should have /password-recovery-html-content/{email} endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/password-recovery-html-content/{email}" in endpoint_paths


class TestLimiterConfiguration:
    """Test suite for rate limiter configuration"""

    def test_limiter_uses_remote_address(self):
        """Should use remote address as limiter key"""
        # Assert - limiter is initialized with get_remote_address
        assert limiter.key_func == __import__("slowapi.util", fromlist=["get_remote_address"]).get_remote_address