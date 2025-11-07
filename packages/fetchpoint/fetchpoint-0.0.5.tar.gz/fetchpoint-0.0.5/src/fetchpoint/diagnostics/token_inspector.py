"""
Token inspection utilities for MSAL JWT tokens.

This module provides functionality to decode, inspect, and analyze JWT tokens
used for SharePoint authentication via MSAL.
"""

import base64
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TokenClaims(BaseModel):
    """Structured representation of JWT token claims."""

    iss: str | None = Field(None, description="Issuer (Azure AD tenant)")
    aud: str | None = Field(None, description="Audience (SharePoint resource)")
    app_id: str | None = Field(None, alias="appid", description="Application ID")
    tenant_id: str | None = Field(None, alias="tid", description="Tenant ID")
    roles: list[str] = Field(default_factory=list, description="Application roles")
    scp: str | None = Field(None, description="Scopes (delegated permissions)")
    iat: int | None = Field(None, description="Issued at (unix timestamp)")
    exp: int | None = Field(None, description="Expiration (unix timestamp)")
    nbf: int | None = Field(None, description="Not before (unix timestamp)")
    ver: str | None = Field(None, description="Token version")
    uti: str | None = Field(None, description="Unique token identifier")

    class Config:
        populate_by_name = True


class TokenInspectionResult(BaseModel):
    """Result of token inspection including decoded claims and analysis."""

    raw_token: str = Field(description="Original JWT token string")
    header: dict[str, Any] = Field(description="JWT header (algorithm, type)")
    claims: TokenClaims = Field(description="Structured claims from JWT payload")
    raw_claims: dict[str, Any] = Field(description="Complete raw JWT payload")
    is_expired: bool = Field(description="Whether token has expired")
    is_valid_time: bool = Field(description="Whether current time is within token validity period")
    expires_in_seconds: int | None = Field(None, description="Seconds until expiration (negative if expired)")
    issued_ago_seconds: int | None = Field(None, description="Seconds since token was issued")


class TokenInspector:
    """Utility for inspecting and analyzing JWT tokens."""

    @staticmethod
    def decode_jwt_part(part: str) -> dict[str, Any]:
        """
        Decode a base64-encoded JWT part (header or payload).

        Args:
            part: Base64-encoded string (URL-safe, no padding)

        Returns:
            Decoded JSON as dictionary

        Raises:
            ValueError: If decoding fails
        """
        # Add padding if needed (JWT uses base64url without padding)
        padding = 4 - (len(part) % 4)
        if padding != 4:
            part += "=" * padding

        try:
            decoded_bytes = base64.urlsafe_b64decode(part)
            return json.loads(decoded_bytes.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to decode JWT part: {e}") from e

    @staticmethod
    def parse_token(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Parse a JWT token into header and payload.

        Args:
            token: JWT token string (format: header.payload.signature)

        Returns:
            Tuple of (header_dict, payload_dict)

        Raises:
            ValueError: If token format is invalid
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid JWT format: expected 3 parts, got {len(parts)}")

        header = TokenInspector.decode_jwt_part(parts[0])
        payload = TokenInspector.decode_jwt_part(parts[1])

        return header, payload

    @staticmethod
    def inspect_token(token: str) -> TokenInspectionResult:
        """
        Perform comprehensive inspection of a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenInspectionResult with decoded claims and analysis

        Raises:
            ValueError: If token format is invalid or cannot be decoded
        """
        header, payload = TokenInspector.parse_token(token)

        # Parse structured claims
        claims = TokenClaims.model_validate(payload)

        # Time-based analysis
        now = datetime.now(timezone.utc)
        now_ts = int(now.timestamp())

        is_expired = False
        is_valid_time = True
        expires_in_seconds = None
        issued_ago_seconds = None

        if claims.exp is not None:
            is_expired = now_ts >= claims.exp
            expires_in_seconds = claims.exp - now_ts

        if claims.nbf is not None:
            is_valid_time = now_ts >= claims.nbf
            if claims.exp is not None:
                is_valid_time = is_valid_time and now_ts < claims.exp

        if claims.iat is not None:
            issued_ago_seconds = now_ts - claims.iat

        return TokenInspectionResult(
            raw_token=token,
            header=header,
            claims=claims,
            raw_claims=payload,
            is_expired=is_expired,
            is_valid_time=is_valid_time,
            expires_in_seconds=expires_in_seconds,
            issued_ago_seconds=issued_ago_seconds,
        )

    @staticmethod
    def format_timestamp(timestamp: int | None) -> str:
        """
        Format a Unix timestamp to human-readable string.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            Formatted datetime string (UTC) or "N/A" if None
        """
        if timestamp is None:
            return "N/A"

        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    @staticmethod
    def format_duration(seconds: int | None) -> str:
        """
        Format a duration in seconds to human-readable string.

        Args:
            seconds: Duration in seconds (can be negative)

        Returns:
            Formatted duration string (e.g., "2h 15m", "-30m")
        """
        if seconds is None:
            return "N/A"

        is_negative = seconds < 0
        abs_seconds = abs(seconds)

        hours = abs_seconds // 3600
        minutes = (abs_seconds % 3600) // 60
        secs = abs_seconds % 60

        parts: list[str] = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        result = " ".join(parts)
        return f"-{result}" if is_negative else result
