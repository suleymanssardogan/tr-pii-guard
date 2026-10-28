import re

from tr_pii_guard import redact
from tr_pii_guard.redactor import _extra_detectors, register_detector


def test_register_custom_detector():
    def find_secret(text):
        return list(re.finditer(r"GIZLI-\d+", text))

    register_detector("OZEL", find_secret)
    try:
        masked, mapping = redact("Kod: GIZLI-42 burada.")
        assert "GIZLI-42" not in masked
        assert "[OZEL_1]" in masked
        assert mapping["[OZEL_1]"] == "GIZLI-42"
    finally:
        _extra_detectors.clear()
