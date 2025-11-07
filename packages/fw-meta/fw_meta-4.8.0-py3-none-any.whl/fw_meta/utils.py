"""Utility functions for fw-meta."""

import re
import string


def sanitize_label(value: str) -> str:
    """Sanitize and truncate labels for filesystem dir/filename compatibility."""
    # replace '*' with 'star' (to retain eg. DICOM MR T2* domain context)
    value = re.sub(r"\*", r"star", value)
    # replace any occurrences of (one or more) invalid chars w/ an underscore
    unprintable = [chr(c) for c in range(128) if chr(c) not in string.printable]
    invalid_chars = "*/:<>?\\|\t\n\r\x0b\x0c" + "".join(unprintable)
    value = re.sub(rf"[{re.escape(invalid_chars):s}]+", "_", value)
    # finally, truncate to 255 chars and return
    return value[:255]
