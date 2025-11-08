#!/usr/bin/env python3
"""Example 08: Basic Template Usage

This example demonstrates the simplest way to use B8TeX templates:
- Using compile_template() function for quick document creation
- NeurIPS, ICLR, and ACL templates
- Different status modes (draft, final, confidential)
- Structured sections vs. raw LaTeX content
- Document metadata (organization, doc_type, doc_id)

Templates provide pre-configured styles for academic conferences and
professional documents without needing to manage LaTeX preambles.

All examples include metadata (organization, doc_type, doc_id) to demonstrate
proper document tracking and identification.
"""

from pathlib import Path

import b8tex
from b8tex.templates import Author, Section, compile_template

# Configure logging to see what's happening
b8tex.configure_logging(level=20)  # INFO level


def example_neurips_simple():
    """Simplest possible NeurIPS document."""
    print("\n" + "=" * 70)
    print("Example 1: Minimal NeurIPS Document")
    print("=" * 70)

    result = compile_template(
        template="neurips",
        title="My First Neural Network Paper",
        authors="John Doe",
        abstract="This paper presents a novel approach to neural networks.",
        content=r"""
\section{Introduction}
Neural networks have revolutionized machine learning.

\section{Methods}
We used a standard feedforward architecture.

\section{Results}
Our model achieved 95\% accuracy.

\section{Conclusion}
Neural networks work great!
""",
    )

    print(f"\n✓ Compilation successful: {result.success}")
    print(f"  PDF output: {result.pdf_path}")
    print(f"  Compilation took: {result.elapsed:.2f}s")


def example_with_structured_sections():
    """Using Section objects for structured content."""
    print("\n" + "=" * 70)
    print("Example 2: Structured Sections (Type-Safe)")
    print("=" * 70)

    result = compile_template(
        template="neurips",
        title="Structured Document Example",
        authors=[
            Author(name="Alice Smith", affiliation="MIT", email="alice@mit.edu"),
            Author(name="Bob Johnson", affiliation="Stanford"),
        ],
        abstract="We demonstrate structured document building with type-safe sections.",
        keywords=["machine learning", "document generation", "templates"],
        metadata={
            "organization": "Joint Research Collaboration",
            "doc_type": "Conference Paper",
            "doc_id": "NeurIPS-2024-DEMO",
        },
        sections=[
            Section(
                title="Introduction",
                content="This introduction explains our motivation.",
                label="sec:intro",
            ),
            Section(
                title="Background",
                content="Previous work in this area includes...",
                numbered=True,
            ),
            Section(
                title="Methods",
                content="Our experimental setup consisted of...",
            ),
            Section(
                title="Acknowledgments",
                content="We thank the reviewers for their feedback.",
                numbered=False,  # Unnumbered section
            ),
        ],
    )

    print(f"\n✓ Document compiled successfully")
    print(f"  Output: {result.pdf_path}")


def example_draft_vs_final():
    """Different status modes: draft, final, confidential."""
    print("\n" + "=" * 70)
    print("Example 3: Status Modes (Draft vs Final)")
    print("=" * 70)

    # Draft mode (shows line numbers, watermark, etc.)
    draft_result = compile_template(
        template="neurips",
        title="Draft Version of My Paper",
        authors="Research Team",
        status="draft",  # ← DRAFT STATUS
        content=r"""
\section{Work in Progress}
This section needs more work.

\textbf{TODO:} Add more details here.
""",
        output_name="draft_paper",
    )

    print(f"✓ Draft version: {draft_result.pdf_path}")

    # Final mode (clean, publication-ready)
    final_result = compile_template(
        template="neurips",
        title="Final Version of My Paper",
        authors="Research Team",
        status="final",  # ← FINAL STATUS
        content=r"""
\section{Introduction}
This is the polished final version.
""",
        output_name="final_paper",
    )

    print(f"✓ Final version: {final_result.pdf_path}")

    # Confidential mode (for internal documents)
    conf_result = compile_template(
        template="neurips",
        title="Confidential Research Report",
        authors="Internal Team",
        status="confidential",  # ← CONFIDENTIAL STATUS
        metadata={
            "organization": "Research Lab",
            "doc_type": "Internal Report",
            "doc_id": "REP-2024-001",
        },
        content=r"""
\section{Confidential Results}
This contains proprietary information.
""",
        output_name="confidential_report",
    )

    print(f"✓ Confidential version: {conf_result.pdf_path}")


def example_all_templates():
    """Try all available templates: NeurIPS, ICLR, ACL."""
    print("\n" + "=" * 70)
    print("Example 4: All Available Templates")
    print("=" * 70)

    templates = ["neurips", "iclr", "acl"]

    for template_name in templates:
        result = compile_template(
            template=template_name,
            title=f"Example {template_name.upper()} Paper",
            authors="Template Demo Author",
            abstract=f"This demonstrates the {template_name.upper()} template style.",
            content=r"""
\section{Introduction}
Each template has its own distinctive style.

\section{Content}
But all support the same high-level API.
""",
            output_name=f"{template_name}_example",
        )

        print(f"  ✓ {template_name.upper()}: {result.pdf_path}")


def example_custom_output_location():
    """Control output naming."""
    print("\n" + "=" * 70)
    print("Example 5: Custom Output Naming")
    print("=" * 70)

    result = compile_template(
        template="neurips",
        title="Custom Name Example",
        authors="Demo Author",
        content=r"\section{Test} This is a test.",
        output_name="my_custom_paper",  # Custom output name
    )

    print(f"✓ PDF generated with custom name: {result.pdf_path.name}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("B8TeX Template Examples - Basic Usage")
    print("=" * 70)
    print("\nThese examples show the simplest ways to use B8TeX templates.")
    print("No need to write LaTeX preambles - just focus on content!")

    try:
        example_neurips_simple()
        example_with_structured_sections()
        example_draft_vs_final()
        example_all_templates()
        example_custom_output_location()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  - See 09_neurips_template.py for full-featured NeurIPS example")
        print("  - See 10_data_driven_template.py for data-driven documents")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()
