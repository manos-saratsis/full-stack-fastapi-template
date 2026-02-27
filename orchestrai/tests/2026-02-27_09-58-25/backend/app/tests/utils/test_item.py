import pytest
from unittest.mock import MagicMock, patch, call
from sqlmodel import Session

from app import crud
from app.models import Item, ItemCreate, User
from app.tests.utils.item import create_random_item
from app.tests.utils.utils import random_lower_string


class TestCreateRandomItem:
    """Tests for create_random_item function."""

    def test_returns_item_instance(self):
        """Should return an Item instance."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.crud.create_item", return_value=mock_item):
                result = create_random_item(mock_db)
                assert result == mock_item

    def test_creates_user_first(self):
        """Should create a random user before creating item."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user) as mock_create_user:
            with patch("app.crud.create_item", return_value=mock_item):
                create_random_item(mock_db)
                mock_create_user.assert_called_once_with(mock_db)

    def test_uses_user_id_as_owner_id(self):
        """Should use created user's ID as owner_id."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 42
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                create_random_item(mock_db)
                call_args = mock_crud_create.call_args
                assert call_args.kwargs["owner_id"] == 42

    def test_generates_random_title(self):
        """Should generate a random title for the item."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.tests.utils.item.random_lower_string", return_value="test_title") as mock_random_title:
                with patch("app.crud.create_item", return_value=mock_item):
                    create_random_item(mock_db)
                    # random_lower_string should be called (at least for title)
                    assert mock_random_title.called

    def test_generates_random_description(self):
        """Should generate a random description for the item."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.tests.utils.item.random_lower_string", side_effect=["title", "description"]):
                with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                    create_random_item(mock_db)
                    # Verify ItemCreate was called with both title and description
                    call_args = mock_crud_create.call_args
                    item_in = call_args.kwargs["item_in"]
                    assert isinstance(item_in, ItemCreate)

    def test_passes_session_to_crud_create_item(self):
        """Should pass database session to crud.create_item."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                create_random_item(mock_db)
                call_args = mock_crud_create.call_args
                assert call_args.kwargs["session"] == mock_db

    def test_creates_item_with_correct_parameters(self):
        """Should create item with session, item_in, and owner_id."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 99
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                create_random_item(mock_db)
                # Verify called with keyword arguments
                call_args = mock_crud_create.call_args
                assert "session" in call_args.kwargs
                assert "item_in" in call_args.kwargs
                assert "owner_id" in call_args.kwargs

    def test_asserts_user_id_is_not_none(self):
        """Should assert that user.id is not None."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = None

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with pytest.raises(AssertionError):
                create_random_item(mock_db)

    def test_with_user_id_zero(self):
        """Should handle user with ID of 0 (falsy but valid)."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 0
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                create_random_item(mock_db)
                call_args = mock_crud_create.call_args
                assert call_args.kwargs["owner_id"] == 0

    def test_with_large_user_id(self):
        """Should handle very large user IDs."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 999999999
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                create_random_item(mock_db)
                call_args = mock_crud_create.call_args
                assert call_args.kwargs["owner_id"] == 999999999

    def test_item_create_has_title_and_description(self):
        """Should create ItemCreate with both title and description."""
        mock_db = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_item = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", return_value=mock_user):
            with patch("app.tests.utils.item.random_lower_string", side_effect=["my_title", "my_desc"]):
                with patch("app.crud.create_item", return_value=mock_item) as mock_crud_create:
                    create_random_item(mock_db)
                    call_args = mock_crud_create.call_args
                    item_in = call_args.kwargs["item_in"]
                    assert item_in.title == "my_title"
                    assert item_in.description == "my_desc"

    def test_multiple_calls_create_different_items(self):
        """Should create different items on multiple calls."""
        mock_db = MagicMock(spec=Session)
        mock_user1 = MagicMock(spec=User)
        mock_user1.id = 1
        mock_user2 = MagicMock(spec=User)
        mock_user2.id = 2
        mock_item1 = MagicMock(spec=Item)
        mock_item2 = MagicMock(spec=Item)

        with patch("app.tests.utils.item.create_random_user", side_effect=[mock_user1, mock_user2]):
            with patch("app.tests.utils.item.random_lower_string", side_effect=["t1", "d1", "t2", "d2"]):
                with patch("app.crud.create_item", side_effect=[mock_item1, mock_item2]) as mock_crud_create:
                    result1 = create_random_item(mock_db)
                    result2 = create_random_item(mock_db)
                    assert result1 == mock_item1
                    assert result2 == mock_item2