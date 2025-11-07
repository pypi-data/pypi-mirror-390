"""
Network connectivity validation utilities.

This module provides functionality to validate network connectivity, DNS resolution,
and SSL certificates for Azure AD and SharePoint endpoints.
"""

import socket
import ssl
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, Field


class DNSCheckResult(BaseModel):
    """Result of DNS resolution check."""

    hostname: str = Field(description="Hostname checked")
    resolved: bool = Field(description="Whether DNS resolution succeeded")
    ip_addresses: list[str] = Field(default_factory=list, description="Resolved IP addresses")
    error_message: str | None = Field(None, description="Error message if failed")


class SSLCheckResult(BaseModel):
    """Result of SSL certificate check."""

    hostname: str = Field(description="Hostname checked")
    port: int = Field(443, description="Port number")
    valid: bool = Field(description="Whether SSL certificate is valid")
    certificate_info: dict[str, Any] | None = Field(None, description="Certificate details")
    expires_at: str | None = Field(None, description="Certificate expiration date")
    expires_in_days: int | None = Field(None, description="Days until expiration")
    error_message: str | None = Field(None, description="Error message if failed")
    warnings: list[str] = Field(default_factory=list, description="SSL warnings")


class ConnectivityCheckResult(BaseModel):
    """Result of connectivity check to a service."""

    url: str = Field(description="URL checked")
    reachable: bool = Field(description="Whether service is reachable")
    response_time_ms: float | None = Field(None, description="Response time in milliseconds")
    status_code: int | None = Field(None, description="HTTP status code")
    error_message: str | None = Field(None, description="Error message if failed")


