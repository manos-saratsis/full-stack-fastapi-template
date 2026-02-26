import uuid
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


class TestReadUsers:
    """Test read_users endpoint."""

    def test_read_users_success(self):
        """Test successfully reading users with pagination."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        mock_users = [
            User(id=uuid.uuid4(), email="user1@example.com", full_name="User 1"),
            User(id=uuid.uuid4(), email="user2@example.com", full_name="User 2"),
        ]
        
        # Mock count query
        count_mock = MagicMock()
        count_mock.one.return_value = 2
        
        # Mock users query
        users_mock = MagicMock()
        users_mock.all.return_value = mock_users
        
        mock_session.exec.side_effect = [count_mock, users_mock]

        # Act
        result = read_users(session=mock_session, skip=0, limit=100)

        # Assert
        assert isinstance(result, UsersPublic)
        assert result.count == 2
        assert result.data == mock_users

    def test_read_users_with_skip_and_limit(self):
        """Test reading users with custom skip and limit."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        mock_users = [User(id=uuid.uuid4(), email="user1@example.com")]
        
        count_mock = MagicMock()
        count_mock.one.return_value = 10
        
        users_mock = MagicMock()
        users_mock.all.return_value = mock_users
        
        mock_session.exec.side_effect = [count_mock, users_mock]

        # Act
        result = read_users(session=mock_session, skip=5, limit=10)

        # Assert
        assert result.count == 10
        assert len(result.data) == 1

    def test_read_users_empty_result(self):
        """Test reading users when no users exist."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        
        count_mock = MagicMock()
        count_mock.one.return_value = 0
        
        users_mock = MagicMock()
        users_mock.all.return_value = []
        
        mock_session.exec.side_effect = [count_mock, users_mock]

        # Act
        result = read_users(session=mock_session)

        # Assert
        assert result.count == 0
        assert result.data == []


class TestCreateUser:
    """Test create_user endpoint."""

    def test_create_user_success(self):
        """Test successfully creating a new user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_in = UserCreate(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
        )
        new_user = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            full_name="New User",
        )

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = None
            with patch("app.api.routes.users.crud.create_user") as mock_create:
                mock_create.return_value = new_user
                with patch("app.api.routes.users.settings") as mock_settings:
                    mock_settings.emails_enabled = False

                    # Act
                    result = create_user(session=mock_session, user_in=user_in)

                    # Assert
                    assert result == new_user
                    mock_get_user.assert_called_once_with(
                        session=mock_session, email="newuser@example.com"
                    )
                    mock_create.assert_called_once_with(
                        session=mock_session, user_create=user_in
                    )

    def test_create_user_email_already_exists(self):
        """Test creating user with email that already exists."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_in = UserCreate(
            email="existing@example.com",
            password="password123",
        )
        existing_user = User(id=uuid.uuid4(), email="existing@example.com")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = existing_user

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                create_user(session=mock_session, user_in=user_in)
            
            assert exc_info.value.status_code == 400
            assert "already exists" in exc_info.value.detail

    def test_create_user_with_email_enabled(self):
        """Test creating user with email notifications enabled."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_in = UserCreate(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
        )
        new_user = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            full_name="New User",
        )

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = None
            with patch("app.api.routes.users.crud.create_user") as mock_create:
                mock_create.return_value = new_user
                with patch("app.api.routes.users.settings") as mock_settings:
                    mock_settings.emails_enabled = True
                    with patch("app.api.routes.users.generate_new_account_email") as mock_email_gen:
                        mock_email_data = MagicMock()
                        mock_email_data.subject = "Welcome"
                        mock_email_data.html_content = "<p>Welcome</p>"
                        mock_email_gen.return_value = mock_email_data
                        with patch("app.api.routes.users.send_email") as mock_send_email:
                            # Act
                            result = create_user(session=mock_session, user_in=user_in)

                            # Assert
                            assert result == new_user
                            mock_email_gen.assert_called_once()
                            mock_send_email.assert_called_once()


class TestUpdateUserMe:
    """Test update_user_me endpoint."""

    def test_update_user_me_success(self):
        """Test successfully updating current user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            full_name="Old Name",
        )
        user_in = UserUpdateMe(full_name="New Name")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = None
            with patch.object(current_user, "sqlmodel_update") as mock_update:
                # Act
                result = update_user_me(
                    session=mock_session, user_in=user_in, current_user=current_user
                )

                # Assert
                assert result == current_user
                mock_session.add.assert_called_once_with(current_user)
                mock_session.commit.assert_called_once()
                mock_session.refresh.assert_called_once_with(current_user)

    def test_update_user_me_with_new_email(self):
        """Test updating user email with a new one."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
        )
        user_in = UserUpdateMe(email="newemail@example.com")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = None
            with patch.object(current_user, "sqlmodel_update"):
                # Act
                result = update_user_me(
                    session=mock_session, user_in=user_in, current_user=current_user
                )

                # Assert
                assert result == current_user
                mock_get_user.assert_called_once()

    def test_update_user_me_email_already_exists(self):
        """Test updating user with email that already exists for another user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(id=uuid.uuid4(), email="user@example.com")
        other_user = User(id=uuid.uuid4(), email="existing@example.com")
        user_in = UserUpdateMe(email="existing@example.com")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = other_user

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                update_user_me(
                    session=mock_session, user_in=user_in, current_user=current_user
                )
            
            assert exc_info.value.status_code == 409

    def test_update_user_me_same_email(self):
        """Test updating user with same email."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        current_user = User(id=user_id, email="user@example.com")
        user_in = UserUpdateMe(email="user@example.com")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = current_user
            with patch.object(current_user, "sqlmodel_update"):
                # Act - should not raise because IDs match
                result = update_user_me(
                    session=mock_session, user_in=user_in, current_user=current_user
                )

                # Assert
                assert result == current_user


