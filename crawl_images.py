#!/usr/bin/env python3
"""
Ghost Blog Image Crawler
Crawls www.produktiv.me and downloads all images using Firecrawl API.
"""

import os
import re
import json
import time
import logging
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Constants
DEFAULT_OUTPUT_DIR = "./images"
DEFAULT_LIMIT = 100
DEFAULT_CACHE_FILE = "./crawl_cache.json"
PROGRESS_BATCH_SIZE = 10
MAX_WORKERS = 10
IMAGE_PATH_PATTERN = "/content/images/"
VIDEO_PATH_PATTERN = "/content/media/"
VIDEO_EXTENSIONS = ('.mp4', '.webm', '.mov', '.avi')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def load_api_key():
    """Load Firecrawl API key from .env file."""
    load_dotenv()
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        raise ValueError(
            "FIRECRAWL_API_KEY not found. Please create .env file with your API key."
        )
    return api_key


def _serialize_page(page):
    """Convert Firecrawl page object to JSON-serializable dict."""
    page_dict = {'html': getattr(page, 'html', None) or getattr(page, 'markdown', '')}
    if hasattr(page, 'metadata'):
        page_dict['metadata'] = {
            'url': getattr(page.metadata, 'url', None),
            'source_url': getattr(page.metadata, 'source_url', None)
        }
    return page_dict


def _deserialize_page(page_dict):
    """Convert dict back to Firecrawl-like page object."""
    class PageObject:
        def __init__(self, data):
            self.html = data.get('html')
            if 'metadata' in data:
                self.metadata = type('obj', (object,), data['metadata'])()
    return PageObject(page_dict)


def save_crawl_cache(crawl_data, cache_file):
    """Save crawl results to JSON file."""
    serialized = [_serialize_page(page) for page in crawl_data]
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, indent=2)
    logging.info(f"Saved {len(crawl_data)} pages to {cache_file}")


def load_crawl_cache(cache_file):
    """Load crawl results from JSON file."""
    with open(cache_file, 'r', encoding='utf-8') as f:
        serialized = json.load(f)
    crawl_data = [_deserialize_page(page_dict) for page_dict in serialized]
    logging.info(f"Loaded {len(crawl_data)} pages from {cache_file}")
    print(f"📦 Loaded {len(crawl_data)} cached pages from {cache_file}\n")
    return crawl_data


def _print_crawl_progress(data, last_count):
    """Print newly crawled pages."""
    for i in range(last_count, len(data)):
        page = data[i]
        page_url = 'Unknown'
        if hasattr(page, 'metadata'):
            page_url = getattr(page.metadata, 'url', None) or getattr(page.metadata, 'source_url', 'Unknown')
        print(f"  ✓ [{i+1}] {page_url}")


def _poll_crawl_status(app, crawl_id):
    """Poll Firecrawl API for crawl status and display progress updates."""
    last_count = 0
    while True:
        status = app.get_crawl_status(crawl_id)
        current_count = status.completed if hasattr(status, 'completed') else 0
        if current_count > last_count:
            data = status.data if hasattr(status, 'data') else []
            _print_crawl_progress(data, last_count)
            last_count = len(data)
        if hasattr(status, 'status'):
            if status.status == 'completed':
                print(f"\n✅ Crawl completed!\n")
                return status.data if hasattr(status, 'data') else []
            elif status.status == 'failed':
                raise Exception("Crawl failed")
        time.sleep(2)


def get_urls_from_sitemaps(sitemap_urls):
    """Fetch and parse sitemaps to extract URLs."""
    all_urls = []
    for sitemap_url in sitemap_urls:
        logging.info(f"Fetching sitemap: {sitemap_url}")
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        all_urls.extend(urls)
        logging.info(f"  Found {len(urls)} URLs in {sitemap_url}")
    unique_urls = list(set(all_urls))
    logging.info(f"Total unique URLs: {len(unique_urls)}")
    return unique_urls


def scrape_pages(urls):
    """Scrape URLs in parallel using Firecrawl."""
    api_key = load_api_key()
    app = FirecrawlApp(api_key=api_key)
    results = []
    total = len(urls)
    print(f"\n📄 Scraping {total} pages...")

    def scrape_single(url):
        try:
            return app.scrape(url, formats=['html'])
        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scrape_single, url): url for url in urls}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                results.append(result)
            if i % PROGRESS_BATCH_SIZE == 0 or i == total:
                print(f"  ✓ {i}/{total} pages scraped")

    logging.info(f"Scraping completed. Success: {len(results)}/{total}")
    return results


