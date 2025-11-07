"""
Error classification and analysis utilities for Azure AD and SharePoint errors.

This module provides functionality to classify and analyze errors from Azure AD
authentication and SharePoint API calls, providing root cause analysis and
remediation steps.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """Category of error."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    RESOURCE = "resource"
    THROTTLING = "throttling"
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    """Severity level of error."""

    CRITICAL = "critical"  # Service unavailable or major configuration issue
    HIGH = "high"  # Permission or authentication failure
    MEDIUM = "medium"  # Resource not found or temporary issue
    LOW = "low"  # Warning or informational
    INFO = "info"  # Informational only


class ErrorClassification(BaseModel):
    """Classification result for an error."""

    error_code: str | None = Field(None, description="Error code (AADSTS, HTTP status, etc.)")
    category: ErrorCategory = Field(description="Error category")
    severity: ErrorSeverity = Field(description="Error severity")
    title: str = Field(description="Short error title")
    description: str = Field(description="Detailed error description")
    root_cause: str = Field(description="Likely root cause")
    remediation: list[str] = Field(description="Steps to remediate the error")
    documentation_url: str | None = Field(None, description="Link to documentation")


class ErrorClassifier:
    """Utility for classifying and analyzing errors."""

    # Azure AD error code mappings
    AADSTS_ERRORS: dict[str, dict[str, Any]] = {
        "50034": {
            "category": ErrorCategory.CONFIGURATION,
            "severity": ErrorSeverity.HIGH,
            "title": "User Account Not Found",
            "description": "The user account does not exist in the directory",
            "root_cause": "The username/email provided does not exist in Azure AD tenant",
            "remediation": [
                "Verify the username/email is correct",
                "Check that the user exists in Azure AD",
                "Ensure you're using the correct tenant",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts50034",
        },
        "50126": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Invalid Username or Password",
            "description": "Error validating credentials due to invalid username or password",
            "root_cause": "Incorrect password provided for the user account",
            "remediation": [
                "Verify the password is correct",
                "Check for password expiration",
                "Try resetting the password",
                "Check if account is locked or disabled",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts50126",
        },
        "50053": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Account Locked",
            "description": "The account is locked due to too many failed sign-in attempts",
            "root_cause": "Account has been locked due to security policy after multiple failed attempts",
            "remediation": [
                "Wait for the lockout period to expire (usually 30 minutes)",
                "Contact administrator to unlock the account",
                "Review security policies and failed sign-in logs",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts50053",
        },
        "700016": {
            "category": ErrorCategory.CONFIGURATION,
            "severity": ErrorSeverity.CRITICAL,
            "title": "Application Not Found",
            "description": "Application with identifier (client ID) was not found in the directory",
            "root_cause": "The client ID is incorrect or the app registration doesn't exist",
            "remediation": [
                "Verify the AZURE_CLIENT_ID is correct",
                "Check that the app registration exists in Azure AD",
                "Ensure you're using the correct tenant",
                "Verify the app hasn't been deleted",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts700016",
        },
        "50055": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Password Expired",
            "description": "The password is expired",
            "root_cause": "User's password has expired and must be changed",
            "remediation": [
                "User must change their password",
                "Reset the password through Azure AD",
                "Contact administrator for password reset",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts50055",
        },
        "50076": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "MFA Required",
            "description": "Strong authentication required due to Conditional Access policy",
            "root_cause": "Multi-factor authentication is required but not provided",
            "remediation": [
                "Complete MFA challenge when prompted",
                "Ensure MFA is configured for the user account",
                "Check Conditional Access policies requiring MFA",
                "For service principals, use certificate-based authentication or managed identity",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts50076",
        },
        "50079": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "MFA Enrollment Required",
            "description": "MFA enrollment required; user must register security info",
            "root_cause": "User has not enrolled in multi-factor authentication",
            "remediation": [
                "User must enroll in MFA through Azure AD",
                "Visit https://aka.ms/mfasetup to register security info",
                "Contact administrator to configure MFA enrollment",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts50079",
        },
        "7000215": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Invalid Client Secret",
            "description": "Invalid client secret provided",
            "root_cause": "The client secret is incorrect",
            "remediation": [
                "Verify the AZURE_CLIENT_SECRET is correct",
                "Check for typos or copy-paste errors",
                "Regenerate the client secret in Azure AD if needed",
                "Update the environment variable with the correct secret",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts7000215",
        },
        "7000222": {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Client Secret Expired",
            "description": "The provided client secret keys are expired",
            "root_cause": "The client secret has expired (secrets expire after 1-2 years by default)",
            "remediation": [
                "Generate a new client secret in Azure AD",
                "Update the AZURE_CLIENT_SECRET environment variable",
                "Set up a process to rotate secrets before expiration",
                "Consider using certificate-based authentication for longer validity",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts7000222",
        },
        "65001": {
            "category": ErrorCategory.AUTHORIZATION,
            "severity": ErrorSeverity.HIGH,
            "title": "User or Admin Consent Required",
            "description": "The user or administrator has not consented to use the application",
            "root_cause": "Application requires admin consent for requested permissions",
            "remediation": [
                "Have an administrator grant admin consent for the application",
                "Visit the Azure AD portal and grant permissions",
                "Use the admin consent URL: https://login.microsoftonline.com/{tenant}/adminconsent?client_id={client_id}",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts65001",
        },
        "65004": {
            "category": ErrorCategory.AUTHORIZATION,
            "severity": ErrorSeverity.HIGH,
            "title": "User Declined Consent",
            "description": "User declined to consent to access the app",
            "root_cause": "User refused to grant permissions to the application",
            "remediation": [
                "User needs to accept the consent prompt",
                "Administrator can grant consent on behalf of users",
                "Review the permissions requested and adjust if too broad",
            ],
            "doc_url": "https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes#aadsts65004",
        },
    }

    # HTTP status code mappings
    HTTP_ERRORS: dict[int, dict[str, Any]] = {
        401: {
            "category": ErrorCategory.AUTHENTICATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Unauthorized",
            "description": "Authentication failed or token is invalid",
            "root_cause": "Token is missing, expired, or invalid for the requested resource",
            "remediation": [
                "Check that the token is valid and not expired",
                "Verify the token has the correct audience (SharePoint URL)",
                "Ensure the token was acquired for the correct resource",
                "Try acquiring a new token",
            ],
        },
        403: {
            "category": ErrorCategory.AUTHORIZATION,
            "severity": ErrorSeverity.HIGH,
            "title": "Forbidden",
            "description": "Authenticated but not authorized to access the resource",
            "root_cause": "Token is valid but lacks necessary permissions for the operation",
            "remediation": [
                "Check that the app has the required SharePoint permissions",
                "Verify admin consent has been granted",
                "For Sites.Selected, ensure specific site permissions are configured",
                "Review the permissions in the token claims",
            ],
        },
        404: {
            "category": ErrorCategory.RESOURCE,
            "severity": ErrorSeverity.MEDIUM,
            "title": "Not Found",
            "description": "The requested resource does not exist",
            "root_cause": "URL is incorrect or resource has been deleted/moved",
            "remediation": [
                "Verify the SharePoint site URL is correct",
                "Check that the site/list/item exists",
                "Ensure the resource hasn't been deleted or moved",
                "Verify URL spelling and path",
            ],
        },
        429: {
            "category": ErrorCategory.THROTTLING,
            "severity": ErrorSeverity.MEDIUM,
            "title": "Too Many Requests",
            "description": "Request rate limit exceeded",
            "root_cause": "Too many requests sent to SharePoint API in a short time",
            "remediation": [
                "Implement exponential backoff retry logic",
                "Reduce the request rate",
                "Check the Retry-After header for wait time",
                "Consider batching requests",
            ],
        },
        500: {
            "category": ErrorCategory.RESOURCE,
            "severity": ErrorSeverity.CRITICAL,
            "title": "Internal Server Error",
            "description": "Server encountered an error processing the request",
            "root_cause": "SharePoint service error or temporary service issue",
            "remediation": [
                "Retry the request after a short delay",
                "Check SharePoint service health status",
                "Review request payload for malformed data",
                "Contact Microsoft support if persistent",
            ],
        },
        503: {
            "category": ErrorCategory.RESOURCE,
            "severity": ErrorSeverity.CRITICAL,
            "title": "Service Unavailable",
            "description": "Service is temporarily unavailable",
            "root_cause": "SharePoint service is down or undergoing maintenance",
            "remediation": [
                "Wait and retry after a few minutes",
                "Check Microsoft 365 service health dashboard",
                "Implement retry logic with exponential backoff",
            ],
        },
    }

    @staticmethod
    def classify_aadsts_error(error_code: str) -> ErrorClassification:
        """
        Classify an Azure AD error code (AADSTS).

        Args:
            error_code: AADSTS error code (e.g., "50034", "AADSTS50034")

        Returns:
            ErrorClassification with analysis
        """
        # Remove "AADSTS" prefix if present
        clean_code = error_code.replace("AADSTS", "").replace("aadsts", "")

        error_info = ErrorClassifier.AADSTS_ERRORS.get(clean_code)

        if error_info:
            return ErrorClassification(
                error_code=f"AADSTS{clean_code}",
                category=error_info["category"],
                severity=error_info["severity"],
                title=error_info["title"],
                description=error_info["description"],
                root_cause=error_info["root_cause"],
                remediation=error_info["remediation"],
                documentation_url=error_info.get("doc_url"),
            )

        # Unknown AADSTS error
        return ErrorClassification(
            error_code=f"AADSTS{clean_code}",
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            title="Unknown Azure AD Error",
            description=f"Azure AD returned error code AADSTS{clean_code}",
            root_cause="Unknown or undocumented Azure AD error",
            remediation=[
                f"Search for AADSTS{clean_code} in Microsoft documentation",
                "Check Azure AD sign-in logs for more details",
                "Review application configuration in Azure portal",
            ],
            documentation_url="https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes",
        )

    @staticmethod
    def classify_http_error(status_code: int, response_body: str | None = None) -> ErrorClassification:
        """
        Classify an HTTP status code error.

        Args:
            status_code: HTTP status code
            response_body: Optional response body for additional context

        Returns:
            ErrorClassification with analysis
        """
        error_info = ErrorClassifier.HTTP_ERRORS.get(status_code)

        if error_info:
            return ErrorClassification(
                error_code=f"HTTP {status_code}",
                category=error_info["category"],
                severity=error_info["severity"],
                title=error_info["title"],
                description=error_info["description"],
                root_cause=error_info["root_cause"],
                remediation=error_info["remediation"],
                documentation_url=None,
            )

        # Unknown HTTP error
        category = ErrorCategory.UNKNOWN
        severity = ErrorSeverity.MEDIUM

        if 400 <= status_code < 500:
            category = ErrorCategory.AUTHENTICATION if status_code == 401 else ErrorCategory.AUTHORIZATION
            severity = ErrorSeverity.HIGH
        elif 500 <= status_code < 600:
            category = ErrorCategory.RESOURCE
            severity = ErrorSeverity.CRITICAL

        return ErrorClassification(
            error_code=f"HTTP {status_code}",
            category=category,
            severity=severity,
            title=f"HTTP {status_code} Error",
            description=f"Server returned HTTP status code {status_code}",
            root_cause="Unknown HTTP error",
            remediation=[
                "Check the HTTP response body for more details",
                f"Search for HTTP {status_code} error documentation",
                "Review request headers and authentication",
            ],
            documentation_url=None,
        )

    @staticmethod
    def classify_exception(exception: Exception) -> ErrorClassification:
        """
        Classify a Python exception.

        Args:
            exception: Python exception

        Returns:
            ErrorClassification with analysis
        """
        exc_type = type(exception).__name__
        exc_message = str(exception)

        # Check for connection errors
        if "connection" in exc_message.lower() or exc_type in ["ConnectionError", "ConnectTimeout"]:
            return ErrorClassification(
                error_code=exc_type,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                title="Network Connection Error",
                description=f"Failed to establish connection: {exc_message[:200]}",
                root_cause="Network connectivity issue or service unavailable",
                remediation=[
                    "Check network connectivity",
                    "Verify DNS resolution",
                    "Check firewall settings",
                    "Verify the SharePoint URL is correct",
                    "Test connectivity using ping or curl",
                ],
                documentation_url=None,
            )

        # Check for timeout errors
        if "timeout" in exc_message.lower() or exc_type in ["Timeout", "ReadTimeout"]:
            return ErrorClassification(
                error_code=exc_type,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                title="Request Timeout",
                description=f"Request timed out: {exc_message[:200]}",
                root_cause="Request took too long or service is slow",
                remediation=[
                    "Increase timeout value",
                    "Check network latency",
                    "Verify service health",
                    "Try during off-peak hours",
                ],
                documentation_url=None,
            )

        # Generic exception
        return ErrorClassification(
            error_code=exc_type,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            title=f"{exc_type}",
            description=exc_message[:500],
            root_cause="Unexpected error occurred",
            remediation=[
                "Check the full error message and stack trace",
                "Review application logs",
                "Verify input parameters are correct",
            ],
            documentation_url=None,
        )

    @staticmethod
    def format_error_classification(classification: ErrorClassification) -> str:
        """
        Format error classification as human-readable string.

        Args:
            classification: Error classification result

        Returns:
            Formatted multi-line string
        """
        severity_icon = {
            ErrorSeverity.CRITICAL: "🔴",
            ErrorSeverity.HIGH: "🟠",
            ErrorSeverity.MEDIUM: "🟡",
            ErrorSeverity.LOW: "🟢",
            ErrorSeverity.INFO: "ℹ️",
        }

        lines = [
            f"{severity_icon.get(classification.severity, '')} {classification.title}",
            f"Error Code: {classification.error_code or 'N/A'}",
            f"Category: {classification.category.value}",
            f"Severity: {classification.severity.value}",
            "",
            f"Description: {classification.description}",
            "",
            f"Root Cause: {classification.root_cause}",
            "",
            "Remediation Steps:",
        ]

        for i, step in enumerate(classification.remediation, 1):
            lines.append(f"  {i}. {step}")

        if classification.documentation_url:
            lines.append("")
            lines.append(f"Documentation: {classification.documentation_url}")

        return "\n".join(lines)
