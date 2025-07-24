#!/usr/bin/env python3
"""
Test comprehensive MDC processing with multiple docstring sections
"""

from src.pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer

def test_comprehensive_mdc():
    """Test comprehensive MDC processing."""
    
    # Sample docstring with multiple sections
    sample_docstring = """
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
    
    # Create MDC renderer
    renderer = MDCMarkdownRenderer(
        use_mdc=True, 
        mdc_components={
            "arguments": "UArguments",
            "returns": "UReturns", 
            "examples": "UCodeGroup",
            "notes": "UAlert",
            "warnings": "UAlert",
            "raises": "UCallout",
            "code_block": "UCodeGroup"
        }
    )
    
    # Process the docstring
    result = renderer._process_docstring_for_mdc(sample_docstring)
    
    print("Original docstring:")
    print("=" * 80)
    print(sample_docstring)
    print("=" * 80)
    
    print("\nProcessed docstring with MDC components:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    
    # Check for various MDC components
    checks = {
        "Arguments": "::u-arguments" in result,
        "Returns": "::u-returns" in result,
        "Examples": "::u-code-group" in result and "```python" in result,
        "Notes": '::u-alert{type="info" title="Note"}' in result,
        "Warnings": '::u-alert{type="warning" title="Warning"}' in result,
        "Raises": "::u-callout" in result and "ValueError" in result,
    }
    
    print("\nComponent conversion checks:")
    print("-" * 40)
    all_passed = True
    for section, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{section:12}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    overall = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"Overall: {overall}")
    
    return all_passed

if __name__ == "__main__":
    test_comprehensive_mdc()
