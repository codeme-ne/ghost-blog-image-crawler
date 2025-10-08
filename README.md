# Ghost Blog Media Crawler

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

A utility to crawl and download all images and videos from Ghost blogs, organized by article slug for easy migration to self-hosted platforms.

## 🎯 Why Use This?

**Problem:** You're migrating your Ghost blog from Ghost(Pro) to self-hosting and need to download all media files (images, videos) before canceling your subscription.

**Solution:** This tool uses the Firecrawl API to efficiently crawl your Ghost blog and downloads all media files organized by article slug, making migration seamless.

## ✨ Key Features

- ✅ **Dual Mode Operation**: Sitemap-based (precise) or crawl-based (exploratory)
- ✅ **Parallel Processing**: 10 concurrent downloads for speed
- ✅ **Slug-Based Organization**: Media sorted by article for easy migration
- ✅ **Resume Capability**: Skips already downloaded files
- ✅ **Video Support**: Automatically detects and downloads `.mp4`, `.webm`, `.mov` videos
- ✅ **Thumbnail Extraction**: Video thumbnails extracted from HTML attributes
- ✅ **Robust Error Handling**: Individual failures don't stop the process
- ✅ **Streaming Downloads**: Memory-efficient for large video files
- ✅ **Cache Support**: Save crawl results to avoid re-crawling on interruption

## 📋 Prerequisites

- Python 3.8 or higher
- Firecrawl API Key (get one at [firecrawl.dev](https://firecrawl.dev))

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/codeme-ne/ghost-blog-image-crawler.git
cd ghost-blog-image-crawler
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API key

Create a `.env` file in the project root:

```bash
FIRECRAWL_API_KEY=fc-your-api-key-here
```

**IMPORTANT:** The `.env` file is gitignored and will NOT be committed!

## 💻 Quick Start

### Recommended: Sitemap Mode (Precise)

Sitemap mode is more efficient and avoids unwanted pages like tag listings:

```bash
python crawl_images.py \
  --sitemap https://your-ghost-blog.com/sitemap-posts.xml \
  --sitemap https://your-ghost-blog.com/sitemap-pages.xml
```

### Alternative: Crawl Mode (Exploratory)

Follows links from the homepage (may hit unwanted pages):

```bash
python crawl_images.py --url https://your-ghost-blog.com --limit 100
```

## 📖 Usage Examples

### Dry Run (Recommended First Step)

Show found URLs without downloading:

```bash
python crawl_images.py \
  --sitemap https://your-ghost-blog.com/sitemap-posts.xml \
  --dry-run
```

### Small Test Batch

Test with a few pages first:

```bash
python crawl_images.py \
  --url https://your-ghost-blog.com \
  --limit 10
```

### Production with Cache

Save crawl results to protect against crashes:

```bash
./run.sh \
  --sitemap https://your-ghost-blog.com/sitemap-posts.xml \
  --sitemap https://your-ghost-blog.com/sitemap-pages.xml \
  --save-cache
```

### Resume from Cache

If interrupted, resume without re-crawling:

```bash
python crawl_images.py --use-cache
```

### All Available Options

```bash
python crawl_images.py --help

Options:
  --url URL                  Blog URL to crawl (default: https://example.com)
  --sitemap URL              Sitemap XML URL (can be used multiple times)
  --limit N                  Max pages to crawl in crawl mode (default: 100)
  --dry-run                  Show URLs only, don't download
  --output-dir PATH          Output directory (default: ./images)
  --cache-file PATH          Cache file path (default: ./crawl_cache.json)
  --save-cache               Save crawl results to cache
  --use-cache                Load from cache instead of crawling
```

## 📁 Output Structure

Media files are organized by article slug for easy migration:

```
images/
├── first-blog-post/
│   ├── header-image.jpg
│   ├── content-image-1.png
│   └── demo-video.mp4
├── getting-started/
│   ├── screenshot.png
│   └── tutorial-video.mp4
├── _homepage/
│   └── logo.png
└── _shared/
    └── icon.png              # Media appearing on multiple pages
```

**Benefits:**

- Each folder = one article
- Direct migration to new platform
- No date-based searching needed
- Automatic detection of shared media (logos, icons)
- Videos and thumbnails automatically included

## 🔧 Configuration

### Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
FIRECRAWL_API_KEY=fc-your-api-key-here
```

### CLI Flags

- `--sitemap`: (Recommended) Precise URL list from sitemap XML
- `--url`: Base URL for crawl mode
- `--limit`: Max pages in crawl mode (ignored in sitemap mode)
- `--dry-run`: Preview mode
- `--save-cache`: Protect against crashes during long runs
- `--use-cache`: Resume from previous run

## 🐛 Troubleshooting

### "Invalid API key" error

- Check your `.env` file exists and contains valid key
- Verify key starts with `fc-`
- Get a new key at [firecrawl.dev](https://firecrawl.dev)

### "Rate limited" error

- You've hit Firecrawl's rate limit
- Wait a few minutes and try again
- Use `--save-cache` to avoid re-crawling

### Downloads are slow

- Increase `MAX_WORKERS` in `crawl_images.py` (default: 10)
- Check your internet connection
- Large videos take time to stream

### Missing media files

- Check the crawl output for errors
- Some media may be loaded via JavaScript (not captured)
- Verify URLs in dry-run mode first

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Code Style

- OpenBSD-style: Minimal, clear, secure
- Max 20 lines per function
- No type hints (simple utility)
- Error handling with context

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [Firecrawl API](https://firecrawl.dev)
- Built for the Ghost blogging community

---

**Need help?** Open an issue on GitHub or check the [troubleshooting section](#-troubleshooting).
