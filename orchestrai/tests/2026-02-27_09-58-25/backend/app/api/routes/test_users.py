import uuid
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.api.routes.users import (
    create_user,
    delete_user,
    delete_user_me,
    read_user_by_id,
    read_user_me,
    read_users,
    register_user,
    update_password_me,
    update_user,
    update_user_me,
)
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user() -> User:
    """Create a mock user."""
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def mock_superuser() -> User:
    """Create a mock superuser."""
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        full_name="Admin User",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True,
    )


@pytest.fixture
def mock_user_create() -> UserCreate:
    """Create a UserCreate object."""
    return UserCreate(
        email="newuser@example.com",
        password="password123",
        full_name="New User",
    )


@pytest.fixture
def mock_user_register() -> UserRegister:
    """Create a UserRegister object."""
    return UserRegister(
        email="signup@example.com",
        password="password123",
        full_name="Signup User",
    )


class TestReadUsers:
    """Tests for read_users endpoint."""

    def test_read_users_success(self, mock_session: MagicMock, mock_user: User) -> None:
        """Test successfully reading users list."""
        mock_session.exec.side_effect = [
            MagicMock(one=MagicMock(return_value=1)),  # count
            MagicMock(all=MagicMock(return_value=[mock_user])),  # users
        ]

        result = read_users(session=mock_session, skip=0, limit=100)

        assert isinstance(result, UsersPublic)
        assert result.count == 1
        assert len(result.data) == 1
        assert result.data[0].id == mock_user.id

    def test_read_users_with_skip_and_limit(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test reading users with custom skip and limit."""
        mock_session.exec.side_effect = [
            MagicMock(one=MagicMock(return_value=10)),  # count
            MagicMock(all=MagicMock(return_value=[mock_user])),  # users
        ]

        result = read_users(session=mock_session, skip=5, limit=50)

        assert result.count == 10
        assert len(result.data) == 1

    def test_read_users_empty(self, mock_session: MagicMock) -> None:
        """Test reading users when no users exist."""
        mock_session.exec.side_effect = [
            MagicMock(one=MagicMock(return_value=0)),  # count
            MagicMock(all=MagicMock(return_value=[])),  # users
        ]

        result = read_users(session=mock_session, skip=0, limit=100)

        assert result.count == 0
        assert len(result.data) == 0


class TestCreateUser:
    """Tests for create_user endpoint."""

    @patch("app.api.routes.users.crud.get_user_by_email")
    @patch("app.api.routes.users.crud.create_user")
    def test_create_user_success(
        self,
        mock_crud_create: MagicMock,
        mock_crud_get: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
        mock_user_create: UserCreate,
    ) -> None:
        """Test successfully creating a new user."""
        mock_crud_get.return_value = None
        mock_crud_create.return_value = mock_user

        with patch("app.api.routes.users.settings.emails_enabled", False):
            result = create_user(session=mock_session, user_in=mock_user_create)

        assert result.id == mock_user.id
        assert result.email == mock_user.email
        mock_crud_get.assert_called_once()
        mock_crud_create.assert_called_once()

    @patch("app.api.routes.users.crud.get_user_by_email")
    def test_create_user_already_exists(
        self,
        mock_crud_get: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
        mock_user_create: UserCreate,
    ) -> None:
        """Test creating a user that already exists."""
        mock_crud_get.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            create_user(session=mock_session, user_in=mock_user_create)

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @patch("app.api.routes.users.crud.get_user_by_email")
    @patch("app.api.routes.users.crud.create_user")
    @patch("app.api.routes.users.send_email")
    @patch("app.api.routes.users.generate_new_account_email")
    def test_create_user_with_email_enabled(
        self,
        mock_gen_email: MagicMock,
        mock_send_email: MagicMock,
        mock_crud_create: MagicMock,
        mock_crud_get: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
        mock_user_create: UserCreate,
    ) -> None:
        """Test creating a user with email sending enabled."""
        mock_crud_get.return_value = None
        mock_crud_create.return_value = mock_user
        mock_gen_email.return_value = MagicMock(
            subject="Welcome", html_content="<p>Welcome</p>"
        )

        with patch("app.api.routes.users.settings.emails_enabled", True):
            result = create_user(session=mock_session, user_in=mock_user_create)

        assert result.id == mock_user.id
        mock_send_email.assert_called_once()
        mock_gen_email.assert_called_once_with(
            email_to=mock_user_create.email,
            username=mock_user_create.email,
            password=mock_user_create.password,
        )

    @patch("app.api.routes.users.crud.get_user_by_email")
    @patch("app.api.routes.users.crud.create_user")
    def test_create_user_with_email_disabled(
        self,
        mock_crud_create: MagicMock,
        mock_crud_get: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
        mock_user_create: UserCreate,
    ) -> None:
        """Test creating a user with email sending disabled."""
        mock_crud_get.return_value = None
        mock_crud_create.return_value = mock_user

        with patch("app.api.routes.users.settings.emails_enabled", False):
            with patch(
                "app.api.routes.users.send_email"
            ) as mock_send_email:
                result = create_user(session=mock_session, user_in=mock_user_create)

                assert result.id == mock_user.id
                mock_send_email.assert_not_called()


class TestUpdateUserMe:
    """Tests for update_user_me endpoint."""

    def test_update_user_me_success(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test successfully updating current user."""
        user_update = UserUpdateMe(email="newemail@example.com", full_name="New Name")
        mock_session.exec.return_value.all.return_value = []

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get:
            mock_get.return_value = None
            result = update_user_me(
                session=mock_session, user_in=user_update, current_user=mock_user
            )

        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called

    def test_update_user_me_email_exists(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test updating user with email that already exists."""
        other_user = User(
            id=uuid.uuid4(),
            email="existing@example.com",
            full_name="Other User",
            hashed_password="hash",
            is_active=True,
            is_superuser=False,
        )
        user_update = UserUpdateMe(email="existing@example.com")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get:
            mock_get.return_value = other_user

            with pytest.raises(HTTPException) as exc_info:
                update_user_me(
                    session=mock_session, user_in=user_update, current_user=mock_user
                )

            assert exc_info.value.status_code == 409
            assert "already exists" in exc_info.value.detail

    def test_update_user_me_same_email(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test updating user with the same email."""
        user_update = UserUpdateMe(email=mock_user.email)

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get:
            mock_get.return_value = mock_user

            result = update_user_me(
                session=mock_session, user_in=user_update, current_user=mock_user
            )

            assert mock_session.add.called

    def test_update_user_me_no_email(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test updating user without changing email."""
        user_update = UserUpdateMe(full_name="Updated Name")

        result = update_user_me(
            session=mock_session, user_in=user_update, current_user=mock_user
        )

        assert mock_session.add.called
        assert mock_session.commit.called


class TestUpdatePasswordMe:
    """Tests for update_password_me endpoint."""

    @patch("app.api.routes.users.verify_password")
    @patch("app.api.routes.users.get_password_hash")
    def test_update_password_me_success(
        self,
        mock_hash: MagicMock,
        mock_verify: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test successfully updating password."""
        mock_verify.return_value = True
        mock_hash.return_value = "new_hashed_password"

        password_update = UpdatePassword(
            current_password="currentpass", new_password="newpass123"
        )

        result = update_password_me(
            session=mock_session, body=password_update, current_user=mock_user
        )

        assert result.message == "Password updated successfully"
        assert mock_session.add.called
        assert mock_session.commit.called
        mock_verify.assert_called_once_with(
            "currentpass", mock_user.hashed_password
        )
        mock_hash.assert_called_once_with("newpass123")

    @patch("app.api.routes.users.verify_password")
    def test_update_password_me_incorrect_current(
        self,
        mock_verify: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test updating password with incorrect current password."""
        mock_verify.return_value = False

        password_update = UpdatePassword(
            current_password="wrongpass", new_password="newpass123"
        )

        with pytest.raises(HTTPException) as exc_info:
            update_password_me(
                session=mock_session, body=password_update, current_user=mock_user
            )

        assert exc_info.value.status_code == 400
        assert "Incorrect password" in exc_info.value.detail

    @patch("app.api.routes.users.verify_password")
    def test_update_password_me_same_as_current(
        self,
        mock_verify: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test updating password with same as current password."""
        mock_verify.return_value = True

        password_update = UpdatePassword(
            current_password="samepass", new_password="samepass"
        )

        with pytest.raises(HTTPException) as exc_info:
            update_password_me(
                session=mock_session, body=password_update, current_user=mock_user
            )

        assert exc_info.value.status_code == 400
        assert "cannot be the same" in exc_info.value.detail


class TestReadUserMe:
    """Tests for read_user_me endpoint."""

    def test_read_user_me_success(self, mock_user: User) -> None:
        """Test successfully reading current user."""
        result = read_user_me(current_user=mock_user)

        assert result.id == mock_user.id
        assert result.email == mock_user.email


class TestDeleteUserMe:
    """Tests for delete_user_me endpoint."""

    def test_delete_user_me_success(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test successfully deleting current user."""
        result = delete_user_me(session=mock_session, current_user=mock_user)

        assert result.message == "User deleted successfully"
        assert mock_session.delete.called
        assert mock_session.commit.called

    def test_delete_user_me_superuser_cannot_delete(
        self, mock_session: MagicMock, mock_superuser: User
    ) -> None:
        """Test that superuser cannot delete themselves."""
        with pytest.raises(HTTPException) as exc_info:
            delete_user_me(session=mock_session, current_user=mock_superuser)

        assert exc_info.value.status_code == 403
        assert "Super users are not allowed" in exc_info.value.detail


class TestRegisterUser:
    """Tests for register_user endpoint."""

    @patch("app.api.routes.users.crud.get_user_by_email")
    @patch("app.api.routes.users.crud.create_user")
    def test_register_user_success(
        self,
        mock_crud_create: MagicMock,
        mock_crud_get: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
        mock_user_register: UserRegister,
    ) -> None:
        """Test successfully registering a new user."""
        mock_crud_get.return_value = None
        mock_crud_create.return_value = mock_user

        result = register_user(session=mock_session, user_in=mock_user_register)

        assert result.id == mock_user.id
        mock_crud_get.assert_called_once_with(
            session=mock_session, email=mock_user_register.email
        )
        mock_crud_create.assert_called_once()

    @patch("app.api.routes.users.crud.get_user_by_email")
    def test_register_user_already_exists(
        self,
        mock_crud_get: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
        mock_user_register: UserRegister,
    ) -> None:
        """Test registering a user that already exists."""
        mock_crud_get.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            register_user(session=mock_session, user_in=mock_user_register)

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail


class TestReadUserById:
    """Tests for read_user_by_id endpoint."""

    def test_read_user_by_id_own_user(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test reading own user by ID."""
        mock_session.get.return_value = mock_user

        result = read_user_by_id(
            user_id=mock_user.id, session=mock_session, current_user=mock_user
        )

        assert result.id == mock_user.id
        mock_session.get.assert_called_once_with(User, mock_user.id)

    def test_read_user_by_id_other_user_as_superuser(
        self, mock_session: MagicMock, mock_user: User, mock_superuser: User
    ) -> None:
        """Test reading other user by ID as superuser."""
        mock_session.get.return_value = mock_user

        result = read_user_by_id(
            user_id=mock_user.id, session=mock_session, current_user=mock_superuser
        )

        assert result.id == mock_user.id

    def test_read_user_by_id_other_user_as_regular_user(
        self, mock_session: MagicMock, mock_user: User
    ) -> None:
        """Test reading other user by ID as regular user."""
        other_user = User(
            id=uuid.uuid4(),
            email="other@example.com",
            full_name="Other User",
            hashed_password="hash",
            is_active=True,
            is_superuser=False,
        )
        mock_session.get.return_value = other_user

        with pytest.raises(HTTPException) as exc_info:
            read_user_by_id(
                user_id=other_user.id, session=mock_session, current_user=mock_user
            )

        assert exc_info.value.status_code == 403
        assert "doesn't have enough privileges" in exc_info.value.detail


class TestUpdateUser:
    """Tests for update_user endpoint."""

    @patch("app.api.routes.users.crud.update_user")
    @patch("app.api.routes.users.crud.get_user_by_email")
    def test_update_user_success(
        self,
        mock_crud_get_email: MagicMock,
        mock_crud_update: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test successfully updating a user."""
        user_update = UserUpdate(email="updated@example.com", full_name="Updated")
        mock_session.get.return_value = mock_user
        mock_crud_get_email.return_value = None
        mock_crud_update.return_value = mock_user

        result = update_user(
            session=mock_session, user_id=mock_user.id, user_in=user_update
        )

        assert result.id == mock_user.id
        mock_crud_update.assert_called_once()

    def test_update_user_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test updating a user that doesn't exist."""
        user_id = uuid.uuid4()
        mock_session.get.return_value = None
        user_update = UserUpdate(email="updated@example.com")

        with pytest.raises(HTTPException) as exc_info:
            update_user(
                session=mock_session, user_id=user_id, user_in=user_update
            )

        assert exc_info.value.status_code == 404
        assert "does not exist" in exc_info.value.detail

    @patch("app.api.routes.users.crud.get_user_by_email")
    def test_update_user_email_exists(
        self,
        mock_crud_get_email: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test updating user with email that already exists."""
        other_user = User(
            id=uuid.uuid4(),
            email="existing@example.com",
            full_name="Other User",
            hashed_password="hash",
            is_active=True,
            is_superuser=False,
        )
        mock_session.get.return_value = mock_user
        mock_crud_get_email.return_value = other_user
        user_update = UserUpdate(email="existing@example.com")

        with pytest.raises(HTTPException) as exc_info:
            update_user(
                session=mock_session, user_id=mock_user.id, user_in=user_update
            )

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail

    @patch("app.api.routes.users.crud.update_user")
    @patch("app.api.routes.users.crud.get_user_by_email")
    def test_update_user_same_email(
        self,
        mock_crud_get_email: MagicMock,
        mock_crud_update: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test updating user with the same email."""
        mock_session.get.return_value = mock_user
        mock_crud_get_email.return_value = mock_user
        mock_crud_update.return_value = mock_user
        user_update = UserUpdate(email=mock_user.email)

        result = update_user(
            session=mock_session, user_id=mock_user.id, user_in=user_update
        )

        assert result.id == mock_user.id

    @patch("app.api.routes.users.crud.update_user")
    def test_update_user_no_email(
        self,
        mock_crud_update: MagicMock,
        mock_session: MagicMock,
        mock_user: User,
    ) -> None:
        """Test updating user without changing email."""
        mock_session.get.return_value = mock_user
        mock_crud_update.return_value = mock_user
        user_update = UserUpdate(full_name="Updated Name")

        result = update_user(
            session=mock_session, user_id=mock_user.id, user_in=user_update
        )

        assert result.id == mock_user.id
        mock_crud_update.assert_called_once()


class TestDeleteUser:
    """Tests for delete_user endpoint."""

    def test_delete_user_success(
        self, mock_session: MagicMock, mock_user: User, mock_superuser: User
    ) -> None:
        """Test successfully deleting a user."""
        mock_session.get.return_value = mock_user

        result = delete_user(
            session=mock_session, current_user=mock_superuser, user_id=mock_user.id
        )

        assert result.message == "User deleted successfully"
        assert mock_session.exec.called
        assert mock_session.delete.called
        assert mock_session.commit.called

    def test_delete_user_not_found(
        self, mock_session: MagicMock, mock_superuser: User
    ) -> None:
        """Test deleting a user that doesn't exist."""
        user_id = uuid.uuid4()
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_user(
                session=mock_session, current_user=mock_superuser, user_id=user_id
            )

        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail

    def test_delete_user_superuser_cannot_delete_self(
        self, mock_session: MagicMock, mock_superuser: User
    ) -> None:
        """Test that superuser cannot delete themselves."""
        mock_session.get.return_value = mock_superuser

        with pytest.raises(HTTPException) as exc_info:
            delete_user(
                session=mock_session,
                current_user=mock_superuser,
                user_id=mock_superuser.id,
            )

        assert exc_info.value.status_code == 403
        assert "Super users are not allowed" in exc_info.value.detail
        assert mock_session.exec.call_count == 0
        assert mock_session.delete.call_count == 0

    def test_delete_user_with_items(
        self, mock_session: MagicMock, mock_user: User, mock_superuser: User
    ) -> None:
        """Test deleting a user with associated items."""
        mock_session.get.return_value = mock_user

        result = delete_user(
            session=mock_session, current_user=mock_superuser, user_id=mock_user.id
        )

        assert result.message == "User deleted successfully"
        mock_session.exec.assert_called_once()