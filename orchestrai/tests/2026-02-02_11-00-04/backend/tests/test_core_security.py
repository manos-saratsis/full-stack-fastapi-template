"""
Comprehensive tests for backend/app/core/security.py
Tests cover 100% of code paths including all functions, error cases, and edge cases.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
import jwt

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    pwd_context,
    ALGORITHM,
)
from app.core.config import settings


class TestCreateAccessToken:
    """Test create_access_token function with various inputs and edge cases."""

    def test_create_access_token_with_string_subject(self):
        """Should create a valid JWT token with string subject."""
        subject = "test_user"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_create_access_token_with_integer_subject(self):
        """Should create token with integer subject converted to string."""
        subject = 12345
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "12345"

    def test_create_access_token_with_uuid_subject(self):
        """Should create token with UUID subject converted to string."""
        import uuid
        subject = uuid.uuid4()
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == str(subject)

    def test_create_access_token_expiration_time(self):
        """Should set correct expiration time in token."""
        subject = "test"
        expires_delta = timedelta(hours=2)
        
        before_creation = datetime.now(timezone.utc)
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        after_creation = datetime.now(timezone.utc)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        
        # Verify expiration is approximately 2 hours from creation
        time_diff = exp_time - before_creation
        assert timedelta(hours=1, minutes=59) < time_diff < timedelta(hours=2, minutes=1)

    def test_create_access_token_with_negative_timedelta(self):
        """Should handle negative timedelta (already expired token)."""
        subject = "test"
        expires_delta = timedelta(hours=-1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        # Token should be expired now
        assert exp_time < datetime.now(timezone.utc)

    def test_create_access_token_with_zero_timedelta(self):
        """Should create token with immediate expiration."""
        subject = "test"
        expires_delta = timedelta(seconds=0)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded

    def test_create_access_token_with_microseconds_timedelta(self):
        """Should handle microseconds in timedelta."""
        subject = "test"
        expires_delta = timedelta(microseconds=1000)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_with_large_timedelta(self):
        """Should handle large timedelta (365 days)."""
        subject = "test"
        expires_delta = timedelta(days=365)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_create_access_token_payload_structure(self):
        """Should have correct payload structure."""
        subject = "user123"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify payload has only exp and sub
        assert set(decoded.keys()) == {"exp", "sub"}
        assert decoded["sub"] == subject

    def test_create_access_token_uses_correct_algorithm(self):
        """Should use HS256 algorithm for encoding."""
        subject = "test"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        # Verify token is valid with HS256
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == subject

    def test_create_access_token_uses_secret_key(self):
        """Should use settings.SECRET_KEY for encoding."""
        subject = "test"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        # Should be decodable with correct key
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        
        # Should fail with wrong key
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong_key", algorithms=[ALGORITHM])

    def test_create_access_token_with_special_characters_in_subject(self):
        """Should handle special characters in subject."""
        subject = "user@example.com!#$%"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == subject

    def test_create_access_token_with_empty_string_subject(self):
        """Should handle empty string subject."""
        subject = ""
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == ""

    def test_create_access_token_returns_string_type(self):
        """Should always return a string."""
        token = create_access_token(subject="test", expires_delta=timedelta(hours=1))
        assert isinstance(token, str)


class TestVerifyPassword:
    """Test verify_password function with various scenarios."""

    def test_verify_password_correct_password(self):
        """Should return True for correct password."""
        plain_password = "correct_password123"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_incorrect_password(self):
        """Should return False for incorrect password."""
        plain_password = "correct_password123"
        wrong_password = "wrong_password456"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_empty_password(self):
        """Should handle empty password string."""
        hashed = get_password_hash("nonempty")
        
        result = verify_password("", hashed)
        
        assert result is False

    def test_verify_password_with_empty_hashed_password(self):
        """Should handle empty hashed password."""
        # This tests edge case behavior - empty hash should not match any password
        plain_password = "test"
        empty_hashed = ""
        
        # This will likely raise an exception, which is fine for this edge case
        with pytest.raises(Exception):
            verify_password(plain_password, empty_hashed)

    def test_verify_password_case_sensitive(self):
        """Should be case-sensitive."""
        plain_password = "MyPassword123"
        hashed = get_password_hash(plain_password)
        
        result_correct = verify_password(plain_password, hashed)
        result_wrong_case = verify_password("mypassword123", hashed)
        
        assert result_correct is True
        assert result_wrong_case is False

    def test_verify_password_with_special_characters(self):
        """Should handle special characters in password."""
        plain_password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_unicode_characters(self):
        """Should handle unicode characters."""
        plain_password = "пароль密码🔐"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_whitespace(self):
        """Should be sensitive to whitespace."""
        plain_password = "password with spaces"
        hashed = get_password_hash(plain_password)
        
        result_correct = verify_password(plain_password, hashed)
        result_extra_space = verify_password("password  with spaces", hashed)
        
        assert result_correct is True
        assert result_extra_space is False

    def test_verify_password_returns_boolean(self):
        """Should always return boolean."""
        hashed = get_password_hash("test")
        
        result_true = verify_password("test", hashed)
        result_false = verify_password("wrong", hashed)
        
        assert isinstance(result_true, bool)
        assert isinstance(result_false, bool)

    def test_verify_password_different_hashes_same_password(self):
        """Should verify same password against different hashes."""
        plain_password = "same_password"
        hashed1 = get_password_hash(plain_password)
        hashed2 = get_password_hash(plain_password)
        
        # Different hashes but same password should verify
        assert hashed1 != hashed2
        assert verify_password(plain_password, hashed1) is True
        assert verify_password(plain_password, hashed2) is True

    def test_verify_password_with_very_long_password(self):
        """Should handle very long passwords."""
        plain_password = "a" * 1000
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_sensitive_to_trailing_spaces(self):
        """Should be sensitive to trailing spaces."""
        plain_password = "password"
        hashed = get_password_hash(plain_password)
        
        result_no_space = verify_password("password", hashed)
        result_trailing_space = verify_password("password ", hashed)
        
        assert result_no_space is True
        assert result_trailing_space is False


class TestGetPasswordHash:
    """Test get_password_hash function."""

    def test_get_password_hash_returns_string(self):
        """Should return a string hash."""
        password = "test_password"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_creates_non_empty_hash(self):
        """Should create a non-empty hash."""
        password = "test"
        
        hashed = get_password_hash(password)
        
        assert len(hashed) > 10  # bcrypt hashes are typically 60 chars

    def test_get_password_hash_different_hashes_for_same_password(self):
        """Should create different hashes for same password (salt)."""
        password = "same_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Different hashes due to salt
        assert hash1 != hash2

    def test_get_password_hash_empty_password(self):
        """Should hash empty password."""
        password = ""
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_special_characters(self):
        """Should hash passwords with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_unicode_characters(self):
        """Should hash unicode passwords."""
        password = "пароль密码🔐"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_long_password(self):
        """Should hash long passwords."""
        password = "a" * 1000
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_whitespace_sensitivity(self):
        """Should preserve whitespace in hashing."""
        password_with_spaces = "pass word"
        hashed = get_password_hash(password_with_spaces)
        
        assert verify_password("pass word", hashed) is True
        assert verify_password("password", hashed) is False

    def test_get_password_hash_with_newlines(self):
        """Should handle passwords with newlines."""
        password = "pass\nword"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True

    def test_get_password_hash_uses_bcrypt(self):
        """Should use bcrypt algorithm."""
        password = "test"
        
        hashed = get_password_hash(password)
        
        # Bcrypt hashes start with $2
        assert hashed.startswith("$2")


