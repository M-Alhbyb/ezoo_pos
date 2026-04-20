"""
Arabic PDF Support Module

Provides utilities for rendering Arabic text in PDFs with proper RTL direction.
Uses arabic_reshaper and python-bidi for correct Arabic text rendering.
"""

import arabic_reshaper
from bidi.algorithm import get_display


def reshape_arabic(text: str) -> str:
    """
    Reshape Arabic text for proper display in PDFs.

    Args:
        text: The Arabic text to reshape

    Returns:
        Reshaped Arabic text with connected letters
    """
    if not text:
        return text

    try:
        reshaper = arabic_reshaper.ReshaperConfiguration(
            arabic_reshaper.ENABLE_LIGATURES, arabic_reshaper.ENABLE_NO_LAMALEPH
        )
        return arabic_reshaper.reshape(text, reshaper.configuration)
    except Exception:
        return arabic_reshaper.reshape(text)


def apply_bidi(text: str) -> str:
    """
    Apply Bidirectional (BiDi) algorithm for RTL text.

    Args:
        text: The text to process

    Returns:
        Text with BiDi applied for correct RTL display
    """
    if not text:
        return text

    try:
        return get_display(text)
    except Exception:
        return text


def prepare_arabic_text(text: str) -> str:
    """
    Prepare Arabic text for PDF rendering.

    This function:
    1. Reshapes Arabic text to connect letters
    2. Applies BiDi algorithm for RTL direction

    Args:
        text: The Arabic text to prepare

    Returns:
        Prepared text ready for PDF rendering
    """
    if not text:
        return text

    try:
        # Check if text contains Arabic characters
        has_arabic = any("\u0600" <= char <= "\u06ff" for char in text)

        if has_arabic:
            # Reshape Arabic text
            reshaped = reshape_arabic(text)
            # Apply BiDi for RTL
            return apply_bidi(reshaped)

        return text
    except Exception:
        return text


def is_arabic_text(text: str) -> bool:
    """
    Check if text contains Arabic characters.

    Args:
        text: Text to check

    Returns:
        True if text contains Arabic characters
    """
    if not text:
        return False
    return any("\u0600" <= char <= "\u06ff" for char in text)


def prepare_cell_value(value, for_pdf: bool = True) -> str:
    """
    Prepare a cell value for display in PDF tables.

    Args:
        value: The value to prepare (can be str, number, Decimal, etc.)
        for_pdf: Whether to prepare for PDF (apply Arabic reshaping)

    Returns:
        Prepared string value
    """
    if value is None:
        return ""

    from decimal import Decimal

    # Convert to string
    if isinstance(value, Decimal):
        str_value = str(value)
    elif isinstance(value, (int, float)):
        str_value = f"{value:.2f}" if isinstance(value, float) else str(value)
    else:
        str_value = str(value)

    # Apply Arabic processing if needed
    if for_pdf and is_arabic_text(str_value):
        return prepare_arabic_text(str_value)

    return str_value
