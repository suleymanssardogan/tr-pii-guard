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


def find_names(text: str) -> list[_Span]:
    """Find person/location entities in `text` using a Turkish NER model."""
    ner = _get_pipeline()
    return [
        _Span(r["start"], r["end"], text[r["start"] : r["end"]])
        for r in ner(text)
        if r["entity_group"] in _WANTED_LABELS
    ]
