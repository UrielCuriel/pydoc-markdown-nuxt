"""
Utility functions for working with Nuxt Content and MDC syntax.
"""

from typing import Dict, Any, List, Optional
import re


def create_mdc_alert(content: str, type: str = "info", title: Optional[str] = None) -> str:
    """
    Create an MDC alert component.
    
    Args:
        content: The alert content
        type: Alert type (info, warning, error, success)
        title: Optional title for the alert
        
    Returns:
        MDC alert syntax string
    """
    props = f'type="{type}"'
    if title:
        props += f' title="{title}"'
    
    return f"::alert{{{props}}}\n{content}\n::"


def create_mdc_code_group(code_blocks: List[Dict[str, str]]) -> str:
    """
    Create an MDC code group with multiple code blocks.
    
    Args:
        code_blocks: List of dicts with 'language', 'filename', and 'code' keys
        
    Returns:
        MDC code group syntax string
    """
    result = "::code-group\n"
    
    for block in code_blocks:
        lang = block.get('language', 'text')
        filename = block.get('filename', '')
        code = block.get('code', '')
        
        if filename:
            result += f"```{lang} [{filename}]\n"
        else:
            result += f"```{lang}\n"
        
        result += f"{code}\n```\n"
    
    result += "::"
    return result


def create_mdc_tabs(tabs: List[Dict[str, str]]) -> str:
    """
    Create MDC tabs component.
    
    Args:
        tabs: List of dicts with 'title' and 'content' keys
        
    Returns:
        MDC tabs syntax string
    """
    result = "::tabs\n"
    
    for tab in tabs:
        title = tab.get('title', 'Tab')
        content = tab.get('content', '')
        
        result += f"  ::div{{label=\"{title}\"}}\n"
        result += f"  {content}\n"
        result += "  ::\n"
    
    result += "::"
    return result


def create_navigation_entry(title: str, path: str, icon: Optional[str] = None, 
                          badge: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a navigation entry for Nuxt Content.
    
    Args:
        title: Navigation title
        path: Path to the page
        icon: Optional icon name
        badge: Optional badge text
        description: Optional description
        
    Returns:
        Navigation entry dictionary
    """
    entry = {
        "title": title,
        "to": path
    }
    
    if icon:
        entry["icon"] = icon
    if badge:
        entry["badge"] = badge
    if description:
        entry["description"] = description
    
    return entry


def enhance_frontmatter_for_nuxt(frontmatter: Dict[str, Any], 
                                page_type: str = "doc") -> Dict[str, Any]:
    """
    Enhance frontmatter with Nuxt Content specific fields.
    
    Args:
        frontmatter: Base frontmatter dictionary
        page_type: Type of page (doc, guide, reference, example)
        
    Returns:
        Enhanced frontmatter dictionary
    """
    enhanced = frontmatter.copy()
    
    # Add common Nuxt Content fields
    if "layout" not in enhanced:
        enhanced["layout"] = "default"
    
    if "navigation" not in enhanced:
        enhanced["navigation"] = True
    
    # Add page type specific enhancements
    if page_type == "reference":
        enhanced.setdefault("aside", True)
        enhanced.setdefault("toc", True)
    elif page_type == "guide":
        enhanced.setdefault("aside", True)
        enhanced.setdefault("prev", True)
        enhanced.setdefault("next", True)
    elif page_type == "example":
        enhanced.setdefault("prose", True)
        enhanced.setdefault("copy", True)
    
    return enhanced


def generate_api_breadcrumbs(module_path: str, base_url: str = "/docs") -> List[Dict[str, str]]:
    """
    Generate breadcrumb navigation for API documentation.
    
    Args:
        module_path: Full module path (e.g., "mypackage.core.DataProcessor")
        base_url: Base URL for the documentation
        
    Returns:
        List of breadcrumb items
    """
    breadcrumbs = [{"title": "Documentation", "to": base_url}]
    
    parts = module_path.split('.')
    current_path = base_url
    
    for i, part in enumerate(parts):
        current_path += f"/{part}"
        
        if i == len(parts) - 1:
            # Last item (current page) - no link
            breadcrumbs.append({"title": part})
        else:
            breadcrumbs.append({"title": part, "to": current_path})
    
    return breadcrumbs


def format_python_signature_for_mdc(signature: str) -> str:
    """
    Format a Python function signature for better display in MDC.
    
    Args:
        signature: Python function signature string
        
    Returns:
        Formatted signature with syntax highlighting
    """
    # Simple formatting - could be enhanced with more sophisticated parsing
    formatted = signature.replace('(', '(\n  ').replace(', ', ',\n  ').replace(')', '\n)')
    
    return f"```python\n{formatted}\n```"


def create_api_overview_table(classes: List[Dict[str, str]]) -> str:
    """
    Create a table overview of API classes.
    
    Args:
        classes: List of dicts with 'name', 'description', and optional 'link' keys
        
    Returns:
        Markdown table string
    """
    if not classes:
        return ""
    
    table = "| Class | Description |\n"
    table += "|-------|-------------|\n"
    
    for cls in classes:
        name = cls.get('name', '')
        description = cls.get('description', '')
        link = cls.get('link')
        
        if link:
            name = f"[{name}]({link})"
        
        table += f"| {name} | {description} |\n"
    
    return table


class NuxtContentHelper:
    """
    Helper class for generating Nuxt Content compatible documentation.
    """
    
    def __init__(self, base_url: str = "/docs", use_mdc: bool = True):
        self.base_url = base_url
        self.use_mdc = use_mdc
    
    def wrap_with_mdc_if_enabled(self, content: str, component: str, props: str = "") -> str:
        """Wrap content with MDC component if MDC is enabled."""
        if self.use_mdc:
            return f"::{component}{{{props}}}\n{content}\n::"
        return content
    
    def create_hero_section(self, title: str, description: str, 
                          links: Optional[List[Dict[str, str]]] = None) -> str:
        """Create a hero section for documentation pages."""
        content = f"# {title}\n\n{description}\n"
        
        if links:
            content += "\n"
            for link in links:
                label = link.get('label', 'Link')
                url = link.get('url', '#')
                variant = link.get('variant', 'primary')
                
                if self.use_mdc:
                    content += f"::button[{label}]{{to=\"{url}\" variant=\"{variant}\"}}\n"
                else:
                    content += f"[{label}]({url})\n"
        
        if self.use_mdc:
            return f"::hero\n{content}\n::"
        return content
    
    def create_feature_list(self, features: List[Dict[str, str]]) -> str:
        """Create a feature list section."""
        if not features:
            return ""
        
        content = ""
        for feature in features:
            title = feature.get('title', '')
            description = feature.get('description', '')
            icon = feature.get('icon', '')
            
            if self.use_mdc:
                icon_prop = f' icon="{icon}"' if icon else ''
                content += f"::feature{{title=\"{title}\"{icon_prop}}}\n{description}\n::\n\n"
            else:
                content += f"### {title}\n\n{description}\n\n"
        
        return content.strip()