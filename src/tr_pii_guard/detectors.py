"""Regex-based detectors for Turkish PII: TC kimlik no, phone numbers, IBAN."""

import re

TC_NO_PATTERN = re.compile(r"(?<!\d)\d{11}(?!\d)")

# shortcut: fixed area-code range [2-5]xx, no real operator/area-code table;
# widen if a valid number gets missed in practice.
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+90[ .-]?|0090[ .-]?)?0?[ .-]?\(?[2-5]\d{2}\)?"
    r"[ .-]?\d{3}[ .-]?\d{2}[ .-]?\d{2}(?!\d)"
)

IBAN_PATTERN = re.compile(r"TR\d{2}(?:[ ]?\d{4}){5}[ ]?\d{2}\b", re.IGNORECASE)

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


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


def find_tc_no(text: str) -> list[re.Match]:
    """Find valid (checksum-passing) TC kimlik no occurrences in text."""
    return [m for m in TC_NO_PATTERN.finditer(text) if _is_valid_tc_no(m.group())]


def find_phone(text: str) -> list[re.Match]:
    """Find Turkish phone number occurrences in text."""
    return list(PHONE_PATTERN.finditer(text))


def find_iban(text: str) -> list[re.Match]:
    """Find valid (checksum-passing) Turkish IBAN occurrences in text."""
    return [m for m in IBAN_PATTERN.finditer(text) if _is_valid_iban(m.group())]


def find_email(text: str) -> list[re.Match]:
    """Find email address occurrences in text."""
    return list(EMAIL_PATTERN.finditer(text))
