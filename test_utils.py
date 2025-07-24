#!/usr/bin/env python3
"""
Test script for Nuxt Content utilities
"""

import sys
import os

# Add src to path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pydoc_markdown_nuxt.utils import (
    create_mdc_alert,
    create_mdc_code_group,
    create_mdc_tabs,
    create_navigation_entry,
    enhance_frontmatter_for_nuxt,
    generate_api_breadcrumbs,
    format_python_signature_for_mdc,
    create_api_overview_table,
    NuxtContentHelper
)

def test_mdc_components():
    """Test MDC component creation utilities."""
    print("Testing MDC component utilities...")
    
    # Test alert
    alert = create_mdc_alert("This is important information", "warning", "Important")
    expected_alert = '::alert{type="warning" title="Important"}\nThis is important information\n::'
    assert alert == expected_alert
    print("✅ MDC alert creation")
    
    # Test code group
    code_blocks = [
        {"language": "python", "filename": "example.py", "code": "print('Hello, World!')"},
        {"language": "javascript", "filename": "example.js", "code": "console.log('Hello, World!');"}
    ]
    code_group = create_mdc_code_group(code_blocks)
    assert "::code-group" in code_group
    assert "```python [example.py]" in code_group
    assert "```javascript [example.js]" in code_group
    print("✅ MDC code group creation")
    
    # Test tabs
    tabs = [
        {"title": "Tab 1", "content": "Content 1"},
        {"title": "Tab 2", "content": "Content 2"}
    ]
    tab_component = create_mdc_tabs(tabs)
    assert "::tabs" in tab_component
    assert 'label="Tab 1"' in tab_component
    print("✅ MDC tabs creation")

def test_navigation_utilities():
    """Test navigation and frontmatter utilities."""
    print("\nTesting navigation utilities...")
    
    # Test navigation entry
    nav_entry = create_navigation_entry(
        "API Reference", 
        "/docs/api", 
        icon="heroicons:code-bracket",
        badge="New",
        description="Complete API documentation"
    )
    
    expected_keys = {"title", "to", "icon", "badge", "description"}
    assert set(nav_entry.keys()) == expected_keys
    assert nav_entry["title"] == "API Reference"
    print("✅ Navigation entry creation")
    
    # Test frontmatter enhancement
    basic_frontmatter = {"title": "My Page"}
    enhanced = enhance_frontmatter_for_nuxt(basic_frontmatter, "reference")
    
    assert "layout" in enhanced
    assert "navigation" in enhanced
    assert "aside" in enhanced
    assert "toc" in enhanced
    print("✅ Frontmatter enhancement")

def test_api_utilities():
    """Test API documentation utilities."""
    print("\nTesting API utilities...")
    
    # Test breadcrumbs
    breadcrumbs = generate_api_breadcrumbs("mypackage.core.DataProcessor", "/docs")
    
    assert len(breadcrumbs) == 4  # docs, mypackage, core, DataProcessor
    assert breadcrumbs[0]["title"] == "Documentation"
    assert breadcrumbs[0]["to"] == "/docs"
    assert breadcrumbs[-1]["title"] == "DataProcessor"
    assert "to" not in breadcrumbs[-1]  # Last item should not have link
    print("✅ API breadcrumbs generation")
    
    # Test signature formatting
    signature = "def my_function(param1: str, param2: int = 0) -> bool"
    formatted = format_python_signature_for_mdc(signature)
    
    assert formatted.startswith("```python")
    assert formatted.endswith("```")
    print("✅ Python signature formatting")
    
    # Test API overview table
    classes = [
        {"name": "DataProcessor", "description": "Process data efficiently", "link": "/api/data-processor"},
        {"name": "ConfigManager", "description": "Manage configuration settings"}
    ]
    table = create_api_overview_table(classes)
    
    assert "| Class | Description |" in table
    assert "[DataProcessor](/api/data-processor)" in table
    assert "ConfigManager" in table
    print("✅ API overview table creation")

def test_nuxt_content_helper():
    """Test the NuxtContentHelper class."""
    print("\nTesting NuxtContentHelper...")
    
    helper = NuxtContentHelper(base_url="/docs", use_mdc=True)
    
    # Test hero section
    hero = helper.create_hero_section(
        "Welcome to Our API",
        "Complete documentation for our Python library",
        [{"label": "Get Started", "url": "/docs/getting-started", "variant": "primary"}]
    )
    
    assert "::hero" in hero
    assert "Welcome to Our API" in hero
    assert "::button[Get Started]" in hero
    print("✅ Hero section creation")
    
    # Test feature list
    features = [
        {"title": "Easy to Use", "description": "Simple and intuitive API", "icon": "heroicons:heart"},
        {"title": "Fast", "description": "Optimized for performance", "icon": "heroicons:bolt"}
    ]
    feature_list = helper.create_feature_list(features)
    
    assert "::feature" in feature_list
    assert "Easy to Use" in feature_list
    assert 'icon="heroicons:heart"' in feature_list
    print("✅ Feature list creation")
    
    # Test without MDC
    helper_no_mdc = NuxtContentHelper(use_mdc=False)
    hero_no_mdc = helper_no_mdc.create_hero_section("Title", "Description")
    
    assert "::hero" not in hero_no_mdc
    assert "# Title" in hero_no_mdc
    print("✅ Non-MDC mode")

def test_content_examples():
    """Test generating example content."""
    print("\nTesting content examples...")
    
    # Create a complete example page
    helper = NuxtContentHelper()
    
    # Generate different types of content
    alert = create_mdc_alert("Make sure to install dependencies first", "warning")
    
    code_example = create_mdc_code_group([
        {
            "language": "bash",
            "filename": "install.sh", 
            "code": "pip install mypackage"
        },
        {
            "language": "python",
            "filename": "usage.py",
            "code": "from mypackage import DataProcessor\nprocessor = DataProcessor()"
        }
    ])
    
    content = f"""# Getting Started

Welcome to our documentation!

{alert}

## Installation

{code_example}

## Next Steps

Continue with the [API Reference](/docs/api).
"""
    
    # Verify the content contains expected elements
    assert "::alert" in content
    assert "::code-group" in content
    assert "```bash [install.sh]" in content
    assert "```python [usage.py]" in content
    
    print("✅ Complete content example generation")
    print(f"Generated content length: {len(content)} characters")

def main():
    """Run all utility tests."""
    print("Testing pydoc-markdown-nuxt utilities...")
    print("=" * 50)
    
    try:
        test_mdc_components()
        test_navigation_utilities()
        test_api_utilities()
        test_nuxt_content_helper()
        test_content_examples()
        
        print("\n🎉 All utility tests passed!")
        print("\nThe utility functions provide:")
        print("• MDC component generation (alerts, code groups, tabs)")
        print("• Navigation and frontmatter helpers")
        print("• API documentation utilities")
        print("• Content formatting helpers")
        print("• Nuxt Content integration tools")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())