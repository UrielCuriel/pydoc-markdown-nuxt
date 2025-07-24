#!/usr/bin/env python3
"""
Demo script showing pydoc-markdown-nuxt in action with real Python code
"""

import sys
import tempfile
import os
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pydoc_markdown_nuxt.renderer import NuxtRenderer, NuxtPage

# Create a sample Python module to document
SAMPLE_MODULE_CODE = '''
"""
Sample Python module for demonstration.

This module shows how pydoc-markdown-nuxt generates documentation
for a typical Python package.
"""

class DataProcessor:
    """
    A class for processing data with various utilities.
    
    This class provides methods for data validation, transformation,
    and analysis commonly used in data processing pipelines.
    
    Example:
        ```python
        processor = DataProcessor()
        result = processor.validate_data({"name": "John", "age": 30})
        ```
    """
    
    def __init__(self, config=None):
        """
        Initialize the data processor.
        
        Args:
            config (dict, optional): Configuration options for the processor.
                Defaults to None.
        """
        self.config = config or {}
        
    def validate_data(self, data):
        """
        Validate input data against predefined rules.
        
        Args:
            data (dict): The data to validate.
            
        Returns:
            bool: True if data is valid, False otherwise.
            
        Raises:
            ValueError: If data format is invalid.
            
        Example:
            ```python
            processor = DataProcessor()
            is_valid = processor.validate_data({"name": "Alice", "age": 25})
            ```
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        return True
        
    def transform_data(self, data, transformations):
        """
        Apply transformations to the data.
        
        Args:
            data (dict): The input data to transform.
            transformations (list): List of transformation functions.
            
        Returns:
            dict: The transformed data.
        """
        result = data.copy()
        for transform in transformations:
            result = transform(result)
        return result

def calculate_metrics(data_list):
    """
    Calculate statistical metrics for a list of data points.
    
    This function computes common statistical measures including
    mean, median, and standard deviation.
    
    Args:
        data_list (list): List of numerical data points.
        
    Returns:
        dict: Dictionary containing calculated metrics:
            - mean (float): Arithmetic mean
            - median (float): Median value  
            - std_dev (float): Standard deviation
            
    Example:
        ```python
        data = [1, 2, 3, 4, 5]
        metrics = calculate_metrics(data)
        print(f"Mean: {metrics['mean']}")
        ```
    """
    if not data_list:
        return {"mean": 0, "median": 0, "std_dev": 0}
        
    sorted_data = sorted(data_list)
    mean = sum(data_list) / len(data_list)
    
    # Calculate median
    n = len(sorted_data)
    if n % 2 == 0:
        median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        median = sorted_data[n//2]
    
    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in data_list) / len(data_list)
    std_dev = variance ** 0.5
    
    return {
        "mean": mean,
        "median": median, 
        "std_dev": std_dev
    }

class ConfigManager:
    """
    Manages application configuration and settings.
    
    Attributes:
        DEFAULT_CONFIG (dict): Default configuration values.
    """
    
    DEFAULT_CONFIG = {
        "debug": False,
        "timeout": 30,
        "retries": 3
    }
    
    def __init__(self, config_file=None):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str, optional): Path to configuration file.
        """
        self.config_file = config_file
        self.settings = self.DEFAULT_CONFIG.copy()
        
    def load_config(self):
        """Load configuration from file."""
        if self.config_file and os.path.exists(self.config_file):
            # In a real implementation, this would load from file
            pass
            
    def get_setting(self, key, default=None):
        """
        Get a configuration setting.
        
        Args:
            key (str): Setting key to retrieve.
            default: Default value if key not found.
            
        Returns:
            The setting value or default.
        """
        return self.settings.get(key, default)
'''

def create_sample_python_file(temp_dir):
    """Create a sample Python file for documentation."""
    src_dir = os.path.join(temp_dir, 'src', 'mypackage')
    os.makedirs(src_dir, exist_ok=True)
    
    # Create __init__.py
    init_file = os.path.join(src_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('"""MyPackage - A sample Python package for demonstration."""\\n')
        f.write('__version__ = "1.0.0"\\n')
    
    # Create main module
    module_file = os.path.join(src_dir, 'core.py')
    with open(module_file, 'w') as f:
        f.write(SAMPLE_MODULE_CODE)
    
    return src_dir

def demo_nuxt_renderer():
    """Demonstrate the Nuxt renderer with real Python code."""
    print("🚀 pydoc-markdown-nuxt Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Working directory: {temp_dir}")
        
        # Create sample Python code
        src_dir = create_sample_python_file(temp_dir)
        print(f"✅ Created sample Python package at: {src_dir}")
        
        # Set up the renderer
        content_dir = os.path.join(temp_dir, 'content')
        renderer = NuxtRenderer(
            content_directory=content_dir,
            default_frontmatter={
                'layout': 'docs',
                'navigation': True,
                'sidebar': True,
            },
            use_mdc=True,
            base_url='/docs/'
        )
        
        # Configure pages
        pages = [
            NuxtPage(
                title='Home',
                name='index',
                frontmatter={
                    'description': 'Welcome to MyPackage documentation',
                    'icon': 'mdi:home',
                    'hero': True
                }
            ),
            NuxtPage(
                title='API Reference',
                name='api',
                directory='reference',
                frontmatter={
                    'description': 'Complete API documentation',
                    'icon': 'mdi:api',
                    'category': 'API'
                }
            ),
            NuxtPage(
                title='Core Module',
                name='core',
                directory='reference',
                frontmatter={
                    'description': 'Core functionality and classes',
                    'icon': 'mdi:cog',
                    'category': 'API'
                }
            )
        ]
        
        for page in pages:
            renderer.pages.append(page)
        
        # Initialize renderer
        from pydoc_markdown.interfaces import Context
        renderer.init(Context(temp_dir))
        
        # Since we don't have docspec modules in this demo, we'll render empty pages
        # In a real scenario, you'd use pydoc-markdown's loaders to get modules
        print("📝 Rendering pages...")
        renderer.render([])
        
        # Show results
        content_path = Path(content_dir)
        if content_path.exists():
            print(f"\\n✅ Generated Nuxt Content files:")
            for md_file in content_path.rglob('*.md'):
                rel_path = md_file.relative_to(content_path)
                print(f"   📄 {rel_path}")
                
                # Show file content preview
                content = md_file.read_text()
                lines = content.split('\\n')
                print(f"      📋 Preview:")
                for i, line in enumerate(lines[:15]):  # Show first 15 lines
                    print(f"         {line}")
                if len(lines) > 15:
                    print(f"         ... ({len(lines) - 15} more lines)")
                print()
        
        print("🎉 Demo completed! The generated files are ready for Nuxt Content.")
        print("\\n📚 Next steps:")
        print("   1. Copy the generated content/ directory to your Nuxt project")
        print("   2. Install @nuxt/content in your Nuxt project")
        print("   3. Configure Nuxt Content in your nuxt.config.js")
        print("   4. Create pages to display the documentation")
        
        # Create a sample nuxt.config.js snippet
        config_snippet = '''
// Add to your nuxt.config.js
export default {
  modules: [
    '@nuxt/content'
  ],
  content: {
    // Configuration for @nuxt/content
    documentDriven: true,
    highlight: {
      theme: 'github-light'
    }
  }
}
'''
        print(f"\\n⚙️ Sample Nuxt configuration:")
        print(config_snippet)

if __name__ == '__main__':
    demo_nuxt_renderer()