"""
MSAL authentication provider for SharePoint Online.

This module implements modern authentication using Microsoft Authentication Library (MSAL)
with client credentials flow for app-only access to SharePoint Online.
"""

import logging
from typing import TYPE_CHECKING, Callable
from urllib.parse import urlparse

if TYPE_CHECKING:
    from office365.runtime.auth.token_response import TokenResponse  # type: ignore[import-untyped]
    from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
else:
    # Import at runtime to avoid missing stub file errors
    try:
        from office365.runtime.auth.token_response import TokenResponse  # type: ignore[import-untyped]
        from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "office365-rest-python-client is required. Install with: pip install office365-rest-python-client>=2.6.2"
        ) from e

try:
    import msal  # type: ignore[import-untyped]
except ImportError as e:
    raise ImportError("msal is required for MSAL authentication. Install with: pip install msal>=1.33.0") from e

from .exceptions import AuthenticationError, FederatedAuthError
from .models import SharePointMSALConfig

# Configure logger for this module
logger = logging.getLogger(__name__)


def create_msal_authenticated_context(config: SharePointMSALConfig) -> ClientContext:
    """
    Create an authenticated SharePoint client context using MSAL.

    This function handles the complete MSAL authentication flow for app-only access
    to SharePoint Online using Azure AD client credentials.

    Args:
        config: SharePoint MSAL authentication configuration

    Returns:
        ClientContext: Authenticated SharePoint client context

    Raises:
        AuthenticationError: For authentication failures
        FederatedAuthError: For Azure AD specific issues
    """
    logger.info("Starting MSAL authentication for tenant: %s", _mask_tenant_id(config.tenant_id))

    try:
        # Create SharePoint client context with MSAL token callback
        context = _create_msal_client_context(config)

        # Validate the connection by loading web properties
        _validate_connection(context)

        logger.info("MSAL authentication successful for tenant: %s", _mask_tenant_id(config.tenant_id))
        return context

    except Exception as e:
        # Map specific errors to custom exceptions
        raise _map_msal_authentication_error(e, config.tenant_id, config.sharepoint_url)


def build_msal_token_callback(config: SharePointMSALConfig) -> Callable[[], TokenResponse]:
    """
    Build a token acquisition callback for MSAL authentication.

    Creates a callback function that acquires tokens using the client credentials flow.
    This callback can be used with office365-rest-python-client's with_access_token method.

    Args:
        config: SharePoint MSAL authentication configuration

    Returns:
        Callable that returns TokenResponse when invoked

    Example:
        token_callback = build_msal_token_callback(config)
        context = ClientContext(site_url).with_access_token(token_callback)
    """
    parsed = urlparse(config.sharepoint_url)
    resource = f"{parsed.scheme}://{parsed.netloc}"
    authority = f"https://login.microsoftonline.com/{config.tenant_id}"

    app = msal.ConfidentialClientApplication(
        client_id=config.client_id, authority=authority, client_credential=config.client_secret.get_secret_value()
    )

    def acquire_token() -> TokenResponse:
        scopes = [f"{resource}/.default"]
        logger.debug("Acquiring token for scopes: %s", scopes)

        result = app.acquire_token_for_client(scopes=scopes)  # type: ignore[reportUnknownMemberType]
        if not result or "access_token" not in result:
            error_msg = (
                str(result.get("error_description", result.get("error", "Unknown error")))  # type: ignore[reportUnknownMemberType]
                if result
                else "No result returned"
            )
            logger.error("Token acquisition failed: %s", str(error_msg))
            raise RuntimeError(f"Token acquisition failed: {error_msg}")

        logger.debug("Token acquired successfully")
        return TokenResponse.from_json(result)  # type: ignore[reportUnknownMemberType]

    return acquire_token


def _create_msal_client_context(config: SharePointMSALConfig) -> ClientContext:
    """
    Create SharePoint client context with MSAL authentication.

    Args:
        config: SharePoint MSAL authentication configuration

    Returns:
        ClientContext: SharePoint client context with MSAL authentication
    """
    logger.debug("Creating SharePoint client context with MSAL for URL: %s", config.sharepoint_url)

    # Create client context with the SharePoint site URL
    context = ClientContext(config.sharepoint_url)

    # Build and apply MSAL token callback
    token_callback = build_msal_token_callback(config)
    context = context.with_access_token(token_callback)

    return context


