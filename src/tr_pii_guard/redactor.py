"""Combine all PII detectors into a single mask/unmask API."""

from collections import defaultdict

from .detectors import find_email, find_iban, find_phone, find_tc_no

_DETECTORS = (
    ("TC_NO", find_tc_no),
    ("IBAN", find_iban),
    ("TELEFON", find_phone),
    ("EPOSTA", find_email),
)


def _collect_matches(text: str) -> list[tuple[int, int, str, str]]:
    candidates = [
        (m.start(), m.end(), label, m.group())
        for label, finder in _DETECTORS
        for m in finder(text)
    ]
    # Longer matches win when two detectors claim overlapping spans.
    candidates.sort(key=lambda c: (-(c[1] - c[0]), c[0]))

    selected: list[tuple[int, int, str, str]] = []
    occupied: list[tuple[int, int]] = []
    for start, end, label, value in candidates:
        if any(start < o_end and end > o_start for o_start, o_end in occupied):
            continue
        selected.append((start, end, label, value))
        occupied.append((start, end))

    selected.sort(key=lambda c: c[0])
    return selected


def redact(text: str) -> tuple[str, dict[str, str]]:
    """Mask Turkish PII in `text`. Returns (masked_text, mapping) where
    mapping maps each placeholder back to the original value."""
    mapping: dict[str, str] = {}
    counters: dict[str, int] = defaultdict(int)
    pieces = []
    cursor = 0
    for start, end, label, value in _collect_matches(text):
        counters[label] += 1
        placeholder = f"[{label}_{counters[label]}]"
        mapping[placeholder] = value
        pieces.append(text[cursor:start])
        pieces.append(placeholder)
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces), mapping


def restore(masked_text: str, mapping: dict[str, str]) -> str:
    """Reverse `redact`: replace placeholders with their original values."""
    result = masked_text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result
