from tr_pii_guard import redact, restore

VALID_TC_NO = "10000000146"  # checksum-valid test number, not a real person
VALID_IBAN = "TR33 0006 1005 1978 6457 8413 26"


def test_redact_masks_every_type():
    text = (
        f"TC no {VALID_TC_NO}, telefon 0532 123 45 67, "
        f"IBAN {VALID_IBAN}, e-posta test@example.com."
    )
    masked, _ = redact(text)

    assert VALID_TC_NO not in masked
    assert "0532 123 45 67" not in masked
    assert VALID_IBAN not in masked
    assert "test@example.com" not in masked


def test_redact_restore_roundtrip():
    text = f"Kart sahibi, IBAN {VALID_IBAN}, TC no {VALID_TC_NO}."
    masked, mapping = redact(text)
    assert restore(masked, mapping) == text


def test_redact_numbers_repeated_type():
    text = "Birinci telefon 0532 123 45 67, ikinci telefon 0212 123 45 67."
    masked, mapping = redact(text)
    assert "[TELEFON_1]" in masked and "[TELEFON_2]" in masked
    assert restore(masked, mapping) == text


def test_redact_leaves_clean_text_untouched():
    text = "Bugün hava çok güzel."
    masked, mapping = redact(text)
    assert masked == text
    assert mapping == {}


def test_redact_types_filter_restricts_detection():
    text = f"TC no {VALID_TC_NO}, telefon 0532 123 45 67."
    masked, mapping = redact(text, types=["TC_NO"])
    assert VALID_TC_NO not in masked
    assert "0532 123 45 67" in masked
    assert list(mapping.keys()) == ["[TC_NO_1]"]


def test_redact_strict_false_catches_bad_checksum():
    text = "Rastgele sayı 12345678901 burada."
    masked_strict, _ = redact(text)
    masked_loose, _ = redact(text, strict=False)
    assert "12345678901" in masked_strict  # bad checksum, ignored by default
    assert "12345678901" not in masked_loose  # strict=False catches it anyway
