"""Turkish PII detection and redaction for LLM pipelines."""

from .middleware import protect, protect_stream
from .redactor import (
    hash_pii,
    redact,
    register_detector,
    restore,
    restore_stream,
    summary,
)

__version__ = "0.4.0"
__all__ = [
    "hash_pii",
    "protect",
    "protect_stream",
    "redact",
    "register_detector",
    "restore",
    "restore_stream",
    "summary",
]
