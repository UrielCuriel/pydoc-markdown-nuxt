---
title: 'pydoc_markdown_nuxt.renderer'
description: 'Module for rendering Python API documentation in a format suitable for Nuxt Content.'
navigation:
    title: 'pydoc_markdown_nuxt.renderer'
    icon: 'i-codicon-library'
---

Module for rendering Python API documentation in a format suitable for Nuxt Content.
This module defines a customized Markdown renderer that generates Markdown files
with a specific structure for Nuxt Content.

## logger
::reference-header
---
description: >
    API reference for logger
lang: 'python'
type: 'variable'
typing: 'logging.Logger'
navigation:
    title: 'logger'
    icon: 'i-codicon-symbol-variable'
    level: 1
---

```python
logger: logging.Logger = logging.getLogger(__name__)
```
::

## NuxtReferenceResolver
::reference-header
---
description: >
    Custom reference resolver for Nuxt Content.
lang: 'python'
type: 'class'
navigation:
    title: 'NuxtReferenceResolver'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclasses.dataclass
class NuxtReferenceResolver(MarkdownReferenceResolver)
```

Custom reference resolver for Nuxt Content.
This resolver generates links to the Markdown files in the Nuxt Content structure.

### output_dir
::reference-header
---
description: >
    API reference for output_dir
lang: 'python'
type: 'variable'
typing: 'str'
navigation:
    title: 'output_dir'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
output_dir: str = dataclasses.field(default="references")
```
::

### resolve_ref
::reference-header
---
description: >
    Resolve a reference to an object by its name and return the link to its Markdown file.
lang: 'python'
type: 'method'
navigation:
    title: 'resolve_ref'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def resolve_ref(scope: docspec.ApiObject, ref: str) -> str | None
```

Resolve a reference to an object by its name and return the link to its Markdown file.
This method overrides the default reference resolver to generate links
in the format expected by Nuxt Content.

**Arguments**:

- `scope` _docspec.ApiObject_ - The API object to resolve the reference for.
- `ref` _str_ - The reference string to resolve.

**Returns**:

str | None: The resolved link or None if not found.

## NuxtMarkdownRenderer
::reference-header
---
description: >
    Customized Markdown Renderer for Nuxt Content.
lang: 'python'
type: 'class'
navigation:
    title: 'NuxtMarkdownRenderer'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclasses.dataclass
class NuxtMarkdownRenderer(MarkdownRenderer)
```

Customized Markdown Renderer for Nuxt Content.
This renderer generates Markdown files with a specific structure for Nuxt Content.

**Arguments**:

- `insert_header_anchors` _bool_ - Whether to insert anchors in headers.
- `escape_html_in_docstring` _bool_ - Whether to escape HTML in docstrings.
- `object_icons` _dict_ - Icons for different object types.
- `module_frontmatter_template` _str_ - Template for the frontmatter of module files.

### insert_header_anchors
::reference-header
---
description: >
    API reference for insert_header_anchors
lang: 'python'
type: 'variable'
typing: 'bool'
navigation:
    title: 'insert_header_anchors'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
insert_header_anchors: bool = False
```
::

### escape_html_in_docstring
::reference-header
---
description: >
    API reference for escape_html_in_docstring
lang: 'python'
type: 'variable'
typing: 'bool'
navigation:
    title: 'escape_html_in_docstring'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
escape_html_in_docstring: bool = True
```
::

### output_dir
::reference-header
---
description: >
    API reference for output_dir
lang: 'python'
type: 'variable'
typing: 'str'
navigation:
    title: 'output_dir'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
output_dir: str = dataclasses.field(default="references")
```
::

### jinja_env
::reference-header
---
description: >
    API reference for jinja_env
lang: 'python'
type: 'variable'
typing: 'jinja2.Environment'
navigation:
    title: 'jinja_env'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
jinja_env: jinja2.Environment = dataclasses.field(init=False, repr=False)
```
::

### object_icons
::reference-header
---
description: >
    API reference for object_icons
lang: 'python'
type: 'variable'
typing: 'Dict[str, str]'
navigation:
    title: 'object_icons'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
object_icons: Dict[str, str] = dataclasses.field(
        default_factory=lambda: {
            "module": "i-codicon-library",
            "class": "i-codicon-symbol-class",
            "function": "i-codicon-symbol-method",
            "method": "i-codicon-symbol-method-arrow",
            "variable": "i-codicon-symbol-variable",
            "indirection": "i-codicon-symbol-namespace",
            "argument": "i-codicon-symbol-parameter",
            "default": "i-codicon-symbol-property",
        }
    )
