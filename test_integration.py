#!/usr/bin/env python3
"""
Test script to verify that the plugin entry point works correctly
"""

import sys
import os

# Add src to path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_plugin_entry_point():
    """Test that the plugin can be imported as specified in pyproject.toml"""
    print("Testing plugin entry point...")
    
    try:
        # Test the entry point as specified in pyproject.toml:
        # nuxt = "pydoc_markdown_nuxt:NuxtRenderer"
        from pydoc_markdown_nuxt import NuxtRenderer
        print("✅ Successfully imported NuxtRenderer from pydoc_markdown_nuxt")
        
        # Verify it's the correct class
        from pydoc_markdown.interfaces import Renderer
        if issubclass(NuxtRenderer, Renderer):
            print("✅ NuxtRenderer correctly extends Renderer interface")
        else:
            print("❌ NuxtRenderer does not extend Renderer interface")
            return False
            
        # Test instantiation
        renderer = NuxtRenderer()
        print("✅ NuxtRenderer can be instantiated")
        
        # Test it has required methods
        required_methods = ['render', 'init']
        for method in required_methods:
            if hasattr(renderer, method):
                print(f"✅ NuxtRenderer has {method} method")
            else:
                print(f"❌ NuxtRenderer missing {method} method")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import NuxtRenderer: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_pydoc_markdown_integration():
    """Test that the renderer integrates with pydoc-markdown's plugin system"""
    print("\nTesting pydoc-markdown integration...")
    
    try:
        # Test creating a configuration that would use our renderer
        config_yaml = """
renderers:
  - type: nuxt
    content_directory: content/docs
    default_frontmatter:
      layout: docs
      navigation: true
"""
        
        import yaml
        config = yaml.safe_load(config_yaml)
        renderer_config = config['renderers'][0]
        
        print(f"✅ Configuration parsed: {renderer_config}")
        
        # Test that our renderer can be configured with the expected parameters
        from pydoc_markdown_nuxt import NuxtRenderer
        
        renderer = NuxtRenderer(
            content_directory=renderer_config.get('content_directory', 'content'),
            default_frontmatter=renderer_config.get('default_frontmatter', {})
        )
        
        print("✅ NuxtRenderer configured with YAML parameters")
        
        # Verify configuration was applied
        assert renderer.content_directory == 'content/docs'
        assert renderer.default_frontmatter['layout'] == 'docs'
        assert renderer.default_frontmatter['navigation'] == True
        
        print("✅ Configuration parameters correctly applied")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_renderer_discovery():
    """Test that pydoc-markdown could discover our renderer"""
    print("\nTesting renderer discovery mechanism...")
    
    try:
        # Read pyproject.toml manually since toml module isn't available
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        
        # Check for the entry point section
        if '[project.entry-points."pydoc_markdown.interfaces.Renderer"]' in content:
            print("✅ Entry points section found in pyproject.toml")
            
            # Check for our specific entry point
            if 'nuxt = "pydoc_markdown_nuxt:NuxtRenderer"' in content:
                print("✅ Nuxt renderer entry point found")
                
                # Test that the entry point actually resolves
                try:
                    from pydoc_markdown_nuxt import NuxtRenderer
                    print(f"✅ Entry point resolves to {NuxtRenderer}")
                    
                    # Verify it's a proper renderer
                    from pydoc_markdown.interfaces import Renderer
                    if issubclass(NuxtRenderer, Renderer):
                        print("✅ Resolved class is a valid Renderer")
                        return True
                    else:
                        print("❌ Resolved class is not a Renderer")
                        return False
                        
                except ImportError as e:
                    print(f"❌ Could not import from entry point: {e}")
                    return False
            else:
                print("❌ Nuxt renderer entry point not found in pyproject.toml")
                return False
        else:
            print("❌ Entry points section not found in pyproject.toml")
            return False
            
    except Exception as e:
        print(f"❌ Discovery test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Running pydoc-markdown-nuxt integration tests...")
    print("=" * 60)
    
    tests = [
        test_plugin_entry_point,
        test_pydoc_markdown_integration,
        test_renderer_discovery
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                failed += 1
                print("❌ FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED with exception: {e}\n")
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        print("\nThe pydoc-markdown-nuxt extension is ready for use!")
        print("\nTo use it:")
        print("1. Install: pip install pydoc-markdown-nuxt")
        print("2. Configure: Create a pydoc-markdown.yml with 'type: nuxt'")
        print("3. Run: pydoc-markdown")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())