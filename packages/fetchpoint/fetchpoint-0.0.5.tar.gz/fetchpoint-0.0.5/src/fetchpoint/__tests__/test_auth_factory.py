"""Tests for authentication factory functionality."""

from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from fetchpoint.auth_factory import (
    _detect_auth_method,  # pyright: ignore[reportPrivateUsage]
    create_sharepoint_context,
)
from fetchpoint.exceptions import ConfigurationError
from fetchpoint.models import AuthMethod, SharePointAuthConfig, SharePointMSALConfig


class TestAuthFactory:
    """Test authentication factory functions."""

    def test_detect_auth_method_from_config_type_legacy(self):
        """Test auto-detection of auth method from legacy config type."""
        legacy_config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        assert _detect_auth_method(legacy_config, None) == AuthMethod.LEGACY

    def test_detect_auth_method_from_config_type_msal(self):
        """Test auto-detection of auth method from MSAL config type."""
        msal_config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://example.sharepoint.com",
        )

        assert _detect_auth_method(msal_config, None) == AuthMethod.MSAL

    def test_explicit_auth_method_validation_valid(self):
        """Test validation of explicit auth method against config type."""
        legacy_config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        # Valid combination
        assert _detect_auth_method(legacy_config, AuthMethod.LEGACY) == AuthMethod.LEGACY

    def test_explicit_auth_method_validation_invalid(self):
        """Test validation of invalid auth method against config type."""
        legacy_config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        # Invalid combination
        with pytest.raises(ConfigurationError, match="MSAL authentication method requires SharePointMSALConfig"):
            _detect_auth_method(legacy_config, AuthMethod.MSAL)

    def test_explicit_auth_method_string_conversion(self):
        """Test string to enum conversion for auth method."""
        legacy_config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        # Valid string conversion
        assert _detect_auth_method(legacy_config, "legacy") == AuthMethod.LEGACY

        # Invalid string
        with pytest.raises(ConfigurationError, match="Invalid authentication method"):
            _detect_auth_method(legacy_config, "invalid")

    def test_detect_auth_method_unknown_config_type(self):
        """Test error when config type is unknown."""
        unknown_config = Mock()  # Not a valid config type

        with pytest.raises(ConfigurationError, match="Cannot auto-detect authentication method"):
            _detect_auth_method(unknown_config, None)

    @patch("fetchpoint.auth_factory.create_authenticated_context")
    def test_create_context_legacy_auto_detect(self, mock_legacy_auth: Mock):
        """Test creating context with legacy authentication (auto-detected)."""
        config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_legacy_auth.return_value = mock_context

        result = create_sharepoint_context(config)

        assert result == mock_context
        mock_legacy_auth.assert_called_once_with(config)

    @patch("fetchpoint.auth_factory.create_authenticated_context")
    def test_create_context_legacy_explicit(self, mock_legacy_auth: Mock):
        """Test creating context with legacy authentication (explicit)."""
        config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_legacy_auth.return_value = mock_context

        result = create_sharepoint_context(config, AuthMethod.LEGACY)

        assert result == mock_context
        mock_legacy_auth.assert_called_once_with(config)

    @patch("fetchpoint.auth_factory.create_msal_authenticated_context")
    def test_create_context_msal_auto_detect(self, mock_msal_auth: Mock):
        """Test creating context with MSAL authentication (auto-detected)."""
        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://example.sharepoint.com",
        )
        mock_context = Mock()
        mock_msal_auth.return_value = mock_context

        result = create_sharepoint_context(config)

        assert result == mock_context
        mock_msal_auth.assert_called_once_with(config)

    @patch("fetchpoint.auth_factory.create_msal_authenticated_context")
    def test_create_context_msal_explicit(self, mock_msal_auth: Mock):
        """Test creating context with MSAL authentication (explicit)."""
        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://example.sharepoint.com",
        )
        mock_context = Mock()
        mock_msal_auth.return_value = mock_context

        result = create_sharepoint_context(config, AuthMethod.MSAL)

        assert result == mock_context
        mock_msal_auth.assert_called_once_with(config)

    def test_create_context_config_type_mismatch_legacy(self):
        """Test error when config type doesn't match explicit auth method (legacy)."""
        msal_config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://example.sharepoint.com",
        )

        with pytest.raises(ConfigurationError, match="Legacy authentication method requires SharePointAuthConfig"):
            create_sharepoint_context(msal_config, AuthMethod.LEGACY)

    def test_create_context_config_type_mismatch_msal(self):
        """Test error when config type doesn't match explicit auth method (MSAL)."""
        legacy_config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        with pytest.raises(ConfigurationError, match="MSAL authentication method requires SharePointMSALConfig"):
            create_sharepoint_context(legacy_config, AuthMethod.MSAL)

    def test_create_context_unsupported_auth_method(self):
        """Test error with unsupported authentication method."""
        legacy_config = SharePointAuthConfig(
            username="user@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        # Mock an unsupported auth method by creating a custom enum value
        class UnsupportedAuthMethod:
            value = "unsupported"

        with patch("fetchpoint.auth_factory._detect_auth_method") as mock_detect:
            mock_detect.return_value = UnsupportedAuthMethod()

            with pytest.raises(ConfigurationError, match="Unsupported authentication method"):
                create_sharepoint_context(legacy_config)
