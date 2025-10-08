# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Utility script to crawl and download all images and videos from Ghost blogs before migrating from Ghost(Pro) to self-hosting. Organizes media by article slug for seamless migration to any platform.

## Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running the script
```bash
# CRAWL MODE (follows links, may hit unwanted pages)
python crawl_images.py --url https://example.com --limit 100 --dry-run

# SITEMAP MODE (precise, avoids tag pages)
python crawl_images.py --sitemap https://example.com/sitemap-posts.xml \
                       --sitemap https://example.com/sitemap-pages.xml

# Production (with cache)
./run.sh --sitemap URL1 --sitemap URL2 --save-cache

# Resume from cache
python crawl_images.py --use-cache

# All options
python crawl_images.py --help
```

### Using the helper script
```bash
./run.sh  # Activates venv and runs script
```

## Architecture

### Single-File Utility
This is a simple utility script (`crawl_images.py`) with no complex architecture. All logic is in one file following OpenBSD-style simplicity.

### Core Flow

**Crawl Mode** (follows links):
1. **Crawl** → Firecrawl API v2 crawls with real-time updates
2. **Cache** → Saves results to JSON (--save-cache)
3. **Extract** → BeautifulSoup finds images/videos
4. **Organize** → Groups by article slug
5. **Download** → Parallel download (10 workers)
6. **Resume** → Skips existing files

**Sitemap Mode** (precise, recommended):
1. **Parse** → Extracts URLs from XML sitemaps
2. **Scrape** → Parallel scraping via Firecrawl (10 workers)
3. **Extract** → BeautifulSoup finds images/videos
4. **Organize** → Groups by article slug
5. **Download** → Parallel download (10 workers)
6. **Resume** → Skips existing files

### Slug-Based Organization
Media is organized by **article slug** (not date):
```
images/
├── artikel-slug-1/          # Article slug from URL
├── _homepage/               # Special: homepage media
└── _shared/                 # Special: media appearing on multiple pages
```

This structure enables direct migration to new platform - each folder maps to one article.

### Key Design Patterns

**Dual Mode Operation**: 
- Crawl mode: Follows links (may hit unwanted pages like `/tag/*`)
- Sitemap mode: XML-based URL list (precise, no waste)

**Sitemap Parsing**: Fetches XML sitemaps, extracts `<loc>` URLs, deduplicates. Enables exact page count and credit estimation before scraping.

**Parallel Scraping**: `ThreadPoolExecutor` (10 workers) scrapes URLs concurrently. Rate-limited by Firecrawl plan (e.g., 10 scrapes/min).

**Crawl Result Caching**: Saves results to JSON. Resume without re-crawling if crashed.

**Batch Progress Updates**: Shows progress every 10 files for visibility.

**Parallel Downloads**: 10 workers, individual failures don't stop batch.

**Streaming Downloads**: Large videos streamed in 8KB chunks for memory efficiency.

**Resume Capability**: Skips existing files on restart.

**Shared Media Detection**: Multi-page media → `_shared/` folder.

**Video Thumbnail Extraction**: Parses `style` attributes for video posters

## Code Style

- **Max 20 lines per function** (strictly enforced)
- **OpenBSD-style**: Minimal, clear, secure
- **No type hints**: Simple utility doesn't need them
- **Constants**: UPPER_CASE at module level
- **Error handling**: Try-except around risky operations, logging with context
- **No linting/formatting tools**: Manual code review only

## Dependencies

- `firecrawl-py`: Firecrawl API v2 client (scrape/crawl methods)
- `beautifulsoup4`: HTML parsing + XML sitemap parsing
- `requests`: HTTP downloads with streaming
- `python-dotenv`: Environment variables

## Environment

- **API Key**: Stored in `.env` (gitignored, never committed)
- **Python**: 3.8+
- **Output**: `./images/` directory (gitignored, created at runtime)
- **Cache**: `./crawl_cache.json` (gitignored, optional, created with --save-cache)
- **Rate Limits**: Firecrawl plan-dependent (e.g., 10 scrapes/min on free tier)
- **Credits**: 1 credit per page (crawl or scrape, no difference)
