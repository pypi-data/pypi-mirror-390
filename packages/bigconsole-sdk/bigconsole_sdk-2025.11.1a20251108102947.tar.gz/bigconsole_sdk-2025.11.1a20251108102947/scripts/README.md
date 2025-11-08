# Bigconsole SDK - Test Scripts

This directory contains test scripts and examples for the Bigconsole SDK.

## Directory Structure

```
scripts/
├── README.md                          # This file
└── examples/
    ├── test_sdk_installation.py       # Test SDK installation
    ├── test_all_modules.py            # Test all SDK modules
    └── test_bigconsole_operations.py  # Test bigconsole CRUD operations
```

## Test Scripts

### 1. test_sdk_installation.py

**Purpose**: Verify SDK installation and module imports

**Usage**:
```bash
python scripts/examples/test_sdk_installation.py
```

**What it tests**:
- All 21 SDK modules can be imported
- SDK version information
- Basic SDK initialization
- Module availability

**Prerequisites**: None (works with any installation)

### 2. test_all_modules.py

**Purpose**: Comprehensive test of all SDK modules

**Usage**:
```bash
python scripts/examples/test_all_modules.py
```

**What it tests**:
- All modules are accessible from SDK instance
- Key methods exist on each module
- Client configuration options
- Module initialization

**Prerequisites**: None (uses dummy credentials)

### 3. test_bigconsole_operations.py

**Purpose**: Test real bigconsole operations

**Usage**:
```bash
# Set environment variables
export BIGCONSOLE_API_URL='https://api.yourbigconsole.com/graphql'
export BIGCONSOLE_API_KEY='your-api-key-here'

# Run the test
python scripts/examples/test_bigconsole_operations.py
```

**What it tests**:
- List workspaces
- Create workspace
- Get workspace details
- Update workspace
- Delete workspace

**Prerequisites**:
- Valid API URL and API key
- Active bigconsole backend

## Environment Variables

For scripts that require API access:

```bash
# Required for live testing
export BIGCONSOLE_API_URL='https://api.example.com/graphql'
export BIGCONSOLE_API_KEY='your-api-key'

# Optional
export BIGCONSOLE_ORG_ID='your-org-id'
export BIGCONSOLE_PRODUCT_ID='your-product-id'
```

## Quick Start

### 1. Install the SDK

```bash
# From PyPI
pip install bigconsole-sdk

# Or from source
pip install -e .
```

### 2. Run Installation Test

```bash
python scripts/examples/test_sdk_installation.py
```

Expected output:
```
Testing Bigconsole SDK Installation
====================================

✅ Main SDK Package......................... OK
✅ GraphQL Client........................... OK
✅ Workspace Module......................... OK
...
Results: 21/21 modules imported successfully
```

### 3. Run Module Test

```bash
python scripts/examples/test_all_modules.py
```

Expected output:
```
Testing All Bigconsole SDK Modules
==================================

✅ Workspace Management............... Available
   └─ Workspace operations and invitations
...
Module Test Results: 19/19 modules available
```

### 4. Run Live Tests (Optional)

```bash
# Set credentials
export BIGCONSOLE_API_URL='https://api.yourbigconsole.com/graphql'
export BIGCONSOLE_API_KEY='your-api-key'

# Run bigconsole operations test
python scripts/examples/test_bigconsole_operations.py
```

## Adding New Test Scripts

When creating new test scripts:

1. **File Naming**: Use pattern `test_<module>_<operation>.py`
2. **Documentation**: Include docstring at top with purpose and usage
3. **Exit Codes**: Return 0 for success, 1 for failure
4. **Error Handling**: Catch and display meaningful error messages
5. **Environment**: Document required environment variables
6. **Summary**: Print clear test results summary

### Template

```python
#!/usr/bin/env python3
"""
Test Script: <Description>

Purpose: <What this tests>

Prerequisites:
    - SDK installed: pip install bigconsole-sdk
    - Environment variables: BIGCONSOLE_API_URL, BIGCONSOLE_API_KEY

Usage:
    python scripts/examples/test_<name>.py
"""

import sys
import os


def main():
    """Run tests."""
    print("\\n🔍 Test Name\\n")

    # Your test code here

    # Return exit code
    return 0  # Success


if __name__ == "__main__":
    sys.exit(main())
```

## Testing Checklist

Before each release, run:

- [ ] `test_sdk_installation.py` - Verify installation
- [ ] `test_all_modules.py` - Verify all modules
- [ ] `test_bigconsole_operations.py` - Verify API operations
- [ ] Check all scripts have execute permissions
- [ ] Update this README if new scripts added

## Common Issues

### ImportError: No module named 'bigconsole_sdk'

**Solution**:
```bash
pip install bigconsole-sdk
# or for development
pip install -e .
```

### Authentication Failed

**Solution**:
```bash
# Verify environment variables are set
echo $BIGCONSOLE_API_URL
echo $BIGCONSOLE_API_KEY

# Check API key is valid
curl -H "Authorization: Bearer $BIGCONSOLE_API_KEY" $BIGCONSOLE_API_URL
```

### Tests Fail with Connection Error

**Solution**:
- Check network connectivity
- Verify API URL is correct
- Check firewall settings
- Verify backend is running

## Contributing

To contribute new test scripts:

1. Create script in `scripts/examples/`
2. Follow the template above
3. Add documentation to this README
4. Test on multiple Python versions (3.8-3.12)
5. Submit pull request

## Support

For issues or questions:
- GitHub Issues: https://github.com/Algoshred/bigconsole-sdk-python/issues
- Documentation: `/docs/`
- Examples: This directory

---

Last Updated: 2025-11-03
