"""
pydoc-markdown-nuxt: A Nuxt.js renderer for pydoc-markdown

This package provides a renderer for pydoc-markdown that generates documentation
following the Nuxt Content and MDC (Markdown Components) structure.
"""

__version__ = "0.1.0"
__author__ = "Uriel Curiel"
__email__ = "urielcuriel@outlook.com"

from .renderer import NuxtRenderer, NuxtPage
from .utils import (
    create_mdc_alert,
    create_mdc_code_group,
    create_mdc_tabs,
    create_mdc_variables,
    create_mdc_arguments,
    create_variable_or_argument_component,
    create_navigation_entry,
    enhance_frontmatter_for_nuxt,
    generate_api_breadcrumbs,
    format_python_signature_for_mdc,
    create_api_overview_table,
    NuxtContentHelper
)

__all__ = [
    "NuxtRenderer",
    "NuxtPage",
    "create_mdc_alert",
    "create_mdc_code_group", 
    "create_mdc_tabs",
    "create_navigation_entry",
    "enhance_frontmatter_for_nuxt",
    "generate_api_breadcrumbs",
    "format_python_signature_for_mdc",
    "create_api_overview_table",
    "NuxtContentHelper"
]