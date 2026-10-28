"""Command-line interface: tr-pii-guard scan|breach-report <file>"""

from __future__ import annotations

import argparse
import sys

from .breach import breach_report
from .redactor import redact


def _read_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as exc:
        print(f"tr-pii-guard: {exc.strerror}: {path}", file=sys.stderr)
        return None
    except UnicodeDecodeError:
        print(f"tr-pii-guard: {path} UTF-8 metin dosyası değil", file=sys.stderr)
        return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tr-pii-guard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Print a file's content with PII masked")
    scan.add_argument("path", help="Path to a text file")
    scan.add_argument(
        "--use-ner",
        action="store_true",
        help="Also mask names/locations (requires: pip install tr-pii-guard[ner])",
    )

    report = subparsers.add_parser(
        "breach-report",
        help="KVKK-odaklı veri ihlali etki özeti (hukuki tavsiye değildir)",
    )
    report.add_argument("path", help="Path to a text file")
    report.add_argument("--use-ner", action="store_true")

    args = parser.parse_args(argv)

    text = _read_file(args.path)
    if text is None:
        return 1

    if args.command == "scan":
        try:
            masked, _ = redact(text, use_ner=args.use_ner)
        except ImportError as exc:
            print(f"tr-pii-guard: {exc}", file=sys.stderr)
            return 1
        print(masked)
        return 0

    if args.command == "breach-report":
        try:
            result = breach_report(text, use_ner=args.use_ner)
        except ImportError as exc:
            print(f"tr-pii-guard: {exc}", file=sys.stderr)
            return 1
        print(f"Risk seviyesi: {result['risk_level']}")
        print(f"Gerekçe: {result['reason']}")
        print("Tespit sayıları:")
        for label, count in result["counts"].items():
            print(f"  {label}: {count}")
        print(
            "\nNot: Bu teknik bir özettir, hukuki tavsiye değildir. "
            "KVKK bildirim kararı için hukuk/uyum ekibinize danışın."
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
