"""Decorator-based hooks for automatic response mirroring"""

from __future__ import annotations

import json
import logging
from functools import wraps
from typing import TYPE_CHECKING, Any

import orjson
from pydantic import TypeAdapter

from .inference import infer_from_response
from .normalize import upsert_batch, upsert_from_obj
from .registry import Mapping, get, register

if TYPE_CHECKING:
    from collections.abc import Callable

    import httpx

logger = logging.getLogger(__name__)

# Type adapter for validating JSON responses
JsonObjectOrArray: TypeAdapter[dict[str, Any] | list[dict[str, Any]]] = TypeAdapter(
    dict[str, Any] | list[dict[str, Any]]
)


def hybrid_cache(
    resource: str, auto_register: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to automatically mirror HTTP responses to normalized tables.

    This decorator can wrap functions that return httpx.Response objects or
    JSON data directly. It will:
    1. Extract JSON payload from the response
    2. Store raw data for provenance
    3. Upsert to normalized table using registered mapping
    4. Auto-register schema if not found and auto_register=True

    Args:
        resource: Resource name for the mapping
        auto_register: Whether to auto-register schema if not found

    Examples:
        >>> @hybrid_cache(resource="users")
        ... async def get_users(client):
        ...     return await client.get("/api/users")
        >>>
        >>> # With custom table
        >>> @hybrid_cache(resource="forecasts")
        ... async def get_forecasts(client):
        ...     response = await client.get("/api/forecasts")
        ...     return response
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await _process_response(
                func, args, kwargs, resource, auto_register, is_async=True
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return _process_response_sync(func, args, kwargs, resource, auto_register)

        # Return appropriate wrapper based on function type
        if hasattr(func, "__code__") and "async" in str(func.__code__):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def _process_response(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    resource: str,
    auto_register: bool,
    is_async: bool = True,
) -> Any:
    """Process async function response"""
    # Execute the original function
    if is_async:
        result = await func(*args, **kwargs)
    else:
        result = func(*args, **kwargs)

    try:
        # Extract JSON data from various response types
        json_data = _extract_json_data(result)
        if json_data is None:
            return result

        # Validate JSON structure
        try:
            validated_data = JsonObjectOrArray.validate_python(json_data)
        except Exception as e:
            logger.warning(f"Invalid JSON structure for resource {resource}: {e}")
            return result

        # Get or create mapping
        mapping = get(resource)
        if mapping is None:
            if auto_register:
                mapping = _auto_register_mapping(resource, validated_data)
            else:
                logger.warning(f"No mapping found for resource {resource} and auto_register=False")
                return result

        # Process the data
        _mirror_data(resource, validated_data, mapping)

        logger.debug(f"Successfully mirrored data for resource: {resource}")

    except Exception as e:
        logger.error(f"Failed to process response for resource {resource}: {e}")
        # Don't raise - return original result

    return result


def _process_response_sync(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    resource: str,
    auto_register: bool,
) -> Any:
    """Process sync function response"""
    # Execute the original function
    result = func(*args, **kwargs)

    try:
        # Extract JSON data
        json_data = _extract_json_data(result)
        if json_data is None:
            return result

        # Validate JSON structure
        try:
            validated_data = JsonObjectOrArray.validate_python(json_data)
        except Exception as e:
            logger.warning(f"Invalid JSON structure for resource {resource}: {e}")
            return result

        # Get or create mapping
        mapping = get(resource)
        if mapping is None:
            if auto_register:
                mapping = _auto_register_mapping(resource, validated_data)
            else:
                logger.warning(f"No mapping found for resource {resource}")
                return result

        # Process the data
        _mirror_data(resource, validated_data, mapping)

    except Exception as e:
        logger.error(f"Failed to process response for resource {resource}: {e}")

    return result


def _extract_json_data(response: Any) -> dict[str, Any] | list[Any] | None:
    """
    Extract JSON data from various response types.

    Args:
        response: Response object (httpx.Response, dict, list, etc.)

    Returns:
        JSON data or None if not extractable
    """
    # httpx.Response
    if hasattr(response, "json") and callable(response.json):
        try:
            return response.json()  # type: ignore[no-any-return]
        except Exception:
            return None

    # Raw bytes/string content
    if hasattr(response, "content"):
        content = response.content
        if isinstance(content, bytes):
            try:
                return orjson.loads(content)  # type: ignore[no-any-return]
            except Exception:
                return None

    # String content
    if isinstance(response, str):
        try:
            return json.loads(response)  # type: ignore[no-any-return]
        except Exception:
            return None

    # Already parsed JSON
    if isinstance(response, dict | list):
        return response

    # Check for text attribute (some response objects)
    if hasattr(response, "text"):
        try:
            return json.loads(response.text)  # type: ignore[no-any-return]
        except Exception:
            return None

    return None


def _auto_register_mapping(resource: str, data: dict[str, Any] | list[dict[str, Any]]) -> Mapping:
    """Auto-register a mapping by inferring schema from data"""
    try:
        # Infer mapping from data
        mapping = infer_from_response(data, resource)

        # Register it
        register(resource, mapping)

        logger.info(f"Auto-registered mapping for resource: {resource}")
        return mapping

    except Exception as e:
        logger.error(f"Failed to auto-register mapping for {resource}: {e}")
        raise


def _mirror_data(
    resource: str, data: dict[str, Any] | list[dict[str, Any]], mapping: Mapping
) -> None:
    """Mirror data to normalized storage"""
    try:
        if isinstance(data, list):
            # Batch processing for arrays
            if data:  # Only process non-empty arrays
                upsert_batch(
                    resource=resource,
                    objects=data,
                    columns=mapping.columns,
                    table=mapping.table,
                    id_field=mapping.id_field,
                )
        else:
            # Single object
            upsert_from_obj(
                resource=resource,
                obj=data,
                columns=mapping.columns,
                table=mapping.table,
                id_field=mapping.id_field,
            )

    except Exception as e:
        logger.error(f"Failed to mirror data for resource {resource}: {e}")
        raise


# Convenience functions for manual mirroring


def mirror_response(response: httpx.Response, resource: str, auto_register: bool = True) -> None:
    """
    Manually mirror an httpx response.

    Args:
        response: httpx Response object
        resource: Resource name
        auto_register: Whether to auto-register schema

    Examples:
        >>> response = await client.get("/api/users")
        >>> mirror_response(response, "users")
    """
    json_data = _extract_json_data(response)
    if json_data is None:
        raise ValueError("Response does not contain valid JSON")

    mapping = get(resource)
    if mapping is None:
        if auto_register:
            mapping = _auto_register_mapping(resource, json_data)
        else:
            raise ValueError(f"No mapping registered for resource: {resource}")

    _mirror_data(resource, json_data, mapping)


def mirror_json(
    data: dict[str, Any] | list[dict[str, Any]], resource: str, auto_register: bool = True
) -> None:
    """
    Manually mirror JSON data.

    Args:
        data: JSON data (dict or list of dicts)
        resource: Resource name
        auto_register: Whether to auto-register schema

    Examples:
        >>> data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> mirror_json(data, "users")
    """
    mapping = get(resource)
    if mapping is None:
        if auto_register:
            mapping = _auto_register_mapping(resource, data)
        else:
            raise ValueError(f"No mapping registered for resource: {resource}")

    _mirror_data(resource, data, mapping)
