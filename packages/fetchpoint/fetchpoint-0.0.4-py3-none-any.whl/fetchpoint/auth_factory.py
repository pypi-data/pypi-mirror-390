"""
Authentication factory for SharePoint connections.

This module provides a factory pattern for creating authenticated SharePoint contexts
using different authentication methods (legacy UserCredential or modern MSAL).
"""

import logging
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
else:
    # Import at runtime to avoid missing stub file errors
    try:
        from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "office365-rest-python-client is required. Install with: uv add 'office365-rest-python-client>=2.6.0'"
        ) from e

from .authenticator import create_authenticated_context
from .exceptions import ConfigurationError
from .models import AuthMethod, SharePointAuthConfig, SharePointMSALConfig
from .msal_authenticator import create_msal_authenticated_context

# Configure logger for this module
logger = logging.getLogger(__name__)


def create_sharepoint_context(
    config: Union[SharePointAuthConfig, SharePointMSALConfig], auth_method: Union[AuthMethod, str, None] = None
) -> ClientContext:
    """
    Create an authenticated SharePoint client context using the specified authentication method.

    This factory function automatically selects the appropriate authentication provider
    based on the configuration type and optional auth_method parameter.

    Args:
        config: SharePoint authentication configuration (legacy or MSAL)
        auth_method: Authentication method to use (optional, auto-detected from config type)

    Returns:
        ClientContext: Authenticated SharePoint client context

    Raises:
        ConfigurationError: If configuration type doesn't match auth_method
        AuthenticationError: If authentication fails

    Examples:
        # Legacy authentication
        legacy_config = SharePointAuthConfig(...)
        context = create_sharepoint_context(legacy_config)

        # MSAL authentication
        msal_config = SharePointMSALConfig(...)
        context = create_sharepoint_context(msal_config)

        # Explicit auth method specification
        context = create_sharepoint_context(config, AuthMethod.MSAL)
    """
    # Determine authentication method
    detected_method = _detect_auth_method(config, auth_method)

    logger.info("Creating SharePoint context using %s authentication", detected_method.value)

    # Route to appropriate authentication provider
    if detected_method == AuthMethod.LEGACY:
        if not isinstance(config, SharePointAuthConfig):
            raise ConfigurationError(
                f"Legacy authentication requires SharePointAuthConfig, got {type(config).__name__}"
            )
        return create_authenticated_context(config)

    elif detected_method == AuthMethod.MSAL:
        if not isinstance(config, SharePointMSALConfig):
            raise ConfigurationError(f"MSAL authentication requires SharePointMSALConfig, got {type(config).__name__}")
        return create_msal_authenticated_context(config)

    else:
        raise ConfigurationError(f"Unsupported authentication method: {detected_method}")


def _detect_auth_method(
    config: Union[SharePointAuthConfig, SharePointMSALConfig], auth_method: Union[AuthMethod, str, None]
) -> AuthMethod:
    """
    Detect the authentication method based on configuration and explicit method.

    Args:
        config: SharePoint authentication configuration
        auth_method: Explicitly specified authentication method (optional)

    Returns:
        AuthMethod: Detected authentication method

    Raises:
        ConfigurationError: If method detection fails or conflicts occur
    """
    # Convert string to enum if needed
    if isinstance(auth_method, str):
        try:
            auth_method = AuthMethod(auth_method.lower())
        except ValueError:
            raise ConfigurationError(f"Invalid authentication method: {auth_method}")

    # Auto-detect from configuration type if method not specified
    if auth_method is None:
        if isinstance(config, SharePointAuthConfig):
            return AuthMethod.LEGACY
        elif isinstance(config, SharePointMSALConfig):  # type: ignore[reportUnnecessaryIsInstance]
            return AuthMethod.MSAL
        else:
            raise ConfigurationError(f"Cannot auto-detect authentication method for {type(config).__name__}")

    # Validate explicit method matches configuration type
    if auth_method == AuthMethod.LEGACY and not isinstance(config, SharePointAuthConfig):
        raise ConfigurationError("Legacy authentication method requires SharePointAuthConfig")

    if auth_method == AuthMethod.MSAL and not isinstance(config, SharePointMSALConfig):
        raise ConfigurationError("MSAL authentication method requires SharePointMSALConfig")

    return auth_method
