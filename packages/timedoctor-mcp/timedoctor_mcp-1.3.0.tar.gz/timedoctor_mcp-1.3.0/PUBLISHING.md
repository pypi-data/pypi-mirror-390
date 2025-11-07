# Publishing to PyPI

This guide explains how to publish the Time Doctor MCP package to PyPI.

## Prerequisites

1. **PyPI Account:**
   - Create account at https://pypi.org/account/register/
   - Verify your email address

2. **API Token:**
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Name: "timedoctor-mcp" (or any name you prefer)
   - Scope: "Entire account" (or specific project after first upload)
   - Copy the token (starts with `pypi-`)
   - **Save it securely** - you won't see it again!

3. **uv installed:**
   ```bash
   brew install uv  # macOS
   # or see https://docs.astral.sh/uv/
   ```

## Step 1: Prepare for Publishing

### Check the Package Configuration

Verify `pyproject.toml` has all required fields:
- ✅ `name` - Package name on PyPI
- ✅ `version` - Current version (1.0.0)
- ✅ `description` - Short description
- ✅ `readme` - Path to README.md
- ✅ `requires-python` - Python version requirement
- ✅ `authors` - Your information
- ✅ `license` - MIT
- ✅ `dependencies` - All runtime dependencies
- ✅ `project.scripts` - Entry point for uvx
- ✅ `build-system` - Hatchling backend

### Verify Package Name Availability

Check if the name is available:
```bash
pip search timedoctor-mcp
# or visit: https://pypi.org/project/timedoctor-mcp/
```

If the name is taken, update `name` in `pyproject.toml`.

## Step 2: Build the Package

Build both source distribution (.tar.gz) and wheel (.whl):

```bash
# From project root
uv build
```

This creates:
- `dist/timedoctor_mcp-1.0.0.tar.gz` - Source distribution
- `dist/timedoctor_mcp-1.0.0-py3-none-any.whl` - Wheel distribution

**Verify the build:**
```bash
ls -lh dist/
```

## Step 3: Test the Package Locally

Before publishing, test that the package installs correctly:

```bash
# Create a test environment
uv venv test-env
source test-env/bin/activate  # Windows: test-env\Scripts\activate

# Install from the wheel
pip install dist/timedoctor_mcp-1.0.0-py3-none-any.whl

# Test the entry point
timedoctor-mcp --help

# Clean up
deactivate
rm -rf test-env
```

## Step 4: Publish to TestPyPI (Optional but Recommended)

Test publishing on TestPyPI first:

1. **Create TestPyPI account:**
   - https://test.pypi.org/account/register/

2. **Get TestPyPI token:**
   - https://test.pypi.org/manage/account/token/

3. **Publish to TestPyPI:**
   ```bash
   UV_PUBLISH_TOKEN=pypi-your-test-token-here \
     uv publish --publish-url https://test.pypi.org/legacy/
   ```

4. **Test installation from TestPyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ timedoctor-mcp
   ```

## Step 5: Publish to PyPI

Once you've verified everything works:

```bash
# Set your PyPI token as environment variable
export UV_PUBLISH_TOKEN=pypi-your-actual-token-here

# Publish to PyPI
uv publish
```

Or in one command:
```bash
UV_PUBLISH_TOKEN=pypi-your-token-here uv publish
```

**Alternative: Store token in config**
```bash
# Store token (more secure)
echo "UV_PUBLISH_TOKEN=pypi-your-token-here" >> ~/.bashrc
source ~/.bashrc

# Now you can just run:
uv publish
```

## Step 6: Verify Publication

1. **Check PyPI:**
   - Visit https://pypi.org/project/timedoctor-mcp/
   - Verify package details, description, links

2. **Test installation:**
   ```bash
   # In a fresh environment
   uvx timedoctor-mcp --help
   ```

3. **Update README:**
   - Remove the note about "pending PyPI publication"
   - Update installation instructions

## Publishing Updates

When you release a new version:

1. **Update version in `pyproject.toml`:**
   ```toml
   version = "1.0.1"  # or "1.1.0", "2.0.0", etc.
   ```

2. **Commit the version change:**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.1"
   git tag v1.0.1
   git push && git push --tags
   ```

3. **Clean old builds:**
   ```bash
   rm -rf dist/
   ```

4. **Build and publish:**
   ```bash
   uv build
   uv publish
   ```

## Troubleshooting

### Error: "File already exists"
- You've already published this version
- Update the version number in `pyproject.toml`

### Error: "Invalid credentials"
- Check your API token is correct
- Ensure token has correct permissions
- For first upload, use "Entire account" scope

### Error: "Package name conflict"
- The name is already taken on PyPI
- Choose a different name in `pyproject.toml`

### Error: "Missing dependencies"
- Ensure all dependencies are in `pyproject.toml`
- Run `uv build` and check for warnings

### Build Fails
```bash
# Rebuild from scratch
rm -rf dist/ build/ *.egg-info
uv build
```

## Security Best Practices

1. **Never commit API tokens** to git
2. **Use scoped tokens** - Create project-specific tokens after first upload
3. **Rotate tokens regularly**
4. **Store tokens securely** - Use environment variables or secret managers
5. **Enable 2FA** on your PyPI account

## Additional Resources

- **PyPI Help:** https://pypi.org/help/
- **uv Documentation:** https://docs.astral.sh/uv/guides/package/
- **Python Packaging Guide:** https://packaging.python.org/

## GitHub Actions (Optional)

To automate publishing on release:

Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Build package
        run: uv build
      - name: Publish to PyPI
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: uv publish
```

Add your PyPI token to GitHub Secrets:
- Go to repository Settings → Secrets → Actions
- Add secret named `PYPI_TOKEN`

Now publishing happens automatically when you create a GitHub release!

---

**Questions?** Contact: frifster2014@gmail.com
