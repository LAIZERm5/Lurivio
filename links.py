"""URL extraction without guessing OCR substitutions."""
import re
from urllib.parse import urlsplit

_LABEL = r"[a-z0-9\u0400-\u04ff](?:[a-z0-9\u0400-\u04ff-]{0,61}[a-z0-9\u0400-\u04ff])?"
_URL = re.compile(
    rf'(?<![\w@])(?:(?:https?://|www\.)[^\s<>"«»]+|'
    rf'(?:{_LABEL}\.)+(?:[a-z]{{2,63}}|рф)(?:[/:?#][^\s<>"«»]*)?)',
    re.IGNORECASE,
)

def valid_url(value: str) -> bool:
    try:
        p = urlsplit(value)
        if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
            return False
        # Accessing port also validates the numeric port range.
        _ = p.port
        return not any(c.isspace() or ord(c) < 32 for c in value)
    except (ValueError, UnicodeError):
        return False


def extract_urls(text: str) -> list[str]:
    """Keep character case in paths; only add https:// to visible bare domains."""
    found = []
    for match in _URL.finditer(text):
        raw = match.group(0).rstrip('.,;:')
        for left, right in [('(', ')'), ('[', ']'), ('{', '}')]:
            while raw.endswith(right) and raw.count(right) > raw.count(left):
                raw = raw[:-1]
        value = raw if re.match(r'https?://', raw, re.I) else 'https://' + raw
        if valid_url(value) and value not in found:
            found.append(value)
    return found
