import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app.crud import (
    authenticate,
    create_item,
    create_user,
    get_user_by_email,
    update_user,
)
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate


class TestCreateUser:
    """Test create_user function."""

    @patch("app.crud.get_password_hash")
    def test_create_user_success(self, mock_hash):
        """Test creating a user successfully."""
        mock_hash.return_value = "hashed_password"
        mock_session = MagicMock(spec=Session)

        user_create = UserCreate(
            email="user@example.com",
            password="password123",
            full_name="John Doe",
        )

        result = create_user(session=mock_session, user_create=user_create)

        assert result.email == "user@example.com"
        assert result.hashed_password == "hashed_password"
        assert result.full_name == "John Doe"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("app.crud.get_password_hash")
    def test_create_user_minimal(self, mock_hash):
        """Test creating user with minimal fields."""
        mock_hash.return_value = "hashed_password"
        mock_session = MagicMock(spec=Session)

        user_create = UserCreate(
            email="user@example.com",
            password="password123",
        )

        result = create_user(session=mock_session, user_create=user_create)

        assert result.email == "user@example.com"
        assert result.full_name is None
        assert result.is_active is True
        assert result.is_superuser is False

    @patch("app.crud.get_password_hash")
    def test_create_user_with_superuser_flag(self, mock_hash):
        """Test creating superuser."""
        mock_hash.return_value = "hashed_password"
        mock_session = MagicMock(spec=Session)

        user_create = UserCreate(
            email="admin@example.com",
            password="password123",
            is_superuser=True,
        )

        result = create_user(session=mock_session, user_create=user_create)

        assert result.is_superuser is True

    @patch("app.crud.get_password_hash")
    def test_create_user_password_hashing(self, mock_hash):
        """Test that password is hashed during user creation."""
        mock_hash.return_value = "hashed_password"
        mock_session = MagicMock(spec=Session)

        user_create = UserCreate(
            email="user@example.com",
            password="cleartext_password",
        )

        create_user(session=mock_session, user_create=user_create)

        mock_hash.assert_called_once_with("cleartext_password")

    @patch("app.crud.get_password_hash")
    def test_create_user_session_operations_order(self, mock_hash):
        """Test session operations are called in correct order."""
        mock_hash.return_value = "hashed_password"
        mock_session = MagicMock(spec=Session)

        user_create = UserCreate(
            email="user@example.com",
            password="password123",
        )

        create_user(session=mock_session, user_create=user_create)

        # Verify order of calls
        assert mock_session.method_calls[0][0] == "add"
        assert mock_session.method_calls[1][0] == "commit"
        assert mock_session.method_calls[2][0] == "refresh"


class TestUpdateUser:
    """Test update_user function."""

    @patch("app.crud.get_password_hash")
    def test_update_user_email_only(self, mock_hash):
        """Test updating user email only."""
        mock_session = MagicMock(spec=Session)
        db_user = User(
            id=uuid.uuid4(),
            email="old@example.com",
            hashed_password="old_hash",
        )

        user_in = UserUpdate(email="new@example.com")

        result = update_user(session=mock_session, db_user=db_user, user_in=user_in)

        assert result.email == "new@example.com"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("app.crud.get_password_hash")
    def test_update_user_password_only(self, mock_hash):
        """Test updating user password only."""
        mock_hash.return_value = "new_hashed_password"
        mock_session = MagicMock(spec=Session)
        db_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            hashed_password="old_hash",
        )

        user_in = UserUpdate(password="newpassword123")

        result = update_user(session=mock_session, db_user=db_user, user_in=user_in)

        mock_hash.assert_called_once_with("newpassword123")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("app.crud.get_password_hash")
    def test_update_user_multiple_fields(self, mock_hash):
        """Test updating multiple fields."""
        mock_hash.return_value = "new_hashed_password"
        mock_session = MagicMock(spec=Session)
        db_user = User(
            id=uuid.uuid4(),
            email="old@example.com",
            hashed_password="old_hash",
            full_name="Old Name",
        )

        user_in = UserUpdate(
            email="new@example.com",
            password="newpassword123",
            full_name="New Name",
            is_active=False,
        )

        result = update_user(session=mock_session, db_user=db_user, user_in=user_in)

        assert result.email == "new@example.com"
        assert result.full_name == "New Name"
        assert result.is_active is False

    @patch("app.crud.get_password_hash")
    def test_update_user_no_changes(self, mock_hash):
        """Test update with no fields changed."""
        mock_session = MagicMock(spec=Session)
        db_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            hashed_password="hash",
        )

        user_in = UserUpdate()

        result = update_user(session=mock_session, db_user=db_user, user_in=user_in)

        assert result.email == "user@example.com"
        mock_hash.assert_not_called()

    @patch("app.crud.get_password_hash")
    def test_update_user_partial_update(self, mock_hash):
        """Test partial update only sets specified fields."""
        mock_hash.return_value = "new_hash"
        mock_session = MagicMock(spec=Session)
        db_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            hashed_password="old_hash",
            full_name="Original Name",
            is_active=True,
        )

        user_in = UserUpdate(full_name="New Name")

        result = update_user(session=mock_session, db_user=db_user, user_in=user_in)

        assert result.full_name == "New Name"
        assert result.is_active is True
        mock_hash.assert_not_called()

    @patch("app.crud.get_password_hash")
    def test_update_user_all_fields(self, mock_hash):
        """Test updating all possible fields."""
        mock_hash.return_value = "new_hashed_password"
        mock_session = MagicMock(spec=Session)
        db_user = User(
            id=uuid.uuid4(),
            email="old@example.com",
            hashed_password="old_hash",
            full_name="Old Name",
            is_active=True,
            is_superuser=False,
        )

        user_in = UserUpdate(
            email="new@example.com",
            password="newpassword123",
            full_name="New Name",
            is_active=False,
            is_superuser=True,
        )

        result = update_user(session=mock_session, db_user=db_user, user_in=user_in)

        assert result.email == "new@example.com"
        assert result.full_name == "New Name"
        assert result.is_active is False
        assert result.is_superuser is True


class TestGetUserByEmail:
    """Test get_user_by_email function."""

    def test_get_user_by_email_found(self):
        """Test getting user by email when user exists."""
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        expected_user = User(
            id=user_id,
            email="user@example.com",
            hashed_password="hash",
        )

        mock_exec = MagicMock()
        mock_exec.first.return_value = expected_user
        mock_session.exec.return_value = mock_exec

        result = get_user_by_email(session=mock_session, email="user@example.com")

        assert result == expected_user
        assert result.email == "user@example.com"
        mock_session.exec.assert_called_once()

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user does not exist."""