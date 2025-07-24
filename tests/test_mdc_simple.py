"""
Test MDC arguments conversion with pytest.
"""
import pytest
from src.pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer

def test_mdc_conversion(sample_arguments_docstring):
    """Test that MDC arguments are converted correctly."""
    # Create MDC renderer
    renderer = MDCMarkdownRenderer(use_mdc=True, mdc_components={"arguments": "UArguments"})
    
    # Process the docstring
    result = renderer._convert_arguments_to_mdc(sample_arguments_docstring)
    
    # Assert the expected results
    assert "::u-arguments" in result
    assert "param1" in result
    assert "param2: str" in result
    assert "param3: int" in result
    assert "**Arguments**:" not in result
