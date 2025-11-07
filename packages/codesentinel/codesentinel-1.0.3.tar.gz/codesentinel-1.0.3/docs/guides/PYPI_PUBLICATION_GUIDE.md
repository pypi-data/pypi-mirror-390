# CodeSentinel v1.0.3.beta - PyPI Publication Guide

## Overview

This guide provides step-by-step instructions for publishing CodeSentinel v1.0.3.beta to PyPI. The package has completed comprehensive testing and is ready for distribution.

**Version:** 1.0.3.beta (normalized to 1.0.3b0 by PyPI/setuptools)  
**Status:** Tested and approved for publication  
**Distributions Ready:** 2 (sdist + wheel)

## Pre-Publication Checklist

- ✅ Version updated to 1.0.3.beta in setup.py, pyproject.toml, **init**.py
- ✅ Distributions built: sdist (91 KB), wheel (77 KB)
- ✅ All tests passed (22/22)
- ✅ CLI functional (all commands work)
- ✅ GUI functional (wizard launches)
- ✅ File integrity system operational
- ✅ Performance metrics acceptable (1.2s for baseline)
- ✅ No breaking changes detected
- ✅ Documentation current

## Step 1: PyPI Test Repository Setup

### 1.1 Create PyPI Account (if needed)

If you don't have a PyPI account:

1. Visit <https://test.pypi.org/account/register/>
2. Create account and verify email
3. **IMPORTANT:** Save your credentials securely

### 1.2 Create PyPI API Token (Recommended)

For secure uploads without storing passwords:

1. Go to <https://test.pypi.org/legacy/manage/account/tokens/>
2. Click "Add API token"
3. Give it a name: "CodeSentinel v1.0.3.beta"
4. **SAVE THE TOKEN** (shown only once)

### 1.3 Create .pypirc Configuration

Create `~/.pypirc` (Linux/macOS) or `%APPDATA%\pip\pip.ini` (Windows):

```ini
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE
```

**Windows Paths:**

- `C:\Users\USERNAME\AppData\Roaming\pip\pip.ini`

**Permissions:** 600 (chmod on Linux/macOS)

## Step 2: Validate Package

Before uploading, validate the distribution files:

```bash
# Validate wheel
python -m twine check dist/codesentinel-1.0.3b0-py3-none-any.whl

# Validate source distribution
python -m twine check dist/codesentinel-1.0.3b0.tar.gz

# Check all distributions
python -m twine check dist/*
```

Expected output: `reading codesentinel-1.0.3b0-py3-none-any.whl: running egg_info`

## Step 3: Upload to PyPI Test Repository

### 3.1 Upload All Distributions

```bash
python -m twine upload --repository testpypi dist/codesentinel-1.0.3b0*
```

You will be prompted for:

- Username: `__token__`
- Password: `pypi-YOUR_TOKEN_HERE` (paste your token)

### 3.2 Verify Test Upload

1. Check: <https://test.pypi.org/project/codesentinel/>
2. Look for version `1.0.3b0`
3. Verify all files present (sdist + wheel)
4. Check README and metadata display correctly

### 3.3 Test Installation from Test PyPI

In a clean environment:

```bash
# Create test environment
python -m venv test_pypi_install

# Activate (Windows)
test_pypi_install\Scripts\activate

# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ codesentinel==1.0.3b0

# Test it works
codesentinel status
codesentinel --help
```

**Expected result:** Package installs and commands work

## Step 4: Validation Testing from Test PyPI

Run quick validation tests after installing from test PyPI:

```bash
# Test version
codesentinel status | grep Version

# Test integrity
codesentinel integrity generate --patterns "*.py"

# Test dev-audit
codesentinel !!!! --agent
```

All should complete without errors.

## Step 5: Production PyPI Upload (After Test Validation)

### 5.1 Prerequisites

- Test PyPI installation validated successfully
- All test environment tests passed
- Ready for production release

### 5.2 Upload to Production PyPI

```bash
python -m twine upload dist/codesentinel-1.0.3b0*
```

This will upload to: <https://pypi.org/project/codesentinel/>

### 5.3 Verify Production Upload

1. Check: <https://pypi.org/project/codesentinel/>
2. Look for version `1.0.3b0`
3. Verify all metadata is correct
4. Check it shows as "pre-release" (beta)

## Step 6: Production Installation Test

In a clean environment:

```bash
# Create production test environment
python -m venv prod_test

# Activate (Windows)
prod_test\Scripts\activate

# Install from production PyPI (default)
pip install codesentinel==1.0.3b0

# Test it works
codesentinel status
codesentinel integrity --help
```

