"""
MSAL token cache inspection utilities.

This module provides functionality to inspect MSAL token caches and analyze
cached tokens, expiration times, and refresh status.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from msal import TokenCache  # type: ignore[import-untyped]
from pydantic import BaseModel, Field


class CachedToken(BaseModel):
    """Representation of a cached token."""

    credential_type: str = Field(description="Type of credential (AccessToken, RefreshToken, etc.)")
    client_id: str | None = Field(None, description="Application (client) ID")
    authority: str | None = Field(None, description="Authority URL (Azure AD endpoint)")
    realm: str | None = Field(None, description="Tenant ID")
    target: str | None = Field(None, description="Resource/scope for the token")
    expires_on: int | None = Field(None, description="Expiration timestamp (unix)")
    extended_expires_on: int | None = Field(None, description="Extended expiration timestamp")
    cached_at: int | None = Field(None, description="When token was cached")
    is_expired: bool = Field(description="Whether token has expired")
    expires_in_seconds: int | None = Field(None, description="Seconds until expiration (negative if expired)")
    secret_preview: str | None = Field(None, description="Preview of token value (first/last chars)")


class CacheInspectionResult(BaseModel):
    """Result of cache inspection."""

    cache_exists: bool = Field(description="Whether cache exists")
    cache_path: str | None = Field(None, description="Path to cache file if applicable")
    total_entries: int = Field(description="Total number of cache entries")
    access_tokens: list[CachedToken] = Field(default=[], description="Cached access tokens")
    refresh_tokens: list[CachedToken] = Field(default=[], description="Cached refresh tokens")
    id_tokens: list[CachedToken] = Field(default=[], description="Cached ID tokens")
    accounts: list[dict[str, Any]] = Field(default=[], description="Cached accounts")
    has_valid_token: bool = Field(description="Whether any valid (non-expired) access token exists")
    warnings: list[str] = Field(default=[], description="Cache-related warnings")


class CacheInspector:
    """Utility for inspecting MSAL token caches."""

    @staticmethod
    def create_cached_token(cred_type: str, entry: dict[str, Any]) -> CachedToken:
        """
        Create a CachedToken from a cache entry.

        Args:
            cred_type: Credential type
            entry: Raw cache entry dictionary

        Returns:
            CachedToken model
        """
        now_ts = int(datetime.now(timezone.utc).timestamp())

        expires_on = entry.get("expires_on")
        if expires_on:
            expires_on = int(expires_on) if isinstance(expires_on, (int, float, str)) else None

        is_expired = False
        expires_in_seconds = None
        if expires_on:
            is_expired = now_ts >= expires_on
            expires_in_seconds = expires_on - now_ts

        # Create secret preview (first 8 and last 4 chars)
        secret = entry.get("secret")
        secret_preview = None
        if secret and isinstance(secret, str):
            if len(secret) > 20:
                secret_preview = f"{secret[:8]}...{secret[-4:]}"
            else:
                secret_preview = f"{secret[:4]}...{secret[-2:]}"

        return CachedToken(
            credential_type=cred_type,
            client_id=entry.get("client_id"),
            authority=entry.get("authority") or entry.get("environment"),
            realm=entry.get("realm"),
            target=entry.get("target"),
            expires_on=expires_on,
            extended_expires_on=entry.get("extended_expires_on"),
            cached_at=entry.get("cached_at"),
            is_expired=is_expired,
            expires_in_seconds=expires_in_seconds,
            secret_preview=secret_preview,
        )

    @staticmethod
    def inspect_cache(cache: TokenCache) -> CacheInspectionResult:
        """
        Inspect an MSAL TokenCache and extract information.

        Args:
            cache: MSAL TokenCache instance

        Returns:
            CacheInspectionResult with cache analysis
        """
        # Serialize cache to get raw data
        cache_data_str_raw = cache.serialize()  # type: ignore[no-untyped-call]
        cache_data_str: str | None = cache_data_str_raw if isinstance(cache_data_str_raw, str) else None  # type: ignore[redundant-expr]
        cache_data: dict[str, Any] = json.loads(cache_data_str) if cache_data_str else {}

        access_tokens: list[CachedToken] = []
        refresh_tokens: list[CachedToken] = []
        id_tokens: list[CachedToken] = []
        accounts: list[dict[str, Any]] = []

        # Extract access tokens
        access_token_dict: dict[str, Any] = cache_data.get("AccessToken", {})
        for entry in access_token_dict.values():
            token = CacheInspector.create_cached_token("AccessToken", entry)
            access_tokens.append(token)

        # Extract refresh tokens
        refresh_token_dict: dict[str, Any] = cache_data.get("RefreshToken", {})
        for entry in refresh_token_dict.values():
            token = CacheInspector.create_cached_token("RefreshToken", entry)
            refresh_tokens.append(token)

        # Extract ID tokens
        id_token_dict: dict[str, Any] = cache_data.get("IdToken", {})
        for entry in id_token_dict.values():
            token = CacheInspector.create_cached_token("IdToken", entry)
            id_tokens.append(token)

        # Extract accounts
        account_dict: dict[str, Any] = cache_data.get("Account", {})
        accounts = list(account_dict.values())

        # Check if any valid token exists
        has_valid_token = any(not token.is_expired for token in access_tokens)

        # Generate warnings
        warnings: list[str] = []
        if not access_tokens:
            warnings.append("No access tokens found in cache")
        elif not has_valid_token:
            warnings.append("All cached access tokens have expired")

        if not refresh_tokens:
            warnings.append("No refresh tokens found in cache (cannot refresh access tokens)")

        # Count expired tokens
        expired_count = sum(1 for token in access_tokens if token.is_expired)
        if expired_count > 0 and expired_count < len(access_tokens):
            warnings.append(f"{expired_count} of {len(access_tokens)} access tokens have expired")

        total_entries = len(access_tokens) + len(refresh_tokens) + len(id_tokens) + len(accounts)

        return CacheInspectionResult(
            cache_exists=bool(cache_data),
            cache_path=None,  # In-memory cache doesn't have a path
            total_entries=total_entries,
            access_tokens=access_tokens,
            refresh_tokens=refresh_tokens,
            id_tokens=id_tokens,
            accounts=accounts,
            has_valid_token=has_valid_token,
            warnings=warnings,
        )

    @staticmethod
    def inspect_file_cache(cache_file: Path | str) -> CacheInspectionResult:
        """
        Inspect an MSAL cache file.

        Args:
            cache_file: Path to cache file

        Returns:
            CacheInspectionResult with cache analysis

        Raises:
            FileNotFoundError: If cache file doesn't exist
            ValueError: If cache file is invalid
        """
        cache_path = Path(cache_file)

        if not cache_path.exists():
            return CacheInspectionResult(
                cache_exists=False,
                cache_path=str(cache_path),
                total_entries=0,
                has_valid_token=False,
                warnings=["Cache file does not exist"],
            )

        try:
            # Load cache from file
            cache = TokenCache()  # type: ignore[no-untyped-call]
            with open(cache_path, "r") as f:
                cache_data = f.read()
            cache.deserialize(cache_data)  # type: ignore[no-untyped-call]

            result = CacheInspector.inspect_cache(cache)
            result.cache_path = str(cache_path)
            return result

        except Exception as e:
            return CacheInspectionResult(
                cache_exists=True,
                cache_path=str(cache_path),
                total_entries=0,
                has_valid_token=False,
                warnings=[f"Failed to load cache file: {e}"],
            )

    @staticmethod
    def format_cache_info(result: CacheInspectionResult) -> str:
        """
        Format cache inspection result as human-readable string.

        Args:
            result: Cache inspection result

        Returns:
            Formatted multi-line string
        """
        lines: list[str] = []

        if result.cache_path:
            lines.append(f"Cache Path: {result.cache_path}")

        lines.append(f"Cache Exists: {'Yes' if result.cache_exists else 'No'}")
        lines.append(f"Total Entries: {result.total_entries}")
        lines.append(f"Has Valid Token: {'Yes' if result.has_valid_token else 'No'}")

        if result.access_tokens:
            lines.append(f"\nAccess Tokens: {len(result.access_tokens)}")
            for i, token in enumerate(result.access_tokens, 1):
                status = "EXPIRED" if token.is_expired else "VALID"
                expires = CacheInspector._format_timestamp(token.expires_on)
                lines.append(f"  {i}. [{status}] Target: {token.target}, Expires: {expires}")

        if result.refresh_tokens:
            lines.append(f"\nRefresh Tokens: {len(result.refresh_tokens)}")

        if result.id_tokens:
            lines.append(f"ID Tokens: {len(result.id_tokens)}")

        if result.accounts:
            lines.append(f"Accounts: {len(result.accounts)}")

        if result.warnings:
            lines.append("\nWarnings:")
            for warning in result.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)

    @staticmethod
    def _format_timestamp(timestamp: int | None) -> str:
        """Format Unix timestamp to human-readable string."""
        if timestamp is None:
            return "N/A"

        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
