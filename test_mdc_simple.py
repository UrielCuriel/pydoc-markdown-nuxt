#!/usr/bin/env python3
"""
Simple test to verify MDC arguments conversion
"""

from src.pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer

def test_mdc_conversion():
    """Test MDC arguments conversion directly."""
    
    # Sample docstring with Arguments section
    sample_docstring = """
A test function to demonstrate argument rendering.

**Arguments**:

- `param1` - The first parameter
- `param2: str` - The second parameter with type
- `param3: int` - The third parameter with type

**Returns**:

Some return value
"""
    
    # Create MDC renderer
    renderer = MDCMarkdownRenderer(use_mdc=True, mdc_components={"arguments": "UArguments"})
    
    # Process the docstring
    result = renderer._convert_arguments_to_mdc(sample_docstring)
    
    print("Original docstring:")
    print("=" * 50)
    print(sample_docstring)
    print("=" * 50)
    
    print("\nProcessed docstring:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # Check if MDC component was generated
    if "::u-arguments" in result:
        print("✅ SUCCESS: MDC arguments component found!")
        return True
    else:
        print("❌ FAIL: MDC arguments component NOT found")
        if "**Arguments**:" in result:
            print("Found traditional Arguments section - conversion failed")
        else:
            print("No Arguments section found at all")
        return False

if __name__ == "__main__":
    test_mdc_conversion()
