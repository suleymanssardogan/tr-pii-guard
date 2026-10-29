"""Regression test for a real O(n^2) bug in overlap resolution.

Found by stress-testing a 34MB synthetic leak file through the CLI: it
didn't finish in 2 minutes. Root cause: _collect_matches() checked every
candidate match against the full list of already-accepted matches, so
redact() scaled quadratically with the number of PII items in the text.
Fixed by clustering overlapping candidates first (local, independent of
total document length) and resolving each small cluster separately --
this test fails hard under the old O(n^2) behavior and comfortably
passes under the O(n log n) fix.
"""

import time

from tr_pii_guard import redact

_LINE = (
    "Müşteri: Ahmet Yılmaz, TC no 10000000146, telefon 0532 123 45 67, "
    "e-posta test@example.com, filler filler filler."
)


def test_redact_scales_past_many_matches_without_quadratic_blowup():
    text = "\n".join([_LINE] * 8000)  # ~800,000 characters, ~32,000 PII matches

    start = time.perf_counter()
    redact(text)
    elapsed = time.perf_counter() - start

    # O(n^2) took ~6.2s for this input size before the fix; O(n log n)
    # takes ~0.1s. A generous 2s ceiling catches a quadratic regression
    # without being flaky on a slow CI machine.
    assert elapsed < 2.0, f"redact() took {elapsed:.2f}s -- looks like a quadratic regression"
