"""Combine all PII detectors into a single mask/unmask API."""

from collections import defaultdict
from typing import Callable

from .detectors import find_email, find_iban, find_phone, find_tc_no

_BASE_DETECTORS = (
    ("TC_NO", find_tc_no),
    ("IBAN", find_iban),
    ("TELEFON", find_phone),
    ("EPOSTA", find_email),
)

_extra_detectors: list[tuple[str, Callable]] = []


def register_detector(label: str, finder) -> None:
    """Register a custom detector used by every later `redact()` call.

    `finder(text)` must return matches exposing `.start()`, `.end()`, `.group()`
    (anything `re.finditer` returns satisfies this).
    """
    _extra_detectors.append((label, finder))


def _collect_matches(text: str, detectors) -> list[tuple[int, int, str, str]]:
    candidates = [
        (m.start(), m.end(), label, m.group())
        for label, finder in detectors
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


def redact(text: str, use_ner: bool = False) -> tuple[str, dict[str, str]]:
    """Mask Turkish PII in `text`. Returns (masked_text, mapping) where
    mapping maps each placeholder back to the original value.

    use_ner=True also masks person/location names via an optional Turkish
    NER model (pip install tr-pii-guard[ner]); off by default so the base
    package stays dependency-light.
    """
    detectors = _BASE_DETECTORS + tuple(_extra_detectors)
    if use_ner:
        from .ner import find_names

        detectors = detectors + (("ISIM", find_names),)

    mapping: dict[str, str] = {}
    counters: dict[str, int] = defaultdict(int)
    pieces = []
    cursor = 0
    for start, end, label, value in _collect_matches(text, detectors):
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
