"""
Debugging helper for pydoc-markdown using a Nuxt renderer configuration.
"""

import logging
from typing import Any

import yaml
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.interfaces import Context

CONFIG_YAML: str = """
loaders:
  - type: python
    search_path: [src]

processors:
  - type: filter
    expression: not name.startswith('_')
  - type: filter
    expression: not name.startswith('test_')
  - type: smart
  - type: crossref
  - type: google

renderer:
  type: nuxt
  content_dir: content
  output_dir: references-api
"""


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    # Pass YAML configuration string directly to load_config.
    pydoc = PydocMarkdown()
    config: Any = yaml.safe_load(CONFIG_YAML)
    pydoc.load_config(config)
    context: Context = Context(directory=".")
    # Initialize plugins and run each step explicitly.
    pydoc.init(context)  # Initializes loaders, processors, and renderer.
    modules = pydoc.load_modules()  # Loads modules defined in the configuration.
    pydoc.process(modules)  # Applies processors (filter, smart, crossref…).
    pydoc.render(modules)  # Generates the Nuxt Content files.


if __name__ == "__main__":
    main()
