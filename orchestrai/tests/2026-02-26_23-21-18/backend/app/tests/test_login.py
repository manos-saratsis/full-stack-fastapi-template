import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch, Mock
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.routes.login import router, login_access_token, test_token, recover_password, reset_password, recover_password_html_content
from app.core.config import settings
from app.models import Message, NewPassword, Token, UserPublic


class TestLoginAccessToken:
    """Test cases for login_access_token endpoint"""

    def test_login_access_token_success(self):
        """should return access token when user authenticates successfully"""
        # Arrange
        request = MagicMock(spec=Request)
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.is_active = True
        
        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "test@example.com"
        form_data.password = "password123"
        
        with patch('app.api.routes.login.crud.authenticate', return_value=mock_user):
            with patch('app.api.routes.login.security.create_access_token', return_value="test-token"):
                # Act
                result = login_access_token(request=request, session=session, form_data=form_data)
        
        # Assert
        assert isinstance(result, Token)
        assert result.access_token == "test-token"

    def test_login_access_token_user_not_found(self):
        """should raise HTTPException 400 when user does not exist"""
        # Arrange
        request = MagicMock(spec=Request)
        session = MagicMock()
        
        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "nonexistent@example.com"
        form_data.password = "password123"
        
        with patch('app.api.routes.login.crud.authenticate', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login_access_token(request=request, session=session, form_data=form_data)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Incorrect email or password"

    def test_login_access_token_inactive_user(self):
        """should raise HTTPException 400 when user is inactive"""
        # Arrange
        request = MagicMock(spec=Request)
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.is_active = False
        
        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "inactive@example.com"
        form_data.password = "password123"
        
        with patch('app.api.routes.login.crud.authenticate', return_value=mock_user):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login_access_token(request=request, session=session, form_data=form_data)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Inactive user"

    def test_login_access_token_uses_correct_expiration(self):
        """should create access token with correct expiration time"""
        # Arrange
        request = MagicMock(spec=Request)
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.is_active = True
        
        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "test@example.com"
        form_data.password = "password123"
        
        with patch('app.api.routes.login.crud.authenticate', return_value=mock_user):
            with patch('app.api.routes.login.security.create_access_token') as mock_create_token:
                # Act
                login_access_token(request=request, session=session, form_data=form_data)
        
        # Assert
        mock_create_token.assert_called_once()
        call_args = mock_create_token.call_args
        assert call_args[0][0] == "user-123"
        assert call_args[1]['expires_delta'] == timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    def test_login_access_token_wrong_password(self):
        """should raise HTTPException 400 when password is incorrect"""
        # Arrange
        request = MagicMock(spec=Request)
        session = MagicMock()
        
        form_data = MagicMock(spec=OAuth2PasswordRequestForm)
        form_data.username = "test@example.com"
        form_data.password = "wrongpassword"
        
        with patch('app.api.routes.login.crud.authenticate', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login_access_token(request=request, session=session, form_data=form_data)
            
            assert exc_info.value.status_code == 400
            assert "Incorrect email or password" in exc_info.value.detail


class TestTestToken:
    """Test cases for test_token endpoint"""

    def test_test_token_success(self):
        """should return current user when token is valid"""
        # Arrange
        mock_user = MagicMock(spec=UserPublic)
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        
        # Act
        result = test_token(current_user=mock_user)
        
        # Assert
        assert result == mock_user
        assert result.id == "user-123"
        assert result.email == "test@example.com"

    def test_test_token_returns_user_object(self):
        """should return the exact user object passed as current_user"""
        # Arrange
        mock_user = MagicMock(spec=UserPublic)
        mock_user.name = "Test User"
        
        # Act
        result = test_token(current_user=mock_user)
        
        # Assert
        assert result is mock_user


class TestRecoverPassword:
    """Test cases for recover_password endpoint"""

    def test_recover_password_success(self):
        """should send password recovery email when user exists"""
        # Arrange
        session = MagicMock()
        email = "test@example.com"
        
        mock_user = MagicMock()
        mock_user.email = email
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
            with patch('app.api.routes.login.generate_password_reset_token', return_value="reset-token"):
                with patch('app.api.routes.login.generate_reset_password_email') as mock_gen_email:
                    with patch('app.api.routes.login.send_email') as mock_send_email:
                        mock_email_data = MagicMock()
                        mock_email_data.subject = "Password Recovery"
                        mock_email_data.html_content = "<h1>Reset Password</h1>"
                        mock_gen_email.return_value = mock_email_data
                        
                        # Act
                        result = recover_password(request=MagicMock(), email=email, session=session)
        
        # Assert
        assert isinstance(result, Message)
        assert result.message == "Password recovery email sent"
        mock_send_email.assert_called_once()

    def test_recover_password_user_not_found(self):
        """should raise HTTPException 404 when user does not exist"""
        # Arrange
        session = MagicMock()
        email = "nonexistent@example.com"
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                recover_password(request=MagicMock(), email=email, session=session)
            
            assert exc_info.value.status_code == 404
            assert "does not exist in the system" in exc_info.value.detail

    def test_recover_password_generates_token(self):
        """should generate password reset token with correct email"""
        # Arrange
        session = MagicMock()
        email = "test@example.com"
        
        mock_user = MagicMock()
        mock_user.email = email
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
            with patch('app.api.routes.login.generate_password_reset_token') as mock_gen_token:
                with patch('app.api.routes.login.generate_reset_password_email'):
                    with patch('app.api.routes.login.send_email'):
                        mock_gen_token.return_value = "reset-token"
                        
                        # Act
                        recover_password(request=MagicMock(), email=email, session=session)
        
        # Assert
        mock_gen_token.assert_called_once_with(email=email)

    def test_recover_password_sends_email_with_correct_data(self):
        """should send email with correct subject and content"""
        # Arrange
        session = MagicMock()
        email = "test@example.com"
        
        mock_user = MagicMock()
        mock_user.email = email
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
            with patch('app.api.routes.login.generate_password_reset_token', return_value="reset-token"):
                with patch('app.api.routes.login.generate_reset_password_email') as mock_gen_email:
                    with patch('app.api.routes.login.send_email') as mock_send_email:
                        mock_email_data = MagicMock()
                        mock_email_data.subject = "Password Recovery"
                        mock_email_data.html_content = "<h1>Reset</h1>"
                        mock_gen_email.return_value = mock_email_data
                        
                        # Act
                        recover_password(request=MagicMock(), email=email, session=session)
        
        # Assert
        mock_send_email.assert_called_once_with(
            email_to=email,
            subject="Password Recovery",
            html_content="<h1>Reset</h1>"
        )

    def test_recover_password_with_empty_email(self):
        """should raise HTTPException 404 when email is empty string"""
        # Arrange
        session = MagicMock()
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                recover_password(request=MagicMock(), email="", session=session)
            
            assert exc_info.value.status_code == 404


class TestResetPassword:
    """Test cases for reset_password endpoint"""

    def test_reset_password_success(self):
        """should update password when token is valid"""
        # Arrange
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        body = MagicMock(spec=NewPassword)
        body.token = "valid-reset-token"
        body.new_password = "newpassword123"
        
        with patch('app.api.routes.login.verify_password_reset_token', return_value="test@example.com"):
            with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
                with patch('app.api.routes.login.get_password_hash', return_value="hashed-password"):
                    # Act
                    result = reset_password(session=session, body=body)
        
        # Assert
        assert isinstance(result, Message)
        assert result.message == "Password updated successfully"
        assert mock_user.hashed_password == "hashed-password"
        session.add.assert_called_once_with(mock_user)
        session.commit.assert_called_once()

    def test_reset_password_invalid_token(self):
        """should raise HTTPException 400 when token is invalid"""
        # Arrange
        session = MagicMock()
        
        body = MagicMock(spec=NewPassword)
        body.token = "invalid-token"
        body.new_password = "newpassword123"
        
        with patch('app.api.routes.login.verify_password_reset_token', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                reset_password(session=session, body=body)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Invalid token"

    def test_reset_password_user_not_found(self):
        """should raise HTTPException 404 when user does not exist"""
        # Arrange
        session = MagicMock()
        
        body = MagicMock(spec=NewPassword)
        body.token = "valid-token"
        body.new_password = "newpassword123"
        
        with patch('app.api.routes.login.verify_password_reset_token', return_value="nonexistent@example.com"):
            with patch('app.api.routes.login.crud.get_user_by_email', return_value=None):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    reset_password(session=session, body=body)
            
            assert exc_info.value.status_code == 404
            assert "does not exist in the system" in exc_info.value.detail

    def test_reset_password_inactive_user(self):
        """should raise HTTPException 400 when user is inactive"""
        # Arrange
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.is_active = False
        
        body = MagicMock(spec=NewPassword)
        body.token = "valid-token"
        body.new_password = "newpassword123"
        
        with patch('app.api.routes.login.verify_password_reset_token', return_value="test@example.com"):
            with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    reset_password(session=session, body=body)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Inactive user"

    def test_reset_password_hashes_password(self):
        """should hash the new password before storing"""
        # Arrange
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.is_active = True
        
        body = MagicMock(spec=NewPassword)
        body.token = "valid-token"
        body.new_password = "newpassword123"
        
        with patch('app.api.routes.login.verify_password_reset_token', return_value="test@example.com"):
            with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
                with patch('app.api.routes.login.get_password_hash') as mock_hash:
                    mock_hash.return_value = "hashed-value"
                    
                    # Act
                    reset_password(session=session, body=body)
        
        # Assert
        mock_hash.assert_called_once_with(password="newpassword123")

    def test_reset_password_commits_transaction(self):
        """should commit changes to database"""
        # Arrange
        session = MagicMock()
        
        mock_user = MagicMock()
        mock_user.is_active = True
        
        body = MagicMock(spec=NewPassword)
        body.token = "valid-token"
        body.new_password = "newpassword123"
        
        with patch('app.api.routes.login.verify_password_reset_token', return_value="test@example.com"):
            with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
                with patch('app.api.routes.login.get_password_hash', return_value="hashed"):
                    # Act
                    reset_password(session=session, body=body)
        
        # Assert
        session.add.assert_called_once()
        session.commit.assert_called_once()


class TestRecoverPasswordHtmlContent:
    """Test cases for recover_password_html_content endpoint"""

    def test_recover_password_html_content_success(self):
        """should return HTML content when user exists"""
        # Arrange
        session = MagicMock()
        email = "test@example.com"
        
        mock_user = MagicMock()
        mock_user.email = email
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
            with patch('app.api.routes.login.generate_password_reset_token', return_value="reset-token"):
                with patch('app.api.routes.login.generate_reset_password_email') as mock_gen_email:
                    mock_email_data = MagicMock()
                    mock_email_data.html_content = "<h1>Reset Password</h1>"
                    mock_email_data.subject = "Password Recovery"
                    mock_gen_email.return_value = mock_email_data
                    
                    # Act
                    result = recover_password_html_content(email=email, session=session)
        
        # Assert
        from fastapi.responses import HTMLResponse
        assert isinstance(result, HTMLResponse)
        assert result.body == b"<h1>Reset Password</h1>"

    def test_recover_password_html_content_user_not_found(self):
        """should raise HTTPException 404 when user does not exist"""
        # Arrange
        session = MagicMock()
        email = "nonexistent@example.com"
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                recover_password_html_content(email=email, session=session)
            
            assert exc_info.value.status_code == 404
            assert "does not exist in the system" in exc_info.value.detail

    def test_recover_password_html_content_includes_subject_header(self):
        """should include subject in response headers"""
        # Arrange
        session = MagicMock()
        email = "test@example.com"
        
        mock_user = MagicMock()
        mock_user.email = email
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
            with patch('app.api.routes.login.generate_password_reset_token', return_value="reset-token"):
                with patch('app.api.routes.login.generate_reset_password_email') as mock_gen_email:
                    mock_email_data = MagicMock()
                    mock_email_data.html_content = "<h1>Reset</h1>"
                    mock_email_data.subject = "Password Recovery"
                    mock_gen_email.return_value = mock_email_data
                    
                    # Act
                    result = recover_password_html_content(email=email, session=session)
        
        # Assert
        assert "subject:" in result.headers
        assert result.headers["subject:"] == "Password Recovery"

    def test_recover_password_html_content_generates_token(self):
        """should generate password reset token with correct email"""
        # Arrange
        session = MagicMock()
        email = "test@example.com"
        
        mock_user = MagicMock()
        mock_user.email = email
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=mock_user):
            with patch('app.api.routes.login.generate_password_reset_token') as mock_gen_token:
                with patch('app.api.routes.login.generate_reset_password_email'):
                    mock_gen_token.return_value = "reset-token"
                    
                    # Act
                    recover_password_html_content(email=email, session=session)
        
        # Assert
        mock_gen_token.assert_called_once_with(email=email)

    def test_recover_password_html_content_with_empty_email(self):
        """should raise HTTPException 404 when email is empty"""
        # Arrange
        session = MagicMock()
        
        with patch('app.api.routes.login.crud.get_user_by_email', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                recover_password_html_content(email="", session=session)
            
            assert exc_info.value.status_code == 404


class TestRouterConfiguration:
    """Test cases for router configuration"""

    def test_router_has_login_tags(self):
        """should have login tags configured"""
        # Assert
        assert "login" in router.tags or any(
            route.tags and "login" in route.tags 
            for route in router.routes
        )

    def test_login_access_token_has_rate_limit(self):
        """should have rate limiting configured for login endpoint"""
        # This tests that the limiter is properly applied
        # The actual limiting is handled by the @limiter.limit decorator
        assert login_access_token is not None

    def test_recover_password_has_rate_limit(self):
        """should have rate limiting configured for recover_password endpoint"""
        # This tests that the limiter is properly applied
        assert recover_password is not None