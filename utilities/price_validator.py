"""
Small helper to validate that a captured price looks reasonable.

The assignment asks us to print the device price — this makes sure we are not
accidentally printing empty text or unrelated page content.
"""

import re

# Matches common Amazon price formats, e.g. $799.00 or INR 56,104.14
PRICE_PATTERN = re.compile(r"(?:[\$₹€£]\s*)?[\d,]+(?:\.\d{2})?")


def is_valid_price(price: str) -> bool:
    """Return True when the string contains a numeric price value."""
    if not price or not price.strip():
        return False
    return PRICE_PATTERN.search(price.strip()) is not None
