"""PII detection and redaction."""

import re

# PII detection patterns
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
API_KEY_PATTERN = re.compile(
    r"\b(sk-[a-zA-Z0-9]{20,}|[a-zA-Z0-9]{32,})\b"
)


def detect_pii(text: str) -> list[str]:
    """
    Detect PII in text.

    Args:
        text: Input text to scan for PII

    Returns:
        List of detected PII types
    """
    detected: list[str] = []

    if EMAIL_PATTERN.search(text):
        detected.append("email")

    if PHONE_PATTERN.search(text):
        detected.append("phone")

    if SSN_PATTERN.search(text):
        detected.append("ssn")

    if CREDIT_CARD_PATTERN.search(text):
        detected.append("credit_card")

    if API_KEY_PATTERN.search(text):
        detected.append("api_key")

    return detected


def redact_pii(text: str) -> tuple[str, list[str]]:
    """
    Redact PII in text.

    Args:
        text: Input text to redact

    Returns:
        Tuple of (redacted_text, detected_pii_types)
    """
    detected_types: list[str] = []
    redacted = text

    # Email
    if EMAIL_PATTERN.search(redacted):
        detected_types.append("email")
        redacted = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", redacted)

    # Phone
    if PHONE_PATTERN.search(redacted):
        detected_types.append("phone")
        redacted = PHONE_PATTERN.sub("[PHONE_REDACTED]", redacted)

    # SSN
    if SSN_PATTERN.search(redacted):
        detected_types.append("ssn")
        redacted = SSN_PATTERN.sub("[SSN_REDACTED]", redacted)

    # Credit card
    if CREDIT_CARD_PATTERN.search(redacted):
        detected_types.append("credit_card")
        redacted = CREDIT_CARD_PATTERN.sub("[CC_REDACTED]", redacted)

    # API key
    if API_KEY_PATTERN.search(redacted):
        detected_types.append("api_key")
        redacted = API_KEY_PATTERN.sub("[API_KEY_REDACTED]", redacted)

    return redacted, detected_types

