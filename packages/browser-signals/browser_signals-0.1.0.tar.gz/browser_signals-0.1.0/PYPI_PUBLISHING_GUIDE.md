# PyPI Publishing Guide for browser-signals

## Pre-Publishing Checklist

### ✅ Already Done

- [x] Project structure with `src/` layout
- [x] `pyproject.toml` with proper metadata
- [x] README.md with clear documentation
- [x] LICENSE file (MIT)
- [x] Version number set to 0.1.0
- [x] Author information updated
- [x] GitHub repository URLs configured
- [x] MANIFEST.in created

### 📝 To Do Before First Publish

1. **Update your email in `pyproject.toml`**
   - Currently set to: `aquil@aquilabdullah.com`
   - Change to your actual email address

2. **Verify package name availability**
   - Visit <https://pypi.org/project/browser-signals/>
   - If the name is taken, you'll need to choose a different name

3. **Install build tools**

   ```bash
   pip install --upgrade build twine
   ```

4. **Create PyPI account**
   - Register at <https://pypi.org/account/register/>
   - Register at <https://test.pypi.org/account/register/> (for testing)

5. **Set up API tokens (recommended over passwords)**
   - Go to <https://pypi.org/manage/account/token/>
   - Create a new API token
   - Save it securely (you'll only see it once)

## Publishing Steps

### Test on TestPyPI First (Recommended)

1. **Build the package**

   ```bash
   cd /Users/aquilabdullah/devel/aquil/projects/browser-signals
   python -m build
   ```

   This creates `dist/browser_signals-0.1.0-py3-none-any.whl` and `.tar.gz` files

2. **Upload to TestPyPI**

   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

   - Username: `__token__`
   - Password: your TestPyPI API token (including the `pypi-` prefix)

3. **Test installation from TestPyPI**

   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps browser-signals
   ```

4. **Verify the package works**
   - Create a new virtual environment
   - Install your package
   - Test import and basic functionality

### Publish to PyPI (Production)

1. **Clean previous builds** (if you made changes after testing)

   ```bash
   rm -rf dist/ build/ src/*.egg-info
   python -m build
   ```

2. **Upload to PyPI**

   ```bash
   python -m twine upload dist/*
   ```

   - Username: `__token__`
   - Password: your PyPI API token (including the `pypi-` prefix)

3. **Verify on PyPI**
   - Visit <https://pypi.org/project/browser-signals/>
   - Check that all information displays correctly

4. **Test installation**

   ```bash
   pip install browser-signals
   ```

## Using .pypirc for Easier Authentication

Create `~/.pypirc` to store credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YourActualAPITokenHere

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YourTestPyPIAPITokenHere
```

Then you can upload without entering credentials:

```bash
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

## Future Releases

For subsequent releases:

1. **Update version number** in two places:
   - `pyproject.toml` → `[project] version = "0.1.1"`
   - `src/browser_signals/__init__.py` → `__version__ = "0.1.1"`

2. **Clean, build, and upload**:

   ```bash
   rm -rf dist/ build/ src/*.egg-info
   python -m build
   python -m twine upload dist/*
   ```

## Troubleshooting

### "File already exists" error

- You cannot re-upload the same version
- Increment the version number and rebuild

### Import errors after installation

- Verify package structure: ensure `src/browser_signals/__init__.py` exports the right symbols
- Check dependencies in `pyproject.toml`

### Missing files in distribution

- Update `MANIFEST.in`
- Run `python -m build` and inspect the `.tar.gz` contents:

  ```bash
  tar -tzf dist/browser_signals-0.1.0.tar.gz
  ```

## Automated Publishing with GitHub Actions

Consider setting up automated releases. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
