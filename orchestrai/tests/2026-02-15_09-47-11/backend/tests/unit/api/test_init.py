import pytest
from unittest.mock import patch, MagicMock
from fastapi import APIRouter

from app.api.main import api_router
from app.core.config import settings


class TestApiInit:
    """Test api/__init__.py module."""

    def test_api_init_is_importable(self):
        """should be able to import api module"""
        import app.api
        assert app.api is not None

    def test_api_init_file_exists(self):
        """should have __init__.py file"""
        import app.api
        assert hasattr(app.api, '__file__')
        assert app.api.__file__.endswith('__init__.py')