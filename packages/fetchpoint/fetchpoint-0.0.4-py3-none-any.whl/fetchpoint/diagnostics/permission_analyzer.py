"""
Permission analysis utilities for SharePoint MSAL tokens.

This module provides functionality to analyze and validate SharePoint permissions
from JWT token claims.
"""

from enum import Enum

from pydantic import BaseModel, Field

from .token_inspector import TokenClaims


class PermissionType(str, Enum):
    """Type of SharePoint permission."""

    APPLICATION = "application"  # App-only permissions (roles)
    DELEGATED = "delegated"  # Delegated permissions (scopes)


class SharePointPermission(str, Enum):
    """Common SharePoint permissions."""

    # Application permissions (roles)
    SITES_READ_ALL = "Sites.Read.All"
    SITES_READWRITE_ALL = "Sites.ReadWrite.All"
    SITES_FULLCONTROL_ALL = "Sites.FullControl.All"
    SITES_SELECTED = "Sites.Selected"
    SITES_MANAGE_ALL = "Sites.Manage.All"

    # Delegated permissions (scopes)
    ALLSITES_READ = "AllSites.Read"
    ALLSITES_WRITE = "AllSites.Write"
    ALLSITES_FULLCONTROL = "AllSites.FullControl"
    ALLSITES_MANAGE = "AllSites.Manage"
    MYFILES_READ = "MyFiles.Read"
    MYFILES_WRITE = "MyFiles.Write"


class PermissionLevel(str, Enum):
    """Permission level for access control."""

    READ = "read"
    WRITE = "write"
    FULLCONTROL = "fullcontrol"
    MANAGE = "manage"
    NONE = "none"


class PermissionAnalysis(BaseModel):
    """Analysis result for token permissions."""

    permission_type: PermissionType = Field(description="Type of permissions (application/delegated)")
    permissions: list[str] = Field(description="List of granted permissions")
    has_read_access: bool = Field(description="Whether token has read access")
    has_write_access: bool = Field(description="Whether token has write access")
    has_fullcontrol: bool = Field(description="Whether token has full control")
    effective_level: PermissionLevel = Field(description="Effective permission level")
    missing_permissions: list[str] = Field(default_factory=list, description="Recommended permissions that are missing")
    warnings: list[str] = Field(default_factory=list, description="Security or configuration warnings")


