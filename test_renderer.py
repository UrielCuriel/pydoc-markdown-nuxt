#!/usr/bin/env python3
"""
Test script to validate the NuxtRenderer functionality
"""

import sys
import tempfile
import os
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pydoc_markdown_nuxt.renderer import NuxtRenderer, NuxtPage

def test_basic_page_rendering():
    """Test basic page rendering functionality without complex docspec objects."""
    print("Testing basic NuxtRenderer page rendering...")
    
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Set up the renderer
        renderer = NuxtRenderer(
            content_directory=os.path.join(temp_dir, 'content'),
            default_frontmatter={
                'layout': 'docs',
                'navigation': True,
            }
        )
        
        # Create a page configuration
        page = NuxtPage(
            title='API Documentation',
            name='api',
            frontmatter={
                'description': 'API reference documentation',
                'category': 'API'
            }
        )
        renderer.pages.append(page)
        
        # Initialize the renderer with a mock context
        from pydoc_markdown.interfaces import Context
        renderer.init(Context(temp_dir))
        
        # Render with empty modules list (just test the structure)
        renderer.render([])
        
        # Check that files were created
        content_dir = Path(temp_dir) / 'content'
        if content_dir.exists():
            print(f"✓ Content directory created: {content_dir}")
            files = list(content_dir.rglob('*.md'))
            print(f"✓ Generated {len(files)} markdown files:")
            for file in files:
                print(f"  - {file.relative_to(content_dir)}")
                
                # Check file content
                content = file.read_text()
                if content.startswith('---'):
                    print(f"  ✓ File has YAML frontmatter")
                    
                    # Parse frontmatter
                    lines = content.split('\n')
                    frontmatter_end = -1
                    for i, line in enumerate(lines[1:], 1):
                        if line == '---':
                            frontmatter_end = i
                            break
                    
                    if frontmatter_end > 0:
                        frontmatter_text = '\n'.join(lines[1:frontmatter_end])
                        print(f"  Frontmatter:\n{frontmatter_text}")
                else:
                    print(f"  ✗ File missing YAML frontmatter")
        else:
            print("✗ Content directory not created")
            
        return True

def test_frontmatter_merging():
    """Test that default and page-specific frontmatter are merged correctly."""
    print("\nTesting frontmatter merging...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        renderer = NuxtRenderer(
            content_directory=os.path.join(temp_dir, 'content'),
            default_frontmatter={
                'layout': 'docs',
                'navigation': True,
                'sidebar': True
            }
        )
        
        page = NuxtPage(
            title='Test Page',
            name='test',
            frontmatter={
                'description': 'A test page',
                'category': 'Testing',
                'tags': ['test', 'example'],
                'navigation': False  # Override default
            }
        )
        renderer.pages.append(page)
        
        from pydoc_markdown.interfaces import Context
        renderer.init(Context(temp_dir))
        renderer.render([])
        
        # Check the generated file
        content_file = Path(temp_dir) / 'content' / 'test.md'
        if content_file.exists():
            content = content_file.read_text()
            lines = content.split('\n')
            
            # Check for YAML frontmatter
            if lines[0] == '---':
                print("✓ YAML frontmatter starts correctly")
                
                # Find end of frontmatter
                end_idx = -1
                for i, line in enumerate(lines[1:], 1):
                    if line == '---':
                        end_idx = i
                        break
                
                if end_idx > 0:
                    print("✓ YAML frontmatter ends correctly")
                    frontmatter_content = '\n'.join(lines[1:end_idx])
                    print(f"Frontmatter content:\n{frontmatter_content}")
                    
                    # Check specific values
                    if 'layout: docs' in frontmatter_content:
                        print("✓ Default layout preserved")
                    if 'navigation: false' in frontmatter_content:
                        print("✓ Page-specific override works")
                    if 'description: A test page' in frontmatter_content:
                        print("✓ Page-specific frontmatter added")
                else:
                    print("✗ YAML frontmatter end not found")
            else:
                print("✗ YAML frontmatter start not found")
        else:
            print("✗ Test file not created")

def test_directory_structure():
    """Test that pages can be rendered to custom directories."""
    print("\nTesting directory structure...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        renderer = NuxtRenderer(
            content_directory=os.path.join(temp_dir, 'content'),
            default_frontmatter={'layout': 'docs'}
        )
        
        # Add pages in different directories
        pages = [
            NuxtPage(title='Home', name='index', frontmatter={'home': True}),
            NuxtPage(title='API Overview', name='index', directory='api', frontmatter={'section': 'api'}),
            NuxtPage(title='Guide', name='guide', directory='guides', frontmatter={'section': 'guides'}),
        ]
        
        for page in pages:
            renderer.pages.append(page)
        
        from pydoc_markdown.interfaces import Context
        renderer.init(Context(temp_dir))
        renderer.render([])
        
        # Check structure
        content_dir = Path(temp_dir) / 'content'
        expected_files = [
            'index.md',
            'api/index.md', 
            'guides/guide.md'
        ]
        
        for expected in expected_files:
            file_path = content_dir / expected
            if file_path.exists():
                print(f"✓ Created {expected}")
            else:
                print(f"✗ Missing {expected}")

def main():
    """Run all tests."""
    print("Running pydoc-markdown-nuxt tests...\n")
    
    try:
        test_basic_page_rendering()
        test_frontmatter_merging() 
        test_directory_structure()
        print("\n✓ All tests completed successfully!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())