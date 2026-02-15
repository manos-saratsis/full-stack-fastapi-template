import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import jwt

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    ALGORITHM,
    pwd_context,
)
from app.core.config import settings


class TestCreateAccessToken:
    """Test create_access_token function with all edge cases."""

    def test_create_access_token_with_string_subject(self):
        """should create valid JWT token when subject is string"""
        subject = "test_user_123"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # Verify token is decodable
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_create_access_token_with_numeric_subject(self):
        """should convert numeric subject to string"""
        subject = 12345
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "12345"

    def test_create_access_token_with_uuid_subject(self):
        """should convert UUID subject to string"""
        from uuid import UUID
        subject = UUID('12345678-1234-5678-1234-567812345678')
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == str(subject)

    def test_create_access_token_expiration_in_future(self):
        """should set expiration time in the future"""
        subject = "test_user"
        expires_delta = timedelta(minutes=60)
        
        before_creation = datetime.now(timezone.utc)
        token = create_access_token(subject, expires_delta)
        after_creation = datetime.now(timezone.utc)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Verify expiration is roughly 60 minutes in future
        expected_min = before_creation + expires_delta
        expected_max = after_creation + expires_delta
        assert expected_min <= exp_datetime <= expected_max

    def test_create_access_token_with_zero_delta(self):
        """should create token with immediate expiration when delta is zero"""
        subject = "test_user"
        expires_delta = timedelta(seconds=0)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        # Expiration should be very close to now
        assert decoded["exp"] > 0

    def test_create_access_token_with_negative_delta(self):
        """should create token with past expiration when delta is negative"""
        subject = "test_user"
        expires_delta = timedelta(minutes=-10)
        
        token = create_access_token(subject, expires_delta)
        
        # Token is created but would be expired
        assert isinstance(token, str)

    def test_create_access_token_with_large_delta(self):
        """should handle large expiration deltas"""
        subject = "test_user"
        expires_delta = timedelta(days=365)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_uses_correct_algorithm(self):
        """should use HS256 algorithm"""
        subject = "test_user"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        # Decode header to verify algorithm
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"

    def test_create_access_token_uses_secret_key(self):
        """should use settings.SECRET_KEY for encoding"""
        subject = "test_user"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        # Should decode with correct secret
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject
        
        # Should fail with wrong secret
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong_secret_key", algorithms=[ALGORITHM])

    def test_create_access_token_with_empty_string_subject(self):
        """should handle empty string subject"""
        subject = ""
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == ""

    def test_create_access_token_with_special_characters_in_subject(self):
        """should handle special characters in subject"""
        subject = "user@example.com!@#$%"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == subject

    def test_create_access_token_payload_has_required_fields(self):
        """should always include exp and sub in payload"""
        subject = "test_user"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(subject, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        assert "sub" in decoded


class TestVerifyPassword:
    """Test verify_password function with all paths."""

    def test_verify_password_with_correct_password(self):
        """should return True when password matches hash"""
        plain_password = "TestPassword123!"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_incorrect_password(self):
        """should return False when password does not match hash"""
        plain_password = "TestPassword123!"
        hashed = get_password_hash(plain_password)
        wrong_password = "WrongPassword456!"
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_with_empty_password(self):
        """should handle empty password"""
        plain_password = ""
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_empty_password_and_wrong_input(self):
        """should fail when verifying wrong password against empty hash"""
        plain_password = ""
        hashed = get_password_hash(plain_password)
        wrong_password = "SomePassword"
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_with_special_characters(self):
        """should handle passwords with special characters"""
        plain_password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_unicode_characters(self):
        """should handle unicode passwords"""
        plain_password = "Pässwörd123!αβγδ"
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_case_sensitive(self):
        """should be case sensitive"""
        plain_password = "TestPassword123!"
        hashed = get_password_hash(plain_password)
        wrong_case = "testpassword123!"
        
        result = verify_password(wrong_case, hashed)
        
        assert result is False

    def test_verify_password_with_whitespace(self):
        """should be sensitive to whitespace"""
        plain_password = "Password123"
        hashed = get_password_hash(plain_password)
        with_space = "Password 123"
        
        result = verify_password(with_space, hashed)
        
        assert result is False

    def test_verify_password_with_long_password(self):
        """should handle long passwords"""
        plain_password = "A" * 100
        hashed = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed)
        
        assert result is True

    def test_verify_password_with_different_hash_same_password(self):
        """should work with different hashes of same password"""
        plain_password = "TestPassword123!"
        hash1 = get_password_hash(plain_password)
        hash2 = get_password_hash(plain_password)
        
        result1 = verify_password(plain_password, hash1)
        result2 = verify_password(plain_password, hash2)
        
        assert result1 is True
        assert result2 is True
        # Hashes should be different due to salt
        assert hash1 != hash2


class TestGetPasswordHash:
    """Test get_password_hash function."""

    def test_get_password_hash_returns_string(self):
        """should return a string hash"""
        password = "TestPassword123!"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_returns_bcrypt_hash(self):
        """should return bcrypt formatted hash"""
        password = "TestPassword123!"
        
        hashed = get_password_hash(password)
        
        assert hashed.startswith("$2b$")

    def test_get_password_hash_different_hash_each_call(self):
        """should produce different hash each time due to salt"""
        password = "TestPassword123!"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2

    def test_get_password_hash_with_empty_password(self):
        """should hash empty password"""
        password = ""
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_with_special_characters(self):
        """should handle special characters"""
        password = "P@ssw0rd!#$%^&*()"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_with_unicode(self):
        """should handle unicode characters"""
        password = "Pässwörd123!αβγδ"
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_with_long_password(self):
        """should handle long passwords"""
        password = "A" * 200
        
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)

    def test_get_password_hash_is_verifiable(self):
        """should produce hash that can be verified"""
        password = "TestPassword123!"
        
        hashed = get_password_hash(password)
        verified = verify_password(password, hashed)
        
        assert verified is True


class TestModuleConstants:
    """Test module-level constants."""

    def test_algorithm_constant(self):
        """should define ALGORITHM constant"""
        assert ALGORITHM == "HS256"

    def test_pwd_context_is_configured(self):
        """should have pwd_context configured"""
        assert pwd_context is not None
        assert hasattr(pwd_context, 'verify')
        assert hasattr(pwd_context, 'hash')

    def test_pwd_context_uses_bcrypt(self):
        """should use bcrypt scheme"""
        password = "TestPassword123!"
        hashed = pwd_context.hash(password)
        assert hashed.startswith("$2b$")