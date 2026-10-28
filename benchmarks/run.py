"""Run the hand-labeled corpus through each detector and report precision/recall.

Usage: python3 benchmarks/run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus import CASES

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from tr_pii_guard.detectors import find_email, find_iban, find_phone, find_tc_no

DETECTORS = {
    "tc_no": find_tc_no,
    "iban": find_iban,
    "telefon": find_phone,
    "eposta": find_email,
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


def main():
    results = evaluate()
    print(f"Corpus: {len(CASES)} hand-labeled sentences\n")
    print(f"{'Tip':<10}{'TP':>4}{'FP':>4}{'FN':>4}{'Precision':>12}{'Recall':>10}")
    for label, (tp, fp, fn, precision, recall) in results.items():
        print(f"{label:<10}{tp:>4}{fp:>4}{fn:>4}{precision:>12.2f}{recall:>10.2f}")


if __name__ == "__main__":
    main()
