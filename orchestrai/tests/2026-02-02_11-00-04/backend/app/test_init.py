"""Tests for backend/app/__init__.py"""
import pytest


def test_init_module_imports():
    """Test that __init__.py can be imported without errors."""
    # This tests that the module exists and is importable
    # Since __init__.py is empty, we just verify it can be imported
    import app
    assert app is not None