from tr_pii_guard import protect

VALID_TC_NO = "10000000146"


def test_protect_masks_before_call_and_restores_after():
    seen_prompts = []

    def fake_llm(prompt):
        seen_prompts.append(prompt)
        return f"Received: {prompt}"

    original_prompt = f"Müşteri TC no {VALID_TC_NO} için işlem yap."
    result = protect(fake_llm, original_prompt)

    assert VALID_TC_NO not in seen_prompts[0]
    assert VALID_TC_NO in result
    assert result == f"Received: {original_prompt}"
