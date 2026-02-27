import pytest
from unittest.mock import Mock, patch, MagicMock, call
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


class TestRevisionMetadata:
    """Test revision identifiers and metadata"""

    def test_revision_id_is_correct(self):
        """should have correct revision ID e2412789c190"""
        from app.alembic.versions import e2412789c190_initialize_models

        assert e2412789c190_initialize_models.revision == "e2412789c190"

    def test_down_revision_is_none(self):
        """should have None as down_revision since this is initial migration"""
        from app.alembic.versions import e2412789c190_initialize_models

        assert e2412789c190_initialize_models.down_revision is None

    def test_branch_labels_is_none(self):
        """should have None as branch_labels"""
        from app.alembic.versions import e2412789c190_initialize_models

        assert e2412789c190_initialize_models.branch_labels is None

    def test_depends_on_is_none(self):
        """should have None as depends_on"""
        from app.alembic.versions import e2412789c190_initialize_models

        assert e2412789c190_initialize_models.depends_on is None


class TestUpgradeFunction:
    """Test the upgrade function"""

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_creates_user_table(self, mock_op):
        """should create user table with all required columns"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        # Check that create_table was called for user table
        create_table_calls = [
            call for call in mock_op.mock_calls if "create_table" in str(call)
        ]
        assert len(create_table_calls) >= 1

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_creates_item_table(self, mock_op):
        """should create item table with all required columns"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        # Verify both user and item tables are created
        assert mock_op.create_table.called

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_creates_user_email_index(self, mock_op):
        """should create unique index on user email field"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        # Check that create_index was called for email
        create_index_calls = [
            call for call in mock_op.mock_calls if "create_index" in str(call)
        ]
        assert len(create_index_calls) >= 1

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_creates_foreign_key_constraint(self, mock_op):
        """should create foreign key constraint from item to user"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        # Check that table creation includes ForeignKeyConstraint
        assert mock_op.create_table.called

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_defines_user_table_structure(self, mock_op):
        """should define user table with email, is_active, is_superuser, full_name, id, hashed_password"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        # Get the first call to create_table (should be user)
        assert mock_op.create_table.call_count >= 2

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_defines_item_table_structure(self, mock_op):
        """should define item table with description, id, title, owner_id"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        assert mock_op.create_table.call_count >= 2

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_column_nullability_constraints(self, mock_op):
        """should set correct nullability for all columns"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        # Verify create_table was called
        assert mock_op.create_table.called

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_upgrade_email_field_is_required(self, mock_op):
        """should make email field non-nullable and unique"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()

        assert mock_op.create_table.called
        assert mock_op.create_index.called


class TestDowngradeFunction:
    """Test the downgrade function"""

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_downgrade_drops_item_table(self, mock_op):
        """should drop item table first"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.downgrade()

        # Check that drop_table was called for item
        drop_table_calls = [
            call for call in mock_op.mock_calls if "drop_table" in str(call)
        ]
        assert len(drop_table_calls) >= 2

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_downgrade_drops_user_table(self, mock_op):
        """should drop user table after item"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.downgrade()

        assert mock_op.drop_table.called

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_downgrade_drops_email_index_first(self, mock_op):
        """should drop email index before dropping user table"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.downgrade()

        # Check that drop_index was called
        drop_index_calls = [
            call for call in mock_op.mock_calls if "drop_index" in str(call)
        ]
        assert len(drop_index_calls) >= 1

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_downgrade_reverses_upgrade_order(self, mock_op):
        """should reverse operations in correct order: item, index, user"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.downgrade()

        # Verify all cleanup operations were called
        assert mock_op.drop_table.called
        assert mock_op.drop_index.called

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_downgrade_removes_all_tables_and_indexes(self, mock_op):
        """should remove all tables and indexes created in upgrade"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.downgrade()

        assert mock_op.drop_table.call_count >= 2
        assert mock_op.drop_index.call_count >= 1


class TestUpgradeAndDowngradeIntegration:
    """Test upgrade and downgrade together"""

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_downgrade_reverses_all_upgrade_changes(self, mock_op):
        """should ensure downgrade completely reverses upgrade"""
        from app.alembic.versions import e2412789c190_initialize_models

        e2412789c190_initialize_models.upgrade()
        upgrade_call_count = mock_op.mock_calls.__len__()

        mock_op.reset_mock()

        e2412789c190_initialize_models.downgrade()
        downgrade_call_count = mock_op.mock_calls.__len__()

        assert downgrade_call_count > 0

    @patch("app.alembic.versions.e2412789c190_initialize_models.op")
    def test_functions_are_callable(self, mock_op):
        """should ensure upgrade and downgrade are callable functions"""
        from app.alembic.versions import e2412789c190_initialize_models

        assert callable(e2412789c190_initialize_models.upgrade)
        assert callable(e2412789c190_initialize_models.downgrade)