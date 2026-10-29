"""Optional Turkish NER-based name/location detection (PERSON/LOC).

Needs the `ner` extra: pip install tr-pii-guard[ner]
The model is loaded lazily on first use so importing this package never
forces the transformers/torch download.
"""

_MODEL_NAME = "savasy/bert-base-turkish-ner-cased"
_WANTED_LABELS = {"PER", "LOC"}

_pipeline = None


class _Span:
    """Minimal re.Match-like wrapper so NER results fit the same
    (start(), end(), group()) interface the regex detectors use."""

    def __init__(self, start: int, end: int, value: str):
        self._start = start
        self._end = end
        self._value = value

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end

    def group(self) -> str:
        return self._value


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise ImportError(
                "İsim/adres tespiti için ek bağımlılıklar gerekli: "
                "pip install tr-pii-guard[ner]"
            ) from exc
        _pipeline = pipeline("ner", model=_MODEL_NAME, aggregation_strategy="simple")
    return _pipeline


def find_names(text: str, min_score: float = 0.8) -> list[_Span]:
    """Find person/location entities in `text` using a Turkish NER model.

    min_score filters out low-confidence predictions. Measured against a
    held-out corpus, common clean detections score 0.88+, while garbled
    subword fragments (the model splitting one word's subwords across
    mismatched entity types on rare/foreign names) and the "email
    local-part misread as a name" false positive both score well below
    0.8. The 0.8 default is a real precision/recall trade-off, not a free
    win: on a 1000-sentence external benchmark it took precision from
    0.60 to 0.72 but recall from 0.68 to 0.64 -- some genuine low-
    confidence detections get filtered out too. Pass a lower value (e.g.
    0.5) to favor recall over precision; see BENCHMARK.md.
    """
    ner = _get_pipeline()
    return [
        _Span(r["start"], r["end"], text[r["start"] : r["end"]])
        for r in ner(text)
        if r["entity_group"] in _WANTED_LABELS and r["score"] >= min_score
    ]
