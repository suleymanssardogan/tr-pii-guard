"""Command-line interface: tr-pii-guard scan <file>"""

import argparse
import sys

from .redactor import redact


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

    args = parser.parse_args(argv)

    try:
        with open(args.path, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(f"tr-pii-guard: {exc.strerror}: {args.path}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"tr-pii-guard: {args.path} UTF-8 metin dosyası değil", file=sys.stderr)
        return 1

    try:
        masked, _ = redact(text, use_ner=args.use_ner)
    except ImportError as exc:
        print(f"tr-pii-guard: {exc}", file=sys.stderr)
        return 1

    print(masked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
