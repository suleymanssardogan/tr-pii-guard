from tr_pii_guard import protect_stream, redact
from tr_pii_guard.redactor import restore_stream

VALID_TC_NO = "10000000146"


def _char_by_char(text):
    yield from text


def test_restore_stream_rebuilds_text_split_character_by_character():
    text = f"Önce TC no {VALID_TC_NO} sonra metin, telefon 0532 123 45 67 de var."
    masked, mapping = redact(text)

    rebuilt = "".join(restore_stream(_char_by_char(masked), mapping))

    assert rebuilt == text


def test_restore_stream_with_no_pii_passes_through_untouched():
    chunks = ["Bugün ", "hava ", "güzel."]
    assert "".join(restore_stream(chunks, {})) == "Bugün hava güzel."


def test_restore_stream_never_overshoots_the_final_text():
    text = f"TC no {VALID_TC_NO} burada."
    masked, mapping = redact(text)

    combined_so_far = ""
    for piece in restore_stream(_char_by_char(masked), mapping):
        combined_so_far += piece
        # Every intermediate state must be a correct prefix of the final
        # text -- streaming never emits a wrong guess it has to "fix" later.
        assert text.startswith(combined_so_far)
    assert combined_so_far == text


def test_protect_stream_restores_across_chunk_boundaries():
    original_prompt = f"Müşterinin TC no {VALID_TC_NO}, işlemi yapar mısın?"

    def fake_streaming_llm(masked_prompt):
        reply = f"Tabii, {masked_prompt} için işlem yapıldı."
        yield from _char_by_char(reply)

    pieces = list(protect_stream(fake_streaming_llm, original_prompt))
    result = "".join(pieces)

    assert VALID_TC_NO in result
    assert "[TC_NO_1]" not in result