def crawl_website(url, limit):
    """Crawl website with Firecrawl with real-time status updates."""
    api_key = load_api_key()
    app = FirecrawlApp(api_key=api_key)
    logging.info(f"Starting crawl of {url} with limit={limit}")
    print("\n🔍 Starting crawl (live updates)...")

    try:
        crawl_job = app.start_crawl(url, limit=limit, scrape_options={'formats': ['html']})
        print(f"  📋 Crawl job started: {crawl_job.id}\n")
        data = _poll_crawl_status(app, crawl_job.id)
        logging.info(f"Crawl completed. Found {len(data)} pages")
        return data
    except Exception as e:
        logging.error(f"Crawl failed: {e}")
        raise


def extract_slug_from_url(url):
    """Extract article slug from Ghost blog URL."""
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    
    # Homepage or root
    if not path_parts:
        return '_homepage'
    
    # Single path segment is likely an article slug
    # e.g., https://produktiv.me/artikel-name/
    if len(path_parts) == 1:
        return path_parts[0]
    
    # Multiple segments, use the last meaningful one
    # e.g., https://produktiv.me/category/artikel-name/
    return path_parts[-1]


def _extract_images_from_soup(soup, base_url):
    """Extract all image URLs from BeautifulSoup object."""
    images = []
    for img_tag in soup.find_all('img'):
        src = img_tag.get('src')
        if src:
            absolute_url = urljoin(base_url, src)
            if IMAGE_PATH_PATTERN in absolute_url:
                images.append(absolute_url)
    return images


def _extract_video_thumbnail(video_tag, base_url):
    """Extract thumbnail URL from video tag style attribute."""
    style = video_tag.get('style', '')
    if 'url(' in style:
        url_match = re.search(r"url\(['\"]?([^'\"]+)['\"]?\)", style)
        if url_match:
            thumb_url = url_match.group(1)
            absolute_thumb_url = urljoin(base_url, thumb_url)
            if IMAGE_PATH_PATTERN in absolute_thumb_url or VIDEO_PATH_PATTERN in absolute_thumb_url:
                return absolute_thumb_url
    return None


def _extract_videos_from_soup(soup, base_url):
    """Extract video URLs and thumbnails from BeautifulSoup object."""
    videos = []
    thumbnails = []
    
    for video_tag in soup.find_all('video'):
        src = video_tag.get('src')
        if src:
            absolute_url = urljoin(base_url, src)
            if VIDEO_PATH_PATTERN in absolute_url:
                videos.append(absolute_url)
                
                # Extract poster/thumbnail from style attribute
                thumb_url = _extract_video_thumbnail(video_tag, base_url)
                if thumb_url:
                    thumbnails.append(thumb_url)
    
    return videos, thumbnails


def _get_page_info(page):
    """Extract page URL and slug from Firecrawl page object."""
    html = getattr(page, 'html', None) or getattr(page, 'markdown', '')
    if not html:
        return None, None, None
    
    page_url = 'Unknown'
    if hasattr(page, 'metadata'):
        page_url = getattr(page.metadata, 'url', None) or getattr(page.metadata, 'source_url', 'Unknown')
    
    slug = extract_slug_from_url(page_url)
    return html, page_url, slug


def _extract_media_from_page(page, base_url):
    """Extract all media (images, videos, thumbnails) from a single page."""
    html, page_url, slug = _get_page_info(page)
    if html is None:
        return None, None, []
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract all media
    images = _extract_images_from_soup(soup, base_url)
    videos, thumbnails = _extract_videos_from_soup(soup, base_url)
    
    # Combine into (media_type, url) tuples
    page_media = [('image', url) for url in images]
    page_media.extend([('video', url) for url in videos])
    page_media.extend([('image', url) for url in thumbnails])
    
    return slug, page_url, page_media


def _print_page_media_summary(slug, page_url, media_list):
    """Print summary of media found on a page."""
    if media_list:
        print(f"  ✓ [{slug}] {page_url}")
        for media_type, media_url in media_list:
            media_filename = os.path.basename(urlparse(media_url).path)
            icon = "🎬" if media_type == 'video' else "→"
            print(f"    {icon} {media_filename}")
    else:
        print(f"  ✗ [{slug}] {page_url} (no media)")


