import pytest
from unittest.mock import Mock, MagicMock, patch
import random
import string

from fastapi.testclient import TestClient
from app.tests.utils.utils import (
    random_lower_string,
    random_email,
    get_superuser_token_headers,
)


class TestRandomLowerString:
    """Test random_lower_string function."""

    def test_random_lower_string_length(self):
        """Should return a string of length 32."""
        result = random_lower_string()
        assert len(result) == 32

    def test_random_lower_string_is_string(self):
        """Should return a string type."""
        result = random_lower_string()
        assert isinstance(result, str)

    def test_random_lower_string_is_lowercase(self):
        """Should contain only lowercase letters."""
        result = random_lower_string()
        assert result.islower()
        assert result.isalpha()

    def test_random_lower_string_uniqueness(self):
        """Should generate different strings on multiple calls."""
        result1 = random_lower_string()
        result2 = random_lower_string()
        # Extremely unlikely to be the same (1 in 26^32)
        assert result1 != result2

    def test_random_lower_string_contains_only_ascii_lowercase(self):
        """Should contain only ASCII lowercase letters."""
        result = random_lower_string()
        assert all(c in string.ascii_lowercase for c in result)

    def test_random_lower_string_multiple_calls(self):
        """Should return valid string format on multiple calls."""
        for _ in range(10):
            result = random_lower_string()
            assert len(result) == 32
            assert isinstance(result, str)
            assert result.islower()


class TestRandomEmail:
    """Test random_email function."""

    def test_random_email_format(self):
        """Should return a valid email format."""
        result = random_email()
        assert "@" in result
        assert "." in result

    def test_random_email_structure(self):
        """Should have format: string@string.com."""
        result = random_email()
        parts = result.split("@")
        assert len(parts) == 2
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0
        assert parts[1].endswith(".com")

    def test_random_email_local_part_length(self):
        """Should have local part of 32 lowercase characters."""
        result = random_email()
        local_part = result.split("@")[0]
        assert len(local_part) == 32
        assert local_part.isalpha()
        assert local_part.islower()

    def test_random_email_domain_structure(self):
        """Should have domain of 32 lowercase characters + '.com'."""
        result = random_email()
        domain = result.split("@")[1]
        domain_name = domain.replace(".com", "")
        assert len(domain_name) == 32
        assert domain.endswith(".com")
        assert domain_name.isalpha()
        assert domain_name.islower()

    def test_random_email_is_string(self):
        """Should return a string type."""
        result = random_email()
        assert isinstance(result, str)

    def test_random_email_uniqueness(self):
        """Should generate different emails on multiple calls."""
        email1 = random_email()
        email2 = random_email()
        # Extremely unlikely to be the same
        assert email1 != email2

    def test_random_email_multiple_calls(self):
        """Should generate valid emails on multiple calls."""
        for _ in range(10):
            result = random_email()
            assert "@" in result
            assert ".com" in result
            assert len(result) > 0


class TestGetSuperuserTokenHeaders:
    """Test get_superuser_token_headers function."""

    def test_get_superuser_token_headers_success(self):
        """Should return valid authorization headers when login succeeds."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_token_12345"}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "admin"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "password123"
            mock_settings.API_V1_STR = "/api/v1"

            result = get_superuser_token_headers(mock_client)

            assert isinstance(result, dict)
            assert "Authorization" in result
            assert result["Authorization"] == "Bearer test_token_12345"

    def test_get_superuser_token_headers_post_call(self):
        """Should call client.post with correct login endpoint."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "superuser"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "pass"
            mock_settings.API_V1_STR = "/api/v1"

            get_superuser_token_headers(mock_client)

            mock_client.post.assert_called_once_with(
                "/api/v1/login/access-token",
                data={"username": "superuser", "password": "pass"}
            )

    def test_get_superuser_token_headers_credentials_from_settings(self):
        """Should use FIRST_SUPERUSER and FIRST_SUPERUSER_PASSWORD from settings."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "admin_user"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "admin_pass"
            mock_settings.API_V1_STR = "/api/v1"

            get_superuser_token_headers(mock_client)

            call_args = mock_client.post.call_args
            assert call_args[1]["data"]["username"] == "admin_user"
            assert call_args[1]["data"]["password"] == "admin_pass"

    def test_get_superuser_token_headers_token_extraction(self):
        """Should correctly extract access_token from response."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        test_token = "my_special_token_xyz"
        mock_response.json.return_value = {"access_token": test_token}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "admin"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "pass"
            mock_settings.API_V1_STR = "/api/v1"

            result = get_superuser_token_headers(mock_client)

            assert result["Authorization"] == f"Bearer {test_token}"

    def test_get_superuser_token_headers_bearer_prefix(self):
        """Should include 'Bearer ' prefix in Authorization header."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "abc123"}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "user"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "pass"
            mock_settings.API_V1_STR = "/api/v1"

            result = get_superuser_token_headers(mock_client)

            assert result["Authorization"].startswith("Bearer ")

    def test_get_superuser_token_headers_returns_dict(self):
        """Should return a dictionary with string keys and values."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "admin"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "pass"
            mock_settings.API_V1_STR = "/api/v1"

            result = get_superuser_token_headers(mock_client)

            assert isinstance(result, dict)
            assert all(isinstance(k, str) for k in result.keys())
            assert all(isinstance(v, str) for v in result.values())

    def test_get_superuser_token_headers_empty_token(self):
        """Should handle empty token from response."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": ""}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "admin"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "pass"
            mock_settings.API_V1_STR = "/api/v1"

            result = get_superuser_token_headers(mock_client)

            assert result["Authorization"] == "Bearer "

    def test_get_superuser_token_headers_api_endpoint_construction(self):
        """Should correctly construct API endpoint from settings."""
        mock_client = MagicMock(spec=TestClient)
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "token"}
        mock_client.post.return_value = mock_response

        with patch("app.tests.utils.utils.settings") as mock_settings:
            mock_settings.FIRST_SUPERUSER = "admin"
            mock_settings.FIRST_SUPERUSER_PASSWORD = "pass"
            mock_settings.API_V1_STR = "/api/custom"

            get_superuser_token_headers(mock_client)

            mock_client.post.assert_called_once()
            call_url = mock_client.post.call_args[0][0]
            assert call_url == "/api/custom/login/access-token"