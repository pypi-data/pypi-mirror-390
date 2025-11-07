"""Resource mirroring with auto-inference and schema management"""

from .hooks import hybrid_cache, mirror_json
from .inference import SchemaInferrer, infer_from_response
from .normalize import save_raw, upsert_from_obj
from .registry import Mapping, clear_registry, get, list_resources, register

__all__ = [
    "hybrid_cache",
    "mirror_json",
    "SchemaInferrer",
    "infer_from_response",
    "Mapping",
    "register",
    "get",
    "list_resources",
    "clear_registry",
    "save_raw",
    "upsert_from_obj",
]
