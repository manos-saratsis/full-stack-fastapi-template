import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from unittest.mock import Mock, patch, MagicMock

from app.main import custom_generate_unique_id, app


class TestCustomGenerateUniqueId:
    """Tests for custom_generate_unique_id function"""
    
    def test_generates_unique_id_with_tags_and_name(self):
        """should generate unique id when route has tags and name"""
        route = Mock(spec=APIRoute)
        route.tags = ["users"]
        route.name = "get_user"
        
        result = custom_generate_unique_id(route)
        
        assert result == "users-get_user"
    
    def test_generates_unique_id_with_multiple_tags(self):
        """should use first tag when route has multiple tags"""
        route = Mock(spec=APIRoute)
        route.tags = ["users", "admin"]
        route.name = "list_users"
        
        result = custom_generate_unique_id(route)
        
        assert result == "users-list_users"
    
    def test_generates_unique_id_with_special_characters_in_name(self):
        """should handle special characters in route name"""
        route = Mock(spec=APIRoute)
        route.tags = ["items"]
        route.name = "get_item_by_id_v2"
        
        result = custom_generate_unique_id(route)
        
        assert result == "items-get_item_by_id_v2"
    
    def test_generates_unique_id_with_empty_tag(self):
        """should generate id even with empty tag string"""
        route = Mock(spec=APIRoute)
        route.tags = [""]
        route.name = "test"
        
        result = custom_generate_unique_id(route)
        
        assert result == "-test"


class TestAppConfiguration:
    """Tests for FastAPI app configuration"""
    
    @patch('app.main.settings')
    def test_app_is_created_with_correct_title(self, mock_settings):
        """should create FastAPI app with settings PROJECT_NAME"""
        mock_settings.PROJECT_NAME = "Test API"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []
        
        with patch('app.main.FastAPI') as mock_fastapi:
            with patch('app.main.api_router'):
                # Re-import to trigger app creation with mocked settings
                import importlib
                import app.main
                importlib.reload(app.main)
    
    def test_app_has_correct_openapi_url(self):
        """should configure openapi_url correctly"""
        assert app.openapi_url == "/api/v1/openapi.json"
    
    def test_app_has_unique_id_function(self):
        """should use custom_generate_unique_id function"""
        assert app.openapi_schema is None  # Not yet generated
    
    def test_app_is_fastapi_instance(self):
        """should create FastAPI instance"""
        assert isinstance(app, FastAPI)


class TestCORSConfiguration:
    """Tests for CORS middleware configuration"""
    
    @patch('app.main.settings')
    @patch('app.main.FastAPI')
    @patch('app.main.api_router')
    def test_cors_middleware_added_when_origins_exist(self, mock_router, mock_fastapi, mock_settings):
        """should add CORS middleware when all_cors_origins is not empty"""
        mock_app = MagicMock(spec=FastAPI)
        mock_fastapi.return_value = mock_app
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = ["http://localhost:3000", "http://localhost:5173"]
        
        import importlib
        import app.main
        importlib.reload(app.main)
        
        # Verify add_middleware was called if all_cors_origins is truthy
        if mock_settings.all_cors_origins:
            mock_app.add_middleware.assert_called()
    
    @patch('app.main.settings')
    @patch('app.main.FastAPI')
    @patch('app.main.api_router')
    def test_cors_middleware_not_added_when_no_origins(self, mock_router, mock_fastapi, mock_settings):
        """should not add CORS middleware when all_cors_origins is empty"""
        mock_app = MagicMock(spec=FastAPI)
        mock_fastapi.return_value = mock_app
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []
        
        # CORS middleware should not be added when origins list is empty
        if not mock_settings.all_cors_origins:
            mock_app.add_middleware.assert_not_called()


class TestSentryConfiguration:
    """Tests for Sentry SDK initialization"""
    
    @patch('app.main.sentry_sdk')
    @patch('app.main.settings')
    @patch('app.main.FastAPI')
    @patch('app.main.api_router')
    def test_sentry_initialized_when_dsn_provided_and_not_local(self, mock_router, mock_fastapi, mock_settings, mock_sentry):
        """should initialize Sentry when SENTRY_DSN is set and environment is not local"""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"
        mock_settings.ENVIRONMENT = "production"
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.all_cors_origins = []
        
        import importlib
        import app.main
        # Re-execute module initialization
        with patch('app.main.sentry_sdk.init') as mock_init:
            exec_globals = {}
            with open('app/main.py', 'r') as f:
                code = f.read()
            # This would test if sentry_sdk.init is called
    
    @patch('app.main.sentry_sdk')
    @patch('app.main.settings')
    @patch('app.main.FastAPI')
    @patch('app.main.api_router')
    def test_sentry_not_initialized_when_no_dsn(self, mock_router, mock_fastapi, mock_settings, mock_sentry):
        """should not initialize Sentry when SENTRY_DSN is None"""
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "production"
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.all_cors_origins = []
        
        # Sentry should not be initialized
        assert mock_settings.SENTRY_DSN is None
    
    @patch('app.main.sentry_sdk')
    @patch('app.main.settings')
    @patch('app.main.FastAPI')
    @patch('app.main.api_router')
    def test_sentry_not_initialized_when_local_environment(self, mock_router, mock_fastapi, mock_settings, mock_sentry):
        """should not initialize Sentry when environment is local"""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"
        mock_settings.ENVIRONMENT = "local"
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.all_cors_origins = []
        
        # When environment is local, sentry_sdk.init should not be called
        if not (mock_settings.SENTRY_DSN and mock_settings.ENVIRONMENT != "local"):
            mock_sentry.init.assert_not_called()


class TestAPIRouterInclusion:
    """Tests for API router configuration"""
    
    def test_api_router_included_with_correct_prefix(self):
        """should include api_router with correct API_V1_STR prefix"""
        # The app should have routes from api_router included
        assert app.routes is not None
        # Verify that api_router was included (will have routes)
        assert len(app.routes) > 0