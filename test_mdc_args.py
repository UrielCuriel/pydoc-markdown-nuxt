#!/usr/bin/env python3
"""
Test script to verify MDC arguments generation
"""

import tempfile
import os
from pathlib import Path

from src.pydoc_markdown_nuxt.renderer import NuxtRenderer, NuxtPage
import docspec

def test_mdc_arguments():
    """Test that MDC arguments are generated correctly."""
    
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in: {tmpdir}")
        
        # Create a simple function with arguments documentation
        func = docspec.Function(
            name="test_function",
            location=docspec.Location(filename="test.py", lineno=1),
            modifiers=None,
            return_type=None,
            decorations=None,
            docstring="""
            A test function to demonstrate argument rendering.
            
            **Arguments**:
            
            - `param1` - The first parameter
            - `param2: str` - The second parameter with type
            - `param3: int` - The third parameter with type
            
            **Returns**:
            
            Some return value
            """,
            args=[
                docspec.Argument(
                    name="param1", 
                    type=None,
                    location=docspec.Location(filename="test.py", lineno=1)
                ),
                docspec.Argument(
                    name="param2", 
                    type=None,
                    location=docspec.Location(filename="test.py", lineno=1)
                ),
                docspec.Argument(
                    name="param3", 
                    type=None,
                    location=docspec.Location(filename="test.py", lineno=1)
                ),
            ]
        )
        
        # Create a module containing the function
        module = docspec.Module(
            name="test_module",
            location=docspec.Location(filename="test.py", lineno=1),
            docstring="Test module",
            members=[func]
        )
        
        # Import Pages class
        from pydoc_markdown.util.pages import Pages
        
        # Create renderer configuration
        pages = Pages()
        pages.append(NuxtPage(
            title="Test",
            name="test",
            source="README.md"  # Use a simpler approach
        ))
        
        renderer = NuxtRenderer(
            content_directory=tmpdir,
            use_mdc=True,
            mdc_components={"arguments": "UArguments"},
            pages=pages
        )
        
        # Create a simple README file to test
        readme_content = '''
# Test Function

A test function to demonstrate argument rendering.

**Arguments**:

- `param1` - The first parameter
- `param2: str` - The second parameter with type
- `param3: int` - The third parameter with type

**Returns**:

Some return value
'''
        
        with open(os.path.join(tmpdir, "../README.md"), "w") as f:
            f.write(readme_content)
        
        # Mock context
        class MockContext:
            directory = Path(".")
        
        renderer.init(MockContext())
        
        # Render the documentation
        renderer.render([module])
        
        # Check the output
        output_file = Path(tmpdir) / "test.md"
        if output_file.exists():
            content = output_file.read_text()
            print("Generated content:")
            print("=" * 50)
            print(content)
            print("=" * 50)
            
            # Check if MDC component was generated
            if "::u-arguments" in content:
                print("✅ SUCCESS: MDC arguments component found!")
            else:
                print("❌ FAIL: MDC arguments component NOT found")
                print("Looking for traditional Arguments section...")
                if "**Arguments**:" in content:
                    print("Found traditional Arguments section - conversion failed")
                else:
                    print("No Arguments section found at all")
        else:
            print(f"❌ FAIL: Output file {output_file} was not created")

if __name__ == "__main__":
    test_mdc_arguments()
