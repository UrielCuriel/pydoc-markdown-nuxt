"""
Pytest configuration file for pydoc-markdown-nuxt.

This file contains shared fixtures and configuration for all tests.
"""

import os
import sys

import pytest

# Add src to path so we can import our module without installing it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Fixture for temporary test directory
@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for test output."""
    test_dir = tmp_path / "test_output"
    test_dir.mkdir(exist_ok=True)
    return test_dir


# Fixture for sample docstrings
@pytest.fixture
def sample_arguments_docstring():
    """Provide a sample docstring with arguments section."""
    return """
A test function to demonstrate argument rendering.

**Arguments**:

- `param1` - The first parameter
- `param2: str` - The second parameter with type
- `param3: int` - The third parameter with type

**Returns**:

Some return value
"""


@pytest.fixture
def comprehensive_docstring():
    """Provide a comprehensive docstring with multiple sections."""
    return """
A comprehensive test function to demonstrate all docstring conversions.

**Arguments**:

- `param1` - The first parameter
- `param2: str` - The second parameter with type
- `param3: int` - The third parameter with type

**Returns**:

A dictionary containing the processed results with keys 'status' and 'data'.

**Examples**:

```python
result = test_function("hello", "world", 42)
print(result)
```

```bash
# You can also use it from command line
python script.py --param1 hello --param2 world --param3 42
```

**Notes**:

This function is designed to be used in testing scenarios. Make sure to handle
the return value appropriately.

**Warnings**:

Do not use this function in production without proper validation of inputs.

**Raises**:

- `ValueError`: When param3 is negative
- `TypeError`: When param2 is not a string
"""
