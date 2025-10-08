# Code Style & Conventions

## General Philosophy
**OpenBSD-Style Simplicity** - Minimalistic, clear, secure code

## Function Design
- **Maximum 20 lines per function** (strictly followed in this project)
- Each function does one thing well
- Descriptive names that explain purpose

## Code Structure
- **Constants**: UPPER_CASE at module level
  - Example: `DEFAULT_OUTPUT_DIR`, `MAX_WORKERS`, `VIDEO_EXTENSIONS`
- **Functions**: lowercase_with_underscores
- **Module docstring**: Present at top of file
- **Function docstrings**: Present for all functions (brief one-liners)

## Type Hints
- **Not used** in this project (simple utility script)
- Focus on clarity through naming and docstrings

## Error Handling
- Try-except blocks around risky operations
- Logging for all errors with context
- Graceful degradation (single failures don't stop entire process)
- Example: Individual download failures logged but don't stop batch

## Logging
- Python `logging` module with INFO level
- Format: `%(asctime)s - %(levelname)s - %(message)s`
- All major operations logged (crawl start, downloads, errors)

## Parallel Processing
- `ThreadPoolExecutor` for concurrent downloads
- `MAX_WORKERS = 10` for parallel downloads
- `as_completed()` for processing results as they finish

## File Operations
- Streaming downloads for large files (`requests.get(stream=True)`)
- `os.makedirs(exist_ok=True)` for directory creation
- Always check if file exists before downloading (resume capability)

## Security
- User-Agent header to prevent bot blocking
- Timeouts on HTTP requests (30s for images, 60s for videos)
- API keys in `.env` file (never committed)

## No Linting/Formatting Tools
- Project doesn't use black, flake8, mypy, or similar tools
- Simple utility script with manual code review