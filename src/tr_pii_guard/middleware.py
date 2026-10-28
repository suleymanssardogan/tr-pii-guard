"""Generic wrapper: redact PII before an LLM call, restore it after.

Takes a plain callable so no LLM SDK (openai, anthropic, ...) is imported
or required here.
"""

from .redactor import redact, restore, restore_stream


def protect(llm_call, prompt: str, use_ner: bool = False, types=None, strict: bool = True, **kwargs) -> str:
    """Redact PII in `prompt`, call `llm_call(masked_prompt, **kwargs)`, then
    restore the original PII inside whatever text it returns.

    `llm_call` is any text-in/text-out callable, e.g.:

        protect(lambda p: openai_client.responses.create(input=p).output_text, prompt)
    """
    masked_prompt, mapping = redact(prompt, use_ner=use_ner, types=types, strict=strict)
    response_text = llm_call(masked_prompt, **kwargs)
    return restore(response_text, mapping)


def protect_stream(llm_call, prompt: str, use_ner: bool = False, types=None, strict: bool = True, **kwargs):
    """Like `protect`, but for a streaming LLM call: `llm_call` must return an
    iterable of text chunks (e.g. an OpenAI/Anthropic streaming response).
    Yields restored chunks as they arrive, buffering only as much as needed
    so a placeholder split across chunk boundaries still restores correctly.

        for piece in protect_stream(lambda p: client.stream(p), prompt):
            print(piece, end="", flush=True)
    """
    masked_prompt, mapping = redact(prompt, use_ner=use_ner, types=types, strict=strict)
    chunks = llm_call(masked_prompt, **kwargs)
    yield from restore_stream(chunks, mapping)