def _validate_connection(context: ClientContext) -> None:
    """
    Validate the MSAL authentication by loading web properties.

    Args:
        context: SharePoint client context to validate

    Raises:
        Exception: If connection validation fails
    """
    logger.debug("Validating MSAL connection by loading web properties")

    # Load web properties to test authentication
    web = context.web
    context.load(web)
    context.execute_query()

    logger.debug("MSAL connection validation successful")


def _mask_tenant_id(tenant_id: str) -> str:
    """
    Mask tenant ID for secure logging.

    Shows only the first 8 characters of the tenant ID for security.

    Args:
        tenant_id: Tenant ID to mask

    Returns:
        Masked tenant ID for logging
    """
    if len(tenant_id) <= 8:
        return "***"
    return tenant_id[:8] + "***"


def _map_msal_authentication_error(error: Exception, tenant_id: str, site_url: str) -> Exception:
    """
    Map MSAL authentication errors to appropriate custom exceptions.

    Args:
        error: Original exception from MSAL authentication
        tenant_id: Azure AD tenant ID
        site_url: SharePoint site URL

    Returns:
        Exception: Mapped custom exception
    """
    error_str = str(error).lower()

    # Handle Azure AD specific errors
    if "aadsts" in error_str:
        return _create_msal_specific_error(error_str, tenant_id, site_url)

    # Handle permission/authorization errors
    if "403" in error_str or "forbidden" in error_str:
        return _create_msal_permission_error(tenant_id, site_url)

    # Handle general authentication errors
    if "401" in error_str or "unauthorized" in error_str:
        return _create_msal_general_auth_error(error_str, tenant_id, site_url)

    # Handle network/connection errors
    if "timeout" in error_str or "connection" in error_str:
        return _create_msal_connection_error(error_str, site_url)

    # Default to general authentication error
    return AuthenticationError(f"MSAL authentication failed: {error}", tenant_id=tenant_id, site_url=site_url)


def _create_msal_specific_error(error_str: str, tenant_id: str, site_url: str) -> FederatedAuthError:
    """Create Azure AD specific MSAL error."""
    if "aadsts700016" in error_str:
        message = "Invalid client ID. Verify the Azure AD application (client) ID is correct."
    elif "aadsts7000215" in error_str:
        message = "Invalid client secret. Verify the client secret is correct and not expired."
    elif "aadsts500011" in error_str:
        message = (
            "Invalid resource/scope. Ensure the scope uses the correct SharePoint host (*.sharepoint.com/.default)."
        )
    elif "aadsts50034" in error_str:
        message = "User account does not exist in the target tenant. Verify the tenant ID and user account."
    else:
        message = f"Azure AD authentication failed. Error: {error_str}"

    return FederatedAuthError(message, tenant_id=tenant_id, site_url=site_url, auth_provider="Azure AD (MSAL)")


def _create_msal_permission_error(tenant_id: str, site_url: str) -> AuthenticationError:
    """Create MSAL permission-specific error."""
    return AuthenticationError(
        "Access denied. The application may not have appropriate SharePoint permissions. "
        "Verify API permissions (Sites.Read.All/Sites.ReadWrite.All or Sites.Selected) and admin consent.",
        tenant_id=tenant_id,
        site_url=site_url,
    )


def _create_msal_general_auth_error(error_str: str, tenant_id: str, site_url: str) -> AuthenticationError:
    """Create general MSAL authentication error."""
    return AuthenticationError(
        f"MSAL authentication failed. Please verify your Azure AD configuration. Details: {error_str}",
        tenant_id=tenant_id,
        site_url=site_url,
    )


def _create_msal_connection_error(error_str: str, site_url: str) -> AuthenticationError:
    """Create MSAL connection-specific error."""
    return AuthenticationError(
        f"Connection failed during MSAL authentication. Please check network connectivity. Details: {error_str}",
        site_url=site_url,
    )
