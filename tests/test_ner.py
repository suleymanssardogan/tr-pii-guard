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


def test_find_names_default_min_score_filters_email_fragment():
    """The known "email local-part misread as a name" false positive
    (e.g. "yilmaz" from ahmet.yilmaz@...) scores well below the 0.8
    default, so find_names() alone -- not just redact()'s overlap
    resolution -- should no longer surface it."""
    pytest.importorskip("transformers")

    from tr_pii_guard.ner import find_names

    results = find_names("E-posta adresim ahmet.yilmaz@example.com, yazabilirsiniz.")
    assert results == []


def test_find_names_min_score_is_configurable():
    pytest.importorskip("transformers")

    from tr_pii_guard.ner import find_names

    text = "E-posta adresim ahmet.yilmaz@example.com, yazabilirsiniz."
    strict = find_names(text, min_score=0.8)
    loose = find_names(text, min_score=0.0)
    assert len(loose) >= len(strict)


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
