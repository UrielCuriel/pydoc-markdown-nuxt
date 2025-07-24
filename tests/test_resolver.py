"""
Test NuxtContentResolver functionality with pytest.
"""
import pytest
from pathlib import Path

@pytest.mark.integration
def test_content_resolver(temp_test_dir):
    """Test that the content resolver correctly processes cross-references."""
    # First, create a copy of the test configuration pointing to our temp directory
    config_content = """
loaders:
  - type: python
    search_path: [.]
    modules: [test_resolver]

renderer:
  type: nuxt
  content_directory: {temp_dir}
  enable_content_resolver: true
  api_references_path: "api"
  enable_navigation_generation: false
  default_frontmatter:
    layout: default
    navigation: true
  pages:
    - title: "Test Resolver Documentation"
      name: index
      contents:
        - test_resolver.*
""".format(temp_dir=str(temp_test_dir))
    
    # Write the config to a temporary file
    config_path = temp_test_dir / "test_resolver_config.yml"
    config_path.write_text(config_content)
    
    # Run pydoc-markdown with the config
    import subprocess
    import os
    
    result = subprocess.run(
        ["pydoc-markdown", str(config_path)], 
        capture_output=True,
        text=True,
        check=False
    )
    
    # Check if the command succeeded
    assert result.returncode == 0, f"pydoc-markdown failed: {result.stderr}"
    
    # Check for generated files
    index_path = temp_test_dir / "index.md"
    assert index_path.exists()
    
    # Verify content resolution in the generated file
    content = index_path.read_text()
    
    # Check for resolved cross-references
    assert "/api/ExampleClass" in content or "/api/test_resolver.ExampleClass" in content
    assert "/api/ExampleSubclass" in content or "/api/test_resolver.ExampleSubclass" in content
    
    # Cross-reference in docstring should be processed
    assert "See also: [ExampleSubclass]" in content
