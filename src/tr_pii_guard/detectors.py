"""Regex-based detectors for Turkish PII: TC kimlik no, phone numbers, IBAN."""

import re

TC_NO_PATTERN = re.compile(r"(?<!\d)\d{11}(?!\d)")

# shortcut: fixed area-code range [2-5]xx, no real operator/area-code table;
# widen if a valid number gets missed in practice.
# The "0" trunk prefix is one atomic optional group (with its own optional
# parens/separator) so a bare 10-digit number can't leak a leading space
# or stray "(" into the match when there's no "0" to anchor it.
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+90[ .-]?|0090[ .-]?)?(?:\(?0\)?[ .-]?)?"
    r"\(?[2-5]\d{2}\)?[ .-]?\d{3}[ .-]?\d{2}[ .-]?\d{2}(?!\d)"
)

IBAN_PATTERN = re.compile(r"TR\d{2}(?:[ ]?\d{4}){5}[ ]?\d{2}\b", re.IGNORECASE)

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Well-known, prefix-anchored API key/token formats. Unlike free-text PII,
# these have fixed, documented shapes, so false-positive risk stays low
# without a checksum. Azure is deliberately excluded -- its keys have no
# consistent prefix, so a safe pattern isn't possible.
API_KEY_PATTERN = re.compile(
    r"(?:"
    r"sk-ant-[A-Za-z0-9_-]{20,}"  # Anthropic
    r"|sk-proj-[A-Za-z0-9_-]{20,}"  # OpenAI (project key)
    r"|sk-[A-Za-z0-9]{20,}"  # OpenAI (legacy)
    r"|AKIA[0-9A-Z]{16}"  # AWS access key id
    r"|gh[pousr]_[A-Za-z0-9]{36,}"  # GitHub (personal/oauth/user/server/refresh)
    r"|AIza[0-9A-Za-z_-]{35}"  # Google API key
    r"|xox[baprs]-[0-9A-Za-z-]{10,}"  # Slack token
    r"|sk_(?:live|test)_[0-9a-zA-Z]{24,}"  # Stripe
    r"|npm_[A-Za-z0-9]{36}"  # npm token
    r"|pypi-[A-Za-z0-9_-]{50,}"  # PyPI token
    r"|AC[0-9a-fA-F]{32}"  # Twilio account SID
    r"|SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}"  # SendGrid
    r")"
)

# PEM-encoded private key/certificate blocks (SSH, TLS, RSA, ...). The
# backreference requires the END label to match the BEGIN label, so this
# only fires on a real, well-formed PEM block.
PEM_BLOCK_PATTERN = re.compile(r"-----BEGIN ([A-Z ]+)-----.*?-----END \1-----", re.DOTALL)


def _is_valid_tc_no(digits: str) -> bool:
    if len(digits) != 11 or not digits.isdigit() or digits[0] == "0":
        return False
    d = [int(c) for c in digits]
    odd_sum = d[0] + d[2] + d[4] + d[6] + d[8]
    even_sum = d[1] + d[3] + d[5] + d[7]
    d10 = (odd_sum * 7 - even_sum) % 10
    d11 = (odd_sum + even_sum + d10) % 10
    return d10 == d[9] and d11 == d[10]


def _is_valid_iban(iban: str) -> bool:
    iban = iban.replace(" ", "").upper()
    if not re.fullmatch(r"TR\d{24}", iban):
        return False
    rearranged = iban[4:] + iban[:4]
    numeric = "".join(str(int(ch, 36)) for ch in rearranged)
    return int(numeric) % 97 == 1


def find_tc_no(text: str, validate: bool = True) -> list[re.Match]:
    """Find TC kimlik no occurrences in text.

    validate=True (default) keeps only checksum-passing matches, cutting
    false positives. validate=False keeps every 11-digit candidate, trading
    precision for recall.
    """
    matches = TC_NO_PATTERN.finditer(text)
    if validate:
        return [m for m in matches if _is_valid_tc_no(m.group())]
    return list(matches)


def find_phone(text: str) -> list[re.Match]:
    """Find Turkish phone number occurrences in text."""
    return list(PHONE_PATTERN.finditer(text))


def find_iban(text: str, validate: bool = True) -> list[re.Match]:
    """Find Turkish IBAN occurrences in text.

    validate=True (default) keeps only checksum-passing matches; validate=False
    keeps every format-matching candidate.
    """
    matches = IBAN_PATTERN.finditer(text)
    if validate:
        return [m for m in matches if _is_valid_iban(m.group())]
    return list(matches)


def find_email(text: str) -> list[re.Match]:
    """Find email address occurrences in text."""
    return list(EMAIL_PATTERN.finditer(text))


def find_api_key(text: str) -> list[re.Match]:
    """Find common API key/token formats (OpenAI, Anthropic, AWS, GitHub,
    Google, Slack, Stripe, npm, PyPI, Twilio, SendGrid) and PEM-encoded
    private key/certificate blocks in text."""
    return list(API_KEY_PATTERN.finditer(text)) + list(PEM_BLOCK_PATTERN.finditer(text))
