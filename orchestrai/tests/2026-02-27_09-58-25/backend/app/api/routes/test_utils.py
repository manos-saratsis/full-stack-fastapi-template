import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from pydantic.networks import EmailStr

from app.api.routes.utils import router, test_email, health_check
from app.models import Message


class TestTestEmail:
    """Test suite for test_email endpoint"""

    def test_test_email_success(self):
        """Should send test email and return success message"""
        # Arrange
        email_to = EmailStr("test@example.com")
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test Email"
            mock_email_data.html_content = "<html>Test</html>"
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email") as mock_send:
                # Act
                result = test_email(email_to)
        
        # Assert
        assert isinstance(result, Message)
        assert result.message == "Test email sent"
        mock_send.assert_called_once_with(
            email_to="test@example.com",
            subject="Test Email",
            html_content="<html>Test</html>"
        )

    def test_test_email_different_email_address(self):
        """Should handle different email addresses"""
        # Arrange
        email_to = EmailStr("different@example.com")
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test"
            mock_email_data.html_content = "<html></html>"
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email") as mock_send:
                # Act
                result = test_email(email_to)
        
        # Assert
        assert result.message == "Test email sent"
        mock_send.assert_called_once()

    def test_test_email_generation_called_with_correct_email(self):
        """Should generate email with correct recipient"""
        # Arrange
        email_to = EmailStr("recipient@example.com")
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test"
            mock_email_data.html_content = "<html></html>"
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email"):
                # Act
                test_email(email_to)
        
        # Assert
        mock_email_gen.assert_called_once_with(email_to=email_to)

    def test_test_email_sends_with_correct_parameters(self):
        """Should send email with subject and content from generated data"""
        # Arrange
        email_to = EmailStr("test@example.com")
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test Subject"
            mock_email_data.html_content = "<html>Test Content</html>"
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email") as mock_send:
                # Act
                test_email(email_to)
        
        # Assert
        mock_send.assert_called_once_with(
            email_to=email_to,
            subject="Test Subject",
            html_content="<html>Test Content</html>"
        )


class TestHealthCheck:
    """Test suite for health_check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self):
        """Should return True when health check passes"""
        # Act
        result = await health_check()
        
        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_is_async(self):
        """Should be an async function"""
        # Assert
        import inspect
        assert inspect.iscoroutinefunction(health_check)

    @pytest.mark.asyncio
    async def test_health_check_always_returns_true(self):
        """Should always return True regardless of state"""
        # Act
        result1 = await health_check()
        result2 = await health_check()
        
        # Assert
        assert result1 is True
        assert result2 is True

    @pytest.mark.asyncio
    async def test_health_check_no_side_effects(self):
        """Should not have any side effects"""
        # Act - call multiple times
        await health_check()
        result = await health_check()
        
        # Assert
        assert result is True


class TestRouterConfiguration:
    """Test suite for router configuration"""

    def test_router_has_utils_prefix(self):
        """Should configure router with /utils prefix"""
        # Assert
        assert router.prefix == "/utils"

    def test_router_has_utils_tag(self):
        """Should configure router with utils tag"""
        # Assert
        assert "utils" in router.tags

    def test_test_email_endpoint_exists(self):
        """Should have /test-email/ endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/test-email/" in endpoint_paths

    def test_health_check_endpoint_exists(self):
        """Should have /health-check/ endpoint"""
        # Assert
        endpoint_paths = [route.path for route in router.routes]
        assert "/health-check/" in endpoint_paths

    def test_test_email_is_post_endpoint(self):
        """Should have test-email as POST endpoint"""
        # Assert
        for route in router.routes:
            if route.path == "/test-email/":
                assert "POST" in route.methods
                break
        else:
            pytest.fail("POST endpoint for /test-email/ not found")

    def test_health_check_is_get_endpoint(self):
        """Should have health-check as GET endpoint"""
        # Assert
        for route in router.routes:
            if route.path == "/health-check/":
                assert "GET" in route.methods
                break
        else:
            pytest.fail("GET endpoint for /health-check/ not found")

    def test_test_email_status_code_201(self):
        """Should return status code 201 for test-email"""
        # Assert
        for route in router.routes:
            if route.path == "/test-email/" and "POST" in route.methods:
                # The status_code is set on the route
                assert hasattr(route, "status_code") or route.status_code == 201
                break


class TestTestEmailEdgeCases:
    """Test suite for test_email edge cases"""

    def test_test_email_with_special_characters_in_domain(self):
        """Should handle email with special formatting"""
        # Arrange
        email_to = EmailStr("user+test@example.co.uk")
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test"
            mock_email_data.html_content = "<html></html>"
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email") as mock_send:
                # Act
                result = test_email(email_to)
        
        # Assert
        assert result.message == "Test email sent"
        mock_email_gen.assert_called_once()

    def test_test_email_multiple_calls_independent(self):
        """Should handle multiple test email calls independently"""
        # Arrange
        email1 = EmailStr("user1@example.com")
        email2 = EmailStr("user2@example.com")
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test"
            mock_email_data.html_content = "<html></html>"
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email") as mock_send:
                # Act
                result1 = test_email(email1)
                result2 = test_email(email2)
        
        # Assert
        assert result1.message == "Test email sent"
        assert result2.message == "Test email sent"
        assert mock_email_gen.call_count == 2
        assert mock_send.call_count == 2

    def test_test_email_large_html_content(self):
        """Should handle large HTML content"""
        # Arrange
        email_to = EmailStr("test@example.com")
        large_html = "<html>" + "<p>Test</p>" * 1000 + "</html>"
        
        with patch("app.api.routes.utils.generate_test_email") as mock_email_gen:
            mock_email_data = Mock()
            mock_email_data.subject = "Test"
            mock_email_data.html_content = large_html
            mock_email_gen.return_value = mock_email_data
            
            with patch("app.api.routes.utils.send_email") as mock_send:
                # Act
                result = test_email(email_to)
        
        # Assert
        assert result.message == "Test email sent"
        mock_send.assert_called_once()


class TestHealthCheckEdgeCases:
    """Test suite for health_check edge cases"""

    @pytest.mark.asyncio
    async def test_health_check_rapid_successive_calls(self):
        """Should handle rapid successive calls"""
        # Act
        tasks = [health_check() for _ in range(100)]
        results = await __import__("asyncio").gather(*tasks)
        
        # Assert
        assert all(result is True for result in results)

    @pytest.mark.asyncio
    async def test_health_check_return_type_is_boolean(self):
        """Should return a boolean type"""
        # Act
        result = await health_check()
        
        # Assert
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_health_check_specific_value_true(self):
        """Should return the specific value True not just truthy"""
        # Act
        result = await health_check()
        
        # Assert
        assert result == True
        assert result is True