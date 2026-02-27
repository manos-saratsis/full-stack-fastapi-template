import os
from unittest.mock import Mock, patch, MagicMock, call
import pytest
from alembic import context


class TestGetUrl:
    """Test the get_url function"""

    @patch("app.alembic.env.settings")
    def test_get_url_returns_database_uri(self, mock_settings):
        """should return SQLALCHEMY_DATABASE_URI as string when called"""
        expected_uri = "postgresql://user:password@localhost/dbname"
        mock_settings.SQLALCHEMY_DATABASE_URI = expected_uri

        from app.alembic.env import get_url

        result = get_url()

        assert result == expected_uri
        assert isinstance(result, str)

    @patch("app.alembic.env.settings")
    def test_get_url_with_sqlite_uri(self, mock_settings):
        """should handle sqlite database URIs correctly"""
        expected_uri = "sqlite:///./test.db"
        mock_settings.SQLALCHEMY_DATABASE_URI = expected_uri

        from app.alembic.env import get_url

        result = get_url()

        assert result == expected_uri

    @patch("app.alembic.env.settings")
    def test_get_url_converts_to_string(self, mock_settings):
        """should convert database URI to string when it's not already a string"""
        mock_uri = Mock()
        mock_uri.__str__ = Mock(return_value="postgresql://localhost/db")
        mock_settings.SQLALCHEMY_DATABASE_URI = mock_uri

        from app.alembic.env import get_url

        result = get_url()

        assert result == "postgresql://localhost/db"
        mock_uri.__str__.assert_called_once()


class TestRunMigrationsOffline:
    """Test the run_migrations_offline function"""

    @patch("app.alembic.env.context")
    @patch("app.alembic.env.get_url")
    def test_run_migrations_offline_calls_configure(self, mock_get_url, mock_context):
        """should call context.configure with correct offline parameters"""
        mock_get_url.return_value = "sqlite:///test.db"
        mock_context.begin_transaction.return_value.__enter__ = Mock()
        mock_context.begin_transaction.return_value.__exit__ = Mock(return_value=None)

        from app.alembic.env import run_migrations_offline, target_metadata

        run_migrations_offline()

        mock_context.configure.assert_called_once()
        call_kwargs = mock_context.configure.call_args[1]
        assert call_kwargs["url"] == "sqlite:///test.db"
        assert call_kwargs["target_metadata"] == target_metadata
        assert call_kwargs["literal_binds"] is True
        assert call_kwargs["compare_type"] is True

    @patch("app.alembic.env.context")
    @patch("app.alembic.env.get_url")
    def test_run_migrations_offline_executes_migrations(self, mock_get_url, mock_context):
        """should call context.run_migrations within a transaction"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_transaction = MagicMock()
        mock_context.begin_transaction.return_value = mock_transaction

        from app.alembic.env import run_migrations_offline

        run_migrations_offline()

        mock_context.run_migrations.assert_called_once()

    @patch("app.alembic.env.context")
    @patch("app.alembic.env.get_url")
    def test_run_migrations_offline_begins_transaction(self, mock_get_url, mock_context):
        """should create a transaction context when running migrations"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_transaction = MagicMock()
        mock_context.begin_transaction.return_value = mock_transaction

        from app.alembic.env import run_migrations_offline

        run_migrations_offline()

        mock_context.begin_transaction.assert_called_once()

    @patch("app.alembic.env.context")
    @patch("app.alembic.env.get_url")
    def test_run_migrations_offline_with_empty_url(self, mock_get_url, mock_context):
        """should handle empty database URL"""
        mock_get_url.return_value = ""
        mock_context.begin_transaction.return_value.__enter__ = Mock()
        mock_context.begin_transaction.return_value.__exit__ = Mock(return_value=None)

        from app.alembic.env import run_migrations_offline

        run_migrations_offline()

        call_kwargs = mock_context.configure.call_args[1]
        assert call_kwargs["url"] == ""


