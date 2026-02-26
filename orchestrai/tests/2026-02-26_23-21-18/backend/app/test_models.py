import uuid
from pydantic import ValidationError
import pytest
from app.models import (
    User,
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
    UserPublic,
    UsersPublic,
    Item,
    ItemBase,
    ItemCreate,
    ItemUpdate,
    ItemPublic,
    ItemsPublic,
    Message,
    Token,
    TokenPayload,
    NewPassword,
)


class TestUserBase:
    def test_user_base_creation_with_all_fields(self):
        user = UserBase(
            email="test@example.com",
            is_active=True,
            is_superuser=False,
            full_name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name == "Test User"

    def test_user_base_creation_with_defaults(self):
        user = UserBase(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name is None

    def test_user_base_invalid_email(self):
        with pytest.raises(ValidationError):
            UserBase(email="invalid-email")

    def test_user_base_email_max_length(self):
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError):
            UserBase(email=long_email)

    def test_user_base_full_name_max_length(self):
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", full_name=long_name)

    def test_user_base_is_active_false(self):
        user = UserBase(email="test@example.com", is_active=False)
        assert user.is_active is False

    def test_user_base_is_superuser_true(self):
        user = UserBase(email="test@example.com", is_superuser=True)
        assert user.is_superuser is True


class TestUserCreate:
    def test_user_create_with_valid_password(self):
        user = UserCreate(
            email="test@example.com",
            password="validpassword123",
            full_name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.password == "validpassword123"
        assert user.full_name == "Test User"

    def test_user_create_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="short"
            )

    def test_user_create_password_too_long(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="a" * 41
            )

    def test_user_create_password_min_length(self):
        user = UserCreate(
            email="test@example.com",
            password="12345678"
        )
        assert user.password == "12345678"

    def test_user_create_password_max_length(self):
        user = UserCreate(
            email="test@example.com",
            password="a" * 40
        )
        assert user.password == "a" * 40


class TestUserRegister:
    def test_user_register_with_all_fields(self):
        user = UserRegister(
            email="test@example.com",
            password="validpassword123",
            full_name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.password == "validpassword123"
        assert user.full_name == "Test User"

    def test_user_register_without_full_name(self):
        user = UserRegister(
            email="test@example.com",
            password="validpassword123"
        )
        assert user.full_name is None

    def test_user_register_invalid_email(self):
        with pytest.raises(ValidationError):
            UserRegister(
                email="invalid",
                password="validpassword123"
            )

    def test_user_register_password_too_short(self):
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                password="short"
            )


class TestUserUpdate:
    def test_user_update_with_all_fields(self):
        user = UserUpdate(
            email="test@example.com",
            is_active=True,
            is_superuser=False,
            password="newpassword123",
            full_name="Updated Name"
        )
        assert user.email == "test@example.com"
        assert user.password == "newpassword123"

    def test_user_update_with_none_email(self):
        user = UserUpdate(
            email=None,
            is_active=True
        )
        assert user.email is None

    def test_user_update_with_none_password(self):
        user = UserUpdate(
            password=None,
            is_active=True,
            email="test@example.com"
        )
        assert user.password is None

    def test_user_update_invalid_email(self):
        with pytest.raises(ValidationError):
            UserUpdate(
                email="invalid",
                is_active=True
            )

    def test_user_update_password_too_short(self):
        with pytest.raises(ValidationError):
            UserUpdate(
                password="short",
                is_active=True,
                email="test@example.com"
            )


class TestUserUpdateMe:
    def test_user_update_me_with_all_fields(self):
        user = UserUpdateMe(
            full_name="New Name",
            email="new@example.com"
        )
        assert user.full_name == "New Name"
        assert user.email == "new@example.com"

    def test_user_update_me_with_none_fields(self):
        user = UserUpdateMe()
        assert user.full_name is None
        assert user.email is None

    def test_user_update_me_invalid_email(self):
        with pytest.raises(ValidationError):
            UserUpdateMe(email="invalid")


class TestUpdatePassword:
    def test_update_password_valid(self):
        pwd = UpdatePassword(
            current_password="currentpass123",
            new_password="newpass123456"
        )
        assert pwd.current_password == "currentpass123"
        assert pwd.new_password == "newpass123456"

    def test_update_password_current_too_short(self):
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="short",
                new_password="newpass123456"
            )

    def test_update_password_new_too_short(self):
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="currentpass123",
                new_password="short"
            )

    def test_update_password_new_too_long(self):
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="currentpass123",
                new_password="a" * 41
            )


