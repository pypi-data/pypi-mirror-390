"""Exceptions for HTTP caching layer"""


class CacheError(Exception):
    """Base exception for cache operations"""

    pass


class ConfigurationError(CacheError):
    """Configuration-related errors"""

    pass


class StorageError(CacheError):
    """Storage-related errors"""

    pass


class ValidationError(CacheError):
    """Validation-related errors"""

    pass
