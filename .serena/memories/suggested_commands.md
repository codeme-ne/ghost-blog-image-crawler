# Suggested Commands

## Setup Commands

### Initial Setup
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file with API key
echo "FIRECRAWL_API_KEY=fc-your-key-here" > .env
```

## Development Commands

### Running the Crawler

#### Dry Run (Recommended First)
```bash
# Show what would be downloaded without downloading
python crawl_images.py --limit 10 --dry-run
```

#### Test Download
```bash
# Download from 10 pages for testing
python crawl_images.py --limit 10
```

#### Production Run (WITH CACHE PROTECTION)
```bash
# Download all media with cache protection
python crawl_images.py --limit 1000 --save-cache

# If download crashes, resume from cache without re-crawling
python crawl_images.py --use-cache
```

#### Using Shell Script (with venv)
```bash
# Automatically uses .venv/bin/python
./run.sh --limit 10 --dry-run
./run.sh --limit 1000 --save-cache
./run.sh --use-cache
```

#### All Options
```bash
python crawl_images.py --help

# Options:
#   --url URL             Blog URL (default: https://www.produktiv.me)
#   --limit N             Max pages to crawl (default: 100)
#   --dry-run             Only show URLs, don't download
#   --output-dir PATH     Output directory (default: ./images)
#   --cache-file PATH     Cache file path (default: ./crawl_cache.json)
#   --save-cache          Save crawl results to cache after crawling
#   --use-cache           Load from cache instead of crawling
```

### Custom URL
```bash
# Crawl different Ghost blog
python crawl_images.py --url https://other-blog.com --limit 50 --save-cache
```

## File Management

### View Downloaded Media
```bash
# List downloaded media by article
ls -R images/

# Count downloaded files
find images/ -type f | wc -l

# Check disk usage
du -sh images/
```

### Clean Up
```bash
# Remove all downloaded media
rm -rf images/

# Remove cache file
rm -f crawl_cache.json

# Remove virtual environment
rm -rf .venv/
```

## Git Commands
```bash
# Status
git status

# Add changes (note: .env, images/, and crawl_cache.json are gitignored)
git add .

# Commit
git commit -m "description"

# Push
git push
```

## System Information
Platform: Linux
Python: 3.8+

## No Testing/Linting Commands
This project doesn't have test suites, linting, or formatting tools configured.
It's a simple utility script for one-time use.