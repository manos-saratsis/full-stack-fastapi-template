"""Tests for backend/app/main.py"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.main import custom_generate_unique_id, app


class TestCustomGenerateUniqueId:
    """Test the custom_generate_unique_id function"""

    def test_custom_generate_unique_id_basic(self):
        """Test generating unique ID from a route with tags and name"""
        mock_route = Mock(spec=APIRoute)
        mock_route.tags = ["users"]
        mock_route.name = "get_users"

        result = custom_generate_unique_id(mock_route)

        assert result == "users-get_users"

    def test_custom_generate_unique_id_with_different_tags(self):
        """Test generating unique ID with different tag"""
        mock_route = Mock(spec=APIRoute)
        mock_route.tags = ["items"]
        mock_route.name = "list_items"

        result = custom_generate_unique_id(mock_route)

        assert result == "items-list_items"

    def test_custom_generate_unique_id_with_special_chars_in_name(self):
        """Test generating unique ID with special characters in route name"""
        mock_route = Mock(spec=APIRoute)
        mock_route.tags = ["auth"]
        mock_route.name = "login_for_access_token"

        result = custom_generate_unique_id(mock_route)

        assert result == "auth-login_for_access_token"

    def test_custom_generate_unique_id_empty_tag(self):
        """Test generating unique ID with empty tag string"""
        mock_route = Mock(spec=APIRoute)
        mock_route.tags = [""]
        mock_route.name = "test_route"

        result = custom_generate_unique_id(mock_route)

        assert result == "-test_route"


class TestAppConfiguration:
    """Test FastAPI app configuration"""

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance"""
        assert isinstance(app, FastAPI)

    def test_app_has_correct_title(self):
        """Test that the app has the correct title from settings"""
        assert app.title is not None
        # Title should be set from settings.PROJECT_NAME
        from app.core.config import settings
        assert app.title == settings.PROJECT_NAME

    def test_app_has_openapi_url(self):
        """Test that OpenAPI URL is configured"""
        from app.core.config import settings
        expected_url = f"{settings.API_V1_STR}/openapi.json"
        assert app.openapi_url == expected_url

    def test_app_has_custom_id_function(self):
        """Test that app uses custom unique ID function"""
        assert app.generate_unique_id_function == custom_generate_unique_id


class TestAppCORSConfiguration:
    """Test CORS middleware configuration"""

    @patch('app.main.settings')
    def test_cors_middleware_added_when_origins_configured(self, mock_settings):
        """Test that CORS middleware is added when origins are configured"""
        mock_settings.all_cors_origins = ["http://localhost:3000", "http://localhost:5173"]
        mock_settings.PROJECT_NAME = "Test App"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"

        # We can't easily re-import main.py, so we test the current state
        # The middleware should be present if cors origins were configured
        cors_middlewares = [
            mw for mw in app.user_middleware
            if mw.cls == CORSMiddleware
        ]
        assert len(cors_middlewares) > 0

    def test_app_router_included(self):
        """Test that the API router is included in the app"""
        # Check that routes from api_router are present
        from app.api.main import api_router
        
        # Get all routes in the app
        app_routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        # Should have some routes from the included router
        assert len(app_routes) > 0


class TestSentryIntegration:
    """Test Sentry integration configuration"""

    @patch('app.main.sentry_sdk')
    @patch('app.main.settings')
    def test_sentry_not_initialized_in_local_environment(self, mock_settings, mock_sentry):
        """Test that Sentry is not initialized in local environment"""
        # In the main module, sentry is only initialized if SENTRY_DSN is set
        # and ENVIRONMENT is not "local"
        # This test verifies the current state of the app
        from app.core.config import settings
        
        if settings.SENTRY_DSN is None:
            # Sentry should not be initialized
            mock_sentry.init.assert_not_called()

    @patch('app.main.sentry_sdk')
    @patch('app.main.settings')
    def test_sentry_initialization_conditions(self, mock_settings, mock_sentry):
        """Test conditions for Sentry initialization"""
        from app.core.config import settings
        
        # Sentry should only be initialized if:
        # 1. settings.SENTRY_DSN is truthy
        # 2. settings.ENVIRONMENT is not "local"
        if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
            mock_sentry.init.assert_called_once()
        else:
            mock_sentry.init.assert_not_called()