# Publishing Guide

This guide explains how to publish `ass-to-lrc` to PyPI.

## Prerequisites

1. **Install Task**: <https://taskfile.dev/installation/>
2. **PyPI Account**: Create accounts on:
   - [PyPI](https://pypi.org/account/register/)
   - [TestPyPI](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate API tokens from your account settings

## Setup Authentication

### Option 1: Environment Variables (Recommended)

```bash
export UV_PUBLISH_TOKEN=pypi-YOUR-PYPI-TOKEN-HERE

# For TestPyPI
export UV_PUBLISH_TOKEN=pypi-YOUR-TESTPYPI-TOKEN-HERE
```

### Option 2: Pass token directly

```bash
# PyPI
uv publish --token pypi-YOUR-TOKEN

# TestPyPI
uv publish --token pypi-YOUR-TOKEN --publish-url https://test.pypi.org/legacy/
```

### Option 3: Use keyring

UV supports system keyring for secure credential storage. See UV documentation for details.

## Publishing Workflow

### 1. Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "0.2.0"  # Update this
```

### 2. Update Changelog

Document changes in `README.md` or `CHANGELOG.md`

### 3. Run Quality Checks

```bash
# Run all checks
task qa

# Or individually
task lint
task format-check
task typecheck
task test
```

### 4. Build Package

```bash
task build
```

This creates:

- `dist/ass_to_lrc-X.Y.Z-py3-none-any.whl`
- `dist/ass-to-lrc-X.Y.Z.tar.gz`

### 5. Test on TestPyPI First

```bash
# Upload to TestPyPI
task publish-test

# Test installation
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    ass-to-lrc

# Test the package
ass2lrc --version
```

### 6. Publish to PyPI

```bash
# Upload to production PyPI (with token)
export UV_PUBLISH_TOKEN=pypi-YOUR-PYPI-TOKEN
task publish

# Or use task directly (interactive)
task publish
```

### 7. Create Git Tag

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 8. Create GitHub Release

Go to GitHub repository → Releases → Draft a new release:

- Tag: `v0.2.0`
- Title: `Release 0.2.0`
- Description: Changelog entries
- Upload distribution files from `dist/`

## GitHub Actions Publishing

### Automatic Publishing on Release

1. Create a new release on GitHub
2. GitHub Actions will automatically:
   - Run tests
   - Build package
   - Upload to PyPI

### Manual Publishing

Go to Actions → Publish to PyPI → Run workflow:

- Choose target: `testpypi` or `pypi`

### Setup GitHub Secrets

For manual workflow, add to repository secrets:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token

**Note**: With Trusted Publishers (recommended), you don't need secrets!

### Setup Trusted Publishers (Recommended)

#### For PyPI

1. Go to <https://pypi.org/manage/account/publishing/>
2. Add publisher:
   - PyPI Project Name: `ass-to-lrc`
   - Owner: `nattadasu` (your GitHub username)
   - Repository name: `ass-to-lrc`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`

#### For TestPyPI

1. Go to <https://test.pypi.org/manage/account/publishing/>
2. Add same configuration with environment name: `testpypi`

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): Add functionality (backwards compatible)
- **PATCH** (0.0.1): Bug fixes (backwards compatible)

Examples:

- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: Stable release

## Checklist

Before publishing, ensure:

- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG updated
- [ ] All tests passing (`task test`)
- [ ] Code formatted (`task format`)
- [ ] Type check passing (`task typecheck`)
- [ ] Linter passing (`task lint`)
- [ ] Tested on TestPyPI
- [ ] Git tag created
- [ ] GitHub release created

## Troubleshooting

### "File already exists"

You cannot republish the same version. Bump the version number.

### "Invalid credentials"

Check your API token in the `UV_PUBLISH_TOKEN` environment variable or use the `--token` flag.

### "Package name taken"

The package name might be taken. Choose a different name in `pyproject.toml`.

### Build fails

```bash
# Clean and rebuild
task clean
task build
```

## Useful Commands

```bash
# Show current version
task version

# Install in development mode
task install-dev

# Run all quality checks
task qa

# Clean build artifacts
task clean

# Build package
task build

# Publish to TestPyPI
export UV_PUBLISH_TOKEN=pypi-YOUR-TESTPYPI-TOKEN
task publish-test

# Publish to PyPI
export UV_PUBLISH_TOKEN=pypi-YOUR-PYPI-TOKEN
task publish
```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Documentation](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Task Documentation](https://taskfile.dev/)