class TestUser:
    def test_user_creation_with_hashed_password(self):
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashedpass",
            full_name="Test User"
        )
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashedpass"
        assert user.full_name == "Test User"

    def test_user_id_auto_generation(self):
        user1 = User(
            email="test1@example.com",
            hashed_password="hashedpass1"
        )
        user2 = User(
            email="test2@example.com",
            hashed_password="hashedpass2"
        )
        assert user1.id != user2.id

    def test_user_items_relationship_empty(self):
        user = User(
            email="test@example.com",
            hashed_password="hashedpass"
        )
        assert user.items == []


class TestUserPublic:
    def test_user_public_creation(self):
        user_id = uuid.uuid4()
        user = UserPublic(
            id=user_id,
            email="test@example.com",
            is_active=True,
            is_superuser=False,
            full_name="Test User"
        )
        assert user.id == user_id
        assert user.email == "test@example.com"

    def test_user_public_requires_id(self):
        with pytest.raises(ValidationError):
            UserPublic(
                email="test@example.com"
            )


class TestUsersPublic:
    def test_users_public_with_data(self):
        user_id = uuid.uuid4()
        users = UsersPublic(
            data=[
                UserPublic(
                    id=user_id,
                    email="test@example.com"
                )
            ],
            count=1
        )
        assert len(users.data) == 1
        assert users.count == 1

    def test_users_public_empty_list(self):
        users = UsersPublic(data=[], count=0)
        assert len(users.data) == 0
        assert users.count == 0

    def test_users_public_multiple_users(self):
        users = UsersPublic(
            data=[
                UserPublic(id=uuid.uuid4(), email="user1@example.com"),
                UserPublic(id=uuid.uuid4(), email="user2@example.com"),
            ],
            count=2
        )
        assert users.count == 2


class TestItemBase:
    def test_item_base_with_all_fields(self):
        item = ItemBase(
            title="Test Item",
            description="Test Description"
        )
        assert item.title == "Test Item"
        assert item.description == "Test Description"

    def test_item_base_without_description(self):
        item = ItemBase(title="Test Item")
        assert item.title == "Test Item"
        assert item.description is None

    def test_item_base_title_empty(self):
        with pytest.raises(ValidationError):
            ItemBase(title="")

    def test_item_base_title_max_length(self):
        long_title = "a" * 256
        with pytest.raises(ValidationError):
            ItemBase(title=long_title)

    def test_item_base_description_max_length(self):
        long_desc = "a" * 256
        with pytest.raises(ValidationError):
            ItemBase(
                title="Test",
                description=long_desc
            )

    def test_item_base_title_single_char(self):
        item = ItemBase(title="A")
        assert item.title == "A"


class TestItemCreate:
    def test_item_create_with_all_fields(self):
        item = ItemCreate(
            title="Test Item",
            description="Test Description"
        )
        assert item.title == "Test Item"
        assert item.description == "Test Description"

    def test_item_create_inherits_from_base(self):
        item = ItemCreate(title="Test")
        assert isinstance(item, ItemBase)


class TestItemUpdate:
    def test_item_update_with_all_fields(self):
        item = ItemUpdate(
            title="Updated Title",
            description="Updated Description"
        )
        assert item.title == "Updated Title"
        assert item.description == "Updated Description"

    def test_item_update_with_none_title(self):
        item = ItemUpdate(title=None, description="Description")
        assert item.title is None

    def test_item_update_title_empty_string(self):
        with pytest.raises(ValidationError):
            ItemUpdate(title="")

    def test_item_update_title_too_long(self):
        with pytest.raises(ValidationError):
            ItemUpdate(title="a" * 256)


