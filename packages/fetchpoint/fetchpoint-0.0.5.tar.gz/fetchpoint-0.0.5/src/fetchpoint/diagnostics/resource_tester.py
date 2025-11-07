"""
SharePoint resource access testing utilities.

This module provides functionality to test access to specific SharePoint resources
such as document libraries, folders, and files for permission validation.
"""

import time
from enum import Enum
from urllib.parse import quote, urlparse

import requests
from pydantic import BaseModel, Field

from .permission_analyzer import PermissionLevel, SharePointPermission


class ResourceType(str, Enum):
    """Type of SharePoint resource."""

    FOLDER = "folder"
    FILE = "file"
    LIBRARY = "library"
    LIST = "list"


class ResourceTestResult(BaseModel):
    """Result of testing a single SharePoint resource."""

    resource_type: ResourceType = Field(description="Type of resource tested")
    resource_url: str = Field(description="Full SharePoint URL of the resource")
    server_relative_url: str = Field(description="Server-relative URL used for API call")
    status_code: int | None = Field(None, description="HTTP status code returned")
    success: bool = Field(description="Whether the test succeeded")
    response_time_ms: float | None = Field(None, description="Response time in milliseconds")
    error_message: str | None = Field(None, description="Error message if failed")
    permission_issue: bool = Field(False, description="Whether failure is due to permissions")
    required_permission_level: PermissionLevel = Field(
        PermissionLevel.READ, description="Permission level required for this resource"
    )
    missing_azure_permissions: list[str] = Field(
        default_factory=list, description="Azure AD permissions that may be missing"
    )


class ResourceTestSuite(BaseModel):
    """Results of testing multiple SharePoint resources."""

    site_url: str = Field(description="SharePoint site URL")
    total_tests: int = Field(description="Total number of resources tested")
    passed_tests: int = Field(description="Number of tests that passed")
    failed_tests: int = Field(description="Number of tests that failed")
    test_results: list[ResourceTestResult] = Field(description="Individual test results")
    overall_success: bool = Field(description="Whether all tests passed")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations based on results")