class PermissionAnalyzer:
    """Utility for analyzing SharePoint permissions from tokens."""

    # Mapping of permissions to their levels
    PERMISSION_LEVELS: dict[str, PermissionLevel] = {
        # Application permissions
        SharePointPermission.SITES_READ_ALL.value: PermissionLevel.READ,
        SharePointPermission.SITES_SELECTED.value: PermissionLevel.READ,
        SharePointPermission.SITES_READWRITE_ALL.value: PermissionLevel.WRITE,
        SharePointPermission.SITES_FULLCONTROL_ALL.value: PermissionLevel.FULLCONTROL,
        SharePointPermission.SITES_MANAGE_ALL.value: PermissionLevel.MANAGE,
        # Delegated permissions
        SharePointPermission.ALLSITES_READ.value: PermissionLevel.READ,
        SharePointPermission.MYFILES_READ.value: PermissionLevel.READ,
        SharePointPermission.ALLSITES_WRITE.value: PermissionLevel.WRITE,
        SharePointPermission.MYFILES_WRITE.value: PermissionLevel.WRITE,
        SharePointPermission.ALLSITES_FULLCONTROL.value: PermissionLevel.FULLCONTROL,
        SharePointPermission.ALLSITES_MANAGE.value: PermissionLevel.MANAGE,
    }

    @staticmethod
    def extract_permissions(claims: TokenClaims) -> tuple[PermissionType, list[str]]:
        """
        Extract permissions from token claims.

        Args:
            claims: Parsed token claims

        Returns:
            Tuple of (permission_type, permissions_list)
        """
        # Check for application permissions (roles)
        if claims.roles:
            return PermissionType.APPLICATION, claims.roles

        # Check for delegated permissions (scopes)
        if claims.scp:
            scopes = [s.strip() for s in claims.scp.split()]
            return PermissionType.DELEGATED, scopes

        # No permissions found
        return PermissionType.APPLICATION, []

    @staticmethod
    def determine_effective_level(permissions: list[str]) -> PermissionLevel:
        """
        Determine the effective permission level from a list of permissions.

        Args:
            permissions: List of permission strings

        Returns:
            Highest effective permission level
        """
        if not permissions:
            return PermissionLevel.NONE

        levels: list[PermissionLevel] = []
        for perm in permissions:
            level = PermissionAnalyzer.PERMISSION_LEVELS.get(perm, PermissionLevel.NONE)
            levels.append(level)

        # Return highest level (order: MANAGE > FULLCONTROL > WRITE > READ > NONE)
        level_priority = {
            PermissionLevel.MANAGE: 4,
            PermissionLevel.FULLCONTROL: 3,
            PermissionLevel.WRITE: 2,
            PermissionLevel.READ: 1,
            PermissionLevel.NONE: 0,
        }

        max_level = max(levels, key=lambda x: level_priority[x])
        return max_level

    @staticmethod
    def analyze_permissions(
        claims: TokenClaims, required_level: PermissionLevel = PermissionLevel.READ
    ) -> PermissionAnalysis:
        """
        Analyze permissions from token claims and validate against requirements.

        Args:
            claims: Parsed token claims
            required_level: Minimum required permission level

        Returns:
            PermissionAnalysis with detailed analysis and recommendations
        """
        perm_type, permissions = PermissionAnalyzer.extract_permissions(claims)
        effective_level = PermissionAnalyzer.determine_effective_level(permissions)

        # Determine access levels
        level_priority = {
            PermissionLevel.MANAGE: 4,
            PermissionLevel.FULLCONTROL: 3,
            PermissionLevel.WRITE: 2,
            PermissionLevel.READ: 1,
            PermissionLevel.NONE: 0,
        }

        effective_priority = level_priority[effective_level]
        has_read = effective_priority >= level_priority[PermissionLevel.READ]
        has_write = effective_priority >= level_priority[PermissionLevel.WRITE]
        has_fullcontrol = effective_priority >= level_priority[PermissionLevel.FULLCONTROL]

        # Check for missing permissions
        missing_permissions = []
        warnings = []

        if not permissions:
            missing_permissions.append(
                SharePointPermission.SITES_READ_ALL.value
                if perm_type == PermissionType.APPLICATION
                else SharePointPermission.ALLSITES_READ.value
            )
            warnings.append("No SharePoint permissions found in token")

        # Check if required level is met
        required_priority = level_priority[required_level]
        if effective_priority < required_priority:
            if perm_type == PermissionType.APPLICATION:
                if required_level == PermissionLevel.WRITE:
                    missing_permissions.append(SharePointPermission.SITES_READWRITE_ALL.value)
                elif required_level == PermissionLevel.FULLCONTROL:
                    missing_permissions.append(SharePointPermission.SITES_FULLCONTROL_ALL.value)
            else:
                if required_level == PermissionLevel.WRITE:
                    missing_permissions.append(SharePointPermission.ALLSITES_WRITE.value)
                elif required_level == PermissionLevel.FULLCONTROL:
                    missing_permissions.append(SharePointPermission.ALLSITES_FULLCONTROL.value)

            warnings.append(f"Token has {effective_level.value} access but {required_level.value} is required")

        # Check for overly broad permissions
        if SharePointPermission.SITES_FULLCONTROL_ALL.value in permissions:
            warnings.append(
                "Token has FullControl.All - consider using more restrictive permissions "
                "(Sites.Read.All or Sites.ReadWrite.All)"
            )

        # Check for Sites.Selected without additional context
        if SharePointPermission.SITES_SELECTED.value in permissions and len(permissions) == 1:
            warnings.append("Token uses Sites.Selected - ensure specific site permissions are configured in Azure AD")

        return PermissionAnalysis(
            permission_type=perm_type,
            permissions=permissions,
            has_read_access=has_read,
            has_write_access=has_write,
            has_fullcontrol=has_fullcontrol,
            effective_level=effective_level,
            missing_permissions=missing_permissions,
            warnings=warnings,
        )

    @staticmethod
    def format_permissions(analysis: PermissionAnalysis) -> str:
        """
        Format permission analysis as human-readable string.

        Args:
            analysis: Permission analysis result

        Returns:
            Formatted multi-line string
        """
        lines = [
            f"Permission Type: {analysis.permission_type.value}",
            f"Effective Level: {analysis.effective_level.value}",
            f"Granted Permissions: {', '.join(analysis.permissions) if analysis.permissions else 'None'}",
            f"Read Access: {'✓' if analysis.has_read_access else '✗'}",
            f"Write Access: {'✓' if analysis.has_write_access else '✗'}",
            f"Full Control: {'✓' if analysis.has_fullcontrol else '✗'}",
        ]

        if analysis.missing_permissions:
            lines.append(f"Missing Permissions: {', '.join(analysis.missing_permissions)}")

        if analysis.warnings:
            lines.append("Warnings:")
            for warning in analysis.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)
