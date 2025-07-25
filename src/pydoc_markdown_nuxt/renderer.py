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
from pydoc_markdown.contrib.renderers.markdown import MarkdownReferenceResolver, MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer, Resolver
from pydoc_markdown.util.knownfiles import KnownFiles
from pydoc_markdown.util.misc import escape_except_blockquotes
from pydoc_markdown.util.pages import GenericPage, Pages

from .utils import (
    _convert_to_kebab_case,
    create_mdc_alert,
    create_mdc_arguments,
    create_mdc_code_group,
    create_mdc_variables,
)

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
    mdc_components: t.Dict[str, str] = dataclasses.field(
        default_factory=lambda: {
            "arguments": "UArguments",
            "variables": "UVariables",
            "returns": "UReturns",
            "examples": "UCodeGroup",
            "notes": "UAlert",
            "warnings": "UAlert",
            "raises": "UCallout",
            "see_also": "UCard",
            "code_block": "UCodeGroup",
        }
    )

    def __post_init__(self) -> None:
        self._resolver = t.cast(MarkdownReferenceResolver, NuxtContentResolver(self.content_directory))

    def _render_object(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        """Override to process docstrings and convert Arguments sections to MDC components."""
        if not isinstance(obj, docspec.Module) or self.render_module_header:
            self._render_header(fp, level, obj)

        render_view_source = not isinstance(obj, (docspec.Module, docspec.Variable))
        self._maybe_render_source(fp, obj, render_view_source, position="before signature")
        self._render_signature_block(fp, obj)
        self._maybe_render_source(fp, obj, render_view_source, position="after signature")
        self._maybe_render_docstring(fp, obj)

    def _maybe_render_source(self, fp: t.TextIO, obj: docspec.ApiObject, render_view_source: bool, position: str):
        """Render the source link before or after the signature.

        Args:
            fp (t.TextIO): File-like object where the output is written.
            obj (docspec.ApiObject): API object being rendered.
            render_view_source (bool): Whether the source link should be
                rendered.
            position (str): Either ``"before signature"`` or
                ``"after signature"``.
        """
        if not render_view_source:
            return
        url = self.source_linker.get_source_url(obj) if self.source_linker else None
        source_string = self.source_format.replace("{url}", str(url)) if url else None
        if source_string and self.source_position == position:
            fp.write(source_string + "\n\n")

    def _maybe_render_docstring(self, fp: t.TextIO, obj: docspec.ApiObject):
        """Process and render an object's docstring.

        Args:
            fp (t.TextIO): File-like object where the output is written.
            obj (docspec.ApiObject): API object whose docstring is being
                rendered.
        """
        if not obj.docstring:
            return
        docstring_content = obj.docstring.content
        if self.use_mdc:
            docstring_content = self._process_docstring_for_mdc(docstring_content)
        if self.escape_html_in_docstring:
            docstring_content = escape_except_blockquotes(docstring_content)
        lines = docstring_content.split("\n")
        if self.docstrings_as_blockquote:
            lines = ["> " + x for x in lines]
        fp.write("\n".join(lines))
        fp.write("\n\n")

    def _process_docstring_for_mdc(self, docstring: str) -> str:
        """Convert conventional docstring sections to MDC components.

        Args:
            docstring (str): Raw docstring text.

        Returns:
            The transformed docstring where supported sections are replaced with
            MDC components.
        """

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
        """Convert multiple code blocks to an MDC code group.

        Args:
            docstring (str): The docstring text to process.

        Returns:
            The docstring with consecutive code blocks replaced by a single MDC
            code group component when applicable.
        """
        import re

        # Pattern to match multiple consecutive code blocks
        code_block_pattern = r"```(\w+)?\n(.*?)\n```"

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
            lines_between = docstring[last_end : match.start()].count("\n")

            if current_group and lines_between > 2:
                # Start a new group
                groups.append(current_group)
                current_group = []

            language = match.group(1) or "text"
            code = match.group(2).strip()
            current_group.append({"language": language, "filename": language, "code": code, "match": match})
            last_end = match.end()

        if current_group:
            groups.append(current_group)

        # Replace groups with MDC components (only if group has multiple blocks)
        result = docstring
        offset = 0

        for group in groups:
            if len(group) > 1:  # Only convert groups with multiple blocks
                # Create MDC code group
                component = self.mdc_components.get("code_block", "UCodeGroup")
                code_blocks = []

                for block in group:
                    code_blocks.append(
                        {"language": block["language"], "filename": block["language"], "code": block["code"]}
                    )

                mdc_code_group = create_mdc_code_group(code_blocks, component)

                # Replace the entire group
                first_match = group[0]["match"]
                last_match = group[-1]["match"]

                start_pos = first_match.start() + offset
                end_pos = last_match.end() + offset

                result = result[:start_pos] + mdc_code_group + result[end_pos:]
                offset += len(mdc_code_group) - (end_pos - start_pos)

        return result

    def _convert_section_to_mdc(self, docstring: str, section_name: str, component_key: str) -> str:
        """Convert a docstring section with list items to an MDC component.

        Args:
            docstring (str): The docstring text to search in.
            section_name (str): Name of the section (e.g. ``"Arguments"``).
            component_key (str): Key used to look up the MDC component name.

        Returns:
            The docstring with the specified section replaced by an MDC
            component if it contains items.
        """
        import re

        # Pattern to match sections like **Arguments**: with list items
        # Handle optional whitespace and indentation
        pattern = rf"\*\*{section_name}\*\*:\s*\n\s*\n((?:\s*- `[^`]+` - .+\n?)+)"

        def replace_section(match):
            items_text = match.group(1)
            if not items_text.strip():
                return match.group(0)

            # Parse the items
            items = []
            item_pattern = r"\s*- `([^`]+)` - (.+)"
            for item_match in re.finditer(item_pattern, items_text):
                item_name = item_match.group(1)
                item_description = item_match.group(2).strip()

                # Try to extract type information from the item_name if it contains type hints
                if ":" in item_name:
                    name_parts = item_name.split(":", 1)
                    name = name_parts[0].strip()
                    type_info = name_parts[1].strip()
                else:
                    name = item_name
                    type_info = ""

                items.append({"name": name, "type": type_info, "content": item_description})

            if not items:
                return match.group(0)

            # Generate appropriate MDC component
            component = self.mdc_components.get(component_key, f"U{section_name}")

            if component_key == "arguments":
                return create_mdc_arguments(items, component)
            else:
                return create_mdc_variables(items, component)  # Use variables format for other sections

        return re.sub(pattern, replace_section, docstring, flags=re.MULTILINE)

    def _convert_returns_to_mdc(self, docstring: str) -> str:
        """Convert ``Returns`` sections to MDC components.

        Args:
            docstring (str): Docstring text to transform.

        Returns:
            The docstring with ``Returns`` sections wrapped in the configured
            MDC component.
        """
        import re

        # Pattern to match **Returns**: sections
        pattern = r"\*\*Returns\*\*:\s*\n\n([^*]+)(?=\n\n\*\*|\Z)"

        def replace_returns(match):
            content = match.group(1).strip()
            component = self.mdc_components.get("returns", "UReturns")
            component_name = _convert_to_kebab_case(component)

            return f"::{component_name}\n{content}\n::"

        return re.sub(pattern, replace_returns, docstring, flags=re.DOTALL)

    def _convert_examples_to_mdc(self, docstring: str) -> str:
        """Convert ``Examples`` sections to MDC code groups.

        Args:
            docstring (str): Docstring text to transform.

        Returns:
            The docstring with ``Examples`` sections converted to MDC code group
            components when code blocks are detected.
        """
        import re

        # Pattern to match **Examples**: sections that contain code
        pattern = r"\*\*Examples\*\*:\s*\n\n(.*?)(?=\n\n\*\*|\Z)"

        def replace_examples(match):
            content = match.group(1).strip()
            component = self.mdc_components.get("examples", "UCodeGroup")

            # If content contains code blocks, extract them
            code_pattern = r"```(\w+)?\n(.*?)\n```"
            code_matches = list(re.finditer(code_pattern, content, re.DOTALL))

            if code_matches:
                code_blocks = []
                for code_match in code_matches:
                    language = code_match.group(1) or "text"
                    code = code_match.group(2).strip()
                    code_blocks.append({"language": language, "filename": language, "code": code})

                return create_mdc_code_group(code_blocks, component)
            else:
                # No code blocks, return as simple content
                return f"**Examples**:\n\n{content}"

        return re.sub(pattern, replace_examples, docstring, flags=re.DOTALL)

    def _convert_notes_to_mdc(self, docstring: str) -> str:
        """Convert ``Notes`` sections to alert components.

        Args:
            docstring (str): Docstring text to transform.

        Returns:
            The docstring where ``Notes`` sections are replaced by MDC alert
            components.
        """
        import re

        pattern = r"\*\*Notes?\*\*:\s*\n\n(.*?)(?=\n\n\*\*|\Z)"

        def replace_notes(match):
            content = match.group(1).strip()
            component = self.mdc_components.get("notes", "UAlert")
            return create_mdc_alert(content, "info", "Note", component)

        return re.sub(pattern, replace_notes, docstring, flags=re.DOTALL)

    def _convert_warnings_to_mdc(self, docstring: str) -> str:
        """Convert ``Warnings`` sections to alert components.

        Args:
            docstring (str): Docstring text to transform.

        Returns:
            The docstring where ``Warnings`` sections are replaced by MDC alert
            components.
        """
        import re

        pattern = r"\*\*Warnings?\*\*:\s*\n\n(.*?)(?=\n\n\*\*|\Z)"

        def replace_warnings(match):
            content = match.group(1).strip()
            component = self.mdc_components.get("warnings", "UAlert")
            return create_mdc_alert(content, "warning", "Warning", component)

        return re.sub(pattern, replace_warnings, docstring, flags=re.DOTALL)

    def _convert_raises_to_mdc(self, docstring: str) -> str:
        """Convert ``Raises`` sections to callout components.

        Args:
            docstring (str): Docstring text to transform.

        Returns:
            The docstring where ``Raises`` sections are replaced with MDC callou
            t components summarizing the exceptions raised.
        """
        import re

        pattern = r"\*\*Raises\*\*:\s*\n\n(.*?)(?=\n\n\*\*|\Z)"

        def replace_raises(match):
            items_text = match.group(1).strip()
            if not items_text:
                return match.group(0)

            component = self.mdc_components.get("raises", "UCallout")
            component_name = _convert_to_kebab_case(component)

            # Parse exception items
            exceptions = []
            item_pattern = r"- `([^`]+)`: (.+)"
            for item_match in re.finditer(item_pattern, items_text):
                exception_type = item_match.group(1)
                description = item_match.group(2).strip()
                exceptions.append(f"**{exception_type}**: {description}")

            if exceptions:
                content = "\n".join(exceptions)
                return f"::{component_name}\n---\ntype: error\n---\n{content}\n::"

            return match.group(0)

        return re.sub(pattern, replace_raises, docstring, flags=re.DOTALL)

    def _convert_arguments_to_mdc(self, docstring: str) -> str:
        """Convert ``Arguments`` sections to MDC components.

        Args:
            docstring (str): Docstring text to transform.

        Returns:
            The docstring with ``Arguments`` sections converted to the
            configured MDC component.
        """
        return self._convert_section_to_mdc(docstring, "Arguments", "arguments")


class NuxtContentResolver(MarkdownReferenceResolver):
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
            base_path (str): The base URL path for the API documentation
                (e.g., ``'/docs/api'``)
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
            scope (docspec.ApiObject): The current API object scope.
            ref (str): The reference string (e.g., ``'my.module.MyClass'`` or a
                relative reference).

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
    object_icons: t.Dict[str, str] = dataclasses.field(
        default_factory=lambda: {
            "module": "i-material-symbols-light-book-4-spark-outline-rounded",
            "class": "i-material-symbols-light-class-outline-rounded",
            "function": "i-material-symbols-light-function-outline-rounded",
            "method": "i-material-symbols-light-function-outline-rounded",
            "variable": "i-material-symbols-light-variable-outline-rounded",
            "attribute": "i-material-symbols-light-variable-outline-rounded",
            "page": "i-material-symbols-light-book-4-spark-outline-rounded",
        }
    )

    #: Configuration for MDC components. Maps component types to component names.
    #: Default components are from Nuxt UI.
    mdc_components: t.Dict[str, str] = dataclasses.field(
        default_factory=lambda: {
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
            "feature": "ULandingCard",
        }
    )

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
        """Render a single page to a Markdown file.

        Args:
            modules (t.List[docspec.Module]): List of modules available for
                rendering.
            page (NuxtPage): Page configuration describing what to render.
            filename (str): Destination file path.
        """

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        frontmatter = self._build_frontmatter(modules, page)

        source_content = self._read_source_content(page)
        api_content = self._render_api_content(modules, page)

        content = self._combine_content(source_content, api_content)
        self._write_page_file(filename, frontmatter, content)

    def _read_source_content(self, page: NuxtPage) -> str:
        """Read the content of ``page.source`` if specified.

        Args:
            page (NuxtPage): Page configuration.

        Returns:
            The text from the source file or an empty string if it does not
            exist.
        """
        page_source = getattr(page, "source", None)
        if page_source is not None:
            source_path = Path(self._context.directory) / page_source
            if source_path.is_file():
                return source_path.read_text()
            else:
                logger.warning('Page "%s" source file "%s" not found.', page.name, source_path)
        return ""

    def _render_api_content(self, modules: t.List[docspec.Module], page: NuxtPage) -> str:
        """Render API objects configured in the page.

        Args:
            modules (t.List[docspec.Module]): Available modules.
            page (NuxtPage): Page configuration.

        Returns:
            Rendered Markdown for the API objects contained in the page.
        """
        import io

        with io.StringIO() as buffer:
            if hasattr(page, "contents") and page.contents:
                self._render_page_contents(buffer, modules, page.contents)
            return buffer.getvalue()

    def _render_page_contents(self, buffer: t.TextIO, modules: t.List[docspec.Module], contents: t.List[str]) -> None:
        """Render the API objects listed in ``contents``.

        Args:
            buffer (t.TextIO): Buffer to write to.
            modules (t.List[docspec.Module]): Available modules.
            contents (t.List[str]): List of module names to render.
        """
        for content_name in contents:
            module = self._find_module_by_name(modules, content_name)
            if module:
                self.markdown._render_object(buffer, 1, module)
                self._render_module_members(buffer, module)

    def _find_module_by_name(self, modules: t.List[docspec.Module], name: str) -> t.Optional[docspec.Module]:
        """Find a module by name.

        Args:
            modules (t.List[docspec.Module]): List of modules to search.
            name (str): Name of the module.

        Returns:
            The matching module or ``None`` if not found.
        """
        for module in modules:
            if module.name == name:
                return module
        return None

    def _render_module_members(self, buffer: t.TextIO, module: docspec.Module) -> None:
        """Render all members of a module.

        Args:
            buffer (t.TextIO): Buffer to write to.
            module (docspec.Module): Module whose members will be rendered.
        """
        for member in module.members:
            self.markdown._render_object(buffer, 2, member)

    def _combine_content(self, source_content: str, api_content: str) -> str:
        """Combine source markdown with rendered API documentation.

        Args:
            source_content (str): Markdown from an external file.
            api_content (str): Markdown generated from API objects.

        Returns:
            The combined Markdown content.
        """
        if source_content and api_content:
            return source_content + "\n\n" + api_content
        return source_content or api_content

    def _write_page_file(self, filename: str, frontmatter: t.Dict[str, t.Any], content: str) -> None:
        """Write a Markdown file including YAML frontmatter.

        Args:
            filename (str): Destination path for the file.
            frontmatter (t.Dict[str, t.Any]): Dictionary of frontmatter
                values.
            content (str): Rendered Markdown content.
        """
        with open(filename, "w", encoding="utf8") as fp:
            fp.write("---\n")
            fp.write(str(yaml.safe_dump(frontmatter, default_flow_style=False, allow_unicode=True)))
            fp.write("---\n\n")
            fp.write(content)

    def _build_frontmatter(self, modules: t.List[docspec.Module], page: NuxtPage) -> t.Dict[str, t.Any]:
        """Assemble the frontmatter dictionary for a page.

        Args:
            modules (t.List[docspec.Module]): List of modules available to
                render.
            page (NuxtPage): Page configuration being processed.

        Returns:
            The merged frontmatter dictionary.
        """
        frontmatter = {**self.default_frontmatter, **page.frontmatter}
        primary_object = modules[0] if len(modules) == 1 else None

        if "title" not in frontmatter:
            frontmatter["title"] = page.title

        if self._needs_description(frontmatter, primary_object):
            docstring = ""
            if primary_object and getattr(primary_object, "docstring", None) and primary_object.docstring is not None:
                docstring = primary_object.docstring.content.strip()
            frontmatter["description"] = docstring.split("\n", 1)[0] if docstring else ""

        # Only build navigation object if it's a dict or if we need to add defaults to objects
        navigation_value = frontmatter.get("navigation")
        if isinstance(navigation_value, dict):
            frontmatter["navigation"] = self._build_navigation(frontmatter, primary_object)
        # If navigation is a boolean or other type, leave it as is

        if "seo" not in frontmatter:
            frontmatter["seo"] = {
                "title": f"{frontmatter['title']} - Diseño técnico",
                "description": frontmatter.get("description", ""),
            }

        return frontmatter

    def _needs_description(
        self,
        frontmatter: t.Dict[str, t.Any],
        primary_object: t.Optional[docspec.ApiObject],
    ) -> bool:
        """Check if a description should be added to frontmatter.

        Args:
            frontmatter (t.Dict[str, t.Any]): Frontmatter being generated.
            primary_object (t.Optional[docspec.ApiObject]): Primary API object
                used for the page.

        Returns:
            ``True`` if a description should be derived from ``primary_object``.
        """
        return bool(
            "description" not in frontmatter
            and primary_object
            and getattr(primary_object, "docstring", None)
            and primary_object.docstring is not None
        )

    def _build_navigation(
        self, frontmatter: t.Dict[str, t.Any], primary_object: t.Optional[docspec.ApiObject]
    ) -> t.Dict[str, t.Any]:
        """Build the navigation dictionary for a page.

        Args:
            frontmatter (t.Dict[str, t.Any]): The frontmatter collected so
                far.
            primary_object (t.Optional[docspec.ApiObject]): Primary API object
                rendered on the page, if any.

        Returns:
            A navigation dictionary suitable for Nuxt Content.
        """
        navigation_value = frontmatter.get("navigation", {})
        if isinstance(navigation_value, bool):
            # If navigation is True, create a default navigation dict
            # If navigation is False, we still create a dict but might handle it differently
            navigation = {}
        elif isinstance(navigation_value, dict):
            navigation = navigation_value.copy()
        else:
            navigation = {}

        if "title" not in navigation:
            navigation["title"] = frontmatter["title"]
        if "icon" not in navigation:
            icon_key = self._get_icon_key(primary_object)
            navigation["icon"] = self.object_icons.get(icon_key, self.object_icons["page"])
        return navigation

    def _get_icon_key(self, primary_object: t.Optional[docspec.ApiObject]) -> str:
        """Return the icon key for a given API object."""
        if not primary_object:
            return "page"
        if isinstance(primary_object, docspec.Module):
            return "module"
        if isinstance(primary_object, docspec.Class):
            return "class"
        if isinstance(primary_object, docspec.Function):
            return "function"
        if isinstance(primary_object, docspec.Variable):
            return "variable"
        return "page"

    def render(self, modules: t.List[docspec.Module]) -> None:
        """Render all pages to the content directory."""
        logger.info(f"Rendering documentation to {self.content_directory}")

        os.makedirs(self.content_directory, exist_ok=True)
        known_files = KnownFiles(self.content_directory)

        if self.clean_render:
            self._cleanup_files(known_files)

        with known_files:
            self._render_all_pages(modules, known_files)

    def _cleanup_files(self, known_files: KnownFiles) -> None:
        """Remove previously generated files.

        Args:
            known_files (KnownFiles): Tracker object containing files from the
                last render.
        """
        for file_ in known_files.load():
            try:
                os.remove(file_.name)
                logger.debug(f"Removed {file_.name}")
            except FileNotFoundError:
                pass

    def _get_page_filename(self, item, page):
        """Determine the output filename for a page.

        Args:
            item: Page tree node.
            page (NuxtPage): Page configuration.

        Returns:
            Full path to the output file.
        """
        if hasattr(page, "directory") and page.directory:
            directory = os.path.join(self.content_directory, page.directory)
            name = page.name if page.name is not None else "index"
            return os.path.join(directory, name + page.extension)
        else:
            # For pages without directory, place them directly in content_directory
            name = page.name if page.name is not None else "index"
            return os.path.join(self.content_directory, name + page.extension)

    def _render_all_pages(self, modules: t.List[docspec.Module], known_files: KnownFiles) -> None:
        """Render all configured pages and track generated files.

        Args:
            modules (t.List[docspec.Module]): List of modules available for
                rendering.
            known_files (KnownFiles): Tracker object for generated files.
        """
        for item in self.pages.iter_hierarchy():
            page = item.page
            filename = self._get_page_filename(item, page)
            if filename:
                self._render_page(modules, page, filename)
                known_files.append(filename)
                logger.info(f"Rendered {filename}")

    def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
        """Return a resolver for cross-references.

        Args:
            modules (t.List[docspec.Module]): Modules that will be rendered.

        Returns:
            Resolver instance for translating API references to URLs.
        """

        # Determine the base path for URLs, removing the root "content" directory.
        # e.g., if content_directory is "content/docs/api", base_path becomes "docs/api"
        parts = Path(self.content_directory).parts
        if parts and parts[0].lower() == "content":
            base_path = posixpath.join(*parts[1:])
        else:
            base_path = self.content_directory

        return NuxtContentResolver(base_path)
