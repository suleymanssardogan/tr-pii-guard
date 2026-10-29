"""External, held-out NER validation against a real public dataset.

Unlike benchmarks/corpus.py (hand-crafted, canonical "Name Name,
Location'dan geldi" sentences), this runs find_names() against real
Turkish Wikipedia sentences from turkish-nlp-suite/turkish-wikiNER's
*test* split (not used to train savasy/bert-base-turkish-ner-cased, the
model this project uses) -- a genuinely independent sanity check, not
just a re-statement of our own easy examples.

Needs: pip install pandas pyarrow (one-off, not a project dependency).
Usage: python3 benchmarks/external_wikiner_eval.py [n_sentences]
"""

import re
import sys
import time
import urllib.request
from pathlib import Path

PARQUET_URL = (
    "https://huggingface.co/datasets/turkish-nlp-suite/turkish-wikiNER/"
    "resolve/refs%2Fconvert%2Fparquet/default/test/0000.parquet"
)
CACHE_PATH = Path(__file__).parent / ".cache" / "turkish-wikiner-test.parquet"

# Turkish possessive/case clitics attached with an apostrophe
# ("Medea'nın" -> "Medea", "Yıldırım Demirören'e" -> "Yıldırım Demirören").
# This dataset includes the clitic in the entity span; our model (correctly,
# linguistically) usually doesn't. Stripped only from the END of a string,
# so it can't damage a name that legitimately contains an apostrophe
# mid-string (e.g. "Eto'o").
_SUFFIX_RE = re.compile(
    r"'(nın|nin|nun|nün|ın|in|un|ün|ya|ye|da|de|ta|te|dan|den|tan|ten|yı|yi|yu|yü|nı|ni|a|e)$"
)

LABELS = [
    "O", "B-CARDINAL", "B-DATE", "B-EVENT", "B-FAC", "B-GPE", "B-LANGUAGE", "B-LAW",
    "B-LOC", "B-MONEY", "B-NORP", "B-ORDINAL", "B-ORG", "B-PERCENT", "B-PERSON",
    "B-PRODUCT", "B-QUANTITY", "B-TIME", "B-TITLE", "B-WORK_OF_ART",
    "I-CARDINAL", "I-DATE", "I-EVENT", "I-FAC", "I-GPE", "I-LANGUAGE", "I-LAW",
    "I-LOC", "I-MONEY", "I-NORP", "I-ORDINAL", "I-ORG", "I-PERCENT", "I-PERSON",
    "I-PRODUCT", "I-QUANTITY", "I-TIME", "I-TITLE", "I-WORK_OF_ART",
]
# GPE (countries/cities/states) is conceptually "location" too; this
# dataset's finer-grained scheme just splits it from LOC (natural/geographic
# features). Our 2-category model doesn't make that distinction, so both
# count as ground truth for a fair comparison.
WANTED = {"PERSON", "LOC", "GPE"}


def normalize(s: str) -> str:
    return _SUFFIX_RE.sub("", s)


def extract_entities(tokens, tags):
    spans, current, current_type = [], [], None
    for tok, tag_id in zip(tokens, tags):
        label = LABELS[tag_id]
        if label == "O":
            if current:
                spans.append(" ".join(current))
                current, current_type = [], None
            continue
        prefix, etype = label.split("-", 1)
        if etype not in WANTED:
            if current:
                spans.append(" ".join(current))
                current, current_type = [], None
            continue
        if prefix == "B" or etype != current_type:
            if current:
                spans.append(" ".join(current))
            current, current_type = [tok], etype
        else:
            current.append(tok)
    if current:
        spans.append(" ".join(current))
    return spans


def load_test_split():
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE_PATH.exists():
        print(f"İndiriliyor: {PARQUET_URL}")
        urllib.request.urlretrieve(PARQUET_URL, CACHE_PATH)

    import pandas as pd

    return pd.read_parquet(CACHE_PATH)


def report(label, tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    print(f"[{label}] TP={tp} FP={fp} FN={fn}  Precision={precision:.3f} Recall={recall:.3f}")


def main():
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from tr_pii_guard.ner import find_names

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    df = load_test_split().head(n)
    print(f"Değerlendirilen cümle sayısı: {len(df)} (turkish-nlp-suite/turkish-wikiNER test split)")

    tp = fp = fn = 0
    ntp = nfp = nfn = 0
    start = time.perf_counter()
    for _, row in df.iterrows():
        tokens = list(row["tokens"])
        tags = list(row["tags"])
        text = " ".join(tokens)
        expected = set(extract_entities(tokens, tags))
        found = {m.group() for m in find_names(text)}
        tp += len(found & expected)
        fp += len(found - expected)
        fn += len(expected - found)

        n_expected = {normalize(s) for s in expected}
        n_found = {normalize(s) for s in found}
        ntp += len(n_found & n_expected)
        nfp += len(n_found - n_expected)
        nfn += len(n_expected - n_found)
    elapsed = time.perf_counter() - start

    report("ham, tam string eşleşmesi", tp, fp, fn)
    report("iyelik eki normalize edilmiş", ntp, nfp, nfn)
    print(f"Süre: {elapsed:.1f}s ({elapsed / len(df) * 1000:.1f} ms/cümle)")


if __name__ == "__main__":
    main()
