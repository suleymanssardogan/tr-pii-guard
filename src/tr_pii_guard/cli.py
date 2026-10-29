"""Command-line interface: tr-pii-guard scan|breach-report <file-or-dir>"""

from __future__ import annotations

import argparse
import csv
import json
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


def _read_csv_by_column(path: Path) -> dict[str, str]:
    """Read a CSV file into {"filename.csv:column": "val1\\nval2\\n..."} --
    real leak dumps are usually structured exports, not prose, and a
    per-column breakdown tells a human which field (e.g. "tc_no") actually
    held the PII, not just a flat whole-file total."""
    columns: dict[str, list[str]] = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for name in reader.fieldnames or []:
            columns[name] = []
        for row in reader:
            for name, value in row.items():
                if value:
                    columns.setdefault(name, []).append(value)
    return {f"{path.name}:{col}": "\n".join(vals) for col, vals in columns.items() if vals}


def _gather_texts(path_str: str) -> dict[str, str] | None:
    """Resolve `path_str` (a file or a directory) into {source_name: text},
    reading .csv files column-by-column instead of as one text blob.
    Returns None (after printing an error) if nothing usable was found."""
    path = Path(path_str)

    if path.is_dir():
        texts: dict[str, str] = {}
        for file_path in sorted(path.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() == ".csv":
                try:
                    texts.update(_read_csv_by_column(file_path))
                except (OSError, UnicodeDecodeError, csv.Error):
                    print(f"tr-pii-guard: atlandı (okunamadı): {file_path}", file=sys.stderr)
                continue
            try:
                texts[str(file_path.relative_to(path))] = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                print(f"tr-pii-guard: atlandı (okunamadı): {file_path}", file=sys.stderr)
        if not texts:
            print(f"tr-pii-guard: {path_str} içinde okunabilir dosya bulunamadı", file=sys.stderr)
            return None
        return texts

    if path.suffix.lower() == ".csv":
        try:
            texts = _read_csv_by_column(path)
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            print(f"tr-pii-guard: {path_str} okunamadı: {exc}", file=sys.stderr)
            return None
        if not texts:
            print(f"tr-pii-guard: {path_str} içinde okunabilir sütun bulunamadı", file=sys.stderr)
            return None
        return texts

    text = _read_file(path_str)
    if text is None:
        return None
    return {path_str: text}


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
    report.add_argument(
        "path", help="Path to a text/CSV file OR a directory (recursively scanned)"
    )
    report.add_argument("--use-ner", action="store_true")
    report.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

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
        texts = _gather_texts(args.path)
        if texts is None:
            return 1

        try:
            result = breach_report_many(texts, use_ner=args.use_ner)
        except ImportError as exc:
            print(f"tr-pii-guard: {exc}", file=sys.stderr)
            return 1

        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if len(texts) > 1:
            print(f"{len(texts)} kaynak tarandı.\n")
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