class NetworkValidationResult(BaseModel):
    """Comprehensive network validation result."""

    dns_checks: list[DNSCheckResult] = Field(description="DNS resolution checks")
    ssl_checks: list[SSLCheckResult] = Field(description="SSL certificate checks")
    connectivity_checks: list[ConnectivityCheckResult] = Field(description="Connectivity checks")
    overall_healthy: bool = Field(description="Whether all checks passed")
    warnings: list[str] = Field(default_factory=list, description="Network warnings")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class NetworkValidator:
    """Utility for validating network connectivity and configuration."""

    # Key Azure and SharePoint endpoints to check
    AZURE_ENDPOINTS = ["login.microsoftonline.com", "graph.microsoft.com"]

    @staticmethod
    def check_dns(hostname: str) -> DNSCheckResult:
        """
        Check DNS resolution for a hostname.

        Args:
            hostname: Hostname to resolve

        Returns:
            DNSCheckResult with resolution details
        """
        try:
            ip_addresses = socket.gethostbyname_ex(hostname)[2]
            return DNSCheckResult(hostname=hostname, resolved=True, ip_addresses=ip_addresses, error_message=None)
        except socket.gaierror as e:
            return DNSCheckResult(
                hostname=hostname, resolved=False, ip_addresses=[], error_message=f"DNS resolution failed: {e}"
            )
        except Exception as e:
            return DNSCheckResult(
                hostname=hostname, resolved=False, ip_addresses=[], error_message=f"Unexpected error: {e}"
            )

    @staticmethod
    def check_ssl(hostname: str, port: int = 443) -> SSLCheckResult:
        """
        Check SSL certificate for a hostname.

        Args:
            hostname: Hostname to check
            port: Port number (default: 443)

        Returns:
            SSLCheckResult with certificate details
        """
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    if not cert:
                        return SSLCheckResult(
                            hostname=hostname,
                            port=port,
                            valid=False,
                            certificate_info=None,
                            expires_at=None,
                            expires_in_days=None,
                            error_message="No certificate information available",
                            warnings=["Could not retrieve certificate information"],
                        )

                    # Extract certificate info
                    cert_info: dict[str, Any] = {
                        "subject": str(cert.get("subject", "")),
                        "issuer": str(cert.get("issuer", "")),
                        "version": cert.get("version"),
                        "serialNumber": cert.get("serialNumber"),
                    }

                    # Check expiration
                    not_after = cert.get("notAfter")
                    expires_at: str | None = None
                    expires_in_days: int | None = None
                    warnings: list[str] = []

                    if not_after and isinstance(not_after, str):
                        expires_at_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(
                            tzinfo=timezone.utc
                        )
                        expires_at = expires_at_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                        expires_in_days = (expires_at_dt - datetime.now(timezone.utc)).days

                        if expires_in_days < 0:
                            warnings.append("Certificate has expired")
                        elif expires_in_days < 30:
                            warnings.append(f"Certificate expires soon ({expires_in_days} days)")

                    return SSLCheckResult(
                        hostname=hostname,
                        port=port,
                        valid=len(warnings) == 0 or warnings[0] != "Certificate has expired",
                        certificate_info=cert_info,
                        expires_at=expires_at,
                        expires_in_days=expires_in_days,
                        error_message=None,
                        warnings=warnings,
                    )

        except ssl.SSLError as e:
            return SSLCheckResult(
                hostname=hostname,
                port=port,
                valid=False,
                certificate_info=None,
                expires_at=None,
                expires_in_days=None,
                error_message=f"SSL error: {e}",
                warnings=["Invalid or untrusted SSL certificate"],
            )
        except socket.timeout:
            return SSLCheckResult(
                hostname=hostname,
                port=port,
                valid=False,
                certificate_info=None,
                expires_at=None,
                expires_in_days=None,
                error_message="Connection timeout",
            )
        except Exception as e:
            return SSLCheckResult(
                hostname=hostname,
                port=port,
                valid=False,
                certificate_info=None,
                expires_at=None,
                expires_in_days=None,
                error_message=f"Unexpected error: {e}",
            )

    @staticmethod
    def check_connectivity(url: str, timeout: int = 10) -> ConnectivityCheckResult:
        """
        Check HTTP/HTTPS connectivity to a URL.

        Args:
            url: URL to check
            timeout: Request timeout in seconds

        Returns:
            ConnectivityCheckResult with connectivity details
        """
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            end_time = time.time()

            response_time_ms = (end_time - start_time) * 1000

            return ConnectivityCheckResult(
                url=url,
                reachable=True,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                error_message=None,
            )

        except requests.exceptions.Timeout:
            return ConnectivityCheckResult(
                url=url,
                reachable=False,
                response_time_ms=None,
                status_code=None,
                error_message=f"Connection timeout after {timeout} seconds",
            )
        except requests.exceptions.ConnectionError as e:
            return ConnectivityCheckResult(
                url=url,
                reachable=False,
                response_time_ms=None,
                status_code=None,
                error_message=f"Connection error: {str(e)[:200]}",
            )
        except Exception as e:
            return ConnectivityCheckResult(
                url=url,
                reachable=False,
                response_time_ms=None,
                status_code=None,
                error_message=f"Unexpected error: {str(e)[:200]}",
            )

    @staticmethod
    def validate_sharepoint_connectivity(site_url: str) -> NetworkValidationResult:
        """
        Perform comprehensive network validation for SharePoint connectivity.

        Args:
            site_url: SharePoint site URL to validate

        Returns:
            NetworkValidationResult with all validation results
        """
        dns_checks: list[DNSCheckResult] = []
        ssl_checks: list[SSLCheckResult] = []
        connectivity_checks: list[ConnectivityCheckResult] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        # Extract hostname from SharePoint URL
        parsed_url = urlparse(site_url)
        sharepoint_host = parsed_url.hostname

        if not sharepoint_host:
            return NetworkValidationResult(
                dns_checks=dns_checks,
                ssl_checks=ssl_checks,
                connectivity_checks=connectivity_checks,
                overall_healthy=False,
                warnings=["Invalid SharePoint URL"],
                recommendations=["Provide a valid SharePoint URL (e.g., https://company.sharepoint.com/sites/site)"],
            )

        # 1. DNS Checks
        # Check SharePoint hostname
        sp_dns: DNSCheckResult = NetworkValidator.check_dns(sharepoint_host)
        dns_checks.append(sp_dns)

        if not sp_dns.resolved:
            warnings.append(f"Cannot resolve SharePoint hostname: {sharepoint_host}")
            recommendations.append("Check DNS configuration and network connectivity")

        # Check Azure endpoints
        for endpoint in NetworkValidator.AZURE_ENDPOINTS:
            result = NetworkValidator.check_dns(endpoint)
            dns_checks.append(result)
            if not result.resolved:
                warnings.append(f"Cannot resolve Azure endpoint: {endpoint}")
                recommendations.append("Check network connectivity to Azure services")

        # 2. SSL Checks
        # Check SharePoint SSL
        sp_ssl: SSLCheckResult = NetworkValidator.check_ssl(sharepoint_host)
        ssl_checks.append(sp_ssl)

        if not sp_ssl.valid:
            warnings.append(f"SSL certificate issue for {sharepoint_host}")
            recommendations.append("Verify SSL certificate is valid and trusted")

        if sp_ssl.warnings:
            warnings.extend([f"{sharepoint_host}: {w}" for w in sp_ssl.warnings])

        # Check Azure endpoints SSL
        for endpoint in NetworkValidator.AZURE_ENDPOINTS:
            result = NetworkValidator.check_ssl(endpoint)
            ssl_checks.append(result)
            if not result.valid:
                warnings.append(f"SSL certificate issue for {endpoint}")

        # 3. Connectivity Checks
        # Check SharePoint site
        sp_connectivity: ConnectivityCheckResult = NetworkValidator.check_connectivity(site_url)
        connectivity_checks.append(sp_connectivity)

        if not sp_connectivity.reachable:
            warnings.append(f"Cannot reach SharePoint site: {site_url}")
            recommendations.append("Check firewall settings and network connectivity")
        elif sp_connectivity.status_code and sp_connectivity.status_code >= 400:
            warnings.append(f"SharePoint site returned HTTP {sp_connectivity.status_code}")

        # Check Azure AD login endpoint
        azure_ad_url = "https://login.microsoftonline.com"
        azure_connectivity: ConnectivityCheckResult = NetworkValidator.check_connectivity(azure_ad_url)
        connectivity_checks.append(azure_connectivity)

        if not azure_connectivity.reachable:
            warnings.append("Cannot reach Azure AD login endpoint")
            recommendations.append("Check connectivity to login.microsoftonline.com")

        # Determine overall health
        overall_healthy = (
            all(c.resolved for c in dns_checks)
            and all(c.valid for c in ssl_checks)
            and all(c.reachable for c in connectivity_checks)
        )

        # Add success recommendation
        if overall_healthy:
            recommendations.append("All network checks passed - connectivity is healthy")

        return NetworkValidationResult(
            dns_checks=dns_checks,
            ssl_checks=ssl_checks,
            connectivity_checks=connectivity_checks,
            overall_healthy=overall_healthy,
            warnings=warnings,
            recommendations=recommendations,
        )

    @staticmethod
    def format_network_validation(result: NetworkValidationResult) -> str:
        """
        Format network validation result as human-readable string.

        Args:
            result: Network validation result

        Returns:
            Formatted multi-line string
        """
        lines = [
            "Network Validation Results",
            f"Overall Health: {'✓ HEALTHY' if result.overall_healthy else '✗ ISSUES DETECTED'}",
            "",
        ]

        # DNS Checks
        lines.append(f"DNS Resolution Checks ({len(result.dns_checks)}):")
        for check in result.dns_checks:
            status = "✓" if check.resolved else "✗"
            ips = ", ".join(check.ip_addresses) if check.ip_addresses else "N/A"
            lines.append(f"  {status} {check.hostname:40} → {ips}")
            if check.error_message:
                lines.append(f"     Error: {check.error_message}")

        # SSL Checks
        lines.append(f"\nSSL Certificate Checks ({len(result.ssl_checks)}):")
        for check in result.ssl_checks:
            status = "✓" if check.valid else "✗"
            expiry = f"Expires: {check.expires_at} ({check.expires_in_days} days)" if check.expires_at else "N/A"
            lines.append(f"  {status} {check.hostname:40} {expiry}")
            if check.error_message:
                lines.append(f"     Error: {check.error_message}")
            for warning in check.warnings:
                lines.append(f"     ⚠ {warning}")

        # Connectivity Checks
        lines.append(f"\nConnectivity Checks ({len(result.connectivity_checks)}):")
        for check in result.connectivity_checks:
            status = "✓" if check.reachable else "✗"
            time_text = f"({check.response_time_ms:.0f}ms)" if check.response_time_ms else ""
            status_text = f"[{check.status_code}]" if check.status_code else ""
            lines.append(f"  {status} {check.url:50} {status_text} {time_text}")
            if check.error_message:
                lines.append(f"     Error: {check.error_message}")

        # Warnings
        if result.warnings:
            lines.append("\n⚠ Warnings:")
            for warning in result.warnings:
                lines.append(f"  - {warning}")

        # Recommendations
        if result.recommendations:
            lines.append("\nRecommendations:")
            for rec in result.recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)