class TestUpdatePasswordMe:
    """Test update_password_me endpoint."""

    def test_update_password_me_success(self):
        """Test successfully updating password."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            hashed_password="hashed_old_password",
        )
        body = UpdatePassword(
            current_password="old_password",
            new_password="new_password",
        )

        with patch("app.api.routes.users.verify_password") as mock_verify:
            mock_verify.return_value = True
            with patch("app.api.routes.users.get_password_hash") as mock_hash:
                mock_hash.return_value = "hashed_new_password"

                # Act
                result = update_password_me(
                    session=mock_session, body=body, current_user=current_user
                )

                # Assert
                assert isinstance(result, Message)
                assert "successfully" in result.message
                assert current_user.hashed_password == "hashed_new_password"
                mock_session.add.assert_called_once_with(current_user)
                mock_session.commit.assert_called_once()

    def test_update_password_me_incorrect_current_password(self):
        """Test updating password with incorrect current password."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            hashed_password="hashed_old_password",
        )
        body = UpdatePassword(
            current_password="wrong_password",
            new_password="new_password",
        )

        with patch("app.api.routes.users.verify_password") as mock_verify:
            mock_verify.return_value = False

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                update_password_me(
                    session=mock_session, body=body, current_user=current_user
                )
            
            assert exc_info.value.status_code == 400
            assert "Incorrect" in exc_info.value.detail

    def test_update_password_me_same_as_current(self):
        """Test updating password to same as current."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            hashed_password="hashed_password",
        )
        body = UpdatePassword(
            current_password="password",
            new_password="password",
        )

        with patch("app.api.routes.users.verify_password") as mock_verify:
            mock_verify.return_value = True

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                update_password_me(
                    session=mock_session, body=body, current_user=current_user
                )
            
            assert exc_info.value.status_code == 400
            assert "same" in exc_info.value.detail


class TestReadUserMe:
    """Test read_user_me endpoint."""

    def test_read_user_me_success(self):
        """Test successfully reading current user."""
        # Arrange
        current_user = User(id=uuid.uuid4(), email="user@example.com")

        # Act
        result = read_user_me(current_user=current_user)

        # Assert
        assert result == current_user


class TestDeleteUserMe:
    """Test delete_user_me endpoint."""

    def test_delete_user_me_success(self):
        """Test successfully deleting current user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            email="user@example.com",
            is_superuser=False,
        )

        # Act
        result = delete_user_me(session=mock_session, current_user=current_user)

        # Assert
        assert isinstance(result, Message)
        assert "successfully" in result.message
        mock_session.delete.assert_called_once_with(current_user)
        mock_session.commit.assert_called_once()

    def test_delete_user_me_is_superuser(self):
        """Test that superuser cannot delete themselves."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        current_user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            is_superuser=True,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_user_me(session=mock_session, current_user=current_user)
        
        assert exc_info.value.status_code == 403
        assert "Super users" in exc_info.value.detail


class TestRegisterUser:
    """Test register_user endpoint."""

    def test_register_user_success(self):
        """Test successfully registering a new user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_in = UserRegister(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
        )
        new_user = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            full_name="New User",
        )

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = None
            with patch("app.api.routes.users.UserCreate.model_validate") as mock_validate:
                mock_validate.return_value = UserCreate(
                    email="newuser@example.com",
                    password="password123",
                    full_name="New User",
                )
                with patch("app.api.routes.users.crud.create_user") as mock_create:
                    mock_create.return_value = new_user

                    # Act
                    result = register_user(session=mock_session, user_in=user_in)

                    # Assert
                    assert result == new_user

    def test_register_user_email_already_exists(self):
        """Test registering with email that already exists."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_in = UserRegister(
            email="existing@example.com",
            password="password123",
        )
        existing_user = User(id=uuid.uuid4(), email="existing@example.com")

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = existing_user

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                register_user(session=mock_session, user_in=user_in)
            
            assert exc_info.value.status_code == 400
            assert "already exists" in exc_info.value.detail


class TestReadUserById:
    """Test read_user_by_id endpoint."""

    def test_read_user_by_id_own_user(self):
        """Test reading own user by ID."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        current_user = User(id=user_id, email="user@example.com", is_superuser=False)
        mock_session.get.return_value = current_user

        # Act
        result = read_user_by_id(
            user_id=user_id, session=mock_session, current_user=current_user
        )

        # Assert
        assert result == current_user

    def test_read_user_by_id_other_user_as_superuser(self):
        """Test reading other user by ID as superuser."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        other_user_id = uuid.uuid4()
        other_user = User(id=other_user_id, email="other@example.com")
        current_user = User(id=uuid.uuid4(), email="admin@example.com", is_superuser=True)
        mock_session.get.return_value = other_user

        # Act
        result = read_user_by_id(
            user_id=other_user_id, session=mock_session, current_user=current_user
        )

        # Assert
        assert result == other_user

    def test_read_user_by_id_other_user_as_regular_user(self):
        """Test reading other user by ID as regular user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        other_user_id = uuid.uuid4()
        other_user = User(id=other_user_id, email="other@example.com")
        current_user = User(id=uuid.uuid4(), email="user@example.com", is_superuser=False)
        mock_session.get.return_value = other_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            read_user_by_id(
                user_id=other_user_id, session=mock_session, current_user=current_user
            )
        
        assert exc_info.value.status_code == 403


