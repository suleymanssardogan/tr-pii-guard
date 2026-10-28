from tr_pii_guard import breach_report

VALID_TC_NO = "10000000146"
VALID_IBAN = "TR33 0006 1005 1978 6457 8413 26"


def test_tc_no_with_contact_info_is_high_risk():
    text = f"TC no {VALID_TC_NO}, telefon 0532 123 45 67."
    report = breach_report(text)

    assert report["risk_level"] == "yüksek"
    assert report["counts"] == {"TC_NO": 1, "TELEFON": 1}
    assert VALID_TC_NO not in str(report)


def test_iban_alone_is_high_risk():
    report = breach_report(f"IBAN {VALID_IBAN}.")
    assert report["risk_level"] == "yüksek"


def test_tc_no_alone_is_medium_risk():
    report = breach_report(f"TC no {VALID_TC_NO}.")
    assert report["risk_level"] == "orta"


def test_only_contact_info_is_low_risk():
    report = breach_report("E-posta ahmet@example.com.")
    assert report["risk_level"] == "düşük"


def test_clean_text_has_no_risk():
    report = breach_report("Bugün hava çok güzel.")
    assert report["risk_level"] == "yok"
    assert report["counts"] == {}
