"""Command-line interface: tr-pii-guard scan|breach-report <file-or-dir>"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .breach import breach_report_many
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


def _read_dir(dir_path: str) -> dict[str, str]:
    """Read every file under `dir_path` into {relative_path: content},
    skipping unreadable/non-UTF-8 files with a warning instead of failing."""
    base = Path(dir_path)
    texts: dict[str, str] = {}
    for file_path in sorted(base.rglob("*")):
        if not file_path.is_file():
            continue
        try:
            texts[str(file_path.relative_to(base))] = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            print(f"tr-pii-guard: atlandı (okunamadı): {file_path}", file=sys.stderr)
    return texts


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
    report.add_argument("path", help="Path to a text file OR a directory (recursively scanned)")
    report.add_argument("--use-ner", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "scan":
        text = _read_file(args.path)
        if text is None:
            return 1
        try:
            masked, _ = redact(text, use_ner=args.use_ner)
        except ImportError as exc:
            print(f"tr-pii-guard: {exc}", file=sys.stderr)
            return 1
        print(masked)
        return 0

    if args.command == "breach-report":
        if Path(args.path).is_dir():
            texts = _read_dir(args.path)
            if not texts:
                print(f"tr-pii-guard: {args.path} içinde okunabilir dosya bulunamadı", file=sys.stderr)
                return 1
        else:
            text = _read_file(args.path)
            if text is None:
                return 1
            texts = {args.path: text}

        try:
            result = breach_report_many(texts, use_ner=args.use_ner)
        except ImportError as exc:
            print(f"tr-pii-guard: {exc}", file=sys.stderr)
            return 1

        if len(texts) > 1:
            print(f"{len(texts)} dosya tarandı.\n")
            for name, file_report in result["per_source"].items():
                if file_report["counts"]:
                    print(f"  {name}: {file_report['counts']} -> risk: {file_report['risk_level']}")
            print()

        print(f"Risk seviyesi: {result['risk_level']}")
        print(f"Gerekçe: {result['reason']}")
        print("Toplam tespit sayıları:")
        for label, count in result["total_counts"].items():
            print(f"  {label}: {count}")
        print(
            "\nNot: Bu teknik bir özettir, hukuki tavsiye değildir. "
            "KVKK bildirim kararı için hukuk/uyum ekibinize danışın."
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
