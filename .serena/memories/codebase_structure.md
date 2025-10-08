# Codebase Structure

## Directory Layout
```
ghost-produktiv-me-images/
├── .env                  # API key (gitignored, not committed)
├── .gitignore            # Git ignore rules
├── .venv/                # Python virtual environment (gitignored)
├── crawl_images.py       # Main script
├── crawl_cache.json      # Crawl results cache (gitignored, optional)
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── run.sh                # Helper script to run with venv
└── images/               # Downloaded media (gitignored, created at runtime)
    ├── artikel-slug-1/
    ├── artikel-slug-2/
    ├── _homepage/
    └── _shared/
```

## Main Script Structure (crawl_images.py)

### Constants (Lines 1-30)
- `DEFAULT_OUTPUT_DIR`: Default output directory
- `DEFAULT_LIMIT`: Default page limit
- `DEFAULT_CACHE_FILE`: Default cache file path (./crawl_cache.json)
- `PROGRESS_BATCH_SIZE`: Progress update frequency (10 files)
- `MAX_WORKERS`: Parallel download workers
- `IMAGE_PATH_PATTERN`: Ghost image URL pattern
- `VIDEO_PATH_PATTERN`: Ghost video URL pattern
- `VIDEO_EXTENSIONS`: Supported video formats

### Core Functions

1. **`load_api_key()`** - Loads Firecrawl API key from .env

2. **NEW: `_serialize_page(page)`** - Converts Firecrawl page object to JSON dict
   - Extracts HTML and metadata for serialization

3. **NEW: `_deserialize_page(page_dict)`** - Converts dict back to page object
   - Recreates Firecrawl-like object from JSON

4. **NEW: `save_crawl_cache(crawl_data, cache_file)`** - Saves crawl results to JSON
   - Serializes all pages and writes to file
   - Logs count of saved pages

5. **NEW: `load_crawl_cache(cache_file)`** - Loads crawl results from JSON
   - Deserializes pages from file
   - Logs count and prints user message

6. **`crawl_website(url, limit)`** - Crawls website with Firecrawl API
   - Starts async crawl job
   - Polls for real-time status updates
   - Returns crawled page data

7. **`extract_slug_from_url(url)`** - Extracts article slug from URL
   - Handles homepage → `_homepage`
   - Handles single segment → slug
   - Handles multiple segments → last segment

8. **`extract_media_urls_with_slugs(crawl_data, base_url)`**
   - Parses HTML with BeautifulSoup
   - Extracts images from `<img>` tags
   - Extracts videos from `<video>` tags
   - Extracts video thumbnails from `style` attributes
   - Detects shared media (appears on multiple pages)
   - Returns list of (media_url, primary_slug) tuples

9. **`download_media_to_slug(url, slug, output_dir)`**
   - Downloads single media file
   - Creates slug-based directory
   - Skips existing files (resume capability)
   - Streams large files
   - Different timeouts for videos vs images

10. **MODIFIED: `_process_download_results(future_to_info, total_count)`**
    - Processes download futures
    - **NEW: Prints progress every 10 files**
    - Returns success/failure counts

11. **MODIFIED: `_execute_parallel_downloads(media_slug_mapping, output_dir)`**
    - Orchestrates parallel downloads
    - **NEW: Shows initial message with total count**
    - **NEW: Passes total_count to progress tracker**

12. **MODIFIED: `_setup_arg_parser()`**
    - Parses CLI arguments
    - **NEW: --cache-file** (default: ./crawl_cache.json)
    - **NEW: --save-cache** (save results after crawl)
    - **NEW: --use-cache** (load from cache, skip crawl)

13. **MODIFIED: `main()`** - Entry point
    - **NEW: Cache loading logic** (use-cache vs crawl)
    - **NEW: Cache saving logic** (save-cache)
    - Extracts media URLs
    - Orchestrates dry-run or downloads

## Key Design Patterns

### NEW: Crawl Result Caching
- Saves Firecrawl API results to JSON after crawling
- Allows resuming downloads without re-crawling
- Protects against crashes during long production runs
- Cache file gitignored (not committed)

### NEW: Batch Progress Updates
- Shows progress every 10 files during downloads
- Format: "✓ 10/150 files processed (10 downloaded, 0 failed)"
- Provides visibility during large download batches

### Slug-Based Organization
Media organized by article slug instead of date/time:
- Easier migration to new platform
- Clear article-to-media mapping
- Special folders: `_homepage`, `_shared`

### Parallel Downloads
- `ThreadPoolExecutor` with 10 workers
- `as_completed()` for result processing
- Individual failures don't stop batch

### Resume Capability
- Checks `os.path.exists()` before download
- Skips existing files
- Allows interrupted downloads to resume

### Streaming Downloads
- `requests.get(stream=True)`
- `iter_content(chunk_size=8192)`
- Memory-efficient for large videos