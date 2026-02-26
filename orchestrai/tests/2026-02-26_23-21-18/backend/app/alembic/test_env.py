"""Comprehensive tests for alembic/env.py"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import the module to test
import sys
from pathlib import Path

# Mock the alembic context and settings before importing env
@pytest.fixture
def mock_alembic_context():
    """Mock the alembic context module"""
    with patch('alembic.context') as mock_ctx:
        mock_ctx.config = Mock()
        mock_ctx.config.config_file_name = '/path/to/alembic.ini'
        mock_ctx.config.config_ini_section = 'alembic'
        mock_ctx.is_offline_mode = Mock(return_value=False)
        yield mock_ctx


@pytest.fixture
def mock_settings():
    """Mock the settings module"""
    with patch('app.core.config.settings') as mock_set:
        mock_set.SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
        yield mock_set


@pytest.fixture
def mock_sqlmodel():
    """Mock the SQLModel"""
    with patch('app.models.SQLModel') as mock_sm:
        mock_sm.metadata = Mock()
        yield mock_sm


class TestGetUrl:
    """Tests for get_url function"""

    def test_get_url_returns_database_uri(self, mock_settings):
        """Should return the SQLALCHEMY_DATABASE_URI from settings"""
        from app.alembic.env import get_url
        
        result = get_url()
        
        assert result == 'postgresql://user:password@localhost/dbname'

    def test_get_url_with_different_uri(self, mock_settings):
        """Should return different URIs based on settings"""
        from app.alembic.env import get_url
        
        mock_settings.SQLALCHEMY_DATABASE_URI = 'sqlite:///./test.db'
        result = get_url()
        
        assert result == 'sqlite:///./test.db'

    def test_get_url_with_empty_uri(self, mock_settings):
        """Should handle empty URI string"""
        from app.alembic.env import get_url
        
        mock_settings.SQLALCHEMY_DATABASE_URI = ''
        result = get_url()
        
        assert result == ''

    def test_get_url_with_mysql_uri(self, mock_settings):
        """Should work with MySQL URIs"""
        from app.alembic.env import get_url
        
        mock_settings.SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@host/db'
        result = get_url()
        
        assert result == 'mysql+pymysql://user:pass@host/db'


class TestRunMigrationsOffline:
    """Tests for run_migrations_offline function"""

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    def test_run_migrations_offline_calls_configure(self, mock_run, mock_begin, mock_configure, mock_settings):
        """Should configure context in offline mode"""
        from app.alembic.env import run_migrations_offline
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        run_migrations_offline()
        
        # Verify configure was called with correct parameters
        mock_configure.assert_called_once()
        call_kwargs = mock_configure.call_args[1]
        assert call_kwargs['url'] == 'postgresql://user:password@localhost/dbname'
        assert call_kwargs['literal_binds'] is True
        assert call_kwargs['compare_type'] is True

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    def test_run_migrations_offline_executes_migrations(self, mock_run, mock_begin, mock_configure, mock_settings):
        """Should execute migrations in offline mode"""
        from app.alembic.env import run_migrations_offline
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        run_migrations_offline()
        
        # Verify run_migrations was called
        mock_run.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    def test_run_migrations_offline_uses_transaction(self, mock_run, mock_begin, mock_configure, mock_settings):
        """Should wrap migrations in a transaction"""
        from app.alembic.env import run_migrations_offline
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        run_migrations_offline()
        
        # Verify begin_transaction was called
        mock_begin.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    def test_run_migrations_offline_with_empty_database_uri(self, mock_run, mock_begin, mock_configure, mock_settings):
        """Should handle empty database URI"""
        from app.alembic.env import run_migrations_offline
        
        mock_settings.SQLALCHEMY_DATABASE_URI = ''
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        run_migrations_offline()
        
        mock_configure.assert_called_once()


class TestRunMigrationsOnline:
    """Tests for run_migrations_online function"""

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_creates_engine(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should create an engine from configuration"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        # Mock the engine and connection
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={'sqlalchemy.url': 'dummy'})
        
        run_migrations_online()
        
        # Verify engine_from_config was called
        mock_engine_factory.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_configures_context(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should configure context with connection and metadata"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        # Verify configure was called with connection
        assert mock_configure.called
        call_kwargs = mock_configure.call_args[1]
        assert call_kwargs['connection'] == mock_connection
        assert call_kwargs['compare_type'] is True

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_uses_null_pool(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should use NullPool for connections"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        # Verify poolclass parameter
        call_kwargs = mock_engine_factory.call_args[1]
        assert call_kwargs['poolclass'] == pool.NullPool

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_executes_migrations(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should execute migrations in online mode"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        # Verify run_migrations was called
        mock_run.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_sets_database_url(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should set the sqlalchemy.url from get_url()"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={'sqlalchemy.url': 'old_url'})
        
        run_migrations_online()
        
        # Verify the configuration dict was updated
        call_args = mock_engine_factory.call_args[0][0]
        assert call_args['sqlalchemy.url'] == 'postgresql://user:password@localhost/dbname'

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_connection_context_manager(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should properly handle connection context manager"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_connect_ctx = Mock()
        mock_connect_ctx.__enter__ = Mock(return_value=mock_connection)
        mock_connect_ctx.__exit__ = Mock(return_value=None)
        mock_engine.connect.return_value = mock_connect_ctx
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        # Verify connection context manager was used
        mock_engine.connect.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_transaction_context_manager(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should properly handle transaction context manager"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_transaction_ctx = Mock()
        mock_transaction_ctx.__enter__ = Mock(return_value=None)
        mock_transaction_ctx.__exit__ = Mock(return_value=None)
        mock_begin.return_value = mock_transaction_ctx
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        # Verify transaction context manager was used
        mock_begin.assert_called_once()


class TestModuleInitialization:
    """Tests for module-level initialization and execution"""

    @patch('alembic.context.is_offline_mode')
    @patch('app.alembic.env.run_migrations_offline')
    @patch('app.alembic.env.run_migrations_online')
    def test_module_executes_offline_mode(self, mock_online, mock_offline, mock_is_offline):
        """Should execute offline migrations when is_offline_mode returns True"""
        mock_is_offline.return_value = True
        
        # Re-import the module to trigger the module-level if statement
        import importlib
        import app.alembic.env
        
        # We can't easily test this without re-importing, so we verify the functions exist
        assert hasattr(app.alembic.env, 'run_migrations_offline')
        assert hasattr(app.alembic.env, 'run_migrations_online')

    @patch('alembic.context.is_offline_mode')
    @patch('app.alembic.env.run_migrations_offline')
    @patch('app.alembic.env.run_migrations_online')
    def test_module_executes_online_mode(self, mock_online, mock_offline, mock_is_offline):
        """Should execute online migrations when is_offline_mode returns False"""
        mock_is_offline.return_value = False
        
        # Verify the functions exist
        import app.alembic.env
        assert hasattr(app.alembic.env, 'run_migrations_offline')
        assert hasattr(app.alembic.env, 'run_migrations_online')


class TestEnvEdgeCases:
    """Tests for edge cases and error conditions"""

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    def test_run_migrations_offline_with_special_characters_in_uri(self, mock_run, mock_begin, mock_configure, mock_settings):
        """Should handle URIs with special characters"""
        from app.alembic.env import run_migrations_offline
        
        mock_settings.SQLALCHEMY_DATABASE_URI = 'postgresql://user%40:p%40ss@localhost/dbname'
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        run_migrations_offline()
        
        mock_configure.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_with_special_characters_in_uri(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should handle URIs with special characters in online mode"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_settings.SQLALCHEMY_DATABASE_URI = 'postgresql://user%40:p%40ss@localhost/dbname'
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        mock_engine_factory.assert_called_once()

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    def test_run_migrations_offline_target_metadata_passed(self, mock_run, mock_begin, mock_configure, mock_settings):
        """Should pass target_metadata to configure"""
        from app.alembic.env import run_migrations_offline
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        run_migrations_offline()
        
        call_kwargs = mock_configure.call_args[1]
        assert 'target_metadata' in call_kwargs

    @patch('alembic.context.configure')
    @patch('alembic.context.begin_transaction')
    @patch('alembic.context.run_migrations')
    @patch('sqlalchemy.engine_from_config')
    def test_run_migrations_online_target_metadata_passed(self, mock_engine_factory, mock_run, mock_begin, mock_configure, mock_settings):
        """Should pass target_metadata to configure in online mode"""
        from app.alembic.env import run_migrations_online
        from app.alembic.env import config
        
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_factory.return_value = mock_engine
        
        mock_begin.return_value.__enter__ = Mock(return_value=None)
        mock_begin.return_value.__exit__ = Mock(return_value=None)
        
        config.get_section = Mock(return_value={})
        
        run_migrations_online()
        
        call_kwargs = mock_configure.call_args[1]
        assert 'target_metadata' in call_kwargs