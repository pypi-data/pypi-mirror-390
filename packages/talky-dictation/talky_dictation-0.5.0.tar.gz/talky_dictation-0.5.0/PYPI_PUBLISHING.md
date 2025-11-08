# PyPI Publishing Guide for Talky

This guide explains how to publish Talky to PyPI (Python Package Index) so users can install it via `pip install talky-dictation`.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **Install Build Tools**:
   ```bash
   pip install --upgrade build twine
   ```

3. **API Tokens** (recommended over passwords):
   - Go to https://pypi.org/manage/account/token/
   - Create an API token with "Upload packages" scope
   - Save it securely (you'll only see it once)

## Testing Locally

### 1. Test Installation from Source

```bash
# From project root
pip install -e .

# Test the command
talky --help

# Test with GPU support
pip install -e ".[gpu]"

# Uninstall
pip uninstall talky-dictation
```

### 2. Build Distribution Packages

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify outputs
ls -lh dist/
# Should see:
#   talky_dictation-0.5.0-py3-none-any.whl
#   talky-dictation-0.5.0.tar.gz
```

### 3. Check Package Quality

```bash
# Check the package
twine check dist/*

# Should output:
#   Checking dist/talky_dictation-0.5.0-py3-none-any.whl: PASSED
#   Checking talky-dictation-0.5.0.tar.gz: PASSED
```

### 4. Test Installation from Built Package

```bash
# Install from wheel
pip install dist/talky_dictation-0.5.0-py3-none-any.whl

# Test
talky --help

# Uninstall
pip uninstall talky-dictation
```

## Publishing to TestPyPI (Practice Run)

### 1. Configure TestPyPI Token

Create/edit `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

### 2. Upload to TestPyPI

```bash
# Upload
twine upload --repository testpypi dist/*

# Enter TestPyPI API token when prompted
# Or use token from ~/.pypirc
```

### 3. Test Installation from TestPyPI

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    talky-dictation

# The --extra-index-url allows dependencies from main PyPI

# Test
talky --help

# Uninstall
pip uninstall talky-dictation
```

## Publishing to PyPI (Production)

### 1. Configure PyPI Token

Update `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE
```

### 2. Upload to PyPI

```bash
# Final check
twine check dist/*

# Upload (production!)
twine upload dist/*

# Enter PyPI API token when prompted
```

### 3. Verify on PyPI

- Visit: https://pypi.org/project/talky-dictation/
- Check that all metadata is correct
- Verify README renders properly

### 4. Test Installation

```bash
# Fresh install from PyPI
pip install talky-dictation

# Test
talky --help
talky --version

# With GPU support
pip install talky-dictation[gpu]
```

## Post-Publication

### 1. Tag Release on GitHub

```bash
git tag -a v0.5.0 -m "Release v0.5.0 - Phase 4 Complete"
git push origin v0.5.0
```

### 2. Create GitHub Release

- Go to: https://github.com/ChrisKalahiki/talky/releases/new
- Select tag: v0.5.0
- Title: "Talky v0.5.0 - Full GUI Release"
- Description: Include changelog
- Attach dist files (optional)

### 3. Announce

Consider announcing on:
- GitHub Discussions
- Reddit: r/linux, r/opensource
- Hacker News
- Linux forums

## Updating the Package

### For New Releases:

1. **Update version** in:
   - `src/talky/version.py`
   - `pyproject.toml`

2. **Update changelog**:
   - Document changes in CHANGELOG.md (create if needed)

3. **Rebuild and upload**:
   ```bash
   rm -rf dist/
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### "File already exists" Error

PyPI doesn't allow overwriting uploads. Solutions:
- Increment version number (e.g., 0.5.0 → 0.5.1)
- Delete from TestPyPI (if testing) and re-upload
- Use `--skip-existing` flag: `twine upload --skip-existing dist/*`

### Metadata Issues

If README doesn't render:
```bash
# Validate README
pip install readme-renderer
python -m readme_renderer README.md -o /tmp/output.html
```

### Missing Files in Package

Check MANIFEST.in and test with:
```bash
python -m build --sdist
tar -tzf dist/talky-dictation-0.5.0.tar.gz | less
```

### Import Errors After Install

Verify package structure:
```bash
pip show -f talky-dictation
```

## Security Best Practices

1. **Never commit tokens** to git
2. **Use API tokens** instead of passwords
3. **Scope tokens** appropriately (per-project if possible)
4. **Rotate tokens** periodically
5. **Use 2FA** on PyPI account

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Setuptools Documentation](https://setuptools.pypa.io/)
- [twine Documentation](https://twine.readthedocs.io/)

## Quick Reference

```bash
# Complete publishing workflow
cd talky/
git pull
# Update version in src/talky/version.py and pyproject.toml
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
# Test install from TestPyPI
twine upload dist/*  # Production
git tag -a v0.5.0 -m "Release v0.5.0"
git push --tags
```
