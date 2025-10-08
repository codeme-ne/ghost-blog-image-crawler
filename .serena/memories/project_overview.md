# Ghost Blog Media Crawler - Project Overview

## Purpose
This project is a utility script to crawl and download all images and videos from www.produktiv.me (a Ghost blog) before canceling Ghost.org Pro hosting. The goal is to prepare for self-hosting migration.

## Key Features
- Downloads images and videos from Ghost blog using Firecrawl API
- Organizes media by article slug (not by date) for easy migration
- Parallel downloads (10 concurrent workers)
- **NEW: Crawl result caching** - Saves crawl results to JSON for crash protection
- **NEW: Batch progress updates** - Shows progress every 10 files during downloads
- Resume capability (skips already downloaded files)
- Real-time crawl progress updates
- Streaming downloads for large video files
- Automatic thumbnail extraction from video elements
- Shared media detection (media appearing on multiple pages)

## Output Structure
Media files are organized by article slug:
```
images/
├── artikel-slug-1/
│   ├── header-image.jpg
│   └── video.mp4
├── _homepage/
│   └── logo.png
└── _shared/
    └── shared-media.png  # Media appearing on multiple pages
```

## Tech Stack
- **Language**: Python 3.8+
- **API**: Firecrawl API v2
- **Key Libraries**:
  - firecrawl-py (Firecrawl API client)
  - beautifulsoup4 (HTML parsing)
  - requests (HTTP downloads)
  - python-dotenv (environment variables)

## Project Type
Simple utility script - single file, no complex architecture, no tests/linting configured

## New Cache Protection Workflow
1. Production run: `./run.sh --limit 1000 --save-cache`
2. If crash during download: `./run.sh --use-cache` (skips re-crawling)