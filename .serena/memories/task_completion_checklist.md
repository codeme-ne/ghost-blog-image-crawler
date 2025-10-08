# Task Completion Checklist

## When a Task is Completed

### Simple Utility Script - Minimal Process

Since this is a one-time utility script with no tests or linting configured:

1. **Verify Code Works**
   - Run with `--dry-run` first to validate
   - Test with small `--limit` before production run
   - Check logs for errors

2. **Check Output**
   - Verify `images/` directory structure looks correct
   - Check files are organized by slug
   - Verify both images and videos are downloaded

3. **Git Workflow** (if changes made)
   ```bash
   git status
   git add .
   git commit -m "Brief description"
   git push
   ```

4. **Environment Safety**
   - Ensure `.env` file is NOT committed (in .gitignore)
   - Ensure `images/` directory is NOT committed (in .gitignore)

## No Automated Checks
- No unit tests to run
- No linting (flake8, pylint, etc.)
- No formatting (black, autopep8, etc.)
- No type checking (mypy)
- No pre-commit hooks

## Manual Code Review Checklist
When modifying code:
- [ ] Functions stay under 20 lines
- [ ] Error handling present for risky operations
- [ ] Logging added for major operations
- [ ] Constants used instead of magic numbers
- [ ] Docstrings present for new functions
- [ ] Code follows OpenBSD-style simplicity

## Production Readiness
Before final production run:
- [ ] API key configured in `.env`
- [ ] Tested with `--dry-run`
- [ ] Tested with small `--limit`
- [ ] Disk space sufficient for downloads
- [ ] Network connection stable