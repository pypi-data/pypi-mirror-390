# Future Features Roadmap

This document outlines planned features for future versions of B8TeX beyond v0.1.0.

## Version 0.2.0 - Template System

### Overview

A template system for creating LaTeX documents from pre-built templates, similar to cookiecutter for Python projects.

### Features

#### Template Management
- Built-in templates (article, beamer, report, thesis)
- Custom template installation from Git URLs
- Template discovery and validation
- Variable substitution in templates

#### CLI Commands
```bash
b8tex template list                    # List available templates
b8tex template show article            # Show template details
b8tex template create my-paper \       # Create from template
    --template=article \
    --title="My Paper" \
    --author="John Doe"
b8tex template install <url>           # Install custom template
```

#### Python API
```python
from b8tex import TemplateManager

manager = TemplateManager()
template = manager.get_template("article")
document = manager.render(template, {
    "title": "My Research Paper",
    "author": "Jane Doe",
    "content": "..."
})
```

### Implementation Plan

**Module Structure:**
```
src/b8tex/templates/
├── __init__.py
├── template.py       # Template dataclass
├── manager.py        # TemplateManager class
├── registry.py       # Template discovery
└── builtin/          # Built-in templates
    ├── article/
    ├── beamer/
    ├── report/
    └── thesis/
```

**Key Classes:**
- `Template` - Template representation with metadata
- `TemplateVar` - Template variable with type and validation
- `TemplateManager` - Template rendering and management
- `TemplateRegistry` - Template discovery

**Built-in Templates:**
1. **Article** - Basic paper/report template
2. **Beamer** - Presentation template with themes
3. **Report** - Multi-chapter report structure
4. **Thesis** - Academic thesis with front matter

**Effort:** 8-12 hours

**Tests:** ~25-30 test cases

---

## Version 0.2.0 - Jinja2 Preprocessor

### Overview

Preprocessing step using Jinja2 template engine for dynamic LaTeX document generation.

### Features

#### Variable Substitution
```latex
\documentclass{article}
\title{<<< title >>>}
\author{<<< author >>>}
\begin{document}
\maketitle
<<< content >>>
\end{document}
```

#### Conditional Content
```latex
<%% if include_abstract %%>
\begin{abstract}
<<< abstract_text >>>
\end{abstract}
<%% endif %%>
```

#### Loops
```latex
\begin{itemize}
<%% for item in items %%>
\item <<< item >>>
<%% endfor %%>
\end{itemize}
```

### Python API

```python
from b8tex import compile_string

result = compile_string(
    latex_template,
    preprocessor_vars={
        "title": "Dynamic Document",
        "author": "Jane Doe",
        "items": ["First", "Second", "Third"],
        "include_abstract": True,
        "abstract_text": "This is the abstract..."
    }
)
```

### LaTeX-Friendly Delimiters

To avoid collisions with LaTeX syntax:
- Variables: `<<< var >>>` instead of `{{ var }}`
- Blocks: `<%% if %%>` instead of `{% if %}`
- Comments: `<# comment #>` instead of `{# comment #}`

### Custom Filters

```python
# LaTeX escaping filter
{{ text | latex }}

# Automatic escaping of special characters: & % $ # _ { } ~ ^ \
```

### Implementation Plan

**Module Structure:**
```
src/b8tex/preprocessors/
├── __init__.py
├── base.py                   # Preprocessor ABC
├── jinja2_preprocessor.py    # Jinja2 implementation
└── passthrough.py            # No-op preprocessor
```

**Integration Points:**
- `BuildOptions.preprocessor` - Configuration
- `Workspace.stage_document()` - Preprocessing step
- `TectonicCompiler.compile_document()` - API parameter

**Dependencies:**
- `jinja2>=3.1.0` (optional dependency)

**Effort:** 6-8 hours

**Tests:** ~20-25 test cases

---

## Version 0.3.0 - Additional Features

### Biber/BibLaTeX Integration

Automatic bibliography processing with tectonic-biber.

**Features:**
- Automatic biber detection
- Bibliography file validation
- Integrated bibliography processing
- Build option: `run_biber=True`

**Effort:** 4-6 hours

### Enhanced Module Graph

Advanced dependency analysis and visualization.

**Features:**
- Circular dependency detection
- Unused resource detection
- GraphViz export
- Critical path analysis

**Effort:** 8-10 hours

### Streaming Diagnostics

Real-time compilation output and progress reporting.

**Features:**
- `run_streaming()` method
- Line-by-line output callbacks
- Progress reporting
- Real-time error display

**Effort:** 10-15 hours

---

## Version 0.4.0 - IDE Integration

### LSP-Style Diagnostics

Language Server Protocol compatible output for IDE integration.

**Features:**
- Structured JSON diagnostics
- File/line/column error locations
- Include stack visualization
- LSP-compatible error format

**Effort:** 15-20 hours

### Language Server

Full LSP server implementation for IDE plugins.

**Features:**
- Diagnostics publishing
- Document compilation on save
- Incremental compilation
- Error location navigation

**Effort:** 30-40 hours

---

## Implementation Priority

### High Priority (v0.2.0)
1. **Template System** - Major differentiator, high user value
2. **Jinja2 Preprocessor** - Enables dynamic documents, synergizes with templates

### Medium Priority (v0.3.0)
3. **Biber Integration** - Improves bibliography workflow
4. **Module Graph Enhancements** - Better debugging
5. **Streaming Diagnostics** - Better UX for large documents

### Lower Priority (v0.4.0+)
6. **LSP Integration** - Specialized use case (IDE developers)
7. **Language Server** - Complex implementation, narrow audience

---

## Getting Involved

These features represent significant development effort. Contributions are welcome!

### How to Contribute

1. **Review** this document and the detailed plans
2. **Discuss** implementation approach in GitHub issues
3. **Implement** features following CONTRIBUTING.md guidelines
4. **Test** thoroughly with comprehensive test cases
5. **Document** with examples and API reference
6. **Submit** pull request for review

### Feature Requests

Have ideas for other features? Open an issue on GitHub!

---

## Design Principles

All future features must adhere to B8TeX's core principles:

✅ **Type Safety** - Full type hints with mypy validation
✅ **No Hacks** - Clean, maintainable implementations
✅ **Security** - Proper validation and error handling
✅ **Performance** - Efficient algorithms, caching where appropriate
✅ **No Over-Engineering** - Simple solutions to real problems
✅ **Comprehensive Tests** - 85%+ coverage for all new code
✅ **Clear Documentation** - Examples and API docs for all features

---

## Timeline Estimates

**v0.2.0** (Templates + Jinja2): 2-3 weeks development time
**v0.3.0** (Enhancements): 2-3 weeks development time
**v0.4.0** (IDE Integration): 4-6 weeks development time

Actual timeline depends on contributor availability and community feedback.

---

## Questions?

For questions about future features:
- Open an issue on GitHub
- Check existing discussions
- Review the CONTRIBUTING.md guide

---

*Last Updated: 2025-01-28*
*B8TeX Version: 0.1.0*
