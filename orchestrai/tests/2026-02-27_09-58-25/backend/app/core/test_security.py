import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import jwt
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
    """Tests for create_access_token function"""

    def test_create_access_token_with_string_subject(self):
        """Should create a valid JWT token with string subject"""
        subject = "test_user_id"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify the token can be decoded
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_create_access_token_with_int_subject(self):
        """Should create a valid JWT token with integer subject"""
        subject = 123
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == str(subject)

    def test_create_access_token_with_zero_expiration(self):
        """Should create token that expires immediately"""
        subject = "test_user"
        expires_delta = timedelta(seconds=0)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_with_negative_expiration(self):
        """Should create token with past expiration time"""
        subject = "test_user"
        expires_delta = timedelta(hours=-1)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        # Token should be created but will be expired
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

    def test_create_access_token_with_large_expiration(self):
        """Should create token with very large expiration time"""
        subject = "test_user"
        expires_delta = timedelta(days=365)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_expiration_time_is_in_future(self):
        """Should ensure expiration time is always in the future"""
        subject = "test_user"
        expires_delta = timedelta(hours=1)
        before_time = datetime.now(timezone.utc)
        
        token = create_access_token(subject, expires_delta)
        
        after_time = datetime.now(timezone.utc)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        
        assert exp_time > before_time
        assert exp_time <= after_time + expires_delta + timedelta(seconds=1)

    def test_create_access_token_with_special_characters_in_subject(self):
        """Should handle special characters in subject"""
        subject = "user@example.com:test&123"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_with_empty_string_subject(self):
        """Should create token with empty string subject"""
        subject = ""
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == ""

    def test_create_access_token_algorithm_is_hs256(self):
        """Should use HS256 algorithm"""
        subject = "test_user"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(subject, expires_delta)
        
        # Decode header to verify algorithm
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"


class TestVerifyPassword:
    """Tests for verify_password function"""

    def test_verify_password_with_correct_password(self):
        """Should return True when password matches hash"""
        plain_password = "correct_password123"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_incorrect_password(self):
        """Should return False when password doesn't match hash"""
        plain_password = "correct_password123"
        wrong_password = "wrong_password123"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_with_empty_password(self):
        """Should handle empty password"""
        plain_password = ""
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_empty_string_against_empty_hash(self):
        """Should return False when comparing empty to non-empty"""
        plain_password = "password"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password("", hashed)
        
        assert result is False

    def test_verify_password_with_special_characters(self):
        """Should handle special characters in password"""
        plain_password = "p@$$w0rd!#%&*"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_unicode_characters(self):
        """Should handle unicode characters in password"""
        plain_password = "pässwörd🔐"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_very_long_password(self):
        """Should handle very long passwords"""
        plain_password = "p" * 1000
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_wrong_long_password(self):
        """Should return False for wrong long password"""
        plain_password = "p" * 1000
        wrong_password = "p" * 999 + "q"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_case_sensitive(self):
        """Should be case sensitive"""
        plain_password = "Password123"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password("password123", hashed)
        
        assert result is False

    def test_verify_password_with_whitespace(self):
        """Should handle whitespace in password"""
        plain_password = "pass word 123"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_whitespace_sensitive(self):
        """Should be sensitive to whitespace differences"""
        plain_password = "password 123"
        wrong_password = "password123"
        hashed = pwd_context.hash(plain_password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False


class TestGetPasswordHash:
    """Tests for get_password_hash function"""

    def test_get_password_hash_returns_string(self):
        """Should return a string hash"""
        password = "test_password"
        
        hash_result = get_password_hash(password)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) > 0

    def test_get_password_hash_creates_different_hashes_for_same_password(self):
        """Should create different hashes for same password (salt variation)"""
        password = "test_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2

    def test_get_password_hash_hashes_are_verifiable(self):
        """Should create hashes that can be verified"""
        password = "test_password"
        
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_get_password_hash_with_empty_password(self):
        """Should hash empty password"""
        password = ""
        
        hash_result = get_password_hash(password)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) > 0
        assert verify_password("", hash_result) is True

    def test_get_password_hash_with_special_characters(self):
        """Should hash password with special characters"""
        password = "p@$$w0rd!#%&*"
        
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_get_password_hash_with_unicode_characters(self):
        """Should hash password with unicode characters"""
        password = "pässwörd🔐"
        
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_get_password_hash_with_very_long_password(self):
        """Should hash very long passwords"""
        password = "p" * 1000
        
        hash_result = get_password_hash(password)
        
        assert isinstance(hash_result, str)
        assert verify_password(password, hash_result) is True

    def test_get_password_hash_contains_bcrypt_prefix(self):
        """Should use bcrypt algorithm (check for $2b$ prefix)"""
        password = "test_password"
        
        hash_result = get_password_hash(password)
        
        # Bcrypt hashes start with $2a$, $2b$, or $2y$
        assert hash_result.startswith("$2")

    def test_get_password_hash_with_whitespace_password(self):
        """Should hash password with whitespace"""
        password = "pass word 123"
        
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_get_password_hash_result_length(self):
        """Should produce consistent hash length"""
        password = "test"
        
        hash_result = get_password_hash(password)
        
        # Bcrypt typically produces hashes of length 60
        assert len(hash_result) == 60


class TestPwdContextConfiguration:
    """Tests for pwd_context configuration"""

    def test_pwd_context_uses_bcrypt(self):
        """Should use bcrypt as the hashing scheme"""
        password = "test_password"
        
        hashed = pwd_context.hash(password)
        
        assert hashed.startswith("$2")

    def test_pwd_context_scheme_is_configured(self):
        """Should have bcrypt scheme configured"""
        assert "bcrypt" in pwd_context.schemes()

    def test_pwd_context_verify_method_exists(self):
        """Should have verify method"""
        assert hasattr(pwd_context, "verify")
        assert callable(pwd_context.verify)

    def test_pwd_context_hash_method_exists(self):
        """Should have hash method"""
        assert hasattr(pwd_context, "hash")
        assert callable(pwd_context.hash)


class TestAlgorithmConstant:
    """Tests for ALGORITHM constant"""

    def test_algorithm_is_hs256(self):
        """Should define ALGORITHM as HS256"""
        assert ALGORITHM == "HS256"

    def test_algorithm_is_string(self):
        """Should be a string type"""
        assert isinstance(ALGORITHM, str)