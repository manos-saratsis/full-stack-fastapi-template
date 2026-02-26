import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session

from app.tests.utils.item import create_random_item
from app.models import Item, ItemCreate


class TestCreateRandomItem:
    """Test create_random_item function."""

    def test_create_random_item_returns_item(self):
        """Should return an Item object."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        mock_item = Mock(spec=Item)
        mock_item.id = 1
        mock_item.title = "test_title"
        mock_item.description = "test_description"
        mock_item.owner_id = 1

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["title_string", "description_string"]

            result = create_random_item(mock_session)

            assert isinstance(result, Mock)
            assert result.id == 1

    def test_create_random_item_calls_create_random_user(self):
        """Should call create_random_user with the session."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["title", "description"]

            create_random_item(mock_session)

            mock_create_user.assert_called_once_with(mock_session)

    def test_create_random_item_uses_user_id(self):
        """Should use the id from the created user."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 42

        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["title", "description"]

            create_random_item(mock_session)

            call_kwargs = mock_crud.create_item.call_args[1]
            assert call_kwargs["owner_id"] == 42

    def test_create_random_item_generates_random_title(self):
        """Should generate random string for item title."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["random_title", "random_desc"]

            create_random_item(mock_session)

            call_kwargs = mock_crud.create_item.call_args[1]
            item_in = call_kwargs["item_in"]
            assert item_in.title == "random_title"

    def test_create_random_item_generates_random_description(self):
        """Should generate random string for item description."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["title", "random_description"]

            create_random_item(mock_session)

            call_kwargs = mock_crud.create_item.call_args[1]
            item_in = call_kwargs["item_in"]
            assert item_in.description == "random_description"

    def test_create_random_item_calls_crud_create_item(self):
        """Should call crud.create_item with correct parameters."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["title", "description"]

            create_random_item(mock_session)

            mock_crud.create_item.assert_called_once()
            call_kwargs = mock_crud.create_item.call_args[1]
            assert call_kwargs["session"] == mock_session
            assert isinstance(call_kwargs["item_in"], ItemCreate)
            assert call_kwargs["owner_id"] == 1

    def test_create_random_item_item_create_structure(self):
        """Should create ItemCreate with title and description."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["my_title", "my_description"]

            create_random_item(mock_session)

            call_kwargs = mock_crud.create_item.call_args[1]
            item_in = call_kwargs["item_in"]
            assert item_in.title == "my_title"
            assert item_in.description == "my_description"

    def test_create_random_item_assertion_on_owner_id(self):
        """Should assert that owner_id is not None."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = None

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_random.side_effect = ["title", "description"]

            with pytest.raises(AssertionError):
                create_random_item(mock_session)

    def test_create_random_item_with_different_user_ids(self):
        """Should work correctly with different user IDs."""
        mock_session = Mock(spec=Session)
        mock_item = Mock(spec=Item)

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_crud.create_item.return_value = mock_item
            mock_random.side_effect = ["title", "description"]

            for user_id in [1, 10, 999, 9999]:
                mock_user = Mock()
                mock_user.id = user_id
                mock_create_user.return_value = mock_user

                create_random_item(mock_session)

                call_kwargs = mock_crud.create_item.call_args[1]
                assert call_kwargs["owner_id"] == user_id

    def test_create_random_item_returns_crud_result(self):
        """Should return the result from crud.create_item."""
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.id = 1

        expected_item = Mock(spec=Item)
        expected_item.id = 100

        with patch("app.tests.utils.item.create_random_user") as mock_create_user, \
             patch("app.tests.utils.item.crud") as mock_crud, \
             patch("app.tests.utils.item.random_lower_string") as mock_random:

            mock_create_user.return_value = mock_user
            mock_crud.create_item.return_value = expected_item
            mock_random.side_effect = ["title", "description"]

            result = create_random_item(mock_session)

            assert result == expected_item
            assert result.id == 100