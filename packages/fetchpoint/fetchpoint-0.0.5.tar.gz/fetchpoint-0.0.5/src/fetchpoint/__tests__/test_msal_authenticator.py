"""Tests for MSAL authentication functionality."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr, ValidationError

from fetchpoint.exceptions import FederatedAuthError
from fetchpoint.models import SharePointMSALConfig
from fetchpoint.msal_authenticator import (
    _mask_tenant_id,  # pyright: ignore[reportPrivateUsage]
    build_msal_token_callback,
    create_msal_authenticated_context,
)


class TestSharePointMSALConfig:
    """Test MSAL configuration model."""

    def test_valid_msal_config(self):
        """Test valid MSAL configuration creation."""
        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://test.sharepoint.com",
        )

        assert config.tenant_id == "12345678-1234-1234-1234-123456789012"
        assert config.client_id == "87654321-4321-4321-4321-210987654321"
        assert config.client_secret.get_secret_value() == "test-secret"

    def test_invalid_tenant_id(self):
        """Test invalid tenant ID validation."""
        with pytest.raises(ValidationError):
            SharePointMSALConfig(
                tenant_id="invalid-uuid",
                client_id="87654321-4321-4321-4321-210987654321",
                client_secret=SecretStr("test-secret"),
                sharepoint_url="https://test.sharepoint.com",
            )

    def test_invalid_client_id(self):
        """Test invalid client ID validation."""
        with pytest.raises(ValidationError):
            SharePointMSALConfig(
                tenant_id="12345678-1234-1234-1234-123456789012",
                client_id="invalid-uuid",
                client_secret=SecretStr("test-secret"),
                sharepoint_url="https://test.sharepoint.com",
            )

    def test_from_dict_valid(self):
        """Test creating config from valid dictionary."""
        config_dict: dict[str, Any] = {
            "tenant_id": "12345678-1234-1234-1234-123456789012",
            "client_id": "87654321-4321-4321-4321-210987654321",
            "client_secret": "test-secret",
            "sharepoint_url": "https://test.sharepoint.com",
        }
        config = SharePointMSALConfig.from_dict(config_dict)
        assert config.tenant_id == "12345678-1234-1234-1234-123456789012"
        assert config.client_id == "87654321-4321-4321-4321-210987654321"

    def test_from_dict_missing_keys(self):
        """Test creating config from dictionary with missing keys."""
        config_dict: dict[str, Any] = {
            "tenant_id": "12345678-1234-1234-1234-123456789012",
            "client_secret": "test-secret",
            # Missing client_id and sharepoint_url
        }
        with pytest.raises(ValueError, match="Missing required MSAL configuration keys"):
            SharePointMSALConfig.from_dict(config_dict)


class TestMSALAuthenticator:
    """Test MSAL authentication functions."""

    def test_mask_tenant_id(self):
        """Test tenant ID masking for logging."""
        tenant_id = "12345678-1234-1234-1234-123456789012"
        masked = _mask_tenant_id(tenant_id)
        assert masked == "12345678***"
        assert len(masked) < len(tenant_id)

    def test_mask_short_tenant_id(self):
        """Test masking of short tenant ID."""
        tenant_id = "short"
        masked = _mask_tenant_id(tenant_id)
        assert masked == "***"

    @patch("fetchpoint.msal_authenticator.msal")
    def test_build_msal_token_callback_success(self, mock_msal: Mock):
        """Test MSAL token callback creation."""
        # Setup mock
        mock_app = Mock()
        mock_msal.ConfidentialClientApplication.return_value = mock_app
        mock_app.acquire_token_for_client.return_value = {"access_token": "test-token", "token_type": "Bearer"}

        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://test.sharepoint.com",
        )

        callback = build_msal_token_callback(config)

        # Test callback execution
        with patch("fetchpoint.msal_authenticator.TokenResponse") as mock_token_response:
            callback()
            mock_token_response.from_json.assert_called_once()

    @patch("fetchpoint.msal_authenticator.msal")
    def test_build_msal_token_callback_failure(self, mock_msal: Mock):
        """Test MSAL token callback failure."""
        # Setup mock
        mock_app = Mock()
        mock_msal.ConfidentialClientApplication.return_value = mock_app
        mock_app.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "Client credentials are invalid",
        }

        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://test.sharepoint.com",
        )

        callback = build_msal_token_callback(config)

        # Test callback execution failure
        with pytest.raises(RuntimeError, match="Token acquisition failed"):
            callback()

    @patch("fetchpoint.msal_authenticator._create_msal_client_context")
    @patch("fetchpoint.msal_authenticator._validate_connection")
    def test_create_msal_authenticated_context_success(self, mock_validate: Mock, mock_create_context: Mock):
        """Test successful MSAL authentication."""
        # Setup mocks
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_validate.return_value = None

        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://test.sharepoint.com",
        )

        # Test successful authentication
        result = create_msal_authenticated_context(config)

        assert result == mock_context
        mock_create_context.assert_called_once_with(config)
        mock_validate.assert_called_once_with(mock_context)

    @patch("fetchpoint.msal_authenticator._create_msal_client_context")
    def test_create_msal_authenticated_context_failure(self, mock_create_context: Mock):
        """Test MSAL authentication failure."""
        # Setup mock to raise exception
        mock_create_context.side_effect = Exception("AADSTS700016: Application with identifier 'invalid' was not found")

        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://test.sharepoint.com",
        )

        # Test authentication failure
        with pytest.raises(FederatedAuthError, match="Invalid client ID"):
            create_msal_authenticated_context(config)

    @patch("fetchpoint.msal_authenticator.ClientContext")
    @patch("fetchpoint.msal_authenticator.build_msal_token_callback")
    def test_create_msal_client_context(self, mock_token_callback: Mock, mock_client_context: Mock):
        """Test creating SharePoint client context with MSAL."""
        # Setup mocks
        mock_context = Mock()
        mock_client_context.return_value = mock_context
        mock_context.with_access_token.return_value = mock_context
        mock_callback = Mock()
        mock_token_callback.return_value = mock_callback

        config = SharePointMSALConfig(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="87654321-4321-4321-4321-210987654321",
            client_secret=SecretStr("test-secret"),
            sharepoint_url="https://test.sharepoint.com",
        )

        from fetchpoint.msal_authenticator import _create_msal_client_context  # pyright: ignore[reportPrivateUsage]

        result = _create_msal_client_context(config)

        assert result == mock_context
        mock_client_context.assert_called_once_with("https://test.sharepoint.com")
        mock_context.with_access_token.assert_called_once_with(mock_callback)

    @patch("fetchpoint.msal_authenticator.ClientContext")
    def test_validate_connection(self, mock_client_context: Mock):
        """Test connection validation."""
        # Setup mock context
        mock_context = Mock()
        mock_web = Mock()
        mock_context.web = mock_web

        from fetchpoint.msal_authenticator import _validate_connection  # pyright: ignore[reportPrivateUsage]

        # Test successful validation
        _validate_connection(mock_context)

        mock_context.load.assert_called_once_with(mock_web)
        mock_context.execute_query.assert_called_once()
