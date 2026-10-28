import pytest


def test_redact_use_ner_without_extra_raises_helpful_error():
    try:
        import transformers  # noqa: F401
    except ImportError:
        pass
    else:
        pytest.skip("transformers is installed; nothing to assert here")

    from tr_pii_guard import redact

    with pytest.raises(ImportError, match="tr-pii-guard\\[ner\\]"):
        redact("Ahmet Yılmaz İstanbul'a gitti.", use_ner=True)


def test_find_names_detects_person():
    pytest.importorskip("transformers")

    from tr_pii_guard.ner import find_names

    results = find_names("Ahmet Yılmaz İstanbul'a gitti.")
    assert any(r.group() for r in results)


def test_redact_use_ner_does_not_leak_name_fragment_from_email():
    """Known limitation: find_names() alone can misread an email's
    local-part (e.g. "ahmet.yilmaz@...") as a person name. redact()'s
    overlap resolution must still pick the longer EPOSTA match and drop
    that fragment -- this is the guarantee that actually matters."""
    pytest.importorskip("transformers")

    from tr_pii_guard import redact

    masked, mapping = redact(
        "E-posta adresim ahmet.yilmaz@example.com, yazabilirsiniz.", use_ner=True
    )

    assert "[ISIM" not in masked
    assert mapping == {"[EPOSTA_1]": "ahmet.yilmaz@example.com"}
