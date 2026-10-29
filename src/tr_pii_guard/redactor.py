"""Combine all PII detectors into a single mask/unmask API."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import Callable

from .detectors import (
    find_api_key,
    find_email,
    find_iban,
    find_phone,
    find_plaka,
    find_tc_no,
    find_vergi_no,
)


def _base_detectors(strict: bool):
    return (
        ("TC_NO", lambda t: find_tc_no(t, validate=strict)),
        ("IBAN", lambda t: find_iban(t, validate=strict)),
        # Listed before TELEFON: a bare 10-digit number can match both
        # patterns, and when both claim the exact same span, the checksum-
        # validated VERGI_NO match should win the tie (see find_vergi_no()).
        ("VERGI_NO", lambda t: find_vergi_no(t, validate=strict)),
        ("TELEFON", find_phone),
        ("EPOSTA", find_email),
        ("API_KEY", find_api_key),
        ("PLAKA", find_plaka),
    )


_extra_detectors: list[tuple[str, Callable]] = []


def register_detector(label: str, finder) -> None:
    """Register a custom detector used by every later `redact()` call.

    `finder(text)` must return matches exposing `.start()`, `.end()`, `.group()`
    (anything `re.finditer` returns satisfies this).
    """
    _extra_detectors.append((label, finder))


def _resolve_cluster(cluster: list[tuple[int, int, str, str]]) -> list[tuple[int, int, str, str]]:
    """Longer matches win when two detectors claim overlapping spans, within
    one cluster of mutually-reachable overlapping candidates."""
    cluster = sorted(cluster, key=lambda c: (-(c[1] - c[0]), c[0]))
    chosen: list[tuple[int, int, str, str]] = []
    occupied: list[tuple[int, int]] = []
    for start, end, label, value in cluster:
        if any(start < o_end and end > o_start for o_start, o_end in occupied):
            continue
        chosen.append((start, end, label, value))
        occupied.append((start, end))
    return chosen


def _collect_matches(text: str, detectors) -> list[tuple[int, int, str, str]]:
    candidates = [
        (m.start(), m.end(), label, m.group())
        for label, finder in detectors
        for m in finder(text)
    ]
    candidates.sort(key=lambda c: c[0])

    # Overlaps in real text are local: a match can only conflict with others
    # whose spans physically reach it. Grouping into maximal overlap clusters
    # first, then resolving each cluster independently, turns what used to be
    # an O(n^2) "check every candidate against every accepted match" scan
    # into O(n log n) -- cluster size depends on local PII density, not on
    # total document length, which is what made scanning a large file
    # (hundreds of thousands of matches) effectively hang before this change.
    selected: list[tuple[int, int, str, str]] = []
    cluster: list[tuple[int, int, str, str]] = []
    cluster_end = -1
    for start, end, label, value in candidates:
        if cluster and start >= cluster_end:
            selected.extend(_resolve_cluster(cluster))
            cluster = []
        cluster.append((start, end, label, value))
        cluster_end = max(cluster_end, end)
    if cluster:
        selected.extend(_resolve_cluster(cluster))

    selected.sort(key=lambda c: c[0])
    return selected


def _resolve_detectors(
    use_ner: bool, types: list[str] | None, strict: bool, ner_min_score: float = 0.8
):
    detectors = _base_detectors(strict) + tuple(_extra_detectors)
    if use_ner:
        from .ner import find_names

        detectors = detectors + (("ISIM", lambda t: find_names(t, min_score=ner_min_score)),)
    if types is not None:
        detectors = tuple(d for d in detectors if d[0] in types)
    return detectors


def redact(
    text: str,
    use_ner: bool = False,
    types: list[str] | None = None,
    strict: bool = True,
    ner_min_score: float = 0.8,
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

    ner_min_score filters low-confidence NER predictions (see find_names()
    in ner.py); only used when use_ner=True.
    """
    detectors = _resolve_detectors(use_ner, types, strict, ner_min_score)

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


def hash_pii(
    text: str,
    salt: str = "",
    use_ner: bool = False,
    types: list[str] | None = None,
    strict: bool = True,
    ner_min_score: float = 0.8,
) -> str:
    """Irreversibly pseudonymize PII in `text` with a salted SHA-256 hash
    instead of a restorable placeholder.

    Unlike redact()/restore(), the original value can never be recovered --
    use this for analytics/logging where you want the same PII value to
    always hash to the same token (useful for joining records) without
    ever being able to read the original back.
    """
    detectors = _resolve_detectors(use_ner, types, strict, ner_min_score)

    pieces = []
    cursor = 0
    for start, end, label, value in _collect_matches(text, detectors):
        digest = hashlib.sha256((salt + value).encode("utf-8")).hexdigest()[:12]
        pieces.append(text[cursor:start])
        pieces.append(f"[{label}_{digest}]")
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def summary(mapping: dict[str, str]) -> dict[str, int]:
    """Count how many PII items of each type `redact()` found, from its
    mapping. Safe for audit logs/metrics: unlike `mapping` itself, this
    never includes the original values -- only counts per label.
    """
    counts: dict[str, int] = defaultdict(int)
    for placeholder in mapping:
        label = placeholder[1:-1].rsplit("_", 1)[0]
        counts[label] += 1
    return dict(counts)


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
