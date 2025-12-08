"""
Input sanitization utilities for prompt injection prevention.

Provides validation and sanitization functions to protect against malicious inputs.
"""

import re
from typing import Optional


def sanitize_query(query: str, max_length: int = 1000) -> str:
    """
    Sanitize user query to prevent prompt injection attacks.

    Args:
        query: Raw user query
        max_length: Maximum allowed query length

    Returns:
        Sanitized query

    Raises:
        ValueError: If query is empty or exceeds max length
    """
    # Remove leading/trailing whitespace
    query = query.strip()

    # Validate length
    if not query:
        raise ValueError("Query cannot be empty")

    if len(query) > max_length:
        raise ValueError(f"Query exceeds maximum length of {max_length} characters")

    # Remove potential system-level commands
    malicious_patterns = [
        r"system\s*:",  # System prompts
        r"assistant\s*:",  # Role manipulation
        r"user\s*:",  # Role manipulation
        r"<\|.*?\|>",  # Special tokens
        r"\[INST\]",  # Instruction markers
        r"\[/INST\]",  # Instruction markers
        r"###\s*Instruction",  # Instruction headers
        r"###\s*System",  # System headers
    ]

    for pattern in malicious_patterns:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE)

    # Limit consecutive newlines
    query = re.sub(r"\n{3,}", "\n\n", query)

    # Remove excessive whitespace
    query = re.sub(r"\s+", " ", query).strip()

    return query


def sanitize_selected_text(text: Optional[str], min_length: int = 1, max_length: int = 1000) -> Optional[str]:
    """
    Sanitize selected text from page.

    Args:
        text: Selected text from page
        min_length: Minimum allowed text length
        max_length: Maximum allowed text length

    Returns:
        Sanitized text or None if invalid
    """
    if text is None:
        return None

    text = text.strip()

    # Validate length
    if len(text) < min_length or len(text) > max_length:
        return None

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format (UUID).

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(uuid_pattern, session_id, re.IGNORECASE))


def detect_prompt_injection(text: str) -> bool:
    """
    Detect potential prompt injection attempts.

    Args:
        text: Text to analyze

    Returns:
        True if potential injection detected, False otherwise
    """
    injection_indicators = [
        r"ignore\s+(previous|above|all)\s+(instructions|prompts?)",
        r"disregard\s+.*?(instructions|rules)",
        r"new\s+instructions?\s*:",
        r"system\s+override",
        r"admin\s+mode",
        r"developer\s+mode",
        r"jailbreak",
        r"you\s+are\s+now",
        r"act\s+as\s+(if|though)",
    ]

    for pattern in injection_indicators:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False
