# Publishing to PyPI

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Create an API token at https://pypi.org/manage/account/token/

## Installation

Install required packages:

```bash
pip install build twine
```

## Building the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This will create two files in the `dist/` directory:
- A `.tar.gz` source distribution
- A `.whl` wheel distribution

## Publishing to PyPI

### Test PyPI (Recommended First)

```bash
# Upload to Test PyPI first to verify everything works
python -m twine upload --repository testpypi dist/*
```

### Production PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (including the `pypi-` prefix)

## Verification

After publishing, verify the package:

```bash
# Install from PyPI
pip install compilelabs

# Test import
python -c "import compilelabs; print(compilelabs.__version__)"
```

## Updating the Package

1. Update the version in `pyproject.toml`
2. Make your changes
3. Rebuild and republish:

```bash
rm -rf dist/
python -m build
python -m twine upload dist/*
```

## Notes

- You can only upload each version once to PyPI
- Use semantic versioning (MAJOR.MINOR.PATCH)
- For placeholder updates, increment the patch version (0.0.1 → 0.0.2)

