from tr_pii_guard.detectors import find_iban, find_phone, find_tc_no

VALID_TC_NO = "10000000146"  # well-known checksum-valid test number, not a real person
VALID_IBAN = "TR33 0006 1005 1978 6457 8413 26"


def test_find_tc_no_valid():
    text = f"Müşteri TC no: {VALID_TC_NO}."
    matches = find_tc_no(text)
    assert [m.group() for m in matches] == [VALID_TC_NO]


def test_find_tc_no_rejects_bad_checksum():
    text = "Rastgele sayı 12345678901 burada."
    assert find_tc_no(text) == []


def test_find_phone_variants():
    samples = [
        "0532 123 45 67",
        "+90 532 123 45 67",
        "05321234567",
        "0212 123 45 67",
    ]
    for s in samples:
        assert find_phone(s), f"should match: {s}"


def test_find_phone_parens_around_leading_zero_fully_consumed():
    # (0532)1234567 - the "(" must not leak into the surrounding text
    text = "arayın: (0532)1234567 lütfen"
    matches = find_phone(text)
    assert [m.group() for m in matches] == ["(0532)1234567"]


def test_find_phone_bare_number_does_not_eat_preceding_space():
    text = "numarası da 5321234567 diyor"
    matches = find_phone(text)
    assert [m.group() for m in matches] == ["5321234567"]


def test_find_iban_valid():
    text = f"IBAN: {VALID_IBAN}"
    matches = find_iban(text)
    assert len(matches) == 1


def test_find_iban_rejects_bad_checksum():
    text = "IBAN: TR33 0006 1005 1978 6457 8413 27"  # last digit tampered
    assert find_iban(text) == []