class TestUpdateUser:
    """Test update_user endpoint."""

    def test_update_user_success(self):
        """Test successfully updating a user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        db_user = User(id=user_id, email="user@example.com", full_name="Old Name")
        user_in = UserUpdate(full_name="New Name")
        updated_user = User(id=user_id, email="user@example.com", full_name="New Name")

        mock_session.get.return_value = db_user

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_email:
            mock_get_email.return_value = None
            with patch("app.api.routes.users.crud.update_user") as mock_update:
                mock_update.return_value = updated_user

                # Act
                result = update_user(session=mock_session, user_id=user_id, user_in=user_in)

                # Assert
                assert result == updated_user

    def test_update_user_not_found(self):
        """Test updating non-existent user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        user_in = UserUpdate(full_name="New Name")
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_user(session=mock_session, user_id=user_id, user_in=user_in)
        
        assert exc_info.value.status_code == 404

    def test_update_user_with_existing_email(self):
        """Test updating user with email that already exists."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        db_user = User(id=user_id, email="user@example.com")
        other_user = User(id=other_user_id, email="existing@example.com")
        user_in = UserUpdate(email="existing@example.com")

        mock_session.get.return_value = db_user

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_email:
            mock_get_email.return_value = other_user

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                update_user(session=mock_session, user_id=user_id, user_in=user_in)
            
            assert exc_info.value.status_code == 409

    def test_update_user_with_same_email(self):
        """Test updating user with same email."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        db_user = User(id=user_id, email="user@example.com")
        user_in = UserUpdate(email="user@example.com")
        updated_user = User(id=user_id, email="user@example.com")

        mock_session.get.return_value = db_user

        with patch("app.api.routes.users.crud.get_user_by_email") as mock_get_email:
            mock_get_email.return_value = db_user
            with patch("app.api.routes.users.crud.update_user") as mock_update:
                mock_update.return_value = updated_user

                # Act
                result = update_user(session=mock_session, user_id=user_id, user_in=user_in)

                # Assert
                assert result == updated_user


class TestDeleteUser:
    """Test delete_user endpoint."""

    def test_delete_user_success(self):
        """Test successfully deleting a user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        current_user = User(id=uuid.uuid4(), email="admin@example.com", is_superuser=True)
        user_to_delete = User(id=user_id, email="user@example.com")

        mock_session.get.return_value = user_to_delete

        # Act
        result = delete_user(session=mock_session, current_user=current_user, user_id=user_id)

        # Assert
        assert isinstance(result, Message)
        assert "successfully" in result.message
        mock_session.exec.assert_called_once()
        mock_session.delete.assert_called_once_with(user_to_delete)
        mock_session.commit.assert_called_once()

    def test_delete_user_not_found(self):
        """Test deleting non-existent user."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        current_user = User(id=uuid.uuid4(), is_superuser=True)
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_user(session=mock_session, current_user=current_user, user_id=user_id)
        
        assert exc_info.value.status_code == 404

    def test_delete_user_self_as_superuser(self):
        """Test that superuser cannot delete themselves."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        current_user = User(id=user_id, email="admin@example.com", is_superuser=True)
        mock_session.get.return_value = current_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_user(session=mock_session, current_user=current_user, user_id=user_id)
        
        assert exc_info.value.status_code == 403
        assert "Super users" in exc_info.value.detail

    def test_delete_user_removes_items(self):
        """Test that deleting a user also deletes their items."""
        # Arrange
        mock_session = MagicMock(spec=Session)
        user_id = uuid.uuid4()
        current_user = User(id=uuid.uuid4(), is_superuser=True)
        user_to_delete = User(id=user_id, email="user@example.com")

        mock_session.get.return_value = user_to_delete

        # Act
        result = delete_user(session=mock_session, current_user=current_user, user_id=user_id)

        # Assert
        assert isinstance(result, Message)
        mock_session.exec.assert_called_once()