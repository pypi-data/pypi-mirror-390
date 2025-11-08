"""High-level API for template-based document compilation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from b8tex.api import compile_document
from b8tex.core.options import BuildOptions
from b8tex.core.results import CompileResult
from b8tex.templates.config import TemplateConfig
from b8tex.templates.document import Section, TemplateDocument
from b8tex.templates.renderer import TemplateRenderer
from b8tex.templates.validation import TemplateValidator

if TYPE_CHECKING:
    from b8tex.templates.config import Author


def compile_template(
    template: str,
    title: str,
    content: str | None = None,
    sections: list[Section] | None = None,
    *,
    authors: list[Author] | str | None = None,
    abstract: str | None = None,
    keywords: list[str] | None = None,
    status: str = "final",
    metadata: dict[str, str] | None = None,
    build_options: BuildOptions | None = None,
    output_name: str = "document",
    validate: bool = True,
    **kwargs,
) -> CompileResult:
    """Compile a document using a template.

    High-level convenience function for template-based compilation.

    Args:
        template: Template name (neurips, iclr, acl)
        title: Document title
        content: Raw LaTeX content (alternative to sections)
        sections: Structured sections (alternative to content)
        authors: List of Author objects or author string
        abstract: Document abstract
        keywords: Document keywords
        status: Document status (final, confidential, internal, draft)
        metadata: Template metadata dict (organization, doc_type, doc_id)
        build_options: B8TeX build options
        output_name: Output file name
        validate: Whether to validate before compilation
        **kwargs: Additional TemplateDocument arguments

    Returns:
        CompileResult from compilation

    Raises:
        ValueError: If validation fails (when validate=True)

    Example:
        >>> from b8tex.templates import compile_template
        >>> result = compile_template(
        ...     template="neurips",
        ...     title="My Paper",
        ...     authors="John Doe",
        ...     abstract="This paper presents...",
        ...     content=r"\\section{Introduction} Hello world!",
        ...     status="draft",
        ... )
    """
    from b8tex.templates.config import TemplateMetadata

    # Build template configuration
    template_metadata = None
    if metadata:
        template_metadata = TemplateMetadata(
            organization=metadata.get("organization"),
            doc_type=metadata.get("doc_type"),
            doc_id=metadata.get("doc_id"),
        )

    config = TemplateConfig(
        template=template,  # type: ignore
        status=status,  # type: ignore
        metadata=template_metadata,
    )

    # Create template document
    template_doc = TemplateDocument(
        title=title,
        config=config,
        content=content,
        sections=sections,
        authors=authors,
        abstract=abstract,
        keywords=keywords,
        **kwargs,
    )

    return compile_template_document(
        template_doc,
        build_options=build_options,
        output_name=output_name,
        validate=validate,
    )


def compile_template_document(
    template_doc: TemplateDocument,
    *,
    build_options: BuildOptions | None = None,
    output_name: str = "document",
    validate: bool = True,
) -> CompileResult:
    """Compile a TemplateDocument to PDF.

    Args:
        template_doc: Template document to compile
        build_options: B8TeX build options
        output_name: Output file name
        validate: Whether to validate before compilation

    Returns:
        CompileResult from compilation

    Raises:
        ValueError: If validation fails (when validate=True)

    Example:
        >>> from b8tex.templates import TemplateDocument, TemplateConfig, Section
        >>> config = TemplateConfig(template="neurips", status="draft")
        >>> doc = TemplateDocument(
        ...     title="My Paper",
        ...     config=config,
        ...     sections=[Section("Introduction", "Content here...")],
        ... )
        >>> result = compile_template_document(doc)
    """
    # Validate document
    if validate:
        validator = TemplateValidator(strict=False)
        issues = validator.validate(template_doc)

        if validator.has_errors(issues):
            error_msg = validator.format_issues(issues)
            raise ValueError(f"Template validation failed:\n{error_msg}")

        # Log warnings/info
        if issues:
            import warnings
            warnings.warn(
                f"Template validation issues:\n{validator.format_issues(issues)}",
                UserWarning,
                stacklevel=2,
            )

    # Render to b8tex Document
    renderer = TemplateRenderer(template_doc)
    b8tex_doc = renderer.to_document(name=output_name)

    # Compile
    return compile_document(b8tex_doc, options=build_options)


def render_template_latex(template_doc: TemplateDocument) -> str:
    """Render a TemplateDocument to LaTeX source (without compilation).

    Useful for debugging or generating LaTeX for external use.

    Args:
        template_doc: Template document to render

    Returns:
        Complete LaTeX source code

    Example:
        >>> latex_source = render_template_latex(doc)
        >>> print(latex_source[:100])
        \\documentclass{article}
        \\usepackage[draft]{neurips}
        ...
    """
    renderer = TemplateRenderer(template_doc)
    return renderer.render_latex()


def validate_template_document(
    template_doc: TemplateDocument,
    strict: bool = False,
) -> tuple[bool, list]:
    """Validate a template document.

    Args:
        template_doc: Document to validate
        strict: If True, treat warnings as errors

    Returns:
        Tuple of (is_valid, issues_list)

    Example:
        >>> is_valid, issues = validate_template_document(doc)
        >>> if not is_valid:
        ...     print("Validation failed:")
        ...     for issue in issues:
        ...         print(f"  - {issue}")
    """
    validator = TemplateValidator(strict=strict)
    issues = validator.validate(template_doc)
    is_valid = not validator.has_errors(issues)
    return is_valid, issues