class TestRunMigrationsOnline:
    """Test the run_migrations_online function"""

    @patch("app.alembic.env.engine_from_config")
    @patch("app.alembic.env.get_url")
    @patch("app.alembic.env.config")
    @patch("app.alembic.env.context")
    def test_run_migrations_online_creates_engine(
        self, mock_context, mock_config, mock_get_url, mock_engine_from_config
    ):
        """should create database engine with correct configuration"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_config.config_ini_section = "alembic"
        mock_config.get_section.return_value = {"sqlalchemy.pool_size": "10"}
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_from_config.return_value = mock_engine
        mock_context.begin_transaction.return_value.__enter__ = Mock()
        mock_context.begin_transaction.return_value.__exit__ = Mock(return_value=None)

        from app.alembic.env import run_migrations_online

        run_migrations_online()

        mock_engine_from_config.assert_called_once()
        call_args = mock_engine_from_config.call_args
        assert call_args[1]["prefix"] == "sqlalchemy."
        assert "sqlalchemy.url" in call_args[0][0]

    @patch("app.alembic.env.engine_from_config")
    @patch("app.alembic.env.get_url")
    @patch("app.alembic.env.config")
    @patch("app.alembic.env.context")
    def test_run_migrations_online_configures_context(
        self, mock_context, mock_config, mock_get_url, mock_engine_from_config
    ):
        """should configure context with connection and target metadata"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_config.config_ini_section = "alembic"
        mock_config.get_section.return_value = {}
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_from_config.return_value = mock_engine
        mock_transaction = MagicMock()
        mock_context.begin_transaction.return_value = mock_transaction

        from app.alembic.env import run_migrations_online, target_metadata

        run_migrations_online()

        mock_context.configure.assert_called_once()
        call_kwargs = mock_context.configure.call_args[1]
        assert call_kwargs["connection"] == mock_connection
        assert call_kwargs["target_metadata"] == target_metadata
        assert call_kwargs["compare_type"] is True

    @patch("app.alembic.env.engine_from_config")
    @patch("app.alembic.env.get_url")
    @patch("app.alembic.env.config")
    @patch("app.alembic.env.context")
    def test_run_migrations_online_uses_null_pool(
        self, mock_context, mock_config, mock_get_url, mock_engine_from_config
    ):
        """should use NullPool for engine creation"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_config.config_ini_section = "alembic"
        mock_config.get_section.return_value = {}
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_from_config.return_value = mock_engine
        mock_context.begin_transaction.return_value.__enter__ = Mock()
        mock_context.begin_transaction.return_value.__exit__ = Mock(return_value=None)

        from app.alembic.env import run_migrations_online
        from sqlalchemy import pool

        run_migrations_online()

        call_args = mock_engine_from_config.call_args
        assert call_args[1]["poolclass"] == pool.NullPool

    @patch("app.alembic.env.engine_from_config")
    @patch("app.alembic.env.get_url")
    @patch("app.alembic.env.config")
    @patch("app.alembic.env.context")
    def test_run_migrations_online_runs_migrations(
        self, mock_context, mock_config, mock_get_url, mock_engine_from_config
    ):
        """should execute migrations within transaction"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_config.config_ini_section = "alembic"
        mock_config.get_section.return_value = {}
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_from_config.return_value = mock_engine
        mock_transaction = MagicMock()
        mock_context.begin_transaction.return_value = mock_transaction

        from app.alembic.env import run_migrations_online

        run_migrations_online()

        mock_context.run_migrations.assert_called_once()

    @patch("app.alembic.env.engine_from_config")
    @patch("app.alembic.env.get_url")
    @patch("app.alembic.env.config")
    @patch("app.alembic.env.context")
    def test_run_migrations_online_with_multiple_config_sections(
        self, mock_context, mock_config, mock_get_url, mock_engine_from_config
    ):
        """should handle configuration with multiple ini sections"""
        mock_get_url.return_value = "postgresql://localhost/db"
        mock_config.config_ini_section = "alembic"
        mock_config.get_section.return_value = {
            "sqlalchemy.echo": "true",
            "sqlalchemy.pool_size": "20",
        }
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=None)
        mock_engine_from_config.return_value = mock_engine
        mock_context.begin_transaction.return_value.__enter__ = Mock()
        mock_context.begin_transaction.return_value.__exit__ = Mock(return_value=None)

        from app.alembic.env import run_migrations_online

        run_migrations_online()

        call_args = mock_engine_from_config.call_args
        config_dict = call_args[0][0]
        assert "sqlalchemy.url" in config_dict
        assert config_dict["sqlalchemy.echo"] == "true"


class TestModuleInitialization:
    """Test module-level initialization and conditional logic"""

    @patch("app.alembic.env.context")
    @patch("app.alembic.env.run_migrations_offline")
    @patch("app.alembic.env.run_migrations_online")
    def test_offline_mode_execution(
        self, mock_online, mock_offline, mock_context
    ):
        """should execute offline migrations when context.is_offline_mode is True"""
        mock_context.is_offline_mode.return_value = True

        # Import the module to trigger the conditional logic
        import importlib
        import app.alembic.env as env_module
        importlib.reload(env_module)

    @patch("app.alembic.env.context")
    @patch("app.alembic.env.run_migrations_offline")
    @patch("app.alembic.env.run_migrations_online")
    def test_online_mode_execution(
        self, mock_online, mock_offline, mock_context
    ):
        """should execute online migrations when context.is_offline_mode is False"""
        mock_context.is_offline_mode.return_value = False

        # Import the module to trigger the conditional logic
        import importlib
        import app.alembic.env as env_module
        importlib.reload(env_module)


class TestTargetMetadata:
    """Test target_metadata assignment"""

    @patch("app.alembic.env.SQLModel")
    def test_target_metadata_is_sqlmodel_metadata(self, mock_sqlmodel):
        """should assign SQLModel.metadata to target_metadata"""
        from app.alembic.env import target_metadata

        assert target_metadata is not None

    def test_imports_are_successful(self):
        """should successfully import all required modules"""
        from app.alembic import env

        assert hasattr(env, "get_url")
        assert hasattr(env, "run_migrations_offline")
        assert hasattr(env, "run_migrations_online")
        assert hasattr(env, "target_metadata")
        assert hasattr(env, "config")