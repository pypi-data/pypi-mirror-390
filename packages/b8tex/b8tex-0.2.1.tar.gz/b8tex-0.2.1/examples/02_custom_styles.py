"""Example using custom style files."""

import shutil
from pathlib import Path
from b8tex import Document, InMemorySource, Resource, compile_document

# Define a custom style package
custom_style = InMemorySource(
    filename="mystyle.sty",
    content=r"""
\ProvidesPackage{mystyle}

% Custom colors
\usepackage{xcolor}
\definecolor{customblue}{RGB}{0,102,204}

% Custom title format
\usepackage{titlesec}
\titleformat{\section}
  {\color{customblue}\Large\bfseries}
  {\thesection}{1em}{}

% Custom command
\newcommand{\highlight}[1]{\textcolor{customblue}{\textbf{#1}}}
""",
)

# Main document that uses the custom style
main_content = InMemorySource(
    filename="main.tex",
    content=r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{mystyle}

\title{Document with Custom Style}
\author{B8TeX User}

\begin{document}

\maketitle

\section{Introduction}

This document uses a \highlight{custom style package} defined in Python!

The style package provides:
\begin{itemize}
    \item Custom colors
    \item Formatted section titles
    \item A highlight command
\end{itemize}

\section{More Content}

B8TeX makes it easy to bundle \highlight{custom packages} with your documents.

\end{document}
""",
)

# Create document with custom style as a resource
document = Document(
    name="styled_doc",
    entrypoint=main_content,
    resources=[Resource(custom_style, kind="sty")],
)

# Compile
result = compile_document(document)

if result.success:
    print(f"Success! PDF at: {result.pdf_path}")

    # Copy PDF to outputs directory
    print("=" * 60)
    print("Copying output to repository...")
    print("=" * 60)

    # Get repo root (examples are in examples/ subdirectory)
    repo_root = Path(__file__).parent.parent
    outputs_dir = repo_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    output_name = "02_custom_styles.pdf"
    output_path = outputs_dir / output_name

    shutil.copy2(result.pdf_path, output_path)

    print(f"Source: {result.pdf_path}")
    print(f"Saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print()
    print("You can now view the output PDF in the outputs/ directory!")
    print("=" * 60)
else:
    print("Compilation failed:")
    for error in result.errors:
        print(f"  {error}")