## Step 7: Create GitHub Release

1. Go to: <https://github.com/joediggidyyy/CodeSentinel/releases>
2. Click "Create a new release"
3. Tag: `v1.0.3-beta`
4. Title: `CodeSentinel v1.0.3.beta - File Integrity Validation System`
5. Release notes:

```markdown
## What's New in v1.0.3.beta

### Major Features
- **File Integrity Validation System**: Comprehensive SHA256-based integrity checking
  - Generate baseline of file states
  - Verify files against baseline
  - Whitelist patterns for expected changes
  - Mark critical files for priority monitoring

### Commands
- `codesentinel integrity generate` - Create file baseline
- `codesentinel integrity verify` - Check against baseline
- `codesentinel integrity whitelist` - Manage exclusion patterns
- `codesentinel integrity critical` - Mark priority files

### Performance
- Baseline generation: ~1.2 seconds
- Verification: ~1.4 seconds
- Supports 1000+ files efficiently

### Bug Fixes
- Fixed process monitor lifecycle
- Improved error handling
- Cross-platform compatibility improvements

### Beta Testing
This is a beta release. Please report issues at:
https://github.com/joediggidyyy/CodeSentinel/issues

### Installation
```bash
pip install codesentinel==1.0.3b0
```

## Rollback Procedure (If Needed)

If critical issues are found after publishing:

### For Test PyPI

1. Contact PyPI support to remove the release
2. Fix issues in the codebase
3. Bump to v1.0.3b1 or v1.0.3rc1
4. Republish with new version

### For Production PyPI

1. Use `python -m twine yank` (requires PyPI permissions)
2. Or contact PyPI support
3. Clearly mark as unsafe with security/critical issue notes

```bash
python -m twine yank codesentinel-1.0.3b0 -r pypi
```

## Troubleshooting

### Issue: "HTTPError: 403 Forbidden" during upload

**Causes:**

- Invalid token
- Token has insufficient permissions
- Token is for wrong repository (test vs. production)

**Solution:**

1. Generate new token from test.pypi.org or pypi.org
2. Update .pypirc with correct token
3. Verify repository URL in .pypirc

### Issue: "File already exists" error

**Cause:** Attempting to upload same version twice

**Solution:**

- Test PyPI: Versions can be re-uploaded (allowed for testing)
- Production PyPI: Cannot re-upload same version (security)
  - Create new version: v1.0.3b1
  - Use `python -m twine yank` if absolutely necessary

### Issue: Package won't install from PyPI

**Causes:**

- Wrong Python version (requires >=3.13)
- Missing dependencies
- Network timeout

**Solution:**

```bash
# Try with verbose output
pip install -v codesentinel==1.0.3b0

# Check Python version
python --version

# Install with --no-cache-dir if needed
pip install --no-cache-dir codesentinel==1.0.3b0
```

## Post-Publication Tasks

### Immediate (within 24 hours)

1. ✅ Announce on GitHub releases
2. ✅ Pin release announcement in Issues
3. ✅ Notify beta testers
4. Monitor for bug reports

### Week 1

- Collect user feedback
- Monitor GitHub issues
- Test on additional platforms if needed

### Before v1.0.3 Final Release

- Review all feedback from beta period
- Create v1.0.3 (remove beta tag) when ready
- Full documentation update
- Final testing cycle

## Version Management

### Current Versions

- Development: v1.0.4-dev (main branch)
- Beta Testing: v1.0.3.beta (feature/v1.0.3-integrity-validation)
- Production: v1.0.1 (main branch, stable)

### Next Steps After Beta

1. Beta period: 2 weeks (collect feedback)
2. v1.0.3 Release Candidate (if major feedback)
3. v1.0.3 Final Production Release

## Documentation References

- **Installation Guide:** README.md
- **File Integrity Docs:** docs/
- **API Documentation:** codesentinel/utils/file_integrity.py
- **Test Results:** V1_0_3_BETA_TEST_REPORT.md

## Support & Communication

- **Issues:** <https://github.com/joediggidyyy/CodeSentinel/issues>
- **Discussions:** <https://github.com/joediggidyyy/CodeSentinel/discussions>
- **Email:** <joediggidy3@gmail.com>

---

**Publication Checklist Generated:** November 6, 2025  
**Status:** Ready for Test PyPI Upload  
**Next Step:** Upload to test.pypi.org and validate
