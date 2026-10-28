from tr_pii_guard import redact, summary

VALID_TC_NO = "10000000146"


def test_summary_counts_without_leaking_raw_values():
    text = (
        f"TC no {VALID_TC_NO}, telefon 0532 123 45 67, "
        "ikinci telefon 0212 123 45 67, mail test@example.com."
    )
    _, mapping = redact(text)

    counts = summary(mapping)

    assert counts == {"TC_NO": 1, "TELEFON": 2, "EPOSTA": 1}
    assert VALID_TC_NO not in repr(counts)
    assert "test@example.com" not in repr(counts)


def test_summary_empty_mapping():
    assert summary({}) == {}
