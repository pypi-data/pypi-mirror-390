"""
Diagnostics utilities for SharePoint MSAL authentication.

This module provides comprehensive diagnostic tools for troubleshooting
SharePoint authentication via MSAL, including:

- Token inspection and JWT analysis
- Permission analysis from token claims
- MSAL token cache inspection
- SharePoint API endpoint testing
- Error classification and remediation
- Network connectivity validation

Example usage:
    from fetchpoint.diagnostics import TokenInspector, PermissionAnalyzer

    # Inspect a JWT token
    result = TokenInspector.inspect_token(access_token)
    print(f"Token expires in: {result.expires_in_seconds} seconds")

    # Analyze permissions
    analysis = PermissionAnalyzer.analyze_permissions(result.claims)
    print(f"Has read access: {analysis.has_read_access}")
"""

from .api_tester import APITester, APITestSuite, EndpointTestResult, EndpointType
from .cache_inspector import CachedToken, CacheInspectionResult, CacheInspector
from .error_classifier import ErrorCategory, ErrorClassification, ErrorClassifier, ErrorSeverity
from .network_validator import (
    ConnectivityCheckResult,
    DNSCheckResult,
    NetworkValidationResult,
    NetworkValidator,
    SSLCheckResult,
)
from .permission_analyzer import (
    PermissionAnalysis,
    PermissionAnalyzer,
    PermissionLevel,
    PermissionType,
    SharePointPermission,
)
from .token_inspector import TokenClaims, TokenInspectionResult, TokenInspector

__all__ = [
    # Token inspection
    "TokenInspector",
    "TokenInspectionResult",
    "TokenClaims",
    # Permission analysis
    "PermissionAnalyzer",
    "PermissionAnalysis",
    "PermissionType",
    "PermissionLevel",
    "SharePointPermission",
    # Cache inspection
    "CacheInspector",
    "CacheInspectionResult",
    "CachedToken",
    # API testing
    "APITester",
    "APITestSuite",
    "EndpointTestResult",
    "EndpointType",
    # Error classification
    "ErrorClassifier",
    "ErrorClassification",
    "ErrorCategory",
    "ErrorSeverity",
    # Network validation
    "NetworkValidator",
    "NetworkValidationResult",
    "DNSCheckResult",
    "SSLCheckResult",
    "ConnectivityCheckResult",
]
