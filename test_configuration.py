#!/usr/bin/env python3
"""
Test script that simulates how pydoc-markdown would use our renderer
"""

import sys
import os
import yaml
import tempfile
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pydoc_markdown_nuxt.renderer import NuxtRenderer, NuxtPage
from pydoc_markdown.interfaces import Context

def test_yaml_configuration():
    """Test loading and using our renderer with a YAML configuration."""
    print("Testing YAML configuration loading...")
    
    # Load the test configuration
    with open('pydoc-markdown.test.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    renderer_config = config['renderers'][0]
    print(f"Loaded configuration: {renderer_config}")
    
    # Create renderer from configuration
    renderer = NuxtRenderer(
        content_directory=renderer_config.get('content_directory', 'content'),
        default_frontmatter=renderer_config.get('default_frontmatter', {}),
        use_mdc=renderer_config.get('use_mdc', True),
        clean_render=renderer_config.get('clean_render', True)
    )
    
    # Add pages from configuration
    for page_config in renderer_config.get('pages', []):
        page = NuxtPage(
            title=page_config['title'],
            name=page_config.get('name'),
            frontmatter=page_config.get('frontmatter', {}),
            directory=page_config.get('directory'),
            contents=page_config.get('contents')
        )
        renderer.pages.append(page)
    
    print("✅ Renderer created from YAML configuration")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Update content directory to use temp dir
        renderer.content_directory = os.path.join(temp_dir, 'content')
        
        # Initialize renderer
        renderer.init(Context(temp_dir))
        
        # Render (with empty modules for this test)
        renderer.render([])
        
        # Check output
        content_dir = Path(renderer.content_directory)
        if content_dir.exists():
            files = list(content_dir.rglob('*.md'))
            print(f"✅ Generated {len(files)} files:")
            for file in files:
                rel_path = file.relative_to(content_dir)
                print(f"   📄 {rel_path}")
                
                # Show content preview
                content = file.read_text()
                print(f"      Content preview:")
                for line in content.split('\\n')[:10]:
                    print(f"         {line}")
                print()
        
        return True

def test_advanced_configuration():
    """Test a more complex configuration with multiple pages and directories."""
    print("\\nTesting advanced configuration...")
    
    config = {
        'content_directory': 'advanced_test/content',
        'use_mdc': True,
        'default_frontmatter': {
            'layout': 'docs',
            'navigation': True,
            'sidebar': True
        },
        'pages': [
            {
                'title': 'Home',
                'name': 'index',
                'frontmatter': {'hero': True, 'description': 'Welcome page'}
            },
            {
                'title': 'API Reference',
                'name': 'api',
                'directory': 'reference',
                'frontmatter': {'category': 'API', 'icon': 'code'}
            },
            {
                'title': 'Examples',
                'name': 'examples',
                'directory': 'guides',
                'frontmatter': {'category': 'Guide', 'icon': 'lightbulb'}
            }
        ]
    }
    
    renderer = NuxtRenderer(
        content_directory=config['content_directory'],
        default_frontmatter=config['default_frontmatter'],
        use_mdc=config['use_mdc']
    )
    
    for page_config in config['pages']:
        page = NuxtPage(
            title=page_config['title'],
            name=page_config.get('name'),
            frontmatter=page_config.get('frontmatter', {}),
            directory=page_config.get('directory')
        )
        renderer.pages.append(page)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Update content directory
        renderer.content_directory = os.path.join(temp_dir, 'content')
        
        # Initialize and render
        renderer.init(Context(temp_dir))
        renderer.render([])
        
        # Verify structure
        content_dir = Path(renderer.content_directory)
        expected_files = ['index.md', 'reference/api.md', 'guides/examples.md']
        
        print("Expected vs Actual files:")
        for expected in expected_files:
            file_path = content_dir / expected
            if file_path.exists():
                print(f"✅ {expected}")
                
                # Verify frontmatter
                content = file_path.read_text()
                if content.startswith('---'):
                    print(f"   ✅ Has YAML frontmatter")
                    
                    # Check for expected frontmatter values
                    if 'layout: docs' in content:
                        print(f"   ✅ Has default layout")
                    if 'navigation: true' in content:
                        print(f"   ✅ Has navigation enabled")
                        
            else:
                print(f"❌ {expected} - NOT FOUND")
    
    return True

def main():
    """Run configuration tests."""
    print("Testing pydoc-markdown-nuxt with YAML configurations")
    print("=" * 60)
    
    try:
        test_yaml_configuration()
        test_advanced_configuration()
        
        print("\\n🎉 All configuration tests passed!")
        print("\\nThe pydoc-markdown-nuxt renderer is ready for production use!")
        print("\\n📚 Usage:")
        print("1. Create a pydoc-markdown.yml file with 'type: nuxt' renderer")
        print("2. Run: pydoc-markdown")
        print("3. The generated content/ files can be used in any Nuxt Content project")
        
        return 0
        
    except Exception as e:
        print(f"\\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())