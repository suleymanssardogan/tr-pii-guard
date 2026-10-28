"""Generic wrapper: redact PII before an LLM call, restore it after.

Takes a plain callable so no LLM SDK (openai, anthropic, ...) is imported
or required here.
"""

from .redactor import redact, restore


def protect(llm_call, prompt: str, use_ner: bool = False, types=None, strict: bool = True, **kwargs) -> str:
    """Redact PII in `prompt`, call `llm_call(masked_prompt, **kwargs)`, then
    restore the original PII inside whatever text it returns.

    `llm_call` is any text-in/text-out callable, e.g.:

        protect(lambda p: openai_client.responses.create(input=p).output_text, prompt)
    """
    masked_prompt, mapping = redact(prompt, use_ner=use_ner, types=types, strict=strict)
    response_text = llm_call(masked_prompt, **kwargs)
    return restore(response_text, mapping)
