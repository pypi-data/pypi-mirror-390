"""
Content validator for TCT protocol (draft-jurkovikj-collab-tunnel-01)

This validator checks TCT compliance through parity validation:
Sitemap etag == M-URL ETag == JSON payload hash

Per draft-01, only Method A is allowed:
- Method A: Canonical JSON Strong-Byte (hash of canonical JSON, per Section 6.2)

This produces valid strong ETags per RFC 9110 with deterministic JSON.
"""

import hashlib
import html
import re
import unicodedata
from typing import Dict, Any, List, Optional


class ContentValidator:
    """
    Validates TCT protocol compliance and content integrity.
    Default compliance uses parity-only checks; normalization is for diagnostics.
    """

    @staticmethod
    def validate_etag(etag: str, content: str) -> bool:
        """
        Diagnostic validation by recomputing hash from content text.
        Not used for compliance. Prefer validate_parity for compliance checks.

        Args:
            etag: ETag header value (e.g., "sha256-abc123..." or W/"sha256-abc123...")
            content: Content text to hash for diagnostics

        Returns:
            True if recomputed hash matches ETag
        """
        etag_clean = ContentValidator.clean_etag(etag)
        etag_hex = etag_clean.replace('sha256-', '')
        normalized = ContentValidator.normalize_minimal(content)
        computed_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        return etag_hex == computed_hash

    @staticmethod
    def clean_etag(etag: str) -> str:
        """Return ETag's hash as 'sha256-<64hex>' (strip W/ and quotes)."""
        e = etag.strip()
        if e.startswith('W/'):
            e = e[2:]
        e = e.strip('"')
        if len(e) == 64 and all(c in '0123456789abcdef' for c in e.lower()):
            return f'sha256-{e}'
        return e

    @staticmethod
    def validate_parity(sitemap_etag: str, response_etag: str, payload_hash: str) -> bool:
        """
        Compliance check: sitemap etag == HTTP ETag == payload.hash
        Per draft-01 Section 7.3
        """
        s = sitemap_etag.strip().strip('"')
        if len(s) == 64 and all(c in '0123456789abcdef' for c in s.lower()):
            s = f'sha256-{s}'
        e = ContentValidator.clean_etag(response_etag)
        p = payload_hash.strip().strip('"')
        if len(p) == 64 and all(c in '0123456789abcdef' for c in p.lower()):
            p = f'sha256-{p}'
        return s == e == p

    @staticmethod
    def normalize_minimal(text: str) -> str:
        """
        Normalize plain-text content following TCT spec (diagnostics only).

        6-step normalization pipeline:
        1. Decode HTML entities (&amp; → &, &#x2014; → —)
        2. Apply Unicode NFKC normalization
        3. Apply Unicode case folding (locale-independent lowercase)
        4. Remove control characters (Unicode category Cc), except TAB, LF, CR
        5. Collapse ASCII whitespace (SPACE, TAB, LF, CR) to single space
        6. Trim leading/trailing whitespace

        Args:
            text: Plain-text content string (no HTML markup)

        Returns:
            Normalized text ready for SHA-256 hashing
        """
        text = html.unescape(text)
        text = unicodedata.normalize('NFKC', text)
        text = text.casefold()
        preserved_cc = {chr(9), chr(10), chr(13)}  # TAB, LF, CR
        text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Cc' or ch in preserved_cc)
        text = re.sub(r'[ \t\n\r]+', ' ', text)
        return text.strip()


    @staticmethod
    def check_headers(headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Check TCT protocol compliance of HTTP headers.

        Args:
            headers: Dictionary of HTTP headers

        Returns:
            Dictionary with compliance check results
        """
        results = {
            'compliant': True,
            'checks': {},
            'errors': [],
            'warnings': []
        }

        # Check Content-Type
        content_type = headers.get('content-type', '').lower()
        results['checks']['json_content_type'] = 'application/json' in content_type

        if not results['checks']['json_content_type']:
            results['errors'].append("Content-Type should be application/json")
            results['compliant'] = False

        # Check ETag
        etag = headers.get('etag', '')
        results['checks']['etag_present'] = bool(etag)
        results['checks']['etag_format'] = False
        results['checks']['etag_weak'] = False

        if etag:
            # Per draft-01 Section 6.2: ETags MUST be strong (no W/ prefix)
            if etag.startswith('W/'):
                results['checks']['etag_weak'] = True
                results['errors'].append(
                    'Weak ETag not allowed in draft-01. '
                    'M-URLs MUST use strong ETags per Section 6.2.'
                )
                results['compliant'] = False
                etag_clean = etag[2:]
            else:
                etag_clean = etag

            results['checks']['etag_format'] = (
                etag_clean.startswith('"sha256-') or
                etag_clean.startswith('sha256-')
            )
            if not results['checks']['etag_format']:
                results['errors'].append("ETag must be 'sha256-<64hex>' format")
                results['compliant'] = False
        else:
            results['errors'].append("ETag header missing")
            results['compliant'] = False

        # Check Link canonical
        link = headers.get('link', '')
        results['checks']['canonical_link'] = 'rel="canonical"' in link.lower()

        if not results['checks']['canonical_link']:
            results['errors'].append("Link header missing rel='canonical'")
            results['compliant'] = False

        # Check Cache-Control
        cache_control = headers.get('cache-control', '').lower()
        results['checks']['must_revalidate'] = 'must-revalidate' in cache_control
        results['checks']['stale_while_revalidate'] = 'stale-while-revalidate' in cache_control

        if not results['checks']['must_revalidate']:
            results['errors'].append("Cache-Control should include must-revalidate")

        # Check Vary (should be Accept-Encoding, not Accept)
        vary = headers.get('vary', '').lower()
        results['checks']['vary_accept_encoding'] = 'accept-encoding' in vary

        if not results['checks']['vary_accept_encoding']:
            results['errors'].append("Vary header should include Accept-Encoding")

        return results

    @staticmethod
    def validate_sitemap_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single sitemap item structure per draft-01 Section 7.1

        Args:
            item: Sitemap item dictionary

        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': []
        }

        # Check required fields per draft-01 Section 7.1
        required_fields = ['cUrl', 'mUrl', 'etag']
        for field in required_fields:
            if field not in item:
                results['errors'].append(f"Missing required field: {field}")
                results['valid'] = False

        # Check URL format
        if 'cUrl' in item and not item['cUrl'].startswith('http'):
            results['errors'].append("cUrl must be absolute URL")
            results['valid'] = False

        if 'mUrl' in item and not item['mUrl'].startswith('http'):
            results['errors'].append("mUrl must be absolute URL")
            results['valid'] = False

        # Check etag format (must be sha256-<64hex>, no quotes)
        if 'etag' in item:
            etag_val = item['etag']
            if not (etag_val.startswith('sha256-') and len(etag_val) == 71):
                results['errors'].append("etag must be 'sha256-<64hex>' format (no quotes)")
                results['valid'] = False

        # Check modified date format (optional field)
        if 'modified' in item:
            modified = item['modified']
            if not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', modified):
                results['errors'].append("modified must be ISO 8601 format")
                results['valid'] = False

        return results

    @staticmethod
    def check_head_get_parity(get_headers: Dict[str, str], head_headers: Dict[str, str]) -> Dict[str, Any]:
        """Verify HEAD returns the same key headers as GET (no body expected)."""
        keys = ['content-type', 'etag', 'link', 'cache-control', 'vary']
        out = {'parity': True, 'mismatches': []}
        gl = {k.lower(): v for k, v in get_headers.items()}
        hl = {k.lower(): v for k, v in head_headers.items()}
        for k in keys:
            if gl.get(k, '').strip() != hl.get(k, '').strip():
                out['parity'] = False
                out['mismatches'].append(k)
        return out
