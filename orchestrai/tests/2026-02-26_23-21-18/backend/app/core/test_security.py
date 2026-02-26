import jwt
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from passlib.context import CryptContext

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    pwd_context,
    ALGORITHM,
)
from app.core.config import settings


class TestCreateAccessToken:
    """Test suite for create_access_token function."""

    def test_create_access_token_with_string_subject(self):
        """Should create a valid JWT token with string subject."""
        subject = "user123"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_create_access_token_with_integer_subject(self):
        """Should create a valid JWT token with integer subject."""
        subject = 12345
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "12345"

    def test_create_access_token_with_custom_object_subject(self):
        """Should create a valid JWT token with custom object converted to string."""
        class CustomObject:
            def __str__(self):
                return "custom_object_id"
        
        subject = CustomObject()
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "custom_object_id"

    def test_create_access_token_expiration_time(self):
        """Should set correct expiration time in token."""
        subject = "user123"
        expires_delta = timedelta(hours=2)
        
        before = datetime.now(timezone.utc)
        token = create_access_token(subject, expires_delta)
        after = datetime.now(timezone.utc)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        
        # Verify expiration is approximately 2 hours in the future
        assert exp_time > before + expires_delta - timedelta(seconds=1)
        assert exp_time < after + expires_delta + timedelta(seconds=1)

    def test_create_access_token_with_zero_expires_delta(self):
        """Should create token with expiration set to now when delta is zero."""
        subject = "user123"
        expires_delta = timedelta(0)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded

    def test_create_access_token_with_negative_expires_delta(self):
        """Should create token with past expiration when delta is negative."""
        subject = "user123"
        expires_delta = timedelta(hours=-1)
        
        token = create_access_token(subject, expires_delta)
        
        # Token can still be created, but will be expired
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

    def test_create_access_token_with_large_expires_delta(self):
        """Should create token with far future expiration."""
        subject = "user123"
        expires_delta = timedelta(days=365)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded

    def test_create_access_token_uses_correct_algorithm(self):
        """Should encode token using HS256 algorithm."""
        subject = "user123"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        # Verify token can be decoded with HS256
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert isinstance(decoded, dict)

    def test_create_access_token_invalid_with_wrong_secret(self):
        """Should not be decodable with wrong secret key."""
        subject = "user123"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong_secret", algorithms=[ALGORITHM])

    def test_create_access_token_empty_subject(self):
        """Should create token with empty string subject."""
        subject = ""
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == ""

    def test_create_access_token_special_characters_in_subject(self):
        """Should handle special characters in subject."""
        subject = "user@example.com#2024!@#$%"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_microseconds_precision(self):
        """Should maintain timestamp precision in token."""
        subject = "user123"
        expires_delta = timedelta(microseconds=500000)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded


class TestVerifyPassword:
    """Test suite for verify_password function."""

    def test_verify_password_correct_password(self):
        """Should return True when password matches hash."""
        plain_password = "MySecurePassword123!"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed_password)
        
        assert result is True

    def test_verify_password_incorrect_password(self):
        """Should return False when password does not match hash."""
        plain_password = "MySecurePassword123!"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password("WrongPassword123!", hashed_password)
        
        assert result is False

    def test_verify_password_empty_plain_password(self):
        """Should handle empty plain password."""
        plain_password = ""
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password("", hashed_password)
        
        assert result is True

    def test_verify_password_empty_mismatch(self):
        """Should return False when comparing non-empty to empty hash."""
        hashed_password = pwd_context.hash("")
        
        result = verify_password("notEmpty", hashed_password)
        
        assert result is False

    def test_verify_password_special_characters(self):
        """Should handle passwords with special characters."""
        plain_password = "P@$$w0rd!#%&*()[]{}|\\:;<>?,./"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed_password)
        
        assert result is True

    def test_verify_password_unicode_characters(self):
        """Should handle passwords with unicode characters."""
        plain_password = "пароль密码🔒"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed_password)
        
        assert result is True

    def test_verify_password_whitespace_sensitive(self):
        """Should be sensitive to whitespace differences."""
        plain_password = "Password123"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password("Password123 ", hashed_password)
        
        assert result is False

    def test_verify_password_case_sensitive(self):
        """Should be case sensitive."""
        plain_password = "MyPassword123"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password("mypassword123", hashed_password)
        
        assert result is False

    def test_verify_password_long_password(self):
        """Should handle very long passwords."""
        plain_password = "a" * 1000
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed_password)
        
        assert result is True

    def test_verify_password_different_hashes_same_password(self):
        """Should verify same password against different hashes."""
        plain_password = "MyPassword123"
        hashed_password1 = pwd_context.hash(plain_password)
        hashed_password2 = pwd_context.hash(plain_password)
        
        # Different hashes due to salt
        assert hashed_password1 != hashed_password2
        
        # But both should verify correctly
        assert verify_password(plain_password, hashed_password1) is True
        assert verify_password(plain_password, hashed_password2) is True

    def test_verify_password_with_none_like_string(self):
        """Should handle string representations of null-like values."""
        plain_password = "None"
        hashed_password = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed_password)
        
        assert result is True


