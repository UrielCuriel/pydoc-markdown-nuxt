"""
Nuxt Content renderer for pydoc-markdown

This module provides a renderer that generates documentation compatible with
Nuxt Content and MDC (Markdown Components) syntax.
"""

from __future__ import annotations

import dataclasses
import logging
import os
import posixpath
import typing as t
from pathlib import Path

import docspec
import yaml

from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer, Resolver
from pydoc_markdown.util.knownfiles import KnownFiles
from pydoc_markdown.util.pages import GenericPage, Pages
from pydoc_markdown.util.misc import escape_except_blockquotes

from .utils import create_mdc_arguments, create_mdc_variables, create_mdc_code_group, create_mdc_alert, _convert_to_kebab_case

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class NuxtPage(GenericPage["NuxtPage"]):
    """
    A page configuration for Nuxt Content.
    
    ### Options
    """
    
    children: t.List["NuxtPage"] = dataclasses.field(default_factory=list)
    
    #: The frontmatter for the page. This will be serialized as YAML at the top of the file.
    frontmatter: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)
    
    #: Override the directory that this page is rendered into (relative to the content directory).
    directory: t.Optional[str] = None
    
    #: The file extension to use for the page. Defaults to ".md"
    extension: str = ".md"


@dataclasses.dataclass
class MDCMarkdownRenderer(MarkdownRenderer):
    """
    Enhanced Markdown renderer that can generate MDC components for arguments and variables.
    """

    content_directory: str = "content"
    
    #: Whether to use MDC syntax for enhanced components
    use_mdc: bool = True
    
    #: Do not generate a table of contents.
    render_toc: bool = False

    #: Configuration for MDC components. Maps component types to component names.
    mdc_components: t.Dict[str, str] = dataclasses.field(default_factory=lambda: {
        "arguments": "UArguments",
        "variables": "UVariables",
        "returns": "UReturns",
        "examples": "UCodeGroup",
        "notes": "UAlert",
        "warnings": "UAlert",
        "raises": "UCallout",
        "see_also": "UCard",
        "code_block": "UCodeGroup",
    })

    _resolver: t.Optional[NuxtContentResolver] = None

    def __post_init__(self) -> None:
        self._resolver = NuxtContentResolver(self.content_directory)

    def _render_object(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        """Override to process docstrings and convert Arguments sections to MDC components."""
        # First render everything except the docstring using the parent method
        if not isinstance(obj, docspec.Module) or self.render_module_header:
            self._render_header(fp, level, obj)

        render_view_source = not isinstance(obj, (docspec.Module, docspec.Variable))

        if render_view_source:
            url = self.source_linker.get_source_url(obj) if self.source_linker else None
            source_string = self.source_format.replace("{url}", str(url)) if url else None
            if source_string and self.source_position == "before signature":
                fp.write(source_string + "\n\n")

        self._render_signature_block(fp, obj)

        if render_view_source:
            if source_string and self.source_position == "after signature":
                fp.write(source_string + "\n\n")

        # Custom docstring processing
        if obj.docstring:
            docstring_content = obj.docstring.content
            
            # Convert Arguments sections to MDC components if enabled
            if self.use_mdc:
                docstring_content = self._process_docstring_for_mdc(docstring_content)
            
            # Apply standard processing
            if self.escape_html_in_docstring:
                docstring_content = escape_except_blockquotes(docstring_content)
            
            lines = docstring_content.split("\n")
            if self.docstrings_as_blockquote:
                lines = ["> " + x for x in lines]
            fp.write("\n".join(lines))
            fp.write("\n\n")
    
    def _process_docstring_for_mdc(self, docstring: str) -> str:
        """Process docstring to convert various sections to MDC components."""
        import re
        
        # Process in order of specificity
        processed = docstring
        
        # 1. Convert Arguments sections
        processed = self._convert_section_to_mdc(processed, "Arguments", "arguments")
        
        # 2. Convert Returns sections
        processed = self._convert_returns_to_mdc(processed)
        
        # 3. Convert Examples sections  
        processed = self._convert_examples_to_mdc(processed)
        
        # 4. Convert Notes sections to alerts
        processed = self._convert_notes_to_mdc(processed)
        
        # 5. Convert Warnings sections to alerts
        processed = self._convert_warnings_to_mdc(processed)
        
        # 6. Convert Raises sections
        processed = self._convert_raises_to_mdc(processed)
        
        # 7. Convert remaining code blocks to MDC code groups (do this last)
        processed = self._convert_code_blocks_to_mdc(processed)
        
        return processed
    
    def _convert_code_blocks_to_mdc(self, docstring: str) -> str:
        """Convert multiple code blocks to MDC code groups."""
        import re
        
        # Pattern to match multiple consecutive code blocks
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        
        # Find all code blocks
        matches = list(re.finditer(code_block_pattern, docstring, re.DOTALL))
        
        if len(matches) <= 1:
            return docstring  # Single or no code blocks, keep as is
        
        # Group consecutive code blocks
        groups = []
        current_group = []
        last_end = 0
        
        for match in matches:
            # Check if this block is close to the previous one (within 2 lines)
            lines_between = docstring[last_end:match.start()].count('\n')
            
            if current_group and lines_between > 2:
                # Start a new group
                groups.append(current_group)
                current_group = []
            
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            current_group.append({
                'language': language,
                'filename': language,
                'code': code,
                'match': match
            })
            last_end = match.end()
        
        if current_group:
            groups.append(current_group)
        
        # Replace groups with MDC components (only if group has multiple blocks)
        result = docstring
        offset = 0
        
        for group in groups:
            if len(group) > 1:  # Only convert groups with multiple blocks
                # Create MDC code group
                component = self.mdc_components.get('code_block', 'UCodeGroup')
                code_blocks = []
                
                for block in group:
                    code_blocks.append({
                        'language': block['language'],
                        'filename': block['language'],
                        'code': block['code']
                    })
                
                mdc_code_group = create_mdc_code_group(code_blocks, component)
                
                # Replace the entire group
                first_match = group[0]['match']
                last_match = group[-1]['match']
                
                start_pos = first_match.start() + offset
                end_pos = last_match.end() + offset
                
                result = result[:start_pos] + mdc_code_group + result[end_pos:]
                offset += len(mdc_code_group) - (end_pos - start_pos)
        
        return result
    
    def _convert_section_to_mdc(self, docstring: str, section_name: str, component_key: str) -> str:
        """Convert a docstring section with list items to MDC component."""
        import re
        
        # Pattern to match sections like **Arguments**: with list items
        pattern = rf'\*\*{section_name}\*\*:\s*\n\n((?:- `[^`]+` - [^\n]+(?:\n|$))*)'
        
        def replace_section(match):
            items_text = match.group(1)
            if not items_text.strip():
                return match.group(0)
            
            # Parse the items
            items = []
            item_pattern = r'- `([^`]+)` - (.+)'
            for item_match in re.finditer(item_pattern, items_text):
                item_name = item_match.group(1)
                item_description = item_match.group(2).strip()
                
                # Try to extract type information from the item_name if it contains type hints
                if ':' in item_name:
                    name_parts = item_name.split(':', 1)
                    name = name_parts[0].strip()
                    type_info = name_parts[1].strip()
                else:
                    name = item_name
                    type_info = ''
                
                items.append({
                    'name': name,
                    'type': type_info,
                    'content': item_description
                })
            
            if not items:
                return match.group(0)
            
            # Generate appropriate MDC component
            component = self.mdc_components.get(component_key, f'U{section_name}')
            
            if component_key == "arguments":
                return create_mdc_arguments(items, component)
            else:
                return create_mdc_variables(items, component)  # Use variables format for other sections
        
        return re.sub(pattern, replace_section, docstring, flags=re.MULTILINE)
    
    def _convert_returns_to_mdc(self, docstring: str) -> str:
        """Convert Returns sections to MDC components."""
        import re
        
        # Pattern to match **Returns**: sections
        pattern = r'\*\*Returns\*\*:\s*\n\n([^*]+?)(?=\n\n\*\*|\Z)'
        
        def replace_returns(match):
            content = match.group(1).strip()
            component = self.mdc_components.get('returns', 'UReturns')
            component_name = _convert_to_kebab_case(component)
            
            return f"::{component_name}\n{content}\n::"
        
        return re.sub(pattern, replace_returns, docstring, flags=re.DOTALL)
    
    def _convert_examples_to_mdc(self, docstring: str) -> str:
        """Convert Examples sections to MDC code groups."""
        import re
        
        # Pattern to match **Examples**: sections that contain code
        pattern = r'\*\*Examples\*\*:\s*\n\n(.*?)(?=\n\n\*\*|\Z)'
        
        def replace_examples(match):
            content = match.group(1).strip()
            component = self.mdc_components.get('examples', 'UCodeGroup')
            
            # If content contains code blocks, extract them
            code_pattern = r'```(\w+)?\n(.*?)\n```'
            code_matches = list(re.finditer(code_pattern, content, re.DOTALL))
            
            if code_matches:
                code_blocks = []
                for code_match in code_matches:
                    language = code_match.group(1) or 'text'
                    code = code_match.group(2).strip()
                    code_blocks.append({
                        'language': language,
                        'filename': language,
                        'code': code
                    })
                
                return create_mdc_code_group(code_blocks, component)
            else:
                # No code blocks, return as simple content
                return f"**Examples**:\n\n{content}"
        
        return re.sub(pattern, replace_examples, docstring, flags=re.DOTALL)
    
    def _convert_notes_to_mdc(self, docstring: str) -> str:
        """Convert Notes sections to alert components."""
        import re
        
        pattern = r'\*\*Notes?\*\*:\s*\n\n([^*]+?)(?=\n\n\*\*|\Z)'
        
        def replace_notes(match):
            content = match.group(1).strip()
            component = self.mdc_components.get('notes', 'UAlert')
            return create_mdc_alert(content, "info", "Note", component)
        
        return re.sub(pattern, replace_notes, docstring, flags=re.DOTALL)
    
    def _convert_warnings_to_mdc(self, docstring: str) -> str:
        """Convert Warnings sections to alert components."""
        import re
        
        pattern = r'\*\*Warnings?\*\*:\s*\n\n([^*]+?)(?=\n\n\*\*|\Z)'
        
        def replace_warnings(match):
            content = match.group(1).strip()
            component = self.mdc_components.get('warnings', 'UAlert')
            return create_mdc_alert(content, "warning", "Warning", component)
        
        return re.sub(pattern, replace_warnings, docstring, flags=re.DOTALL)
    
    def _convert_raises_to_mdc(self, docstring: str) -> str:
        """Convert Raises sections to callout components."""
        import re
        
        pattern = r'\*\*Raises\*\*:\s*\n\n((?:- `[^`]+`: [^\n]+(?:\n|$))*)'
        
        def replace_raises(match):
            items_text = match.group(1)
            if not items_text.strip():
                return match.group(0)
            
            component = self.mdc_components.get('raises', 'UCallout')
            component_name = _convert_to_kebab_case(component)
            
            # Parse exception items
            exceptions = []
            item_pattern = r'- `([^`]+)`: (.+)'
            for item_match in re.finditer(item_pattern, items_text):
                exception_type = item_match.group(1)
                description = item_match.group(2).strip()
                exceptions.append(f"**{exception_type}**: {description}")
            
            if exceptions:
                content = "\n".join(exceptions)
                return f"::{component_name}\n---\ntype: error\n---\n{content}\n::"
            
            return match.group(0)
        
        return re.sub(pattern, replace_raises, docstring, flags=re.MULTILINE)


class NuxtContentResolver(Resolver):
    """
    A resolver for converting API references to Nuxt Content paths.
    
    This resolver converts dotted module references (e.g., 'my.module.MyClass') 
    to Nuxt Content compatible paths (e.g., '/references/my/module/myclass').
    It intelligently resolves local and global references within the API documentation suite.
    """
    
    def __init__(self, base_path: str):
        """
        Initialize the resolver.
        
        Args:
            base_path: The base URL path for the API documentation (e.g., '/docs/api')
        """
        self.base_path = base_path.strip("/")

    def generate_object_id(self, obj: docspec.ApiObject) -> str:
        """Generates a unique ID for an API object, used for anchor links."""
        return ".".join(o.name for o in obj.path)

    def _resolve_local_reference(
        self, scope: docspec.ApiObject, ref_split: t.List[str]
    ) -> t.Optional[docspec.ApiObject]:
        """Finds an object from a reference string starting from the current scope and moving up."""
        obj: t.Optional[docspec.ApiObject] = scope
        while obj:
            resolved = docspec.get_member(obj, ref_split[0])
            if resolved:
                return resolved
            obj = obj.parent
        return None

    def resolve_ref(self, scope: docspec.ApiObject, ref: str) -> t.Optional[str]:
        """
        Resolve a reference to a Markdown file path for Nuxt Content.
        
        Args:
            scope: The current API object scope.
            ref: The reference string (e.g., 'my.module.MyClass' or a relative reference).
            
        Returns:
            The resolved path for Nuxt Content (e.g., '/docs/api/my/module/myclass').
        """
        
        # For now, we assume all references are fully qualified paths from the root.
        # A more robust implementation would use `_resolve_local_reference` and search the API suite.
        # This simple implementation matches the previous behavior but within the new structure.
        
        # Convert dotted name to URL path
        ref_path: str = ref.replace(".", "/")

        # Join parts to form the final link that Nuxt Content can understand
        # The leading slash is important for root-relative paths.
        url: str = posixpath.join("/", self.base_path, ref_path)
        return url.lower()


@dataclasses.dataclass
class NuxtRenderer(Renderer):
    """
    A renderer for Nuxt Content. This renderer generates Markdown files with YAML frontmatter
    that are compatible with Nuxt Content and can utilize MDC (Markdown Components) syntax.
    
    Nuxt Content uses a file-based routing system where Markdown files in the `content/`
    directory are automatically available as pages. This renderer outputs files in a structure
    that follows Nuxt Content conventions.
    
    ### Example Configuration
    
    ```yaml
    renderer:
      type: nuxt
      content_directory: content/docs
      default_frontmatter:
        layout: default
        navigation: true
      pages:
        - title: Home
          name: index
          source: README.md
        - title: API Documentation
          contents:
            - '*'
    ```
    
    ### Options
    """
    
    #: The directory where all generated content files are placed. Default: `content`
    content_directory: str = "content"
    
    #: Clean up files that were previously generated by the renderer before the next
    #: render pass. Defaults to `True`.
    clean_render: bool = True
    
    #: The pages to render.
    pages: Pages[NuxtPage] = dataclasses.field(default_factory=Pages)
    
    #: Default frontmatter that is applied to every page. This will be merged with
    #: each page's individual frontmatter.
    default_frontmatter: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)
    
    #: The #MDCMarkdownRenderer configuration.
    markdown: MDCMarkdownRenderer = dataclasses.field(default_factory=MDCMarkdownRenderer)
    
    #: Whether to use MDC syntax for enhanced components. When enabled, the renderer
    #: will generate content using MDC-compatible syntax for things like code blocks,
    #: alerts, etc.
    use_mdc: bool = True
    

    #: Mapa de iconos para los diferentes tipos de objetos (Iconify)
    object_icons: t.Dict[str, str] = dataclasses.field(default_factory=lambda: {
        "module": "i-material-symbols-light-book-4-spark-outline-rounded",
        "class": "i-material-symbols-light-class-outline-rounded",
        "function": "i-material-symbols-light-function-outline-rounded",
        "method": "i-material-symbols-light-function-outline-rounded",
        "variable": "i-material-symbols-light-variable-outline-rounded",
        "attribute": "i-material-symbols-light-variable-outline-rounded",
        "page": "i-material-symbols-light-book-4-spark-outline-rounded",
    })

    #: Configuration for MDC components. Maps component types to component names.
    #: Default components are from Nuxt UI.
    mdc_components: t.Dict[str, str] = dataclasses.field(default_factory=lambda: {
        "alert": "UAlert",
        "code_group": "UCodeGroup", 
        "tabs": "UTabs",
        "variables": "UVariables",
        "arguments": "UArguments",
        "returns": "UReturns",
        "examples": "UCodeGroup",
        "notes": "UAlert",
        "warnings": "UAlert", 
        "raises": "UCallout",
        "see_also": "UCard",
        "code_block": "UCodeGroup",
        "button": "UButton",
        "card": "UCard",
        "hero": "UPageHero",
        "feature": "ULandingCard"
    })
    
    #: The base URL for the documentation (used for navigation and links)
    base_url: str = "/"
    
    #: Whether to enable table of contents generation for pages.
    #: This will generate a table of contents based on the headers in the Markdown content.
    render_toc: bool = False
    
    def __post_init__(self) -> None:
        self._context: Context
        # Configure MDC renderer with our settings
        self.markdown.use_mdc = self.use_mdc
        self.markdown.mdc_components = self.mdc_components

    def init(self, context: Context) -> None:
        self._context = context
        # Ensure MDC settings are synced
        self.markdown.use_mdc = self.use_mdc
        self.markdown.mdc_components = self.mdc_components
        # Set the resolver in the markdown renderer
        self.markdown.init(context)


    def _render_page(self, modules: t.List[docspec.Module], page: NuxtPage, filename: str) -> None:
        """Render a single page to a file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Merge default frontmatter with page-specific frontmatter
        frontmatter = {**self.default_frontmatter, **page.frontmatter}

        # Determinar el objeto principal para icono y descripción
        primary_object = modules[0] if len(modules) == 1 else None

        # Título
        if "title" not in frontmatter:
            frontmatter["title"] = page.title

        # Descripción automática si no está definida
        if "description" not in frontmatter and primary_object and getattr(primary_object, "docstring", None):
            docstring = primary_object.docstring.content.strip()
            frontmatter["description"] = docstring.split("\n", 1)[0]

        # Autor, fechas, status, tags, etc. (se pueden definir en default_frontmatter)

        # Navigation con icono
        if "navigation" not in frontmatter:
            frontmatter["navigation"] = {}

        if "title" not in frontmatter["navigation"]:
            frontmatter["navigation"]["title"] = frontmatter["title"]

        # Determinar el icono según el tipo de objeto
        if "icon" not in frontmatter["navigation"]:
            icon_key = "page"
            if primary_object and hasattr(primary_object, "type"):
                icon_key = getattr(primary_object.type, "value", "page")
            frontmatter["navigation"]["icon"] = self.object_icons.get(icon_key, self.object_icons["page"])

        # SEO automático si no está definido
        if "seo" not in frontmatter:
            frontmatter["seo"] = {
                "title": f"{frontmatter['title']} - Diseño técnico",
                "description": frontmatter.get("description", "")
            }

        def _write_prefix(fp: t.TextIO) -> None:
            """Write the YAML frontmatter at the beginning of the file."""
            fp.write("---\n")
            fp.write(yaml.safe_dump(frontmatter, default_flow_style=False, allow_unicode=True))
            fp.write("---\n\n")

        page.render(filename, modules, self.markdown, self._context.directory, _write_prefix)

    def render(self, modules: t.List[docspec.Module]) -> None:
        """Render all pages to the content directory."""
        logger.info(f"Rendering documentation to {self.content_directory}")
        
        # Create content directory if it doesn't exist
        os.makedirs(self.content_directory, exist_ok=True)
        
        known_files = KnownFiles(self.content_directory)
        
        if self.clean_render:
            # Remove previously generated files
            for file_ in known_files.load():
                try:
                    os.remove(file_.name)
                    logger.debug(f"Removed {file_.name}")
                except FileNotFoundError:
                    pass

        # Render all pages
        with known_files:
            for item in self.pages.iter_hierarchy():
                page = item.page
                
                # Handle custom directory override
                if hasattr(page, 'directory') and page.directory:
                    # Custom directory handling for NuxtPage
                    directory = os.path.join(self.content_directory, page.directory)
                    filename = os.path.join(directory, page.name + page.extension)
                else:
                    # Use default filename generation
                    filename = item.filename(
                        self.content_directory,
                        page.extension,
                        skip_empty_pages=False
                    )
                
                if filename:
                    self._render_page(modules, page, filename)
                    known_files.append(filename)
                    logger.info(f"Rendered {filename}")

    def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
        """Get a resolver for cross-references."""
        
        # Determine the base path for URLs, removing the root "content" directory.
        # e.g., if content_directory is "content/docs/api", base_path becomes "docs/api"
        parts = Path(self.content_directory).parts
        if parts and parts[0].lower() == 'content':
            base_path = posixpath.join(*parts[1:])
        else:
            base_path = self.content_directory

        return NuxtContentResolver(base_path)