class TestItem:
    def test_item_creation(self):
        item_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        item = Item(
            id=item_id,
            title="Test Item",
            description="Test Description",
            owner_id=owner_id
        )
        assert item.id == item_id
        assert item.title == "Test Item"
        assert item.owner_id == owner_id

    def test_item_id_auto_generation(self):
        owner_id = uuid.uuid4()
        item1 = Item(
            title="Item 1",
            owner_id=owner_id
        )
        item2 = Item(
            title="Item 2",
            owner_id=owner_id
        )
        assert item1.id != item2.id

    def test_item_owner_relationship(self):
        owner_id = uuid.uuid4()
        item = Item(
            title="Test Item",
            owner_id=owner_id
        )
        assert item.owner is None


class TestItemPublic:
    def test_item_public_creation(self):
        item_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        item = ItemPublic(
            id=item_id,
            title="Test Item",
            description="Test Description",
            owner_id=owner_id
        )
        assert item.id == item_id
        assert item.owner_id == owner_id

    def test_item_public_requires_id_and_owner_id(self):
        with pytest.raises(ValidationError):
            ItemPublic(
                title="Test Item",
                owner_id=uuid.uuid4()
            )

    def test_item_public_missing_owner_id(self):
        with pytest.raises(ValidationError):
            ItemPublic(
                id=uuid.uuid4(),
                title="Test Item"
            )


class TestItemsPublic:
    def test_items_public_with_data(self):
        owner_id = uuid.uuid4()
        items = ItemsPublic(
            data=[
                ItemPublic(
                    id=uuid.uuid4(),
                    title="Item 1",
                    owner_id=owner_id
                )
            ],
            count=1
        )
        assert len(items.data) == 1
        assert items.count == 1

    def test_items_public_empty_list(self):
        items = ItemsPublic(data=[], count=0)
        assert len(items.data) == 0
        assert items.count == 0

    def test_items_public_multiple_items(self):
        owner_id = uuid.uuid4()
        items = ItemsPublic(
            data=[
                ItemPublic(id=uuid.uuid4(), title="Item 1", owner_id=owner_id),
                ItemPublic(id=uuid.uuid4(), title="Item 2", owner_id=owner_id),
            ],
            count=2
        )
        assert items.count == 2


class TestMessage:
    def test_message_creation(self):
        msg = Message(message="Test message")
        assert msg.message == "Test message"

    def test_message_empty_string(self):
        msg = Message(message="")
        assert msg.message == ""


class TestToken:
    def test_token_with_default_type(self):
        token = Token(access_token="token123")
        assert token.access_token == "token123"
        assert token.token_type == "bearer"

    def test_token_with_custom_type(self):
        token = Token(access_token="token123", token_type="custom")
        assert token.token_type == "custom"


class TestTokenPayload:
    def test_token_payload_with_sub(self):
        payload = TokenPayload(sub="user123")
        assert payload.sub == "user123"

    def test_token_payload_without_sub(self):
        payload = TokenPayload()
        assert payload.sub is None

    def test_token_payload_with_none_sub(self):
        payload = TokenPayload(sub=None)
        assert payload.sub is None


class TestNewPassword:
    def test_new_password_valid(self):
        pwd = NewPassword(
            token="reset_token_123",
            new_password="newpass123456"
        )
        assert pwd.token == "reset_token_123"
        assert pwd.new_password == "newpass123456"

    def test_new_password_short_password(self):
        with pytest.raises(ValidationError):
            NewPassword(
                token="reset_token_123",
                new_password="short"
            )

    def test_new_password_long_password(self):
        with pytest.raises(ValidationError):
            NewPassword(
                token="reset_token_123",
                new_password="a" * 41
            )