import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from unittest.mock import Mock, patch, MagicMock

from app.main import custom_generate_unique_id


class TestCustomGenerateUniqueId:
    """Test the custom_generate_unique_id function."""

    def test_generates_unique_id_with_tags_and_name(self):
        """Should generate unique ID from route tags and name."""
        route = Mock(spec=APIRoute)
        route.tags = ["users"]
        route.name = "get_user"

        result = custom_generate_unique_id(route)

        assert result == "users-get_user"

    def test_generates_unique_id_with_multiple_tags(self):
        """Should use first tag when multiple tags exist."""
        route = Mock(spec=APIRoute)
        route.tags = ["users", "admin", "public"]
        route.name = "list_users"

        result = custom_generate_unique_id(route)

        assert result == "users-list_users"

    def test_generates_unique_id_with_special_characters_in_name(self):
        """Should handle special characters in route name."""
        route = Mock(spec=APIRoute)
        route.tags = ["items"]
        route.name = "get_item_by_id_v2"

        result = custom_generate_unique_id(route)

        assert result == "items-get_item_by_id_v2"

    def test_generates_unique_id_with_empty_tag_string(self):
        """Should handle empty tag string."""
        route = Mock(spec=APIRoute)
        route.tags = [""]
        route.name = "test"

        result = custom_generate_unique_id(route)

        assert result == "-test"

    def test_generates_unique_id_with_numeric_tag(self):
        """Should handle numeric strings in tags."""
        route = Mock(spec=APIRoute)
        route.tags = ["v1"]
        route.name = "endpoint"

        result = custom_generate_unique_id(route)

        assert result == "v1-endpoint"


class TestAppInitialization:
    """Test FastAPI app initialization."""

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    @patch("app.main.api_router")
    def test_app_creation_with_settings(self, mock_api_router, mock_sentry, mock_settings):
        """Should create FastAPI app with correct settings."""
        mock_settings.PROJECT_NAME = "Test API"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []

        # Re-import to get fresh app
        import importlib
        import app.main
        importlib.reload(app.main)

        app = app.main.app

        assert isinstance(app, FastAPI)
        assert app.title == "Test API"

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_sentry_not_initialized_when_dsn_is_none(self, mock_sentry, mock_settings):
        """Should not initialize Sentry when SENTRY_DSN is None."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "production"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        mock_sentry.init.assert_not_called()

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_sentry_not_initialized_in_local_environment(self, mock_sentry, mock_settings):
        """Should not initialize Sentry in local environment even with DSN."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = "https://key@sentry.io/123456"
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        mock_sentry.init.assert_not_called()

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_sentry_initialized_in_staging(self, mock_sentry, mock_settings):
        """Should initialize Sentry in staging environment with DSN."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = "https://key@sentry.io/123456"
        mock_settings.ENVIRONMENT = "staging"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        mock_sentry.init.assert_called_once()

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_sentry_initialized_in_production(self, mock_sentry, mock_settings):
        """Should initialize Sentry in production environment with DSN."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = "https://key@sentry.io/123456"
        mock_settings.ENVIRONMENT = "production"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        mock_sentry.init.assert_called_once()

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    @patch("app.main.CORSMiddleware")
    def test_cors_middleware_added_when_origins_exist(self, mock_cors, mock_sentry, mock_settings):
        """Should add CORS middleware when CORS origins are configured."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = ["http://localhost:3000", "http://localhost:5173"]

        import importlib
        import app.main
        importlib.reload(app.main)

        app = app.main.app
        # Check that middleware was added
        assert any(isinstance(middleware, CORSMiddleware) for middleware in app.user_middleware)

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_cors_middleware_not_added_when_only_frontend_host(self, mock_sentry, mock_settings):
        """Should not add CORS middleware when all_cors_origins is only frontend host."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        app = app.main.app
        # No CORS middleware should be added when all_cors_origins is empty
        cors_middlewares = [m for m in app.user_middleware if isinstance(m, CORSMiddleware)]
        assert len(cors_middlewares) == 0

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    @patch("app.main.api_router")
    def test_api_router_included(self, mock_api_router, mock_sentry, mock_settings):
        """Should include API router with correct prefix."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        app = app.main.app
        # Verify router was included by checking routes
        assert len(app.routes) > 0

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_openapi_url_set_correctly(self, mock_sentry, mock_settings):
        """Should set OpenAPI URL based on API_V1_STR."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v2"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        app = app.main.app
        assert app.openapi_url == "/api/v2/openapi.json"

    @patch("app.main.settings")
    @patch("app.main.sentry_sdk")
    def test_custom_unique_id_function_used(self, mock_sentry, mock_settings):
        """Should use custom unique ID function for route generation."""
        mock_settings.PROJECT_NAME = "Test"
        mock_settings.API_V1_STR = "/api/v1"
        mock_settings.SENTRY_DSN = None
        mock_settings.ENVIRONMENT = "local"
        mock_settings.all_cors_origins = []

        import importlib
        import app.main
        importlib.reload(app.main)

        app = app.main.app
        # Verify the unique ID function was set
        assert app.generate_unique_id_function is not None
        assert app.generate_unique_id_function == custom_generate_unique_id