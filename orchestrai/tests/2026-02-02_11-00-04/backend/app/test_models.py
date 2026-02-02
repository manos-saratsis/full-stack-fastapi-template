"""
Comprehensive tests for backend/app/models.py
Tests all model classes and their field definitions.
"""

import uuid
from typing import Any

import pytest
from pydantic import ValidationError

from app.models import (
    EmailData,
    Item,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    Message,
    NewPassword,
    Token,
    TokenPayload,
    UpdatePassword,
    User,
    UserBase,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)


class TestUserBase:
    """Test UserBase model"""

    def test_user_base_required_fields(self) -> None:
        """Should create UserBase with required fields"""
        user = UserBase(
            email="test@example.com",
            is_active=True,
            is_superuser=False,
            full_name="Test User",
        )
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name == "Test User"

    def test_user_base_default_values(self) -> None:
        """Should use default values for optional fields"""
        user = UserBase(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name is None

    def test_user_base_invalid_email(self) -> None:
        """Should raise validation error for invalid email"""
        with pytest.raises(ValidationError):
            UserBase(email="not-an-email")

    def test_user_base_email_max_length(self) -> None:
        """Should reject email exceeding max length"""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError):
            UserBase(email=long_email)

    def test_user_base_full_name_max_length(self) -> None:
        """Should reject full_name exceeding max length"""
        with pytest.raises(ValidationError):
            UserBase(
                email="test@example.com",
                full_name="a" * 256,
            )

    def test_user_base_is_active_boolean(self) -> None:
        """Should handle is_active as boolean"""
        user = UserBase(email="test@example.com", is_active=False)
        assert user.is_active is False

    def test_user_base_is_superuser_boolean(self) -> None:
        """Should handle is_superuser as boolean"""
        user = UserBase(email="test@example.com", is_superuser=True)
        assert user.is_superuser is True


class TestUserCreate:
    """Test UserCreate model"""

    def test_user_create_with_all_fields(self) -> None:
        """Should create UserCreate with all fields"""
        user = UserCreate(
            email="test@example.com",
            password="SecurePassword123",
            is_active=True,
            is_superuser=False,
            full_name="Test User",
        )
        assert user.email == "test@example.com"
        assert user.password == "SecurePassword123"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name == "Test User"

    def test_user_create_password_min_length(self) -> None:
        """Should reject password below min length"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="short",
            )

    def test_user_create_password_max_length(self) -> None:
        """Should reject password exceeding max length"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="a" * 41,
            )

    def test_user_create_password_exactly_8_chars(self) -> None:
        """Should accept password with exactly 8 characters"""
        user = UserCreate(
            email="test@example.com",
            password="12345678",
        )
        assert user.password == "12345678"

    def test_user_create_password_exactly_40_chars(self) -> None:
        """Should accept password with exactly 40 characters"""
        user = UserCreate(
            email="test@example.com",
            password="a" * 40,
        )
        assert user.password == "a" * 40


class TestUserRegister:
    """Test UserRegister model"""

    def test_user_register_with_all_fields(self) -> None:
        """Should create UserRegister with all fields"""
        user = UserRegister(
            email="test@example.com",
            password="SecurePassword123",
            full_name="Test User",
        )
        assert user.email == "test@example.com"
        assert user.password == "SecurePassword123"
        assert user.full_name == "Test User"

    def test_user_register_without_full_name(self) -> None:
        """Should create UserRegister without full_name"""
        user = UserRegister(
            email="test@example.com",
            password="SecurePassword123",
        )
        assert user.email == "test@example.com"
        assert user.password == "SecurePassword123"
        assert user.full_name is None

    def test_user_register_invalid_email(self) -> None:
        """Should reject invalid email"""
        with pytest.raises(ValidationError):
            UserRegister(
                email="invalid-email",
                password="SecurePassword123",
            )

    def test_user_register_password_too_short(self) -> None:
        """Should reject password below minimum length"""
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                password="short",
            )

    def test_user_register_full_name_max_length(self) -> None:
        """Should reject full_name exceeding max length"""
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                password="SecurePassword123",
                full_name="a" * 256,
            )


