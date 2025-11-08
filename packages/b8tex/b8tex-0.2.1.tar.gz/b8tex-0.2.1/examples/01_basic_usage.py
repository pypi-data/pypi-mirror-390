"""Basic B8TeX usage example."""

import shutil
from pathlib import Path
from b8tex import Document, compile_string

# Simple example: compile LaTeX from a string
latex_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\title{Hello B8TeX}
\author{Python User}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}

This is a simple example of using B8TeX to compile LaTeX documents.

B8TeX provides a modern, Pythonic interface to the Tectonic LaTeX compiler.

\section{Features}

\begin{itemize}
    \item Type-safe API
    \item Support for in-memory compilation
    \item Project-aware builds
    \item Custom package support
\end{itemize}

\end{document}
"""

# Compile the document
result = compile_string(latex_content, name="hello")

# Check the result
if result.success:
    print(f"Compilation successful!")
    print(f"PDF generated at: {result.pdf_path}")
    print(f"Compilation took: {result.elapsed:.2f} seconds")

    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {warning}")

    # Copy PDF to outputs directory
    print("=" * 60)
    print("Copying output to repository...")
    print("=" * 60)

    # Get repo root (examples are in examples/ subdirectory)
    repo_root = Path(__file__).parent.parent
    outputs_dir = repo_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    output_name = "01_basic_document.pdf"
    output_path = outputs_dir / output_name

    shutil.copy2(result.pdf_path, output_path)

    print(f"Source: {result.pdf_path}")
    print(f"Saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print()
    print("You can now view the output PDF in the outputs/ directory!")
    print("=" * 60)
else:
    print("Compilation failed!")
    for error in result.errors:
        print(f"Error: {error}")
