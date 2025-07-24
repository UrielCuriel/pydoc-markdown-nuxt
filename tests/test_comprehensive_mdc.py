"""
Test comprehensive MDC processing with pytest.
"""
import pytest
from src.pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer

def test_comprehensive_mdc(comprehensive_docstring):
    """Test comprehensive MDC processing."""
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
    result = renderer._process_docstring_for_mdc(comprehensive_docstring)
    
    # Assert expected components
    assert "::u-arguments" in result
    assert "::u-returns" in result
    assert "::u-code-group" in result and "```python" in result
    assert '::u-alert{type="info" title="Note"}' in result
    assert '::u-alert{type="warning" title="Warning"}' in result
    assert "::u-callout" in result and "ValueError" in result
