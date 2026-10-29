"""Regression tests for two real ReDoS-adjacent (catastrophic/polynomial
backtracking) bugs found by fuzzing the detectors with adversarial inputs.

Both had the same shape: an unbounded quantifier (`+` or `.*?`) placed
right before a required literal that might not exist anywhere nearby. Each
scan position then redoes up to O(n) backtracking work, and re.finditer
retries at every position, giving O(n^2) overall -- or worse, effectively
hanging (minutes+) on megabyte-scale input, which is exactly the kind of
input this library's intended use (sanitizing arbitrary user-submitted
text before an LLM call) will see.

Fix: bound every such quantifier to a realistic real-world maximum (RFC
email-length limits; a generous max PEM block size), capping the
backtracking work per position to a constant instead of O(n).
"""

import time

from tr_pii_guard.detectors import find_api_key, find_email

_TIME_LIMIT = 3.0  # generous; the fixed patterns finish in well under 1s


def test_find_email_does_not_hang_on_long_text_with_no_at_sign():
    text = "x" * 2_000_000  # used to hang indefinitely (unbounded local-part before '@')

    start = time.perf_counter()
    result = find_email(text)
    elapsed = time.perf_counter() - start

    assert elapsed < _TIME_LIMIT, f"find_email() took {elapsed:.2f}s -- looks like ReDoS"
    assert result == []


def test_find_api_key_does_not_hang_on_many_unmatched_pem_begins():
    # Many "BEGIN" markers, never a matching "END" -- used to be O(n^2)
    # (each BEGIN scanned toward the end of the string before failing).
    text = "-----BEGIN RSA PRIVATE KEY----- " * 8000

    start = time.perf_counter()
    result = find_api_key(text)
    elapsed = time.perf_counter() - start

    assert elapsed < _TIME_LIMIT, f"find_api_key() took {elapsed:.2f}s -- looks like ReDoS"
    assert result == []
