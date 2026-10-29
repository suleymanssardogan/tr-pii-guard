"""Run the hand-labeled corpus through each detector and report precision/recall.

Usage: python3 benchmarks/run.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus import CASES

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from tr_pii_guard import redact
from tr_pii_guard.detectors import (
    find_api_key,
    find_email,
    find_iban,
    find_phone,
    find_plaka,
    find_tc_no,
    find_vergi_no,
)

DETECTORS = {
    "tc_no": find_tc_no,
    "iban": find_iban,
    "vergi_no": find_vergi_no,
    "telefon": find_phone,
    "eposta": find_email,
    "api_key": find_api_key,
    "plaka": find_plaka,
}


def evaluate():
    results = {}
    for label, finder in DETECTORS.items():
        tp = fp = fn = 0
        for case in CASES:
            found = {m.group() for m in finder(case["text"])}
            expected = set(case[label])
            tp += len(found & expected)
            fp += len(found - expected)
            fn += len(expected - found)
        precision = tp / (tp + fp) if (tp + fp) else float("nan")
        recall = tp / (tp + fn) if (tp + fn) else float("nan")
        results[label] = (tp, fp, fn, precision, recall)
    return results


def evaluate_ner():
    """Same precision/recall measurement, for the optional NER name/location
    detector. Returns None if `transformers`/`torch` aren't installed --
    ner.py itself imports fine without them, the ImportError only fires
    lazily on the first real find_names() call, so that's what we guard."""
    from tr_pii_guard.ner import find_names

    tp = fp = fn = 0
    try:
        for case in CASES:
            found = {m.group() for m in find_names(case["text"])}
            expected = set(case["isim"])
            tp += len(found & expected)
            fp += len(found - expected)
            fn += len(expected - found)
    except ImportError:
        return None
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    return tp, fp, fn, precision, recall


def measure_performance(repeats: int = 200):
    texts = [case["text"] for case in CASES]
    total_chars = sum(len(t) for t in texts) * repeats

    start = time.perf_counter()
    for _ in range(repeats):
        for text in texts:
            redact(text)
    elapsed = time.perf_counter() - start

    calls = len(texts) * repeats
    return elapsed / calls * 1000, total_chars / elapsed


def main():
    results = evaluate()
    print(f"Corpus: {len(CASES)} hand-labeled sentences\n")
    print(f"{'Tip':<10}{'TP':>4}{'FP':>4}{'FN':>4}{'Precision':>12}{'Recall':>10}")
    for label, (tp, fp, fn, precision, recall) in results.items():
        print(f"{label:<10}{tp:>4}{fp:>4}{fn:>4}{precision:>12.2f}{recall:>10.2f}")

    ner_result = evaluate_ner()
    if ner_result is None:
        print("\nisim (NER): transformers/torch kurulu değil, ölçülmedi.")
    else:
        tp, fp, fn, precision, recall = ner_result
        print(f"{'isim (NER)':<10}{tp:>4}{fp:>4}{fn:>4}{precision:>12.2f}{recall:>10.2f}")

    ms_per_call, chars_per_sec = measure_performance()
    print("\nPerformans (regex detector'lar, NER hariç, bu makinede):")
    print(f"  redact() başına ortalama: {ms_per_call:.4f} ms")
    print(f"  throughput: ~{chars_per_sec:,.0f} karakter/saniye")


if __name__ == "__main__":
    main()
