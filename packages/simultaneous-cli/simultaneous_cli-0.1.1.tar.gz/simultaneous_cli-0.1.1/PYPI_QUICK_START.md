# Quick Start: Upload CLI to PyPI

## One-Time Setup

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create API token**: https://pypi.org/manage/account/token/
   - Scope: "Upload packages"
   - Copy the token (starts with `pypi-`)

3. **Store your API token** (choose one method):

   **Option A: Environment Variables** (for CI/CD)
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-token-here
   ```

   **Option B: .pypirc File** (for local development - recommended)
   ```bash
   # Create ~/.pypirc (Linux/Mac) or %USERPROFILE%\.pypirc (Windows)
   [pypi]
   username = __token__
   password = pypi-your-token-here
   ```
   
   See [PYPI_UPLOAD.md](PYPI_UPLOAD.md) for detailed instructions.

## Upload Steps

### Option 1: Using the Helper Script (Recommended)

```bash
# Install build tools
pip install --upgrade build twine

# Test upload to TestPyPI first
python scripts/upload_cli_to_pypi.py --test

# If successful, upload to production PyPI
python scripts/upload_cli_to_pypi.py
```

When prompted:
- Username: `__token__`
- Password: Your API token (e.g., `pypi-AgEIcH...`)

### Option 2: Manual Steps

```bash
cd cli

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build packages
python -m build

# Upload to TestPyPI (test first!)
python -m twine upload --repository testpypi dist/*

# Upload to production PyPI
python -m twine upload dist/*
```

## Before Each Upload

**Always update the version number** in:
1. `cli/pyproject.toml` - `version = "X.X.X"`
2. `cli/__init__.py` - `__version__ = "X.X.X"`

PyPI doesn't allow re-uploading the same version!

## Version Numbering

- **Patch**: `0.1.0` → `0.1.1` (bug fixes)
- **Minor**: `0.1.0` → `0.2.0` (new features)
- **Major**: `0.1.0` → `1.0.0` (breaking changes)

## Verify Installation

```bash
# After TestPyPI upload
pip install --index-url https://test.pypi.org/simple/ simultaneous-cli

# After production PyPI upload
pip install simultaneous-cli

# Test CLI
sim --help
```

## Troubleshooting

- **"Package already exists"**: Increment version number
- **"Invalid credentials"**: Use `__token__` as username, full token as password
- **"File already exists"**: Version already uploaded, increment version

For detailed instructions, see [PYPI_UPLOAD.md](PYPI_UPLOAD.md)

