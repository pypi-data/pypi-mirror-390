"""
Test vectors for content-string normalization and hashing (ASCII-safe).
Generates expected normalized text, sha256 hex, ETag, and contentHash.
"""

from typing import List, Dict
import hashlib
import html
import unicodedata
import re


def normalize_minimal(text: str) -> str:
    text = html.unescape(text)
    text = unicodedata.normalize('NFKC', text)
    text = text.casefold()
    preserved_cc = {chr(9), chr(10), chr(13)}  # TAB, LF, CR
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Cc' or ch in preserved_cc)
    text = re.sub(r'[ \t\n\r]+', ' ', text)
    return text.strip()


def compute(text: str) -> Dict[str, str]:
    norm = normalize_minimal(text)
    h = hashlib.sha256(norm.encode('utf-8')).hexdigest()
    return {
        'input': text,
        'normalized': norm,
        'sha256_hex': h,
        'contentHash': f'sha256-{h}',
        'etag': f'W/"sha256-{h}"',
    }


def demo() -> List[Dict[str, str]]:
    cases = [
        "Hello\tWorld\n",
        "Title\n\nBody text with    spaces",
        "A non-breaking B space &amp; HTML -- entity",
        "  Trim  both  ends  ",
        "Line 1\nLine 2\r\nLine 3\tEnd",
        "Hello\fWorld\fTest",  # Form Feed test (U+000C)
    ]
    return [compute(c) for c in cases]


if __name__ == '__main__':
    import json
    print(json.dumps(demo(), ensure_ascii=False, indent=2))

