"""
FetchPoint - A modern SharePoint client library for Python.

Provides secure, read-only access to SharePoint document libraries with federated
authentication support and comprehensive error handling.
"""

from . import diagnostics
from .auth_factory import create_sharepoint_context
from .authenticator import create_authenticated_context
from .client import SharePointClient
from .config import (
    create_config_from_dict,
    create_msal_config_from_dict,
    create_sharepoint_config,
    create_sharepoint_msal_config,
    # Deprecated - for backward compatibility only
    load_sharepoint_config,
)
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    FederatedAuthError,
    FileDownloadError,
    FileNotFoundError,
    FileSizeLimitError,
    InvalidFileTypeError,
    LibraryNotFoundError,
    PermissionError,
    SharePointError,
)
from .models import AuthMethod, ColumnMapping, ExcelData, FileInfo, FileType, SharePointAuthConfig, SharePointMSALConfig
from .msal_authenticator import build_msal_token_callback, create_msal_authenticated_context

__all__ = [
    # Main API
    "SharePointClient",
    "SharePointAuthConfig",
    "create_sharepoint_config",
    "create_config_from_dict",
    # MSAL Authentication (new)
    "SharePointMSALConfig",
    "AuthMethod",
    "create_sharepoint_msal_config",
    "create_msal_config_from_dict",
    "create_msal_authenticated_context",
    "build_msal_token_callback",
    "create_sharepoint_context",  # Factory function for both auth methods
    # File operations
    "FileInfo",
    "FileType",
    # Excel operations
    "ExcelData",
    "ColumnMapping",
    # Authentication (legacy)
    "create_authenticated_context",
    "load_sharepoint_config",  # Deprecated - for backward compatibility only
    # Diagnostics
    "diagnostics",
    # Exceptions
    "SharePointError",
    "AuthenticationError",
    "FederatedAuthError",
    "FileNotFoundError",
    "FileDownloadError",
    "FileSizeLimitError",
    "ConfigurationError",
    "ConnectionError",
    "PermissionError",
    "LibraryNotFoundError",
    "InvalidFileTypeError",
]

__version__ = "0.1.1"