def _track_media_to_slugs(all_page_data):
    """Build dictionary tracking which slugs contain each media URL."""
    media_to_slugs = {}
    for slug, page_media in all_page_data:
        for _, media_url in page_media:
            if media_url not in media_to_slugs:
                media_to_slugs[media_url] = set()
            media_to_slugs[media_url].add(slug)
    return media_to_slugs


def _assign_primary_slugs(media_to_slugs):
    """Assign primary slug to each media URL, using '_shared' for duplicates."""
    media_slug_mapping = []
    for media_url, slugs in media_to_slugs.items():
        if len(slugs) == 1:
            primary_slug = list(slugs)[0]
        else:
            primary_slug = '_shared'
            logging.info(f"Media {os.path.basename(urlparse(media_url).path)} appears on {len(slugs)} pages: {', '.join(sorted(slugs))}")
        media_slug_mapping.append((media_url, primary_slug))
    return media_slug_mapping


def _build_media_to_slug_mapping(all_page_data):
    """Build final media to slug mapping, detecting shared media."""
    media_to_slugs = _track_media_to_slugs(all_page_data)
    return _assign_primary_slugs(media_to_slugs)


def extract_media_urls_with_slugs(crawl_data, base_url):
    """Extract image and video URLs from crawled HTML and map them to article slugs."""
    print("🖼️  Extracting images and videos from pages:")
    
    all_page_data = []
    for page in crawl_data:
        slug, page_url, page_media = _extract_media_from_page(page, base_url)
        if slug is not None:
            all_page_data.append((slug, page_media))
            _print_page_media_summary(slug, page_url, page_media)
    
    print()
    
    media_slug_mapping = _build_media_to_slug_mapping(all_page_data)
    unique_slugs = len(set(slug for slug, _ in all_page_data))
    logging.info(f"Extracted {len(media_slug_mapping)} unique media URLs (images + videos) across {unique_slugs} articles")
    return media_slug_mapping


def _perform_file_download(url, filepath, timeout, headers):
    """Perform HTTP download and write to file with streaming."""
    with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def _download_with_retry(url, filepath, timeout, headers, slug, filename, max_retries=3):
    """Attempt download with retry logic on failure."""
    for attempt in range(max_retries):
        try:
            _perform_file_download(url, filepath, timeout, headers)
            media_type = "video" if any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS) else "image"
            logging.info(f"Downloaded {media_type}: [{slug}] {filename}")
            return filepath
        except (requests.exceptions.RequestException, IOError) as e:
            logging.warning(f"Attempt {attempt + 1}/{max_retries} failed for [{slug}] {filename}: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                logging.error(f"All {max_retries} attempts failed for [{slug}] {url}")
                Path(filepath).unlink(missing_ok=True)
                raise


def download_media_to_slug(url, slug, output_dir, max_retries=3):
    """Download single media file (image or video) to slug-based directory with retry logic."""
    target_dir = os.path.join(output_dir, slug)
    os.makedirs(target_dir, exist_ok=True)

    filename = os.path.basename(urlparse(url).path)
    filepath = os.path.join(target_dir, filename)

    if os.path.exists(filepath):
        logging.info(f"Skip existing: [{slug}] {filename}")
        return filepath

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    timeout = 60 if any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS) else 30
    
    return _download_with_retry(url, filepath, timeout, headers, slug, filename, max_retries)


def _group_media_by_slug(media_slug_mapping):
    """Group media URLs by slug."""
    slug_groups = {}
    for media_url, slug in media_slug_mapping:
        if slug not in slug_groups:
            slug_groups[slug] = []
        slug_groups[slug].append(media_url)
    return slug_groups


def _print_slug_groups(slug_groups):
    """Print media files grouped by slug."""
    for slug in sorted(slug_groups.keys()):
        print(f"\n📁 {slug}/ ({len(slug_groups[slug])} files)")
        for media_url in sorted(slug_groups[slug]):
            filename = os.path.basename(urlparse(media_url).path)
            is_video = any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)
            icon = "🎬" if is_video else "→"
            print(f"  {icon} {filename}")


