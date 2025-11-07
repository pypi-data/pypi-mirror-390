"""
MSAL authentication provider for SharePoint Online.

This module implements modern authentication using Microsoft Authentication Library (MSAL)
with client credentials flow for app-only access to SharePoint Online.
"""

import logging
import re
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


def _extract_url_from_error(error_str: str) -> str | None:
    """
    Extract URL from error string.

    Looks for patterns like 'for url: https://...' or 'url: https://...'
    in error messages.

    Args:
        error_str: Error string that may contain a URL

    Returns:
        Extracted URL or None if not found
    """
    # Try to find URL patterns in the error string
    patterns = [
        r"for url:\s*(https?://[^\s'\"]+)",  # 'for url: https://...'
        r"url:\s*(https?://[^\s'\"]+)",  # 'url: https://...'
        r"(https?://[^\s'\"]+/_api/[^\s'\"]+)",  # Direct SharePoint API URLs
    ]

    for pattern in patterns:
        match = re.search(pattern, error_str, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _extract_status_code(error_str: str) -> str | None:
    """
    Extract HTTP status code from error string.

    Args:
        error_str: Error string that may contain a status code

    Returns:
        Status code string (e.g., "401", "403") or None if not found
    """
    # Look for HTTP status codes
    patterns = [
        r"(\d{3})\s+(?:client\s+)?error",  # '401 client error'
        r"status\s+(?:code\s+)?(\d{3})",  # 'status code 401'
        r"http\s+(\d{3})",  # 'HTTP 401'
    ]

    for pattern in patterns:
        match = re.search(pattern, error_str, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _map_msal_authentication_error(error: Exception, tenant_id: str, site_url: str) -> Exception:
    """
    Map MSAL authentication errors to appropriate custom exceptions.

    Distinguishes between:
    - Token acquisition failures (MSAL/Azure AD issues)
    - SharePoint authorization failures (token rejected by SharePoint)

    Args:
        error: Original exception from MSAL authentication
        tenant_id: Azure AD tenant ID
        site_url: SharePoint site URL

    Returns:
        Exception: Mapped custom exception
    """
    error_str = str(error).lower()
    error_str_orig = str(error)  # Preserve original case for URL extraction

    # Handle Azure AD specific errors (true MSAL authentication failures)
    if "aadsts" in error_str:
        return _create_msal_specific_error(error_str, tenant_id, site_url)

    # Distinguish between authorization (SharePoint rejects token) and authentication (can't get token)
    # If error contains SharePoint API URL, it means token was acquired but SharePoint rejected it
    sharepoint_api_indicators = ["_api/", "sharepoint.com"]
    is_sharepoint_authorization_error = any(indicator in error_str for indicator in sharepoint_api_indicators)

    # Handle 401/403 errors
    if "403" in error_str or "forbidden" in error_str:
        if is_sharepoint_authorization_error:
            # SharePoint rejected the token (authorization failure)
            return _create_sharepoint_authorization_error(error_str_orig, tenant_id, site_url)
        else:
            # Generic permission error
            return _create_msal_permission_error(tenant_id, site_url)

    if "401" in error_str or "unauthorized" in error_str:
        if is_sharepoint_authorization_error:
            # SharePoint rejected the token (authorization failure)
            return _create_sharepoint_authorization_error(error_str_orig, tenant_id, site_url)
        else:
            # Token acquisition failure (authentication failure)
            return _create_msal_general_auth_error(error_str_orig, tenant_id, site_url)

    # Handle network/connection errors
    if "timeout" in error_str or "connection" in error_str:
        return _create_msal_connection_error(error_str_orig, site_url)

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


def _create_sharepoint_authorization_error(error_str: str, tenant_id: str, site_url: str) -> AuthenticationError:
    """
    Create SharePoint authorization error with clear URL and status display.

    This error occurs when token acquisition succeeded but SharePoint rejected the token.
    """
    # Extract URL and status code from error
    url = _extract_url_from_error(error_str)
    status_code = _extract_status_code(error_str)

    # Build error message with clear structure
    message_parts = ["SharePoint Authorization Failed"]

    if status_code:
        if status_code == "401":
            message_parts.append(f"({status_code} Unauthorized)")
        elif status_code == "403":
            message_parts.append(f"({status_code} Forbidden)")
        else:
            message_parts.append(f"(HTTP {status_code})")

    message = " ".join(message_parts) + "\n"

    # Show the resource URL prominently
    if url:
        message += f"\nResource: {url}"
    else:
        message += f"\nSite: {site_url}"

    if status_code:
        message += f"\nStatus: {status_code}"

    # Explain what happened
    message += "\n\nWhat happened:"
    message += "\n  ✅ Token acquired successfully from Azure AD"
    message += "\n  ❌ SharePoint rejected the token when accessing the resource"

    # Provide likely causes based on status code
    message += "\n\nLikely causes:"
    if status_code == "401":
        message += "\n  • Sites.Selected permission requires explicit site configuration in Azure AD"
        message += "\n  • Admin consent may still be propagating (wait 5-10 minutes)"
        message += "\n  • App not granted access to this specific SharePoint site"
        message += "\n  • Token audience mismatch (check SharePoint URL)"
    elif status_code == "403":
        message += "\n  • Insufficient permissions for this operation"
        message += "\n  • App has read access but attempting write operation"
        message += "\n  • Site-specific permissions not configured"
    else:
        message += "\n  • Verify app permissions in Azure AD"
        message += "\n  • Check admin consent status"
        message += "\n  • Ensure app has access to this SharePoint site"

    # Include debug details
    message += f"\n\nDebug details: {error_str}"

    return AuthenticationError(message, tenant_id=tenant_id, site_url=site_url)


def _create_msal_general_auth_error(error_str: str, tenant_id: str, site_url: str) -> AuthenticationError:
    """Create general MSAL authentication error (for actual token acquisition failures)."""
    return AuthenticationError(
        f"MSAL token acquisition failed. Please verify your Azure AD configuration.\n\nDetails: {error_str}",
        tenant_id=tenant_id,
        site_url=site_url,
    )


def _create_msal_connection_error(error_str: str, site_url: str) -> AuthenticationError:
    """Create MSAL connection-specific error."""
    url = _extract_url_from_error(error_str) or site_url
    return AuthenticationError(
        f"Connection failed during MSAL authentication.\n\nTarget: {url}\n\nPlease check network connectivity.\n\nDetails: {error_str}",  # noqa: E501
        site_url=site_url,
    )