```
::

### module_frontmatter_template
::reference-header
---
description: >
    API reference for module_frontmatter_template
lang: 'python'
type: 'variable'
typing: 'str'
navigation:
    title: 'module_frontmatter_template'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
module_frontmatter_template: str = (
        "---\n"
        "title: '{{ title }}'\n"
        "description: '{{ description }}'\n"
        "navigation:\n"
        "    title: '{{ title }}'\n"
        "    icon: '{{ icon }}'\n"
        "---\n"
    )
```
::

### member_header_template
::reference-header
---
description: >
    API reference for member_header_template
lang: 'python'
type: 'variable'
typing: 'str'
navigation:
    title: 'member_header_template'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
member_header_template: str = (
        "{% if level > 0 %}"
        "{{ '#' * (level + 1) }} {{ title }}\n"
        "{% endif %}"
        "::reference-header\n"
        "---\n"
        "description: >\n"
        "    {{ description }}\n"
        "lang: 'python'\n"
        "type: '{{ object_type }}'\n"
        "{% if object_typing %}"
        "typing: '{{ object_typing }}'\n"
        "{% endif %}"
        "navigation:\n"
        "    title: '{{ title }}'\n"
        "    icon: '{{ icon }}'\n"
        "    level: {{ level }}\n"
        "---\n"
        "{% if object_value %}\n"
        "```python\n"
        "{% if object_typing %}"
        "{{ title }}: {{ object_typing }} = {{ object_value }}\n"
        "{% else %}"
        "{{ title }} = {{ object_value }}\n"
        "{% endif %}"
        "```\n"
        "{% endif %}"
        "::\n"
    )
```
::

### init
::reference-header
---
description: >
    Initializes the renderer. This is called after the configuration is loaded
lang: 'python'
type: 'method'
navigation:
    title: 'init'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def init(context: Context) -> None
```

Initializes the renderer. This is called after the configuration is loaded
but before rendering begins. We create the reference resolver here to ensure
it receives the correct `output_dir`.

**Arguments**:

- `context` _Context_ - The context in which the renderer is initialized.

## NuxtRenderer
::reference-header
---
description: >
    Renderer for Nuxt Content, generating a directory structure for each module
lang: 'python'
type: 'class'
navigation:
    title: 'NuxtRenderer'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclasses.dataclass
class NuxtRenderer(Renderer)
```

Renderer for Nuxt Content, generating a directory structure for each module
and a Markdown file for each member (class/function) of the module.

**Attributes**:

- `content_dir` _str_ - The directory where the content will be stored.
- `output_dir` _str_ - The subdirectory where the rendered files will be placed.
- `markdown` _MarkdownRenderer_ - The Markdown renderer to use for rendering the content.

### markdown
::reference-header
---
description: >
    API reference for markdown
lang: 'python'
type: 'variable'
typing: 'te.Annotated[MarkdownRenderer, DeserializeAs(NuxtMarkdownRenderer)]'
navigation:
    title: 'markdown'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
markdown: te.Annotated[MarkdownRenderer, DeserializeAs(NuxtMarkdownRenderer)] = dataclasses.field(
        default_factory=NuxtMarkdownRenderer
    )
```
::

### content_dir
::reference-header
---
description: >
    API reference for content_dir
lang: 'python'
type: 'variable'
typing: 'str'
navigation:
    title: 'content_dir'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
content_dir: str = "content"
```
::

### output_dir
::reference-header
---
description: >
    API reference for output_dir
lang: 'python'
type: 'variable'
typing: 'str'
navigation:
    title: 'output_dir'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
output_dir: str = "references"
```
::

### init
::reference-header
---
description: >
    API reference for init
lang: 'python'
type: 'method'
navigation:
    title: 'init'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def init(context: Context) -> None
```

### render
::reference-header
---
description: >
    Renderiza los módulos, creando una carpeta por módulo y un archivo por miembro.
lang: 'python'
type: 'method'
navigation:
    title: 'render'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def render(modules: List[docspec.Module]) -> None
```

Renderiza los módulos, creando una carpeta por módulo y un archivo por miembro.

**Arguments**:

- `modules` _List[docspec.Module]_ - Lista de módulos a renderizar.

