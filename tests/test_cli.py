import json

from tr_pii_guard.cli import main

VALID_TC_NO = "10000000146"


def test_cli_scan_masks_file(tmp_path, capsys):
    f = tmp_path / "input.txt"
    f.write_text(f"TC no {VALID_TC_NO}.", encoding="utf-8")

    exit_code = main(["scan", str(f)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert VALID_TC_NO not in out
    assert "[TC_NO_1]" in out


def test_cli_scan_missing_file_gives_clean_error(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    exit_code = main(["scan", str(missing)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err
    assert str(missing) in err


def test_cli_scan_non_utf8_file_gives_clean_error(tmp_path, capsys):
    f = tmp_path / "binary.bin"
    f.write_bytes(b"\xff\xfe\x00\x01")

    exit_code = main(["scan", str(f)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err


def test_cli_breach_report_prints_risk_and_disclaimer(tmp_path, capsys):
    f = tmp_path / "leak.txt"
    f.write_text(f"TC no {VALID_TC_NO}, telefon 0532 123 45 67.", encoding="utf-8")

    exit_code = main(["breach-report", str(f)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "yüksek" in out
    assert VALID_TC_NO not in out
    assert "hukuki tavsiye değildir" in out


def test_cli_breach_report_scans_directory(tmp_path, capsys):
    (tmp_path / "a.txt").write_text(f"TC no {VALID_TC_NO}.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("telefon 0532 123 45 67.", encoding="utf-8")
    (tmp_path / "c.txt").write_text("Bugün hava çok güzel.", encoding="utf-8")

    exit_code = main(["breach-report", str(tmp_path)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "3 kaynak tarandı" in out
    assert "yüksek" in out  # TC no + telefon aynı dökümde birlikte
    assert VALID_TC_NO not in out


def test_cli_breach_report_empty_dir_gives_clean_error(tmp_path, capsys):
    exit_code = main(["breach-report", str(tmp_path)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err


def test_cli_breach_report_json_format(tmp_path, capsys):
    f = tmp_path / "leak.txt"
    f.write_text(f"TC no {VALID_TC_NO}.", encoding="utf-8")

    exit_code = main(["breach-report", str(f), "--format", "json"])
    out = capsys.readouterr().out

    assert exit_code == 0
    payload = json.loads(out)
    assert payload["risk_level"] == "orta"
    assert payload["total_counts"] == {"TC_NO": 1}
    assert VALID_TC_NO not in out


def test_cli_breach_report_csv_reads_by_column(tmp_path, capsys):
    f = tmp_path / "musteriler.csv"
    f.write_text(
        f"ad,tc_no\nAhmet,{VALID_TC_NO}\nAyşe,12345678950\n",
        encoding="utf-8",
    )

    exit_code = main(["breach-report", str(f)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "TC_NO: 2" in out
    assert VALID_TC_NO not in out


def test_cli_breach_report_csv_per_column_breakdown_json(tmp_path, capsys):
    f = tmp_path / "musteriler.csv"
    f.write_text(f"ad,tc_no\nAhmet,{VALID_TC_NO}\n", encoding="utf-8")

    exit_code = main(["breach-report", str(f), "--format", "json"])
    out = capsys.readouterr().out

    assert exit_code == 0
    payload = json.loads(out)
    assert f"{f.name}:tc_no" in payload["per_source"]
    assert payload["per_source"][f"{f.name}:tc_no"]["counts"] == {"TC_NO": 1}


def test_cli_breach_report_csv_inside_scanned_directory(tmp_path, capsys):
    (tmp_path / "musteriler.csv").write_text(
        f"ad,tc_no\nAhmet,{VALID_TC_NO}\n", encoding="utf-8"
    )
    (tmp_path / "notlar.txt").write_text("Bugün hava çok güzel.", encoding="utf-8")

    exit_code = main(["breach-report", str(tmp_path)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "musteriler.csv:tc_no" in out
    assert VALID_TC_NO not in out


def test_cli_breach_report_scans_nested_subdirectories(tmp_path, capsys):
    nested = tmp_path / "alt_klasor"
    nested.mkdir()
    (nested / "gizli.txt").write_text(f"TC no {VALID_TC_NO}.", encoding="utf-8")

    exit_code = main(["breach-report", str(tmp_path)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "TC_NO: 1" in out
    assert VALID_TC_NO not in out


def test_cli_breach_report_missing_single_file_gives_clean_error(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    exit_code = main(["breach-report", str(missing)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err


def test_cli_breach_report_non_utf8_csv_gives_clean_error(tmp_path, capsys):
    f = tmp_path / "bozuk.csv"
    f.write_bytes(b"\xff\xfe\x00\x01")

    exit_code = main(["breach-report", str(f)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err


def test_cli_breach_report_directory_skips_unreadable_files(tmp_path, capsys):
    (tmp_path / "ok.txt").write_text(f"TC no {VALID_TC_NO}.", encoding="utf-8")
    (tmp_path / "bozuk.txt").write_bytes(b"\xff\xfe\x00\x01")
    (tmp_path / "bozuk.csv").write_bytes(b"\xff\xfe\x00\x01")

    exit_code = main(["breach-report", str(tmp_path)])
    out = capsys.readouterr().out
    err = capsys.readouterr().err

    assert exit_code == 0
    assert "TC_NO: 1" in out
    assert "Traceback" not in err


def test_cli_breach_report_empty_csv_gives_clean_error(tmp_path, capsys):
    f = tmp_path / "bos.csv"
    f.write_text("", encoding="utf-8")

    exit_code = main(["breach-report", str(f)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err


def test_cli_scan_use_ner_without_extra_gives_clean_error(tmp_path, capsys):
    try:
        import transformers  # noqa: F401
    except ImportError:
        pass
    else:
        import pytest

        pytest.skip("transformers is installed; nothing to assert here")

    f = tmp_path / "input.txt"
    f.write_text("Ahmet Yılmaz İstanbul'a gitti.", encoding="utf-8")

    exit_code = main(["scan", str(f), "--use-ner"])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err
    assert "tr-pii-guard[ner]" in err
