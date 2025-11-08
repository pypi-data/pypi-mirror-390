#!/usr/bin/env python3
"""Example 09: Full-Featured NeurIPS Paper

This example demonstrates all features of the template system:
- Builder pattern with context managers
- Nested sections and subsections
- Template variables with Jinja2
- Bibliography management
- Custom commands and packages
- Type-safe author management

This shows how to build a complete academic paper programmatically.
"""

from pathlib import Path

import b8tex
from b8tex.templates import DocumentBuilder

# Configure logging
b8tex.configure_logging(level=20)  # INFO level


def build_complete_neurips_paper():
    """Build a complete NeurIPS paper with all features."""
    print("\n" + "=" * 70)
    print("Building Complete NeurIPS Paper")
    print("=" * 70)

    # Use DocumentBuilder for fluent API with context managers
    with DocumentBuilder(
        template="neurips",
        title="Deep Learning for Scientific Computing: A Survey",
        status="draft",
        organization="Machine Learning Research Lab",
        doc_type="Conference Submission",
        doc_id="NeurIPS-2024-001",
    ) as builder:

        # Configure authors
        builder.add_author(
            "Alice Johnson",
            affiliation="Stanford University",
            email="alice@stanford.edu",
        )
        builder.add_author(
            "Bob Chen",
            affiliation="MIT CSAIL",
            email="bob@mit.edu",
        )
        builder.add_author(
            "Carol Martinez",
            affiliation="Google Brain",
            email="carol@google.com",
        )

        # Set abstract
        builder.set_abstract(
            """
            Deep learning has revolutionized scientific computing by providing
            powerful tools for solving partial differential equations, modeling
            complex physical systems, and accelerating numerical simulations.
            This survey provides a comprehensive overview of recent advances in
            physics-informed neural networks, neural operators, and learned
            optimizers for scientific applications. We discuss key challenges,
            benchmark datasets, and future directions in this rapidly evolving field.
            """
        )

        # Add keywords
        builder.add_keyword("deep learning")
        builder.add_keyword("scientific computing")
        builder.add_keyword("physics-informed neural networks")
        builder.add_keyword("neural operators")

        # Set template variables for Jinja2
        builder.set_variable("num_papers_reviewed", 157)
        builder.set_variable("num_benchmarks", 12)
        builder.set_variable("survey_year", 2024)

        # Build structured content with nested sections
        with builder.section("Introduction", label="sec:intro"):
            builder.add_paragraph(
                """
                The integration of deep learning with scientific computing has emerged
                as one of the most promising research directions in both machine learning
                and computational science. Traditional numerical methods, while proven
                and reliable, often struggle with high-dimensional problems and complex
                geometries.
                """
            )

            builder.add_paragraph(
                """
                This survey reviews {{ num_papers_reviewed }} recent papers published
                between 2020 and {{ survey_year }}, covering {{ num_benchmarks }} major
                benchmark datasets. Our goal is to provide researchers with a comprehensive
                overview of the current state of the art.
                """
            )

        with builder.section("Background", label="sec:background"):
            builder.add_text(
                "We first review the fundamental concepts necessary for understanding this field."
            )

            with builder.subsection("Neural Networks for PDEs"):
                builder.add_paragraph(
                    """
                    Physics-informed neural networks (PINNs) encode physical laws directly
                    into the loss function of a neural network. This approach allows the
                    network to learn solutions that satisfy both data constraints and
                    physical principles.
                    """
                )

                builder.add_raw_latex(
                    r"""
                    \begin{equation}
                    \mathcal{L} = \mathcal{L}_{\text{data}} + \lambda \mathcal{L}_{\text{physics}}
                    \end{equation}
                    """
                )

            with builder.subsection("Neural Operators"):
                builder.add_paragraph(
                    """
                    Neural operators learn mappings between function spaces, enabling
                    zero-shot super-resolution and fast solution of parametric PDEs.
                    The Fourier Neural Operator (FNO) has shown particular promise.
                    """
                )

        with builder.section("Methods Survey", label="sec:methods"):
            builder.add_text("We categorize recent approaches into three main families.")

            with builder.subsection("Physics-Informed Approaches"):
                builder.add_text(
                    """
                    These methods incorporate physical constraints through:
                    - Loss function penalties (PINNs)
                    - Architecture design (Hamiltonian neural networks)
                    - Data augmentation (symmetry-preserving transforms)
                    """
                )

            with builder.subsection("Data-Driven Approaches"):
                builder.add_text(
                    """
                    Pure learning-based methods that leverage large simulation datasets:
                    - Supervised learning with numerical simulators
                    - Transfer learning from related tasks
                    - Self-supervised pretraining strategies
                    """
                )

            with builder.subsection("Hybrid Methods"):
                builder.add_text(
                    """
                    Combining classical numerical methods with neural networks:
                    - Neural network-based preconditioners
                    - Learned time-stepping schemes
                    - Adaptive mesh refinement with reinforcement learning
                    """
                )

        with builder.section("Benchmark Results", label="sec:results"):
            builder.add_paragraph(
                """
                We evaluate representative methods from each category on standard
                benchmarks. Table~\\ref{tab:benchmarks} summarizes the key datasets.
                """
            )

            # Note: In a real implementation, you'd add tables here using DataTable
            builder.add_raw_latex(
                r"""
                \begin{table}[h]
                \centering
                \begin{tabular}{lcc}
                \toprule
                Dataset & Equations & Samples \\
                \midrule
                Burgers & 1D PDE & 10,000 \\
                Navier-Stokes & 2D PDE & 5,000 \\
                Maxwell & 3D PDE & 2,500 \\
                \bottomrule
                \end{tabular}
                \caption{Benchmark datasets used for evaluation.}
                \label{tab:benchmarks}
                \end{table}
                """
            )

        with builder.section("Discussion", label="sec:discussion"):
            with builder.subsection("Key Findings"):
                builder.add_paragraph(
                    """
                    Our survey reveals several important trends:
                    - Physics-informed methods excel with limited data
                    - Data-driven approaches scale better to complex systems
                    - Hybrid methods offer the best of both worlds
                    """
                )

            with builder.subsection("Challenges"):
                builder.add_paragraph(
                    """
                    Despite significant progress, several challenges remain:
                    - Training stability for stiff equations
                    - Generalization to out-of-distribution parameters
                    - Computational efficiency for large-scale problems
                    """
                )

            with builder.subsection("Future Directions"):
                builder.add_paragraph(
                    """
                    We identify promising research directions for the coming years:
                    - Foundation models for scientific computing
                    - Uncertainty quantification for neural PDE solvers
                    - Integration with traditional software ecosystems
                    """
                )

        with builder.section("Conclusion", label="sec:conclusion"):
            builder.add_paragraph(
                """
                Deep learning for scientific computing has made remarkable progress
                in recent years. As the field matures, we expect to see increasing
                adoption in industrial applications and tighter integration with
                traditional computational science workflows.
                """
            )

        # Acknowledgments (unnumbered section)
        with builder.section("Acknowledgments", numbered=False):
            builder.add_text(
                """
                We thank the reviewers for their insightful comments.
                This work was supported by NSF Grant #1234567.
                """
            )

        # Build the final document
        doc = builder.build()

    # Compile to PDF
    print(f"\n  Building document with {len(doc.sections)} top-level sections...")

    result = b8tex.compile_template_document(
        doc,
        output_name="neurips_survey_paper",
        validate=True,  # Validate before compilation
    )

    print(f"\n✓ Compilation successful!")
    print(f"  PDF: {result.pdf_path}")
    print(f"  Pages: {result.pdf_path.stat().st_size // 10000} (approx)")
    print(f"  Duration: {result.elapsed:.2f}s")

    return result


