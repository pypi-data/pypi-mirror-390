# Collaboration Tunnel Protocol - Python Client

A Python library for efficiently crawling websites that implement the Collaboration Tunnel Protocol (TCT), achieving up to 90% bandwidth savings through sitemap-first discovery and conditional requests.

## Installation

```bash
pip install collab-tunnel
```

## Quick Start

```python
from collab_tunnel import CollabTunnelCrawler

# Initialize crawler
crawler = CollabTunnelCrawler(user_agent="MyBot/1.0")

# Fetch sitemap
sitemap = crawler.fetch_sitemap("https://example.com/llm-sitemap.json")

# Crawl items
for item in sitemap.items:
    if crawler.should_fetch(item):  # Zero-fetch optimization
        content = crawler.fetch_content(item['mUrl'], item['contentHash'])
        if content:
            print(f"Title: {content['title']}")
            print(f"Content: {content['content'][:200]}...")

# View stats
stats = crawler.get_stats()
print(f"Bandwidth saved: {stats['savings_percentage']}%")
print(f"Requests skipped: {stats['total_skips']}")
```

## Features

- ✅ **Sitemap-First Discovery**: Skip 90%+ of unchanged URLs
- ✅ **Conditional Requests**: 304 Not Modified support
- ✅ **ETag Validation**: Verify content integrity
- ✅ **Bandwidth Tracking**: Monitor savings vs traditional crawling
- ✅ **Handshake Verification**: Validate C-URL ↔ M-URL mapping

## Advanced Usage

### Crawl Entire Site

```python
from collab_tunnel import crawl_site

results = crawl_site(
    "https://example.com/llm-sitemap.json",
    limit=100,
    user_agent="MyBot/1.0"
)

for result in results:
    print(result['title'], result['canonical_url'])
```

### Filter by Date

```python
from datetime import datetime, timedelta
from collab_tunnel import CollabTunnelCrawler

crawler = CollabTunnelCrawler()
sitemap = crawler.fetch_sitemap("https://example.com/llm-sitemap.json")

# Get items modified in last 7 days
recent_items = sitemap.filter_by_date(
    datetime.now() - timedelta(days=7)
)

for item in recent_items:
    content = crawler.fetch_content(item['mUrl'])
    # Process recent content...
```

### Verify Protocol Compliance

```python
from collab_tunnel import ContentValidator

validator = ContentValidator()

# Check headers
headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'ETag': 'W/"sha256-abc123..."',
    'Link': '<https://example.com/post/>; rel="canonical"',
    'Cache-Control': 'max-age=0, must-revalidate, stale-while-revalidate=60, stale-if-error=86400',
    'Vary': 'Accept-Encoding'
}

results = validator.check_headers(headers)
if results['compliant']:
    print("✅ Protocol compliant!")
else:
    print("❌ Errors:", results['errors'])
```

### Validate Profile Field

```python
from collab_tunnel import CollabTunnelCrawler

crawler = CollabTunnelCrawler()

# Fetch M-URL content
content = crawler.fetch_content("https://example.com/post/llm/")

# Check profile field
profile = content.get('profile')
if profile == 'tct-1':
    print("✅ Recognized protocol version: tct-1")
elif profile:
    print(f"⚠️ Unknown protocol version: {profile} (forward compatibility)")
    # Future versions - client can decide how to handle
else:
    print("⚠️ No profile field (legacy or non-compliant endpoint)")

# Validate sitemap profile
sitemap = crawler.fetch_sitemap("https://example.com/llm-sitemap.json")
sitemap_profile = sitemap.data.get('profile')
if sitemap_profile == 'tct-1':
    print("✅ Sitemap protocol version: tct-1")
```

## Protocol Overview

The Collaboration Tunnel Protocol (TCT) enables efficient content delivery through:

1. **Bidirectional Handshake**
   - C-URL (HTML page) → M-URL (JSON endpoint) via `<link rel="alternate">`
   - M-URL → C-URL via `Link: <C-URL>; rel="canonical"` header

2. **Template-Invariant Fingerprinting**
   - Content normalized through 6-step pipeline: decode entities, NFKC, casefold, remove Cc (except TAB/LF/CR), collapse ASCII whitespace, trim; then SHA-256
   - Weak ETag format: `W/"sha256-..."`
   - Stable across theme changes

3. **Sitemap-First Verification**
   - JSON sitemap lists (cUrl, mUrl, contentHash)
   - Skip fetch if hash unchanged (90%+ skip rate)

4. **Conditional Request Discipline**
   - If-None-Match takes precedence
   - 304 Not Modified for unchanged content

## Response Format

### M-URL JSON Payload

```json
{
  "profile": "tct-1",
  "llm_url": "https://example.com/post/llm/",
  "canonical_url": "https://example.com/post/",
  "hash": "sha256-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "title": "Article Title",
  "content": "Article content...",
  "modified": "2025-10-23T18:00:00Z"
}
```

**Profile Field**: `"profile": "tct-1"` enables protocol versioning for future compatibility.

### HTTP Headers

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8
Link: <https://example.com/post/>; rel="canonical"
ETag: W/"sha256-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
Cache-Control: max-age=0, must-revalidate, stale-while-revalidate=60, stale-if-error=86400
Vary: Accept-Encoding
```

**Weak ETag Format**: `W/"sha256-..."` signals semantic (not byte-for-byte) equivalence, per RFC 9110 Section 8.8.1.

### Sitemap Format

```json
{
  "version": 1,
  "profile": "tct-1",
  "items": [
    {
      "cUrl": "https://example.com/post/",
      "mUrl": "https://example.com/post/llm/",
      "modified": "2025-10-23T18:00:00Z",
      "contentHash": "sha256-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

## API Reference

### CollabTunnelCrawler

**Methods:**

- `fetch_sitemap(sitemap_url)` - Fetch and parse sitemap
- `should_fetch(item)` - Check if item needs fetching (zero-fetch logic)
- `fetch_content(m_url, expected_hash)` - Fetch M-URL with conditional request
- `verify_handshake(c_url, m_url)` - Verify bidirectional handshake
- `get_stats()` - Get bandwidth savings statistics

### SitemapParser

**Properties:**

- `items` - List of sitemap items
- `version` - Sitemap version
- `count` - Total number of items

**Methods:**

- `filter_by_date(since)` - Filter items by modification date
- `find_by_canonical(c_url)` - Find item by canonical URL
- `get_stats()` - Get sitemap statistics

### ContentValidator

**Static Methods:**

- `validate_parity(sitemap_hash, etag, payload_hash)` - Compliance: parity-only check
- `validate_etag(etag, content)` - Diagnostic: recompute hash from content
- `normalize_minimal(text)` - Normalization for diagnostics only (6-step TCT spec algorithm)
- `check_headers(headers)` - Check protocol compliance
- `check_head_get_parity(get_headers, head_headers)` - Ensure HEAD mirrors GET headers
- `validate_sitemap_item(item)` - Validate sitemap item structure

## License

MIT License - See LICENSE file for details

## Links

- **Website**: https://llmpages.org
- **GitHub**: https://github.com/antunjurkovic-collab/collab-tunnel-python
- **PyPI**: https://pypi.org/project/collab-tunnel/
- **Documentation**: https://llmpages.org/docs/python/
- **Patent**: US 63/895,763 (Provisional, filed October 2025)

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

- **Issues**: https://github.com/antunjurkovic-collab/collab-tunnel-python/issues
- **Email**: antunjurkovic@gmail.com