def _print_summary_stats(media_slug_mapping, slug_groups):
    """Print summary statistics."""
    print(f"\n📊 Summary:")
    print(f"  Total media files: {len(media_slug_mapping)}")
    print(f"  Articles with media: {len(slug_groups)}")
    video_count = sum(1 for url, _ in media_slug_mapping if any(url.lower().endswith(ext) for ext in VIDEO_EXTENSIONS))
    print(f"  Videos: {video_count}")
    print(f"  Images: {len(media_slug_mapping) - video_count}")


def _print_dry_run_report(media_slug_mapping):
    """Print dry-run report showing all media files grouped by slug."""
    print(f"\nFound {len(media_slug_mapping)} media files (images + videos):\n")
    
    slug_groups = _group_media_by_slug(media_slug_mapping)
    _print_slug_groups(slug_groups)
    _print_summary_stats(media_slug_mapping, slug_groups)


def _process_download_results(future_to_info, total_count):
    """Process download futures and count successes/failures with batch progress."""
    successful = 0
    failed = 0

    for future in as_completed(future_to_info):
        try:
            future.result()
            successful += 1
        except Exception:
            failed += 1

        completed = successful + failed
        if completed % PROGRESS_BATCH_SIZE == 0 or completed == total_count:
            print(f"  ✓ {completed}/{total_count} files processed ({successful} downloaded, {failed} failed)")

    return successful, failed


def _execute_parallel_downloads(media_slug_mapping, output_dir):
    """Execute parallel downloads and return success/failure counts."""
    total_count = len(media_slug_mapping)
    logging.info(f"Starting download of {total_count} media files to {output_dir}")
    print(f"\n📥 Downloading {total_count} files (updates every {PROGRESS_BATCH_SIZE})...\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_info = {
            executor.submit(download_media_to_slug, url, slug, output_dir): (url, slug)
            for url, slug in media_slug_mapping
        }

        successful, failed = _process_download_results(future_to_info, total_count)
    
    logging.info(f"Download complete. Success: {successful}, Failed: {failed}")
    return successful, failed


def _setup_arg_parser():
    """Setup and return argument parser."""
    parser = argparse.ArgumentParser(description='Crawl and download Ghost blog images sorted by article slug')
    parser.add_argument('--url', help='Blog URL (for crawl mode)')
    parser.add_argument('--sitemap', action='append', help='Sitemap URL (for sitemap mode, repeatable)')
    parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT, help='Max pages to crawl (crawl mode only)')
    parser.add_argument('--dry-run', action='store_true', help='Only show URLs and slugs, no download')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help='Output directory')
    parser.add_argument('--cache-file', default=DEFAULT_CACHE_FILE, help='Cache file for crawl results')
    parser.add_argument('--save-cache', action='store_true', help='Save crawl results to cache file')
    parser.add_argument('--use-cache', action='store_true', help='Load from cache instead of crawling')
    return parser


def main():
    """Main function with CLI argument parsing and parallel downloads."""
    parser = _setup_arg_parser()
    args = parser.parse_args()

    # Validate mode selection
    if args.sitemap and args.url:
        raise ValueError("Cannot use both --sitemap and --url. Choose one mode.")
    if not args.sitemap and not args.url and not args.use_cache:
        raise ValueError("Must provide either --sitemap, --url, or --use-cache")

    # Load from cache or fetch data
    if args.use_cache:
        if not os.path.exists(args.cache_file):
            raise FileNotFoundError(f"Cache file not found: {args.cache_file}")
        crawl_data = load_crawl_cache(args.cache_file)
    elif args.sitemap:
        # Sitemap mode
        urls = get_urls_from_sitemaps(args.sitemap)
        crawl_data = scrape_pages(urls)
        if args.save_cache:
            save_crawl_cache(crawl_data, args.cache_file)
            print(f"\n💾 Saved {len(crawl_data)} pages to {args.cache_file}\n")
    else:
        # Crawl mode
        crawl_data = crawl_website(args.url, args.limit)
        if args.save_cache:
            save_crawl_cache(crawl_data, args.cache_file)
            print(f"\n💾 Saved {len(crawl_data)} pages to {args.cache_file}\n")

    # Extract media URLs from crawled pages
    base_url = args.url if args.url else (args.sitemap[0] if args.sitemap else '')
    media_slug_mapping = extract_media_urls_with_slugs(crawl_data, base_url)

    # Either print dry-run report or execute downloads
    if args.dry_run:
        _print_dry_run_report(media_slug_mapping)
    else:
        _execute_parallel_downloads(media_slug_mapping, args.output_dir)


if __name__ == '__main__':
    main()
