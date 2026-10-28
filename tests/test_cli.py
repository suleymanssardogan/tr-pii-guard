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
