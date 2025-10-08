# Implementation Plan: Ghost Content API Integration

## Problem Statement

Ziel: 225 Seiten von neurohackingly.com crawlen
Blocker: Nur 140 Firecrawl Credits übrig (225 benötigt)
Lösung: Ghost Content API (kostenlos, strukturiert, zuverlässig)

## Solution Overview

```
Current:  Firecrawl scrape() -> 1 Credit/Page -> 225 Credits needed
New:      Ghost Content API  -> 0 Credits    -> FREE + FASTER
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│ GHOST API MODE (NEW)                                    │
├─────────────────────────────────────────────────────────┤
│ 1. discover_ghost_api_key(base_url)                     │
│    └─> Extract API key from HTML                        │
│                                                          │
│ 2. fetch_all_ghost_posts(api_url, key)                  │
│    └─> GET /posts/?key=X&page=N (pagination)            │
│                                                          │
│ 3. extract_media_from_post_html(html, slug)             │
│    └─> BeautifulSoup: <img> + <video> URLs              │
│                                                          │
│ 4. [REUSE] download_media_to_slug()                     │
│    └─> Existing parallel download pipeline              │
└─────────────────────────────────────────────────────────┘
```

## Implementation Phases

### PHASE 1: Core Functions (3 new functions)

**1.1 discover_ghost_api_key(base_url)**
- Input: Base URL (e.g., https://neurohackingly.com)
- Process: Fetch homepage HTML, regex search for "ghost/api" pattern
- Output: (api_url, api_key) or (None, None)
- Max lines: 10

**1.2 fetch_all_ghost_posts(api_url, api_key)**
- Input: API URL + Content API Key
- Process:
  - GET /posts/?key=KEY&limit=15&page=1
  - Parse meta.pagination.total
  - Loop through all pages
- Output: List of post dicts [{slug, html, title}, ...]
- Max lines: 15

**1.3 extract_media_from_post_html(html_content, post_slug)**
- Input: Post HTML content + slug
- Process:
  - BeautifulSoup parse HTML
  - Find all <img> src attributes
  - Find all <video> src attributes
  - Convert relative URLs to absolute
  - Deduplicate
- Output: [(media_url, slug), ...]
- Max lines: 12

### PHASE 2: Integration (2 modified functions)

**2.1 _setup_arg_parser() modification**
```
Add arguments:
  --mode {ghost-api,firecrawl-sitemap,firecrawl-crawl}
         Default: ghost-api
  --ghost-api-key API_KEY
         Optional override for manual API key
```

**2.2 main() modification**
```
if args.mode == 'ghost-api':
    api_url, api_key = discover_ghost_api_key(args.url)
    posts = fetch_all_ghost_posts(api_url, api_key)
    media_urls = extract_media_from_all_posts(posts)
    [REUSE existing download pipeline]
else:
    [existing Firecrawl logic unchanged]
```

### PHASE 3: Error Handling & Robustness

**3.1 API Discovery Errors**
- ConnectionError -> "Cannot reach {url}"
- Timeout -> "Timeout after 10s"
- Pattern not found -> "No Ghost API found, use --ghost-api-key"

**3.2 Posts Fetching Errors**
- HTTP 403/401 -> "Invalid API key"
- HTTP 404 -> "API endpoint not found"
- HTTP 429 -> "Rate limited"
- Retry: 3 attempts, exponential backoff (1s, 2s, 4s)

**3.3 Media Extraction Edge Cases**
- Empty HTML -> Return empty list
- Relative URLs -> Convert to absolute (urllib.parse.urljoin)
- Duplicate media -> Deduplicate
- Invalid URLs -> Skip with warning log

### PHASE 4: Testing Strategy

**4.1 Unit Tests**
1. Test discover_ghost_api_key() against neurohackingly.com
2. Test fetch_all_ghost_posts() with limit=1 first
3. Test extract_media_from_post_html() with single post

**4.2 Integration Tests**
1. Dry-run: `python crawl_images.py --mode ghost-api --dry-run`
2. Small batch: Limit to 5 posts, verify folder structure
3. Full production: All 225 posts

**4.3 Validation Points**
- API key matches pattern [a-z0-9]{26}
- First post has 'html', 'slug', 'title' fields
- All URLs are absolute
- Slug-based folders created correctly

### PHASE 5: Documentation Updates

**5.1 CLAUDE.md**
```markdown
### Running the script
# GHOST API MODE (recommended for Ghost blogs)
python crawl_images.py --mode ghost-api --url https://neurohackingly.com

# With manual API key override
python crawl_images.py --mode ghost-api --ghost-api-key YOUR_KEY
```

**5.2 README.md (optional)**
- Add Ghost API mode to commands section
- Note: "Recommended for Ghost blogs (free, fast, reliable)"

## Code Changes Summary

```
Files Modified: 1 (crawl_images.py)
New Functions:  3 (~37 lines total)
Modified Fns:   2 (~25 lines total)
Total New Code: ~62 lines
Dependencies:   0 (reuses requests + BeautifulSoup)
```

## Execution Order

```
1. Implement discover_ghost_api_key()
2. Implement fetch_all_ghost_posts()
3. Implement extract_media_from_post_html()
4. Modify _setup_arg_parser()
5. Modify main() orchestration
   |
   v
6. Unit test each function
7. Integration test --dry-run
8. Small batch test (5 posts)
9. Full production (225 posts)
   |
   v
10. Update CLAUDE.md
11. Update README.md (optional)
```

## Success Metrics

- [ ] 225 Posts successfully fetched
- [ ] All media extracted (images + videos)
- [ ] Slug-based folder structure maintained
- [ ] 0 Firecrawl Credits consumed
- [ ] Resume capability works
- [ ] OpenBSD style maintained (max 20 lines/function)

## Risk Mitigation

**Fallback Chain:**
```
Ghost API FAILS
    |
    v
Jina Reader (10M free tokens)
    |
    v
Firecrawl extract (500k tokens)
    |
    v
Direct Scraping (last resort)
```

## Ready to Execute

- [x] All dependencies installed (requests, BeautifulSoup)
- [x] API key already identified
- [x] Clear implementation plan
- [x] Testing strategy defined
- [x] Rollback options available
