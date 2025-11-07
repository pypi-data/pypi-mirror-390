"""
SharePoint API endpoint testing utilities.

This module provides functionality to test various SharePoint REST API endpoints
for connectivity, authentication, and permission validation.
"""

import time
from enum import Enum
from typing import Any

import requests
from pydantic import BaseModel, Field


class EndpointType(str, Enum):
    """Type of SharePoint API endpoint."""

    WEB = "web"
    SITE = "site"
    LISTS = "lists"
    SEARCH = "search"
    USER_PROFILE = "userprofile"
    CONTEXTINFO = "contextinfo"


class EndpointTestResult(BaseModel):
    """Result of testing a single API endpoint."""

    endpoint_type: EndpointType = Field(description="Type of endpoint tested")
    url: str = Field(description="Full URL that was tested")
    method: str = Field(description="HTTP method used")
    status_code: int | None = Field(None, description="HTTP status code returned")
    success: bool = Field(description="Whether the test succeeded")
    response_time_ms: float | None = Field(None, description="Response time in milliseconds")
    error_message: str | None = Field(None, description="Error message if failed")
    response_data: dict[str, Any] | None = Field(None, description="Response data if successful")
    permission_issue: bool = Field(False, description="Whether failure is due to permissions")


class APITestSuite(BaseModel):
    """Results of testing multiple API endpoints."""

    site_url: str = Field(description="SharePoint site URL tested")
    total_tests: int = Field(description="Total number of tests performed")
    passed_tests: int = Field(description="Number of tests that passed")
    failed_tests: int = Field(description="Number of tests that failed")
    test_results: list[EndpointTestResult] = Field(description="Individual test results")
    overall_success: bool = Field(description="Whether all critical tests passed")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations based on results")


