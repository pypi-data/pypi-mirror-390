# Uploading Simultaneous CLI to PyPI

This guide walks you through uploading the `simultaneous-cli` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (recommended for testing): Create an account at https://test.pypi.org/account/register/
3. **API Token**: Generate an API token from your PyPI account settings:
   - Go to https://pypi.org/manage/account/
   - Scroll to "API tokens"
   - Create a new token with "Upload packages" scope
   - Save the token (format: `pypi-...`)

## Storing Your API Token

You have **three options** for storing your PyPI API token:

### Option 1: Environment Variables (Recommended for CI/CD)

Set environment variables before running the upload script:

```bash
# For production PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here

# For TestPyPI
export TWINE_USERNAME=__token__
export TWINE_TEST_PASSWORD=pypi-your-test-token-here

# Then run the script
python scripts/upload_cli_to_pypi.py
```

**Windows (PowerShell):**
```powershell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-your-token-here"
python scripts/upload_cli_to_pypi.py
```

**Windows (CMD):**
```cmd
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-your-token-here
python scripts/upload_cli_to_pypi.py
```

### Option 2: .pypirc File (Recommended for Local Development)

Create a `.pypirc` file in your home directory:

**Linux/Mac:**
```bash
# Create/edit ~/.pypirc
nano ~/.pypirc
```

**Windows:**
```cmd
# Create/edit %USERPROFILE%\.pypirc
notepad %USERPROFILE%\.pypirc
```

Add this content:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

**Important:** Set file permissions to protect your token:
```bash
# Linux/Mac
chmod 600 ~/.pypirc
```

Twine will automatically use credentials from `.pypirc` - no prompts needed!

### Option 3: Interactive Prompt (Default)

If you don't set environment variables or `.pypirc`, the script will prompt you for credentials when uploading.

## Step 1: Install Build Tools

Make sure you have the latest build tools installed:

```bash
pip install --upgrade build twine
```

## Step 2: Update Version (if needed)

Before uploading, update the version in:
- `cli/pyproject.toml` (in the `[project]` section)
- `cli/__init__.py` (the `__version__` variable)

**Important**: PyPI doesn't allow re-uploading the same version. Always increment the version number.

## Step 3: Clean Previous Builds

Remove any previous build artifacts:

```bash
cd cli
rm -rf dist/ build/ *.egg-info/
```

## Step 4: Build Distribution Packages

Build both source distribution (sdist) and wheel:

```bash
python -m build
```

This creates:
- `dist/simultaneous-cli-X.X.X.tar.gz` (source distribution)
- `dist/simultaneous-cli-X.X.X-py3-none-any.whl` (wheel)

## Step 5: Test on TestPyPI (Recommended)

Before uploading to production PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# When prompted, use:
# Username: __token__
# Password: pypi-<your-testpypi-token>
```

Then test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ simultaneous-cli
```

## Step 6: Upload to Production PyPI

Once tested, upload to production PyPI:

```bash
python -m twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your PyPI API token (starts with `pypi-`)

## Step 7: Verify Installation

After upload, verify the package is available:

```bash
pip install simultaneous-cli
sim --help
```

## Using the Helper Script

For convenience, use the provided script:

```bash
# Test upload to TestPyPI
python scripts/upload_cli_to_pypi.py --test

# Production upload to PyPI
python scripts/upload_cli_to_pypi.py
```

## Troubleshooting

### "Package already exists"
- Increment the version number in `pyproject.toml` and `__init__.py`

### "Invalid credentials"
- Make sure you're using `__token__` as username and your full API token (including `pypi-` prefix) as password

### "File already exists"
- PyPI doesn't allow overwriting existing files. You must increment the version.

### "Missing required field"
- Ensure `pyproject.toml` has all required fields:
  - `name`, `version`, `description`, `readme`, `requires-python`, `license`, `authors`

## Automated Upload with GitHub Actions (Optional)

You can set up GitHub Actions to automatically upload on tag creation. See `.github/workflows/publish-cli.yml` for an example.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

Example: `0.1.0` → `0.1.1` (patch) → `0.2.0` (minor) → `1.0.0` (major)

