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
