import pytest


class TestCoreInit:
    """Test core/__init__.py exports."""

    def test_core_init_is_empty(self):
        """should verify core/__init__.py is properly formed"""
        # core/__init__.py is empty, which is valid
        # This test verifies the file exists and can be imported
        from app import core
        assert hasattr(core, '__file__')
        assert core.__file__.endswith('__init__.py')

    def test_core_module_importable(self):
        """should be able to import core module"""
        import app.core
        assert app.core is not None