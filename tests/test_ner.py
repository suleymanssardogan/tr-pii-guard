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
