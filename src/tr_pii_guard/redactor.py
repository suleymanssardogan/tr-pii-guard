"""Combine all PII detectors into a single mask/unmask API."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import Callable

from .detectors import find_email, find_iban, find_phone, find_tc_no


def _base_detectors(strict: bool):
    return (
        ("TC_NO", lambda t: find_tc_no(t, validate=strict)),
        ("IBAN", lambda t: find_iban(t, validate=strict)),
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


def redact(
    text: str,
    use_ner: bool = False,
    types: list[str] | None = None,
    strict: bool = True,
) -> tuple[str, dict[str, str]]:
    """Mask Turkish PII in `text`. Returns (masked_text, mapping) where
    mapping maps each placeholder back to the original value.

    use_ner=True also masks person/location names via an optional Turkish
    NER model (pip install tr-pii-guard[ner]); off by default so the base
    package stays dependency-light.

    types restricts detection to a subset of labels, e.g. types=["TC_NO", "IBAN"];
    None (default) runs every registered detector.

    strict=False skips TC no/IBAN checksum validation, catching more
    candidates at the cost of more false positives.
    """
    detectors = _base_detectors(strict) + tuple(_extra_detectors)
    if use_ner:
        from .ner import find_names

        detectors = detectors + (("ISIM", find_names),)
    if types is not None:
        detectors = tuple(d for d in detectors if d[0] in types)

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


def restore_stream(chunks: Iterable[str], mapping: dict[str, str]) -> Iterator[str]:
    """Like `restore`, but for a stream of text chunks (e.g. an LLM streaming
    response) where a placeholder like "[TC_NO_1]" can land split across two
    or more chunks.

    Buffers only as many characters as the longest placeholder needs: it
    holds back any trailing text that could still be the start of a not-yet-
    complete placeholder, and flushes everything else immediately.
    """
    if not mapping:
        yield from chunks
        return

    keys = list(mapping)
    max_len = max(len(k) for k in keys)
    buffer = ""
    for chunk in chunks:
        buffer += chunk
        hold = 0
        for length in range(min(max_len, len(buffer)), 0, -1):
            tail = buffer[-length:]
            if any(key.startswith(tail) for key in keys):
                hold = length
                break
        safe_len = len(buffer) - hold
        if safe_len > 0:
            yield restore(buffer[:safe_len], mapping)
            buffer = buffer[safe_len:]
    if buffer:
        yield restore(buffer, mapping)
