"""
pydoc-markdown-nuxt: A Nuxt.js renderer for pydoc-markdown

This package provides a renderer for pydoc-markdown that generates documentation
following the Nuxt Content and MDC (Markdown Components) structure.
"""

__version__ = "0.1.0"
__author__ = "Uriel Curiel"
__email__ = "urielcuriel@outlook.com"

from .renderer import NuxtRenderer

__all__ = ["NuxtRenderer"]