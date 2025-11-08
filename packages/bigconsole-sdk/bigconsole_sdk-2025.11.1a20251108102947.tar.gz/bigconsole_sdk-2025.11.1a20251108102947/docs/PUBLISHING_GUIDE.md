# Bigconsole SDK - Complete Publishing Guide

## Table of Contents

1. [Overview](#overview)
2. [Package Publishing Process](#package-publishing-process)
3. [Version Management](#version-management)
4. [Publishing to Alpha (Beta-Alpha Branch)](#publishing-to-alpha-beta-alpha-branch)
5. [Publishing to Production (Beta-Prod Branch)](#publishing-to-production-beta-prod-branch)
6. [Checking Published Packages](#checking-published-packages)
7. [Published Package History](#published-package-history)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Bigconsole SDK Python package is automatically published to PyPI using GitHub Actions workflows. This guide provides complete instructions for publishing packages, managing versions, and verifying deployments.

### Package Information

- **Package Name**: `bigconsole-sdk`
- **PyPI URL**: https://pypi.org/project/bigconsole-sdk/
- **Repository**: https://github.com/Algoshred/bigconsole-sdk-python
- **Current Version**: 2025.11.0 (using CalVer format)

---

## Package Publishing Process

### Automated CI/CD Pipeline

The SDK uses a sophisticated CI/CD pipeline with two deployment branches:

1. **beta-alpha**: For alpha/pre-release versions (timestamped)
2. **beta-prod**: For production/stable releases (version from pyproject.toml)

### Workflow Files

Located in `.github/workflows/`:

- `deploy-beta-alpha-pybe.yml` - Alpha deployments
- `deploy-beta-prod-pybe.yml` - Production deployments
- `pr-checks-pybe.yml` - Quality checks for pull requests

---

## Version Management

### Version Format

The SDK uses **Calendar Versioning (CalVer)** with the format: `YYYY.MM.PATCH`

Examples:
- `2025.10.0` - October 2025, first release
- `2025.10.1` - October 2025, patch release
- `2025.11.0` - November 2025, new release

### Alpha Versions

Alpha versions append a timestamp: `YYYY.MM.PATCH` + `a{YYYYMMDDHHMMSS}`

Examples:
- `2025.11.0a20251103074441` - Alpha released on Nov 3, 2025 at 07:44:41 UTC

### How to Change Version

#### 1. Edit pyproject.toml

```bash
# Open pyproject.toml
vim pyproject.toml

# Update the version line:
[project]
version = "2025.11.0"  # Change to your new version
```

#### 2. Commit the Version Change

```bash
git add pyproject.toml
git commit -m "chore: bump version to 2025.11.0"
git push origin main
```

#### 3. Merge to Production Branch

```bash
git checkout beta-prod
git merge main
git push origin beta-prod
```

The workflow will automatically detect the version change and publish.

---

## Publishing to Alpha (Beta-Alpha Branch)

### When to Use Alpha

- Testing new features
- Pre-release testing
- Development builds
- Continuous integration testing

### Publishing Process

#### Method 1: Automatic (Recommended)

Push changes to the `beta-alpha` branch:

```bash
# Make your code changes
git checkout beta-alpha
git pull origin beta-alpha

# Make changes to src/, tests/, etc.
# ... edit files ...

# Commit changes
git add .
git commit -m "feat: add new functionality"

# Push to trigger deployment
git push origin beta-alpha
```

#### Method 2: Manual Trigger

```bash
# Trigger workflow manually
gh workflow run "deploy-beta-alpha-pybe.yml" --ref beta-alpha

# Or with options
gh workflow run "deploy-beta-alpha-pybe.yml" --ref beta-alpha -f skip_tests=true
```

### What Happens During Alpha Publishing

1. **Tests Run** (2-3 minutes)
   - Tests on Python 3.8, 3.9, 3.10, 3.11, 3.12
   - Linting (flake8)
   - Formatting checks (black, isort)
   - Type checking (mypy)

2. **Version Generation** (~5 seconds)
   - Base version from pyproject.toml: `2025.11.0`
   - Timestamp added: `a20251103074441`
   - Final version: `2025.11.0a20251103074441`

3. **Package Build** (~15 seconds)
   - Creates wheel (.whl)
   - Creates source distribution (.tar.gz)
   - Validates package structure

4. **Publish to PyPI** (~10 seconds)
   - Uploads to https://pypi.org
   - Uses PYPI_TOKEN for authentication
   - Skips if version already exists

5. **Create GitHub Release** (~5 seconds)
   - Creates pre-release tag
   - Generates release notes
   - Uploads build artifacts

### Expected Output

```
✅ Run Tests - All Python versions passed
✅ Generate alpha version - 2025.11.0a20251103074441
✅ Build package - wheel and source created
✅ Publish to PyPI (Alpha) - Upload successful
✅ Create Git tag - v2025.11.0a20251103074441
✅ Create GitHub Release - Pre-release created
```

### Timeline

Total time: **~2-4 minutes** from push to published

---

## Publishing to Production (Beta-Prod Branch)

### When to Use Production

- Stable releases
- Version milestones
- User-facing releases
- Production deployments

### Publishing Process

#### Step 1: Update Version

```bash
# Edit pyproject.toml
vim pyproject.toml

# Change version:
[project]
version = "2025.11.0"  # Increment version
```

#### Step 2: Commit and Push

```bash
# Commit version change
git add pyproject.toml
git commit -m "chore: bump version to 2025.11.0"

# Merge to beta-prod
git checkout beta-prod
git pull origin beta-prod
git merge main

# Push to trigger deployment
git push origin beta-prod
```

#### Method 2: Force Publish (Same Version)

```bash
# Manually trigger with force option
gh workflow run "deploy-beta-prod-pybe.yml" \
  --ref beta-prod \
  -f force_publish=true
```

### What Happens During Production Publishing

1. **Version Check** (~5 seconds)
   - Reads version from pyproject.toml
   - Checks current version on PyPI
   - Determines if publish needed

2. **Tests Run** (2-3 minutes)
   - Same as alpha: all Python versions
   - All quality checks must pass

3. **Build Package** (~15 seconds)
   - Creates production build
   - No timestamp modification
   - Version as-is from pyproject.toml

4. **Publish to PyPI** (~10 seconds)
   - Uploads stable release
   - No pre-release flag
   - Listed as latest on PyPI

5. **Create GitHub Release** (~5 seconds)
   - Creates stable release (not pre-release)
   - Full release notes
   - Marked as "Latest"

### Expected Output

```
✅ Check Version - 2025.10.0 → 2025.11.0 (will publish)
✅ Run Tests - All Python versions passed
✅ Build package - wheel and source created
✅ Publish to PyPI - Upload successful
✅ Create Git tag - v2025.11.0
✅ Create GitHub Release - Stable release created
```

### Timeline

Total time: **~2-4 minutes** from push to published

---

## Checking Published Packages

### 1. Check on PyPI Website

**Main Package Page**:
https://pypi.org/project/bigconsole-sdk/

**Release History**:
https://pypi.org/project/bigconsole-sdk/#history

**Download Statistics**:
https://pypistats.org/packages/bigconsole-sdk

### 2. Check Using pip Command

```bash
# List all available versions
pip index versions bigconsole-sdk

# Output example:
# bigconsole-sdk (2025.11.0)
# Available versions: 2025.11.0, 2025.11.0a20251103074441, 1.0.0
```

### 3. Check Using PyPI API

```bash
# Get package information
curl -s https://pypi.org/pypi/bigconsole-sdk/json | jq .

# Get latest version
curl -s https://pypi.org/pypi/bigconsole-sdk/json | jq -r '.info.version'

# Get all versions
curl -s https://pypi.org/pypi/bigconsole-sdk/json | jq -r '.releases | keys[]'
```

### 4. Check GitHub Releases

**All Releases**:
https://github.com/Algoshred/bigconsole-sdk-python/releases

**Using GitHub CLI**:
```bash
# List releases
gh release list

# View specific release
gh release view v2025.11.0
```

### 5. Check GitHub Actions

**Workflow Runs**:
https://github.com/Algoshred/bigconsole-sdk-python/actions

**Using GitHub CLI**:
```bash
# List recent runs
gh run list --limit 10

# View specific run
gh run view <run-id>

# Watch running workflow
gh run watch <run-id>
```

### 6. Monitor Deployment Status

```bash
# Check alpha deployments
gh run list --workflow="deploy-beta-alpha-pybe.yml" --limit 5

# Check production deployments
gh run list --workflow="deploy-beta-prod-pybe.yml" --limit 5

# Check PR checks
gh run list --workflow="pr-checks-pybe.yml" --limit 5
```

---

## Published Package History

### Current Published Versions (as of 2025-11-03)

| Version | Type | Published Date | Status | Download |
|---------|------|----------------|---------|----------|
| 2025.11.0a20251103074441 | Alpha | 2025-11-03 | Latest Alpha | [PyPI](https://pypi.org/project/bigconsole-sdk/2025.11.0a20251103074441/) |
| 1.0.0 | Stable | 2025-10-17 | Latest Stable | [PyPI](https://pypi.org/project/bigconsole-sdk/1.0.0/) |
| 1.0.0a20251017103722 | Alpha | 2025-10-17 | Archived | [PyPI](https://pypi.org/project/bigconsole-sdk/1.0.0a20251017103722/) |
| 1.0.0a20251017101704 | Alpha | 2025-10-17 | Archived | [PyPI](https://pypi.org/project/bigconsole-sdk/1.0.0a20251017101704/) |

### Installation Commands

```bash
# Install latest stable version
pip install bigconsole-sdk

# Install specific stable version
pip install bigconsole-sdk==1.0.0

# Install latest alpha/pre-release
pip install --pre bigconsole-sdk

# Install specific alpha version
pip install bigconsole-sdk==2025.11.0a20251103074441

# Upgrade to latest
pip install --upgrade bigconsole-sdk
```

### GitHub Releases

All releases are available at:
https://github.com/Algoshred/bigconsole-sdk-python/releases

- Pre-releases (Alpha): Marked with "Pre-release" badge
- Stable releases: Marked with "Latest" badge

---

## Troubleshooting

### Issue: Workflow Not Triggered

**Problem**: Push to branch doesn't trigger workflow

**Solution**:
```bash
# Check workflow trigger paths in .github/workflows/
# Only these paths trigger workflows:
# - src/**
# - tests/**
# - pyproject.toml
# - setup.py
# - requirements*.txt

# If you only changed docs, workflow won't run
# To force trigger:
gh workflow run "deploy-beta-alpha-pybe.yml" --ref beta-alpha
```

### Issue: Tests Failing

**Problem**: Workflow fails during test phase

**Solution**:
```bash
# Run tests locally first
pytest --verbose

# Check specific test
pytest tests/test_client.py -v

# Check linting
flake8 src/ tests/ examples/

# Check formatting
black --check src/ tests/ examples/
isort --check-only src/ tests/ examples/

# Fix formatting
black src/ tests/ examples/
isort src/ tests/ examples/
```

### Issue: Version Already Exists

**Problem**: "File already exists" error from PyPI

**Solution**:
```bash
# For production: increment version in pyproject.toml
vim pyproject.toml  # Change 2025.11.0 → 2025.11.1

# For alpha: versions are auto-timestamped, this shouldn't happen
# If it does, wait 1 second and push again
```

### Issue: Authentication Failed

**Problem**: PyPI authentication error

**Solution**:
```bash
# Verify PYPI_TOKEN secret exists
gh secret list | grep PYPI_TOKEN

# Check workflow has id-token permission
grep -A 2 "permissions:" .github/workflows/deploy-*.yml

# Should show:
# permissions:
#   contents: write
#   id-token: write
```

### Issue: Package Not Visible on PyPI

**Problem**: Workflow succeeded but package not on PyPI

**Solution**:
```bash
# Wait 2-5 minutes for PyPI to index
# Check workflow logs
gh run view <run-id> --log

# Verify upload step completed
gh run view <run-id> --log | grep "Publish to PyPI"

# Check PyPI status
curl -s https://pypi.org/pypi/bigconsole-sdk/json | jq '.info.version'
```

### Issue: Import Fails After Install

**Problem**: `import bigconsole_sdk` fails

**Solution**:
```bash
# Verify installation
pip show bigconsole-sdk

# Check installed files
pip show --files bigconsole-sdk

# Reinstall
pip uninstall bigconsole-sdk
pip install bigconsole-sdk

# Install from specific version
pip install bigconsole-sdk==2025.11.0a20251103074441
```

---

## Best Practices

### 1. Testing Before Publishing

Always test locally before pushing:

```bash
# Run all tests
pytest --verbose

# Run quality checks
make lint  # or flake8, black, isort

# Build package locally
python -m build

# Test installation
pip install dist/*.whl
python -c "import bigconsole_sdk; print(bigconsole_sdk.__version__)"
```

### 2. Version Numbering

- **Increment patch** (X.X.1) for bug fixes
- **Increment minor** (X.11.0) for new features
- **Increment major** (2026.1.0) for new year or breaking changes

### 3. Alpha Testing

- Always test features in alpha first
- Get feedback on alpha releases
- Fix issues before production release

### 4. Release Notes

Document changes in each release:
- Bug fixes
- New features
- Breaking changes
- Deprecations

### 5. Monitoring

Set up monitoring for:
- GitHub Actions notifications
- PyPI download stats
- User feedback and issues

---

## Quick Reference

### Publish Alpha
```bash
git checkout beta-alpha
# Make changes
git push origin beta-alpha
# Wait 2-4 minutes
```

### Publish Production
```bash
vim pyproject.toml  # Update version
git checkout beta-prod
git merge main
git push origin beta-prod
# Wait 2-4 minutes
```

### Check Status
```bash
gh run list --limit 5
gh release list
pip index versions bigconsole-sdk
```

### Install Package
```bash
pip install bigconsole-sdk              # Latest stable
pip install --pre bigconsole-sdk        # Latest alpha
pip install bigconsole-sdk==2025.11.0   # Specific version
```

---

## Support & Resources

- **Documentation**: `/docs/`
- **Examples**: `/scripts/examples/`
- **Issues**: https://github.com/Algoshred/bigconsole-sdk-python/issues
- **PyPI**: https://pypi.org/project/bigconsole-sdk/
- **CI/CD**: https://github.com/Algoshred/bigconsole-sdk-python/actions

---

Last Updated: 2025-11-03
Version: 2025.11.0
