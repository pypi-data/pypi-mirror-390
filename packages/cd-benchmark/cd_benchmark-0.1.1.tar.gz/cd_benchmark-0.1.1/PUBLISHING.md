# Publishing cd-benchmark to PyPI

## Prerequisites

1. **Create PyPI account** at https://pypi.org/account/register/
2. **Create TestPyPI account** (optional, for testing) at https://test.pypi.org/account/register/

## Installation

Install the necessary tools:

```bash
source .venv_clean/bin/activate
pip install twine
```

## Step 1: Build the package

The package is already built, but if you need to rebuild:

```bash
python -m build
```

This creates:
- `dist/cd_benchmark-0.1.0-py3-none-any.whl`
- `dist/cd_benchmark-0.1.0.tar.gz`

## Step 2: Check the package

Verify that the package is valid:

```bash
twine check dist/*
```

## Step 3 (Optional): Test upload to TestPyPI

Test the upload process first:

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: your TestPyPI username
- Password: your TestPyPI password or API token

Then test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ cd-benchmark
```

## Step 4: Upload to PyPI

When ready, upload to the real PyPI:

```bash
twine upload dist/*
```

You'll be prompted for:
- Username: your PyPI username (or `__token__` if using API token)
- Password: your PyPI password or API token

## Step 5: Verify

After upload, check your package at:
https://pypi.org/project/cd-benchmark/

Install it:

```bash
pip install cd-benchmark
```

## Using API Tokens (Recommended)

Instead of username/password, use API tokens for better security:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Create `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # your token here

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZw...  # your test token here
```

Then you can upload without being prompted:

```bash
twine upload dist/*
```

## Updating the Package

When you make changes and want to release a new version:

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # increment version
   ```

2. Rebuild:
   ```bash
   rm -rf dist/  # remove old builds
   python -m build
   ```

3. Upload:
   ```bash
   twine upload dist/*
   ```

## Important Notes

⚠️ **Before first upload, check:**
- [ ] Package name `cd-benchmark` is available on PyPI
- [ ] All dependencies in `pyproject.toml` are correct
- [ ] README.md looks good (it will be shown on PyPI)
- [ ] Version number follows semantic versioning (e.g., 0.1.0)
- [ ] All tests pass
- [ ] No sensitive data in the code

⚠️ **Cannot delete or overwrite:** Once uploaded to PyPI, you cannot delete a version or reupload the same version number. You must increment the version for any changes.

## Alternative: GitHub Releases

You can also publish releases on GitHub:
1. Create a git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
2. Push the tag: `git push origin v0.1.0`
3. Create a release on GitHub and attach the wheel/tarball files

Users can then install directly from GitHub:
```bash
pip install git+https://github.com/rpritr/network-community-detection-benchmark.git
```