def demonstrate_validation():
    """Show template validation in action."""
    print("\n" + "=" * 70)
    print("Demonstrating Template Validation")
    print("=" * 70)

    from b8tex.templates import TemplateConfig, TemplateDocument, validate_template_document

    # Create a document with some warnings
    config = TemplateConfig(
        template="acl",
        font_size="12pt",  # ACL requires 11pt - this will warn
        two_column=False,  # ACL requires two-column - this will warn
    )

    doc = TemplateDocument(
        title="ACL Paper Example",
        config=config,
        content=r"\section{Test} Content here.",
    )

    # Validate (non-strict mode)
    is_valid, issues = validate_template_document(doc, strict=False)

    print(f"\nValidation result (non-strict): {is_valid}")
    print(f"Issues found: {len(issues)}")

    for issue in issues:
        print(f"  [{issue.severity.upper()}] {issue.message}")

    # Validate (strict mode - warnings become errors)
    is_valid_strict, issues_strict = validate_template_document(doc, strict=True)

    print(f"\nValidation result (strict): {is_valid_strict}")
    print("In strict mode, warnings are treated as errors.")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("B8TeX Template Example - Full NeurIPS Paper")
    print("=" * 70)

    try:
        # Build complete paper
        build_complete_neurips_paper()

        # Show validation
        demonstrate_validation()

        print("\n" + "=" * 70)
        print("Example completed successfully!")
        print("=" * 70)
        print("\nThis example demonstrated:")
        print("  ✓ Fluent builder API with context managers")
        print("  ✓ Nested sections and subsections")
        print("  ✓ Template variables with Jinja2")
        print("  ✓ Type-safe author management")
        print("  ✓ Document validation (strict and non-strict)")
        print("\nNext: See 10_data_driven_template.py for data integration")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
