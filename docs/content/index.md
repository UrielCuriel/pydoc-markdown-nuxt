---
seo:
  title: pydoc-markdown-nuxt - Transform Python Code into Beautiful Nuxt Documentation
  description: The ultimate tool for generating stunning Python API documentation that integrates seamlessly with Nuxt Content. Features MDC components, hierarchical navigation, and customizable themes.
  keywords: 
    - python documentation
    - nuxt content
    - api documentation
    - pydoc-markdown
    - mdc components
    - python docs generator
---

::u-page-hero
#title
Transform Python code into [beautiful docs]{.text-primary}

#description
The most powerful way to generate Python API documentation for Nuxt Content. 

Create stunning, interactive documentation with hierarchical navigation, rich MDC components, and seamless integration into your Nuxt.js projects.

#links
  :::u-button
  ---
  color: primary
  size: xl
  to: /getting-started/introduction
  trailing-icon: i-lucide-rocket
  ---
  Get started
  :::

  :::u-button
  ---
  color: neutral
  icon: simple-icons-github
  size: xl
  to: https://github.com/UrielCuriel/pydoc-markdown-nuxt
  variant: outline
  target: _blank
  ---
  Star on GitHub
  :::

  :::u-button
  ---
  color: gray
  icon: i-lucide-book-open
  size: xl
  to: /3.references
  variant: ghost
  ---
  View Examples
  :::
::

::u-page-section
#title
Why choose pydoc-markdown-nuxt?

#description
The perfect solution for Python developers who want to create professional documentation websites with modern web technologies.

#features
  :::u-page-feature
  ---
  icon: i-simple-icons-python
  ---
  #title
  Built for [Python]{.text-primary}
  
  #description
  Specialized renderer that understands Python modules, classes, functions, and methods. Automatically extracts docstrings, type hints, and generates comprehensive documentation with proper hierarchy.
  :::

  :::u-page-feature
  ---
  icon: i-simple-icons-nuxtdotjs
  ---
  #title
  [Nuxt Content]{.text-primary} Native
  
  #description
  First-class integration with Nuxt Content's file-based routing, automatic navigation, and powerful features. Your docs become part of your Nuxt ecosystem.
  :::

  :::u-page-feature
  ---
  icon: i-lucide-components
  ---
  #title
  [MDC Components]{.text-primary}
  
  #description
  Rich, interactive documentation using MDC components. Beautiful reference headers, syntax highlighting, type annotations, and consistent styling throughout your API docs.
  :::

  :::u-page-feature
  ---
  icon: i-lucide-folder-tree
  ---
  #title
  [Smart Organization]{.text-primary}
  
  #description
  Automatically creates logical directory structures based on your Python modules. Includes navigation files, index pages, and cross-references for large codebases.
  :::

  :::u-page-feature
  ---
  icon: i-lucide-palette
  ---
  #title
  [Visual Excellence]{.text-primary}
  
  #description
  Built-in Iconify integration with contextual icons for modules, classes, functions, and variables. Customizable themes and consistent visual hierarchy.
  :::

  :::u-page-feature
  ---
  icon: i-lucide-zap
  ---
  #title
  [Lightning Fast]{.text-primary}
  
  #description
  Efficient processing with intelligent caching and incremental builds. Generate comprehensive documentation in seconds, not minutes.
  :::
::

::u-page-section
---
class: bg-gray-50 dark:bg-gray-900/50
---
#title
Get started in [minutes]{.text-primary}

#description
From installation to beautiful documentation in just a few simple steps.

#code
```bash
# Install the package
pip install pydoc-markdown-nuxt

# Create configuration
echo "
loaders:
  - type: python
    search_path: [src]
processors:
  - type: filter
    expression: not name.startswith('_')
  - type: smart
  - type: crossref
renderer:
  type: nuxt
  content_dir: docs/content
  output_dir: 3.references
" > pydoc-markdown.yml

# Generate documentation
pydoc-markdown
```

#links
  :::u-button
  ---
  to: /getting-started/3.installation
  icon: i-lucide-download
  color: primary
  variant: outline
  ---
  Installation Guide
  :::

  :::u-button
  ---
  to: /getting-started/4.quick-start
  icon: i-lucide-rocket
  ---
  Quick Start
  :::
::

::u-page-section
#title
Perfect for [every project]{.text-primary}

#description
Whether you're building a small library or managing enterprise-scale Python applications.

#cards
  :::u-page-card
  ---
  icon: i-lucide-code
  ---
  #title
  Open Source Libraries
  
  #description
  Create beautiful documentation for your Python packages that integrates seamlessly with your project website.
  :::

  :::u-page-card
  ---
  icon: i-lucide-building
  ---
  #title
  Enterprise APIs
  
  #description
  Document complex internal APIs with hierarchical organization, cross-references, and team collaboration features.
  :::

  :::u-page-card
  ---
  icon: i-lucide-graduation-cap
  ---
  #title
  Educational Projects
  
  #description
  Perfect for tutorials, courses, and educational materials where clear, navigable documentation is essential.
  :::
::

::u-page-section
---
class: bg-primary-50 dark:bg-primary-950/50
---
#title
Join the community

#description
Get help, share feedback, and contribute to making Python documentation better for everyone.

#links
  :::u-button
  ---
  icon: simple-icons-github
  to: https://github.com/UrielCuriel/pydoc-markdown-nuxt
  target: _blank
  color: primary
  ---
  GitHub Repository
  :::

  :::u-button
  ---
  icon: i-lucide-bug
  to: https://github.com/UrielCuriel/pydoc-markdown-nuxt/issues
  target: _blank
  variant: outline
  ---
  Report Issues
  :::

  :::u-button
  ---
  icon: i-lucide-heart
  to: https://github.com/UrielCuriel/pydoc-markdown-nuxt/blob/main/CONTRIBUTING.md
  target: _blank
  variant: ghost
  ---
  Contribute
  :::
::
