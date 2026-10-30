"""External false-positive check for the regex detectors against real,
genuinely PII-free Turkish text (Wikipedia prose).

Unlike benchmarks/external_wikiner_eval.py, this dataset has no PII labels
to check recall against -- Wikipedia articles don't contain real people's
TC no/IBAN/phone numbers. What it IS good for: confirming the regex
detectors don't over-trigger on large-scale, natural, unscripted text (as
opposed to our hand-crafted corpus, which we wrote ourselves).

Caveat, reported honestly rather than hidden: encyclopedic prose rarely
contains the long digit runs or special characters (10-11 consecutive
digits, "@", "TR"+digits, "sk-"/"AKIA"-style prefixes) these detectors key
off, so a 0-false-positive result here is weaker evidence for TC_NO/
VERGI_NO/IBAN/EPOSTA/API_KEY than for TELEFON/PLAKA. The checksum-
coincidence risk for TC_NO/IBAN/VERGI_NO is deliberately stress-tested
instead by the hand-crafted distractors in benchmarks/corpus.py.

Needs: pip install pandas pyarrow (one-off, not a project dependency).
Usage: python3 benchmarks/external_regex_eval.py [n_sentences]
"""

import re
import sys
from pathlib import Path

from external_wikiner_eval import load_test_split

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
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
    "telefon": find_phone,
    "eposta": find_email,
    "vergi_no": find_vergi_no,
    "plaka": find_plaka,
    "api_key": find_api_key,
}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    df = load_test_split().head(n)
    texts = [" ".join(row["tokens"]) for _, row in df.iterrows()]
    total_chars = sum(len(t) for t in texts)

    longest_digit_run = max(
        (len(m.group()) for t in texts for m in re.finditer(r"\d+", t)), default=0
    )
    print(
        f"{len(texts)} gerçek Wikipedia cümlesi, {total_chars} karakter "
        f"(en uzun rakam dizisi: {longest_digit_run} hane)\n"
    )

    for name, fn in DETECTORS.items():
        hits = [(t, m.group()) for t in texts for m in fn(t)]
        print(f"{name:10s}: {len(hits)} yanlış pozitif")
        for t, val in hits[:5]:
            print(f"    {val!r}  <-  {t[:80]!r}")


if __name__ == "__main__":
    main()