class TestGetPasswordHash:
    """Test suite for get_password_hash function."""

    def test_get_password_hash_returns_string(self):
        """Should return a string hash."""
        password = "MySecurePassword123!"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_bcrypt_format(self):
        """Should return bcrypt formatted hash."""
        password = "MySecurePassword123!"
        
        hashed = get_password_hash(password)
        
        # Bcrypt hashes start with $2a$, $2b$, or $2y$
        assert hashed.startswith("$2")

    def test_get_password_hash_different_hashes_same_password(self):
        """Should produce different hashes for same password (due to salt)."""
        password = "MySecurePassword123!"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2

    def test_get_password_hash_empty_password(self):
        """Should hash empty password."""
        password = ""
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_special_characters(self):
        """Should hash password with special characters."""
        password = "P@$$w0rd!#%&*()[]{}|\\:;<>?,./"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_unicode_characters(self):
        """Should hash password with unicode characters."""
        password = "пароль密码🔒"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_whitespace(self):
        """Should preserve whitespace in password hash."""
        password = "Pass  word  123"
        
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("Password123", hashed) is False

    def test_get_password_hash_long_password(self):
        """Should hash very long password."""
        password = "a" * 1000
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_is_one_way(self):
        """Should not be reversible (one-way hash)."""
        password = "MySecurePassword123!"
        
        hashed = get_password_hash(password)
        
        # Should not be able to extract original password from hash
        assert hashed != password
        assert password not in hashed

    def test_get_password_hash_consistency_with_verify(self):
        """Should produce hashes that verify correctly."""
        password = "TestPassword123"
        
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        
        assert is_valid is True

    def test_get_password_hash_works_with_bcrypt_directly(self):
        """Should produce hashes that bcrypt can verify."""
        password = "MySecurePassword123!"
        
        hashed = get_password_hash(password)
        
        # Can verify with passlib's pwd_context
        assert pwd_context.verify(password, hashed) is True


class TestModuleConstants:
    """Test suite for module-level constants."""

    def test_algorithm_constant(self):
        """Should define ALGORITHM constant."""
        assert ALGORITHM == "HS256"
        assert isinstance(ALGORITHM, str)

    def test_pwd_context_is_crypt_context(self):
        """Should initialize pwd_context as CryptContext."""
        assert isinstance(pwd_context, CryptContext)

    def test_pwd_context_uses_bcrypt(self):
        """Should configure pwd_context to use bcrypt."""
        password = "TestPassword123"
        hashed = pwd_context.hash(password)
        assert pwd_context.verify(password, hashed) is True


class TestIntegration:
    """Integration tests for security functions."""

    def test_password_hash_and_verify_workflow(self):
        """Should support complete password hashing and verification workflow."""
        original_password = "UserPassword123!"
        
        # User registers with password
        hashed = get_password_hash(original_password)
        
        # User logs in with correct password
        assert verify_password(original_password, hashed) is True
        
        # User tries wrong password
        assert verify_password("WrongPassword123!", hashed) is False

    def test_token_creation_and_decode_workflow(self):
        """Should support complete token creation and decoding workflow."""
        user_id = 42
        expires_delta = timedelta(hours=1)
        
        # Create token
        token = create_access_token(user_id, expires_delta)
        
        # Decode and verify
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == str(user_id)
        assert "exp" in decoded

    def test_expired_token_cannot_be_decoded(self):
        """Should create tokens that properly expire."""
        user_id = 42
        expires_delta = timedelta(milliseconds=1)
        
        # Create immediately-expiring token
        token = create_access_token(user_id, expires_delta)
        
        # Wait a bit and try to decode
        import time
        time.sleep(0.1)
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])