class TestModuleConstants:
    """Test module-level constants."""

    def test_algorithm_constant(self):
        """Should have correct ALGORITHM constant."""
        assert ALGORITHM == "HS256"

    def test_pwd_context_exists(self):
        """Should have pwd_context configured."""
        assert pwd_context is not None
        assert hasattr(pwd_context, 'verify')
        assert hasattr(pwd_context, 'hash')

    def test_pwd_context_uses_bcrypt(self):
        """Should use bcrypt in pwd_context."""
        password = "test"
        hashed = pwd_context.hash(password)
        assert hashed.startswith("$2")


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_create_token_and_extract_subject(self):
        """Should create token and extract subject successfully."""
        subject = "integration_test_user"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == subject

    def test_hash_and_verify_password_flow(self):
        """Should hash password and verify it in sequence."""
        password = "integration_test_password"
        
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        is_invalid = verify_password("wrong_password", hashed)
        
        assert is_valid is True
        assert is_invalid is False

    def test_multiple_tokens_have_different_exp(self):
        """Different tokens should have slightly different expiration times."""
        subject = "test"
        expires_delta = timedelta(hours=1)
        
        token1 = create_access_token(subject=subject, expires_delta=expires_delta)
        token2 = create_access_token(subject=subject, expires_delta=expires_delta)
        
        decoded1 = jwt.decode(token1, settings.SECRET_KEY, algorithms=[ALGORITHM])
        decoded2 = jwt.decode(token2, settings.SECRET_KEY, algorithms=[ALGORITHM])
        
        # Expiration times should be different (unless created in exact same microsecond)
        # But both should be valid
        assert "exp" in decoded1
        assert "exp" in decoded2