class TestUserUpdate:
    """Test UserUpdate model"""

    def test_user_update_with_all_fields(self) -> None:
        """Should create UserUpdate with all fields"""
        user = UserUpdate(
            email="new@example.com",
            password="NewPassword123",
            is_active=False,
            is_superuser=True,
            full_name="Updated User",
        )
        assert user.email == "new@example.com"
        assert user.password == "NewPassword123"
        assert user.is_active is False
        assert user.is_superuser is True
        assert user.full_name == "Updated User"

    def test_user_update_optional_fields(self) -> None:
        """Should create UserUpdate with optional fields only"""
        user = UserUpdate(
            email=None,
            password=None,
        )
        assert user.email is None
        assert user.password is None

    def test_user_update_password_invalid_length(self) -> None:
        """Should reject password with invalid length"""
        with pytest.raises(ValidationError):
            UserUpdate(
                email="test@example.com",
                password="short",
            )

    def test_user_update_email_invalid(self) -> None:
        """Should reject invalid email"""
        with pytest.raises(ValidationError):
            UserUpdate(
                email="invalid-email",
            )


class TestUserUpdateMe:
    """Test UserUpdateMe model"""

    def test_user_update_me_with_all_fields(self) -> None:
        """Should create UserUpdateMe with all fields"""
        user = UserUpdateMe(
            email="new@example.com",
            full_name="Updated User",
        )
        assert user.email == "new@example.com"
        assert user.full_name == "Updated User"

    def test_user_update_me_optional_fields(self) -> None:
        """Should create UserUpdateMe with no fields"""
        user = UserUpdateMe()
        assert user.email is None
        assert user.full_name is None

    def test_user_update_me_email_only(self) -> None:
        """Should create UserUpdateMe with email only"""
        user = UserUpdateMe(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.full_name is None

    def test_user_update_me_full_name_only(self) -> None:
        """Should create UserUpdateMe with full_name only"""
        user = UserUpdateMe(full_name="Test User")
        assert user.email is None
        assert user.full_name == "Test User"

    def test_user_update_me_email_invalid(self) -> None:
        """Should reject invalid email"""
        with pytest.raises(ValidationError):
            UserUpdateMe(email="invalid-email")

    def test_user_update_me_full_name_too_long(self) -> None:
        """Should reject full_name exceeding max length"""
        with pytest.raises(ValidationError):
            UserUpdateMe(full_name="a" * 256)


class TestUpdatePassword:
    """Test UpdatePassword model"""

    def test_update_password_valid(self) -> None:
        """Should create UpdatePassword with valid passwords"""
        update = UpdatePassword(
            current_password="CurrentPass123",
            new_password="NewPassword123",
        )
        assert update.current_password == "CurrentPass123"
        assert update.new_password == "NewPassword123"

    def test_update_password_current_too_short(self) -> None:
        """Should reject current_password below minimum length"""
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="short",
                new_password="NewPassword123",
            )

    def test_update_password_new_too_short(self) -> None:
        """Should reject new_password below minimum length"""
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="CurrentPass123",
                new_password="short",
            )

    def test_update_password_both_too_short(self) -> None:
        """Should reject both passwords below minimum length"""
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="short",
                new_password="short",
            )

    def test_update_password_current_too_long(self) -> None:
        """Should reject current_password exceeding max length"""
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="a" * 41,
                new_password="NewPassword123",
            )

    def test_update_password_new_too_long(self) -> None:
        """Should reject new_password exceeding max length"""
        with pytest.raises(ValidationError):
            UpdatePassword(
                current_password="CurrentPass123",
                new_password="a" * 41,
            )


class TestUserModel:
    """Test User database model"""

    def test_user_model_creation(self) -> None:
        """Should create User with all fields"""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
            full_name="Test User",
        )
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name == "Test User"

    def test_user_model_default_id(self) -> None:
        """Should generate default UUID if not provided"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
        )
        assert isinstance(user.id, uuid.UUID)

    def test_user_model_items_relationship(self) -> None:
        """Should have items relationship"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
        )
        assert hasattr(user, "items")


class TestUserPublic:
    """Test UserPublic model"""

    def test_user_public_with_all_fields(self) -> None:
        """Should create UserPublic with all fields"""
        user_id = uuid.uuid4()
        user = UserPublic(
            id=user_id,
            email="test@example.com",
            is_active=True,
            is_superuser=False,
            full_name="Test User",
        )
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name == "Test User"

    def test_user_public_id_required(self) -> None:
        """Should require id field"""
        user_id = uuid.uuid4()
        user = UserPublic(
            id=user_id,
            email="test@example.com",
        )
        assert user.id == user_id


class TestUsersPublic:
    """Test UsersPublic model"""

    def test_users_public_with_data(self) -> None:
        """Should create UsersPublic with user data"""
        user_id = uuid.uuid4()
        user = UserPublic(
            id=user_id,
            email="test@example.com",
        )
        users = UsersPublic(data=[user], count=1)
        assert len(users.data) == 1
        assert users.count == 1
        assert users.data[0].id == user_id

    def test_users_public_empty_data(self) -> None:
        """Should create UsersPublic with empty data"""
        users = UsersPublic(data=[], count=0)
        assert users.data == []
        assert users.count == 0

    def test_users_public_multiple_users(self) -> None:
        """Should create UsersPublic with multiple users"""
        users_list = [
            UserPublic(
                id=uuid.uuid4(),
                email="test1@example.com",
            ),
            UserPublic(
                id=uuid.uuid4(),
                email="test2@example.com",
            ),
        ]
        users = UsersPublic(data=users_list, count=2)
        assert len(users.data) == 2
        assert users.count == 2