class APITester:
    """Utility for testing SharePoint API endpoints."""

    # Standard SharePoint REST API endpoints
    ENDPOINTS: dict[EndpointType, dict[str, str]] = {
        EndpointType.WEB: {"path": "_api/web", "description": "Web properties"},
        EndpointType.SITE: {"path": "_api/site", "description": "Site collection properties"},
        EndpointType.LISTS: {"path": "_api/web/lists", "description": "Lists in the web"},
        EndpointType.CONTEXTINFO: {"path": "_api/contextinfo", "description": "Context information"},
    }

    @staticmethod
    def test_endpoint(site_url: str, endpoint_type: EndpointType, token: str, timeout: int = 30) -> EndpointTestResult:
        """
        Test a specific SharePoint API endpoint.

        Args:
            site_url: SharePoint site URL (e.g., https://company.sharepoint.com/sites/site)
            endpoint_type: Type of endpoint to test
            token: Access token for authentication
            timeout: Request timeout in seconds

        Returns:
            EndpointTestResult with test outcome
        """
        endpoint_info = APITester.ENDPOINTS.get(endpoint_type)
        if not endpoint_info:
            return EndpointTestResult(
                endpoint_type=endpoint_type,
                url="",
                method="GET",
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Unknown endpoint type: {endpoint_type}",
                response_data=None,
                permission_issue=False,
            )

        # Construct URL
        base_url = site_url.rstrip("/")
        endpoint_path = endpoint_info["path"]
        url = f"{base_url}/{endpoint_path}"

        # Prepare headers
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;odata=minimalmetadata"}

        # Determine HTTP method
        method = "POST" if endpoint_type == EndpointType.CONTEXTINFO else "GET"

        try:
            start_time = time.time()

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            else:
                response = requests.post(url, headers=headers, timeout=timeout)

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Check if successful
            success = response.status_code in (200, 201)

            # Parse response data
            response_data = None
            if success and response.content:
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"raw": response.text[:500]}

            # Check for permission issues
            permission_issue = response.status_code in (401, 403)

            error_message = None
            if not success:
                error_message = f"HTTP {response.status_code}: {response.reason}"
                if permission_issue:
                    error_message += " (Authentication or Permission error)"

            return EndpointTestResult(
                endpoint_type=endpoint_type,
                url=url,
                method=method,
                status_code=response.status_code,
                success=success,
                response_time_ms=response_time_ms,
                error_message=error_message,
                response_data=response_data,
                permission_issue=permission_issue,
            )

        except requests.exceptions.Timeout:
            return EndpointTestResult(
                endpoint_type=endpoint_type,
                url=url,
                method=method,
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Request timeout after {timeout} seconds",
                response_data=None,
                permission_issue=False,
            )
        except requests.exceptions.ConnectionError as e:
            return EndpointTestResult(
                endpoint_type=endpoint_type,
                url=url,
                method=method,
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Connection error: {str(e)[:200]}",
                response_data=None,
                permission_issue=False,
            )
        except Exception as e:
            return EndpointTestResult(
                endpoint_type=endpoint_type,
                url=url,
                method=method,
                status_code=None,
                success=False,
                response_time_ms=None,
                error_message=f"Unexpected error: {str(e)[:200]}",
                response_data=None,
                permission_issue=False,
            )

    @staticmethod
    def run_test_suite(site_url: str, token: str, timeout: int = 30) -> APITestSuite:
        """
        Run a comprehensive test suite against SharePoint API endpoints.

        Args:
            site_url: SharePoint site URL
            token: Access token for authentication
            timeout: Request timeout in seconds

        Returns:
            APITestSuite with all test results
        """
        test_results: list[EndpointTestResult] = []

        # Test each endpoint
        for endpoint_type in [EndpointType.WEB, EndpointType.SITE, EndpointType.LISTS, EndpointType.CONTEXTINFO]:
            result = APITester.test_endpoint(site_url, endpoint_type, token, timeout)
            test_results.append(result)

        # Calculate statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.success)
        failed_tests = total_tests - passed_tests

        # Critical endpoints that must pass
        critical_endpoints = {EndpointType.WEB, EndpointType.SITE}
        critical_passed = all(r.success for r in test_results if r.endpoint_type in critical_endpoints)
        overall_success = critical_passed

        # Generate recommendations
        recommendations: list[str] = []

        # Check for permission issues
        permission_failures: list[EndpointTestResult] = [r for r in test_results if r.permission_issue]
        if permission_failures:
            endpoints = ", ".join(r.endpoint_type.value for r in permission_failures)
            recommendations.append(
                f"Permission issues detected on endpoints: {endpoints}. "
                "Check that your app has the necessary SharePoint permissions."
            )

        # Check for connectivity issues
        connection_failures: list[EndpointTestResult] = [
            r for r in test_results if not r.success and not r.permission_issue and r.status_code is None
        ]
        if connection_failures:
            recommendations.append(
                "Network connectivity issues detected. "
                "Check firewall settings, DNS resolution, and network connectivity to SharePoint."
            )

        # Check if lists endpoint failed
        lists_result: EndpointTestResult | None = next(
            (r for r in test_results if r.endpoint_type == EndpointType.LISTS), None
        )
        if lists_result and not lists_result.success:
            if lists_result.permission_issue:
                recommendations.append(
                    "Cannot access lists. This may indicate insufficient read permissions "
                    "or that the app needs Sites.Read.All or higher."
                )

        # Check if all tests passed
        if overall_success and passed_tests == total_tests:
            recommendations.append("All API endpoint tests passed successfully!")

        return APITestSuite(
            site_url=site_url,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            test_results=test_results,
            overall_success=overall_success,
            recommendations=recommendations,
        )

    @staticmethod
    def format_test_results(suite: APITestSuite) -> str:
        """
        Format API test suite results as human-readable string.

        Args:
            suite: API test suite results

        Returns:
            Formatted multi-line string
        """
        lines = [
            "SharePoint API Test Suite",
            f"Site: {suite.site_url}",
            f"Total Tests: {suite.total_tests}",
            f"Passed: {suite.passed_tests} | Failed: {suite.failed_tests}",
            f"Overall: {'✓ PASS' if suite.overall_success else '✗ FAIL'}",
            "",
            "Endpoint Test Results:",
        ]

        for result in suite.test_results:
            status_icon = "✓" if result.success else "✗"
            status_text = f"[{result.status_code}]" if result.status_code else "[ERROR]"
            time_text = f" ({result.response_time_ms:.0f}ms)" if result.response_time_ms else ""

            lines.append(f"  {status_icon} {result.endpoint_type.value:15} {status_text}{time_text}")

            if result.error_message:
                lines.append(f"     Error: {result.error_message}")

        if suite.recommendations:
            lines.append("")
            lines.append("Recommendations:")
            for rec in suite.recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)
