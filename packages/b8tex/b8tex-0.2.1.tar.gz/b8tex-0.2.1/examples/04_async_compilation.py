"""Example demonstrating async compilation with B8TeX.

This example shows how to compile multiple documents concurrently using
B8TeX's async API, which is useful for batch processing or web applications.
"""

import asyncio
import shutil
import time
from pathlib import Path
from b8tex import Document, TectonicCompiler, BuildOptions

# Sample LaTeX documents
DOCUMENTS = [
    (
        "report_1",
        r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{lipsum}

\title{Technical Report 1}
\author{B8TeX Async Demo}
\date{\today}

\begin{document}
\maketitle
\section{Executive Summary}
\lipsum[1-3]
\section{Methodology}
\lipsum[4-6]
\section{Results}
\lipsum[7-9]
\end{document}
""",
    ),
    (
        "report_2",
        r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{lipsum}

\title{Technical Report 2}
\author{B8TeX Async Demo}
\date{\today}

\begin{document}
\maketitle
\section{Introduction}
\lipsum[10-12]
\section{Analysis}
\lipsum[13-15]
\section{Conclusion}
\lipsum[16-18]
\end{document}
""",
    ),
    (
        "report_3",
        r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{lipsum}

\title{Technical Report 3}
\author{B8TeX Async Demo}
\date{\today}

\begin{document}
\maketitle
\section{Background}
\lipsum[19-21]
\section{Implementation}
\lipsum[22-24]
\section{Discussion}
\lipsum[25-27]
\end{document}
""",
    ),
]


async def compile_document_async(compiler, name, content):
    """Compile a single document asynchronously."""
    print(f"Starting compilation of {name}...")

    document = Document.from_string(content, name=name)
    options = BuildOptions()

    # Use the async runner
    start = time.time()
    result = await compiler.runner.run_async(
        cmd=compiler._build_command(
            document.entrypoint, compiler.runner._temp_outdir, options
        ),
        cwd=compiler.runner._temp_workdir,
        timeout=60.0,
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"✓ {name} completed in {elapsed:.2f}s")
        return (name, True, elapsed)
    else:
        print(f"✗ {name} failed in {elapsed:.2f}s")
        return (name, False, elapsed)


async def main():
    """Main async function demonstrating concurrent compilation."""
    print("=" * 60)
    print("B8TeX Async Compilation Demo")
    print("=" * 60)
    print(f"\nCompiling {len(DOCUMENTS)} documents concurrently...\n")

    # Initialize compiler
    compiler = TectonicCompiler()

    # Start timing
    overall_start = time.time()

    # Create tasks for all documents
    tasks = [
        compile_document_async(compiler, name, content)
        for name, content in DOCUMENTS
    ]

    # Run all compilations concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Calculate statistics
    overall_elapsed = time.time() - overall_start
    successful = sum(1 for r in results if isinstance(r, tuple) and r[1])
    failed = len(results) - successful
    total_time = sum(r[2] for r in results if isinstance(r, tuple))

    # Print summary
    print("\n" + "=" * 60)
    print("Compilation Summary")
    print("=" * 60)
    print(f"Total documents: {len(DOCUMENTS)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Wall time: {overall_elapsed:.2f}s")
    print(f"Total compile time: {total_time:.2f}s")
    print(f"Speedup: {total_time / overall_elapsed:.2f}x")
    print()
    print("Note: Async compilation allows multiple documents to be")
    print("compiled concurrently, significantly reducing total time")
    print("for batch operations.")


if __name__ == "__main__":
    # Note: This is a simplified example showing the concept of async compilation
    # In practice, you'd use the full compile_document flow with proper workspace management
    print("\n⚠️  Note: This example demonstrates async patterns.")
    print("For production use, use the async methods on TectonicCompiler.\n")

    # Uncomment to run (requires proper async implementation in runner)
    # asyncio.run(main())

    print("Async compilation example prepared.")
    print("See the runner.run_async() method for full async support.")
    print()
    print("=" * 60)
    print("Note about PDF output:")
    print("=" * 60)
    print("When async compilation is fully implemented, PDFs would be copied to:")
    print("  - outputs/04_async_report_1.pdf")
    print("  - outputs/04_async_report_2.pdf")
    print("  - outputs/04_async_report_3.pdf")
    print("=" * 60)
