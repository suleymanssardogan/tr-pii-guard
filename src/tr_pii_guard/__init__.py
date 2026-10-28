"""Turkish PII detection, redaction, and KVKK breach-impact reporting."""

from .breach import breach_report
from .middleware import protect, protect_stream
from .redactor import (
    hash_pii,
    redact,
    register_detector,
    restore,
    restore_stream,
    summary,
)

__version__ = "0.5.0"
__all__ = [
    "breach_report",
    "hash_pii",
    "protect",
    "protect_stream",
    "redact",
    "register_detector",
    "restore",
    "restore_stream",
    "summary",
]