class TestItemBase:
    """Test ItemBase model"""

    def test_item_base_with_all_fields(self) -> None:
        """Should create ItemBase with all fields"""
        item = ItemBase(
            title="Test Item",
            description="Test Description",
        )
        assert item.title == "Test Item"
        assert item.description == "Test Description"

    def test_item_base_title_required(self) -> None:
        """Should require title field"""
        with pytest.raises(ValidationError):
            ItemBase(title="")

    def test_item_base_title_min_length(self) -> None:
        """Should require title with at least 1 character"""
        item = ItemBase(title="A")
        assert item.title == "A"

    def test_item_base_title_max_length(self) -> None:
        """Should reject title exceeding max length"""
        with pytest.raises(ValidationError):
            ItemBase(title="a" * 256)

    def test_item_base_optional_description(self) -> None:
        """Should allow missing description"""
        item = ItemBase(title="Test Item")
        assert item.title == "Test Item"
        assert item.description is None

    def test_item_base_description_max_length(self) -> None:
        """Should reject description exceeding max length"""
        with pytest.raises(ValidationError):
            ItemBase(
                title="Test Item",
                description="a" * 256,
            )


class TestItemCreate:
    """Test ItemCreate model"""

    def test_item_create_with_all_fields(self) -> None:
        """Should create ItemCreate with all fields"""
        item = ItemCreate(
            title="Test Item",
            description="Test Description",
        )
        assert item.title == "Test Item"
        assert item.description == "Test Description"

    def test_item_create_without_description(self) -> None:
        """Should create ItemCreate without description"""
        item = ItemCreate(title="Test Item")
        assert item.title == "Test Item"
        assert item.description is None


class TestItemUpdate:
    """Test ItemUpdate model"""

    def test_item_update_with_all_fields(self) -> None:
        """Should create ItemUpdate with all fields"""
        item = ItemUpdate(
            title="Updated Item",
            description="Updated Description",
        )
        assert item.title == "Updated Item"
        assert item.description == "Updated Description"

    def test_item_update_optional_fields(self) -> None:
        """Should create ItemUpdate with optional fields"""
        item = ItemUpdate(title=None)
        assert item.title is None

    def test_item_update_title_min_length(self) -> None:
        """Should accept title with minimum length"""
        item = ItemUpdate(title="A")
        assert item.title == "A"

    def test_item_update_empty_title_invalid(self) -> None:
        """Should reject empty title"""
        with pytest.raises(ValidationError):
            ItemUpdate(title="")


class TestItem:
    """Test Item database model"""

    def test_item_model_creation(self) -> None:
        """Should create Item with all fields"""
        item_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        item = Item(
            id=item_id,
            title="Test Item",
            description="Test Description",
            owner_id=owner_id,
        )
        assert item.id == item_id
        assert item.title == "Test Item"
        assert item.description == "Test Description"
        assert item.owner_id == owner_id

    def test_item_model_default_id(self) -> None:
        """Should generate default UUID if not provided"""
        item = Item(
            title="Test Item",
            owner_id=uuid.uuid4(),
        )
        assert isinstance(item.id, uuid.UUID)

    def test_item_model_relationship(self) -> None:
        """Should have owner relationship"""
        item = Item(
            title="Test Item",
            owner_id=uuid.uuid4(),
        )
        assert hasattr(item, "owner")


class TestItemPublic:
    """Test ItemPublic model"""

    def test_item_public_with_all_fields(self) -> None:
        """Should create ItemPublic with all fields"""
        item_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        item = ItemPublic(
            id=item_id,
            title="Test Item",
            description="Test Description",
            owner_id=owner_id,
        )
        assert item.id == item_id
        assert item.title == "Test Item"
        assert item.description == "Test Description"
        assert item.owner_id == owner_id

    def test_item_public_required_fields(self) -> None:
        """Should require id and owner_id fields"""
        item_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        item = ItemPublic(
            id=item_id,
            title="Test Item",
            owner_id=owner_id,
        )
        assert item.id == item_id
        assert item.owner_id == owner_id


