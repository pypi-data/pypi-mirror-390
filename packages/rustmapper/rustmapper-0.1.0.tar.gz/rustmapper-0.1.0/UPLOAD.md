# Quick Upload Guide

Your project is ready to upload to PyPI! Follow these steps:

## Step 1: Install Required Tools

```bash
pip install maturin twine
```

## Step 2: Build the Package

```bash
maturin build --release --sdist
```

This creates both wheel and source distribution files in `target/wheels/`:
- Wheel: `rustmapper-0.1.0-*.whl` (platform-specific binary)
- Source: `rustmapper-0.1.0.tar.gz` (source code)

## Step 3: Check the Package

```bash
twine check target/wheels/*
```

This verifies your package is ready for PyPI.

## Step 4: Upload to PyPI

```bash
twine upload target/wheels/*
```

Twine will automatically use your API token from `~/.pypirc`.

## Step 5: Verify

Visit: https://pypi.org/project/rustmapper/

Your package should appear within a few minutes!

## Test Installation

```bash
# In a new virtual environment
pip install rustmapper

# Test CLI
rustmapper --help

# Test Python import
python -c "from rustmapper import Crawler; print('Success!')"
```

## Troubleshooting

### "File already exists"
You need to increment the version number in:
- `Cargo.toml`
- `pyproject.toml`
- `python/rustmapper/__init__.py`

### "Invalid or non-existent authentication"
Check that `~/.pypirc` has your correct token.

### Build fails
Make sure you have Rust installed:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Next Release

For version 0.2.0:

1. Update version in all files
2. Rebuild: `maturin build --release --sdist`
3. Upload: `twine upload target/wheels/*`

That's it!
