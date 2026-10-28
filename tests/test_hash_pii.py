from tr_pii_guard import hash_pii

VALID_TC_NO = "10000000146"


def test_hash_pii_is_irreversible_and_deterministic_per_salt():
    text = f"TC no {VALID_TC_NO}."

    masked_a = hash_pii(text, salt="tuz1")
    masked_b = hash_pii(text, salt="tuz1")
    masked_c = hash_pii(text, salt="farkli-tuz")

    assert VALID_TC_NO not in masked_a
    assert masked_a == masked_b  # same input + salt -> same hash
    assert masked_a != masked_c  # different salt -> different hash


def test_hash_pii_leaves_clean_text_untouched():
    text = "Bugün hava güzel."
    assert hash_pii(text) == text
