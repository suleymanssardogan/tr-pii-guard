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
    assert "3 dosya tarandı" in out
    assert "yüksek" in out  # TC no + telefon aynı dökümde birlikte
    assert VALID_TC_NO not in out


def test_cli_breach_report_empty_dir_gives_clean_error(tmp_path, capsys):
    exit_code = main(["breach-report", str(tmp_path)])
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "Traceback" not in err
