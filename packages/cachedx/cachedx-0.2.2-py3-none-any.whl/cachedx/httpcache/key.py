"""Cache key generation with request signature support"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..core.util import hash_content


def signature(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    vary_headers: list[str] | None = None,
) -> str:
    """
    Generate a cache key signature for an HTTP request.

    The signature includes:
    - HTTP method (normalized to uppercase)
    - Request path
    - Query parameters (sorted for consistency)
    - Selected headers based on vary_headers
    - Body content hash (for POST/PUT/PATCH)

    Args:
        method: HTTP method
        path: Request path
        params: Query parameters
        headers: Request headers
        body: Request body bytes
        vary_headers: Headers to include in signature (for Vary support)

    Returns:
        32-character cache key

    Examples:
        >>> key = signature("GET", "/api/users", {"limit": 10})
        >>> len(key)
        32
        >>> # Same params in different order should produce same key
        >>> key1 = signature("GET", "/api/users", {"b": 2, "a": 1})
        >>> key2 = signature("GET", "/api/users", {"a": 1, "b": 2})
        >>> key1 == key2
        True
    """
    parts = []

    # Always include method and path
    parts.append(method.upper())
    parts.append(path)

    # Include sorted query parameters
    if params:
        # Ensure consistent ordering
        sorted_params = json.dumps(params, sort_keys=True, separators=(",", ":"))
        parts.append(sorted_params)

    # Include vary headers if specified
    if headers and vary_headers:
        vary_dict = {}
        for header_name in vary_headers:
            # Try different case variations
            value = (
                headers.get(header_name)
                or headers.get(header_name.lower())
                or headers.get(header_name.title())
                or headers.get(header_name.upper())
            )
            if value:
                vary_dict[header_name.lower()] = value

        if vary_dict:
            vary_json = json.dumps(vary_dict, sort_keys=True, separators=(",", ":"))
            parts.append(f"vary:{vary_json}")

    # Include body hash for non-GET requests
    if body:
        body_hash = hash_content(body)
        parts.append(f"body:{body_hash}")

    # Create final signature
    signature_data = "|".join(parts)
    return hashlib.sha256(signature_data.encode("utf-8")).hexdigest()[:32]


def normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Normalize headers for consistent caching.

    Args:
        headers: Request headers

    Returns:
        Normalized headers dict (lowercase keys)
    """
    return {k.lower(): v for k, v in headers.items()}


def extract_vary_headers(headers: dict[str, str], vary_headers: list[str]) -> dict[str, str]:
    """
    Extract specific headers for cache key generation.

    Args:
        headers: All request headers
        vary_headers: List of header names to extract

    Returns:
        Dictionary of extracted headers
    """
    normalized = normalize_headers(headers)
    result = {}

    for header_name in vary_headers:
        norm_name = header_name.lower()
        if norm_name in normalized:
            result[norm_name] = normalized[norm_name]

    return result