class ResourceTester:
    """Utility for testing SharePoint resource access."""

    @staticmethod
    def _extract_server_relative_url(full_url: str, site_url: str) -> str:
        """
        Extract server-relative URL from a full SharePoint URL.

        Args:
            full_url: Full SharePoint URL (e.g., https://tenant.sharepoint.com/sites/site/path/to/folder)
            site_url: Site URL (e.g., https://tenant.sharepoint.com/sites/site)

        Returns:
            Server-relative URL (e.g., /sites/site/path/to/folder)
        """
        parsed_full = urlparse(full_url)
        parsed_site = urlparse(site_url)

        # Get the path portion after the site
        full_path = parsed_full.path
        site_path = parsed_site.path

        if full_path.startswith(site_path):
            # Already have the full path including site
            return full_path
        else:
            # Need to prepend site path
            return f"{site_path.rstrip('/')}/{full_path.lstrip('/')}"

    @staticmethod
    def _infer_resource_type(server_relative_url: str) -> ResourceType:
        """
        Infer the resource type from the URL.

        Args:
            server_relative_url: Server-relative URL

        Returns:
            ResourceType enum
        """
        # Simple heuristic: if it has an extension, it's likely a file
        if "." in server_relative_url.split("/")[-1]:
            return ResourceType.FILE

        # Common library names
        library_names = ["documents", "documenti", "shared documents", "site assets"]
        path_lower = server_relative_url.lower()
        if any(lib in path_lower for lib in library_names):
            return ResourceType.LIBRARY

        # Default to folder
        return ResourceType.FOLDER

    @staticmethod
    def _analyze_permission_failure(
        status_code: int, resource_type: ResourceType, response_text: str = ""
    ) -> tuple[PermissionLevel, list[str]]:
        """
        Analyze a permission failure and determine missing permissions.

        Args:
            status_code: HTTP status code
            resource_type: Type of resource
            response_text: Response text (may contain error details)

        Returns:
            Tuple of (required_permission_level, missing_azure_permissions)
        """
        # For read operations (GET), we need at minimum read access
        required_level = PermissionLevel.READ

        missing_permissions: list[str] = []

        if status_code == 401:
            # Authentication failure - could be token expiry or invalid token
            missing_permissions.extend(
                [SharePointPermission.SITES_READ_ALL.value, "or " + SharePointPermission.ALLSITES_READ.value]
            )
        elif status_code == 403:
            # Authorization failure - user is authenticated but lacks permission
            if resource_type in (ResourceType.FOLDER, ResourceType.LIBRARY):
                missing_permissions.extend(
                    [
                        SharePointPermission.SITES_READ_ALL.value,
                        "or " + SharePointPermission.SITES_SELECTED.value + " (with site-specific permissions)",
                    ]
                )
            elif resource_type == ResourceType.FILE:
                missing_permissions.extend(
                    [
                        SharePointPermission.SITES_READ_ALL.value,
                        "or " + SharePointPermission.SITES_SELECTED.value + " (with site-specific permissions)",
                        "or Files.Read.All",
                    ]
                )

        return required_level, missing_permissions

    @staticmethod
    def test_resource(
        resource_url: str, site_url: str, token: str, resource_type: ResourceType | None = None, timeout: int = 30
    ) -> ResourceTestResult:
        """
        Test access to a specific SharePoint resource.

        Args:
            resource_url: Full URL of the resource to test
            site_url: SharePoint site URL
            token: Access token for authentication
            resource_type: Type of resource (auto-detected if None)
            timeout: Request timeout in seconds

        Returns:
            ResourceTestResult with test outcome
        """
        # Extract server-relative URL
        server_relative_url = ResourceTester._extract_server_relative_url(resource_url, site_url)

        # Infer resource type if not provided
        if resource_type is None:
            resource_type = ResourceTester._infer_resource_type(server_relative_url)

        # Build API endpoint based on resource type
        base_url = site_url.rstrip("/")

        # URL-encode the server-relative URL to handle special characters (spaces, apostrophes, etc.)
        encoded_url = quote(server_relative_url, safe="/")

        if resource_type in (ResourceType.FOLDER, ResourceType.LIBRARY):
            # Use GetFolderByServerRelativeUrl for folders/libraries
            api_path = f"_api/web/GetFolderByServerRelativeUrl('{encoded_url}')"
        elif resource_type == ResourceType.FILE:
            # Use GetFileByServerRelativeUrl for files
            api_path = f"_api/web/GetFileByServerRelativeUrl('{encoded_url}')"
        else:
            # Default to folder
            api_path = f"_api/web/GetFolderByServerRelativeUrl('{encoded_url}')"

        api_url = f"{base_url}/{api_path}"

        # Prepare headers
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;odata=minimalmetadata"}

        try:
            start_time = time.time()
            response = requests.get(api_url, headers=headers, timeout=timeout)
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Check if successful
            success = response.status_code in (200, 201)

            # Check for permission issues
            permission_issue = response.status_code in (401, 403)

            error_message = None
            missing_azure_permissions: list[str] = []
            required_level = PermissionLevel.READ

            if not success:
                error_message = f"HTTP {response.status_code}: {response.reason}"
                if permission_issue:
                    error_message += " (Access Denied)"
                    required_level, missing_azure_permissions = ResourceTester._analyze_permission_failure(
                        response.status_code, resource_type, response.text
                    )

            return ResourceTestResult(
                resource_type=resource_type,
                resource_url=resource_url,
                server_relative_url=server_relative_url,
                status_code=response.status_code,
                success=success,
                response_time_ms=response_time_ms,
                error_message=error_message,
                permission_issue=permission_issue,
                required_permission_level=required_level,
                missing_azure_permissions=missing_azure_permissions,
            )

        except requests.exceptions.Timeout:
            return ResourceTestResult(
                resource_type=resource_type,
                resource_url=resource_url,
                server_relative_url=server_relative_url,
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Request timeout after {timeout} seconds",
                permission_issue=False,
                required_permission_level=PermissionLevel.READ,
                missing_azure_permissions=[],
            )
        except requests.exceptions.ConnectionError as e:
            return ResourceTestResult(
                resource_type=resource_type,
                resource_url=resource_url,
                server_relative_url=server_relative_url,
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Connection error: {str(e)[:200]}",
                permission_issue=False,
                required_permission_level=PermissionLevel.READ,
                missing_azure_permissions=[],
            )
        except Exception as e:
            return ResourceTestResult(
                resource_type=resource_type,
                resource_url=resource_url,
                server_relative_url=server_relative_url,
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Unexpected error: {str(e)[:200]}",
                permission_issue=False,
                required_permission_level=PermissionLevel.READ,
                missing_azure_permissions=[],
            )

    @staticmethod
    def run_test_suite(resource_urls: list[str], site_url: str, token: str, timeout: int = 30) -> ResourceTestSuite:
        """
        Run a comprehensive test suite for multiple SharePoint resources.

        Args:
            resource_urls: List of full resource URLs to test
            site_url: SharePoint site URL
            token: Access token for authentication
            timeout: Request timeout in seconds

        Returns:
            ResourceTestSuite with all test results
        """
        test_results: list[ResourceTestResult] = []

        # Test each resource
        for resource_url in resource_urls:
            result = ResourceTester.test_resource(resource_url, site_url, token, timeout=timeout)
            test_results.append(result)

        # Calculate statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.success)
        failed_tests = total_tests - passed_tests
        overall_success = failed_tests == 0

        # Generate recommendations
        recommendations: list[str] = []

        # Check for permission failures
        permission_failures = [r for r in test_results if r.permission_issue]
        if permission_failures:
            for failure in permission_failures:
                resource_name = failure.server_relative_url.split("/")[-1] or failure.server_relative_url
                recommendations.append(
                    f"❌ ERROR: Access denied to '{resource_name}' - "
                    f"Azure AD missing: {', '.join(failure.missing_azure_permissions)}"
                )

        # Check for connection failures
        connection_failures = [
            r for r in test_results if not r.success and not r.permission_issue and r.status_code is None
        ]
        if connection_failures:
            recommendations.append(
                "Network connectivity issues detected. Check firewall, DNS, and network connectivity to SharePoint."
            )

        # Success message
        if overall_success:
            recommendations.append("✓ All resource access tests passed successfully!")

        return ResourceTestSuite(
            site_url=site_url,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            test_results=test_results,
            overall_success=overall_success,
            recommendations=recommendations,
        )

    @staticmethod
    def format_test_results(suite: ResourceTestSuite) -> str:
        """
        Format resource test suite results as human-readable string.

        Args:
            suite: Resource test suite results

        Returns:
            Formatted multi-line string
        """
        lines = [
            "SharePoint Resource Access Test Suite",
            f"Site: {suite.site_url}",
            f"Total Tests: {suite.total_tests}",
            f"Passed: {suite.passed_tests} | Failed: {suite.failed_tests}",
            f"Overall: {'✓ PASS' if suite.overall_success else '✗ FAIL'}",
            "",
            "Resource Test Results:",
        ]

        for result in suite.test_results:
            status_icon = "✓" if result.success else "✗"
            status_text = f"[{result.status_code}]" if result.status_code else "[ERROR]"
            time_text = f" ({result.response_time_ms:.0f}ms)" if result.response_time_ms else ""
            resource_name = result.server_relative_url.split("/")[-1] or result.server_relative_url

            lines.append(f"  {status_icon} {resource_name:30} {status_text}{time_text}")

            if result.error_message:
                lines.append(f"     Error: {result.error_message}")
                lines.append(f"     URL: {result.resource_url}")

            if result.missing_azure_permissions:
                lines.append(f"     Azure AD Missing: {', '.join(result.missing_azure_permissions)}")

        if suite.recommendations:
            lines.append("")
            lines.append("Recommendations:")
            for rec in suite.recommendations:
                lines.append(f"  {rec}")

        return "\n".join(lines)