class TestItemsPublic:
    """Test ItemsPublic model"""

    def test_items_public_with_data(self) -> None:
        """Should create ItemsPublic with item data"""
        item_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        item = ItemPublic(
            id=item_id,
            title="Test Item",
            owner_id=owner_id,
        )
        items = ItemsPublic(data=[item], count=1)
        assert len(items.data) == 1
        assert items.count == 1

    def test_items_public_empty_data(self) -> None:
        """Should create ItemsPublic with empty data"""
        items = ItemsPublic(data=[], count=0)
        assert items.data == []
        assert items.count == 0

    def test_items_public_multiple_items(self) -> None:
        """Should create ItemsPublic with multiple items"""
        items_list = [
            ItemPublic(
                id=uuid.uuid4(),
                title="Item 1",
                owner_id=uuid.uuid4(),
            ),
            ItemPublic(
                id=uuid.uuid4(),
                title="Item 2",
                owner_id=uuid.uuid4(),
            ),
        ]
        items = ItemsPublic(data=items_list, count=2)
        assert len(items.data) == 2
        assert items.count == 2


class TestMessage:
    """Test Message model"""

    def test_message_creation(self) -> None:
        """Should create Message with message field"""
        msg = Message(message="Test message")
        assert msg.message == "Test message"

    def test_message_empty_string(self) -> None:
        """Should allow empty string"""
        msg = Message(message="")
        assert msg.message == ""

    def test_message_long_string(self) -> None:
        """Should allow long string"""
        long_msg = "a" * 1000
        msg = Message(message=long_msg)
        assert msg.message == long_msg


class TestToken:
    """Test Token model"""

    def test_token_with_access_token(self) -> None:
        """Should create Token with access_token"""
        token = Token(access_token="test_token_123")
        assert token.access_token == "test_token_123"
        assert token.token_type == "bearer"

    def test_token_custom_token_type(self) -> None:
        """Should accept custom token_type"""
        token = Token(access_token="test_token_123", token_type="Bearer")
        assert token.access_token == "test_token_123"
        assert token.token_type == "Bearer"

    def test_token_default_token_type(self) -> None:
        """Should default token_type to bearer"""
        token = Token(access_token="test_token_123")
        assert token.token_type == "bearer"


class TestTokenPayload:
    """Test TokenPayload model"""

    def test_token_payload_with_sub(self) -> None:
        """Should create TokenPayload with sub field"""
        payload = TokenPayload(sub="user@example.com")
        assert payload.sub == "user@example.com"

    def test_token_payload_optional_sub(self) -> None:
        """Should allow missing sub field"""
        payload = TokenPayload()
        assert payload.sub is None

    def test_token_payload_numeric_sub(self) -> None:
        """Should accept numeric sub"""
        payload = TokenPayload(sub="12345")
        assert payload.sub == "12345"


class TestNewPassword:
    """Test NewPassword model"""

    def test_new_password_with_valid_data(self) -> None:
        """Should create NewPassword with valid data"""
        new_pass = NewPassword(
            token="test_token_123",
            new_password="NewPassword123",
        )
        assert new_pass.token == "test_token_123"
        assert new_pass.new_password == "NewPassword123"

    def test_new_password_password_min_length(self) -> None:
        """Should reject password below minimum length"""
        with pytest.raises(ValidationError):
            NewPassword(
                token="test_token_123",
                new_password="short",
            )

    def test_new_password_password_max_length(self) -> None:
        """Should reject password exceeding maximum length"""
        with pytest.raises(ValidationError):
            NewPassword(
                token="test_token_123",
                new_password="a" * 41,
            )

    def test_new_password_empty_token(self) -> None:
        """Should allow empty token"""
        new_pass = NewPassword(
            token="",
            new_password="NewPassword123",
        )
        assert new_pass.token == ""


class TestEmailData:
    """Test EmailData dataclass"""

    def test_email_data_creation(self) -> None:
        """Should create EmailData instance"""
        email_data = EmailData(
            html_content="<html><body>Test</body></html>",
            subject="Test Subject",
        )
        assert email_data.html_content == "<html><body>Test</body></html>"
        assert email_data.subject == "Test Subject"

    def test_email_data_empty_html(self) -> None:
        """Should allow empty HTML content"""
        email_data = EmailData(
            html_content="",
            subject="Test Subject",
        )
        assert email_data.html_content == ""

    def test_email_data_empty_subject(self) -> None:
        """Should allow empty subject"""
        email_data = EmailData(
            html_content="<html></html>",
            subject="",
        )
        assert email_data.subject == ""

    def test_email_data_long_content(self) -> None:
        """Should handle long HTML content"""
        long_html = "<html>" + "a" * 10000 + "</html>"
        email_data = EmailData(
            html_content=long_html,
            subject="Test Subject",
        )
        assert email_data.html_content == long_html