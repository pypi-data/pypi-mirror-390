"""Example of project-based compilation."""

import shutil
from pathlib import Path

from b8tex import (
    BuildOptions,
    Document,
    OutputFormat,
    Project,
    Target,
    TectonicCompiler,
)

# Create a project
project = Project(root=Path.cwd())

# Define multiple build targets
pdf_target = Target(
    name="pdf",
    document=Document.from_string(
        r"""
\documentclass{article}
\title{My Project}
\begin{document}
\maketitle
\section{Introduction}
This is a multi-target project.
\end{document}
""",
        name="project_doc",
    ),
    options=BuildOptions(outfmt=OutputFormat.PDF),
)

# Note: HTML output requires additional Tectonic configuration
# This is just an example of multi-target setup
html_target = Target(
    name="html",
    document=pdf_target.document,  # Same document, different output
    options=BuildOptions(outfmt=OutputFormat.HTML),
)

project.add_target(pdf_target)
# Uncomment if your Tectonic version supports HTML
# project.add_target(html_target)

# Compile the project
compiler = TectonicCompiler()

# Build PDF target
pdf_result = compiler.build_project(project, target="pdf")

if pdf_result.success:
    print(f"PDF built successfully: {pdf_result.pdf_path}")

    # Copy PDF to outputs directory
    print("=" * 60)
    print("Copying output to repository...")
    print("=" * 60)

    # Get repo root (examples are in examples/ subdirectory)
    repo_root = Path(__file__).parent.parent
    outputs_dir = repo_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    output_name = "03_project_build.pdf"
    output_path = outputs_dir / output_name

    shutil.copy2(pdf_result.pdf_path, output_path)

    print(f"Source: {pdf_result.pdf_path}")
    print(f"Saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print()
    print("You can now view the output PDF in the outputs/ directory!")
    print("=" * 60)
else:
    print("PDF build failed")

# Build HTML target (if added)
# html_result = compiler.build_project(project, target="html")
# if html_result.success:
#     print(f"HTML built successfully: {html_result.html_path}")
