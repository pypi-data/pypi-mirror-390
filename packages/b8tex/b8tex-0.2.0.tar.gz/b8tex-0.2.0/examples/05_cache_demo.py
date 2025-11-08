"""Example demonstrating B8TeX's build caching capabilities.

This example shows how B8TeX caches compilation results to avoid
redundant work when compiling the same document multiple times.
"""

import shutil
import time
from pathlib import Path
from b8tex import Document, TectonicCompiler, BuildCache, BuildOptions

# Sample LaTeX document
LATEX_CONTENT = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{lipsum}
\usepackage{amsmath}

\title{Caching Demo Document}
\author{B8TeX}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}

This document demonstrates B8TeX's intelligent build caching.

When you compile the same document multiple times without changes,
B8TeX will use the cached result, dramatically speeding up the build.

\section{Mathematical Content}

The cache fingerprint includes:
\begin{itemize}
    \item All source file contents
    \item Build options
    \item Tectonic version
    \item Dependency graph
\end{itemize}

\subsection{Example Equation}

The quadratic formula is:

\begin{equation}
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\end{equation}

\section{More Content}

\lipsum[1-5]

\subsection{Another Section}

\lipsum[6-10]

\section{Conclusion}

The build cache uses content-addressed storage for artifacts,
providing both speed and efficient disk usage.

\end{document}
"""


def compile_with_timing(compiler, document, label):
    """Compile document and measure time."""
    print(f"\n{label}")
    print("-" * 60)

    start = time.time()
    result = compiler.compile_document(document)
    elapsed = time.time() - start

    if result.success:
        print(f"✓ Compilation successful")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  PDF: {result.pdf_path}")
        if result.warnings:
            print(f"  Warnings: {len(result.warnings)}")
    else:
        print(f"✗ Compilation failed")
        for error in result.errors:
            print(f"  Error: {error}")

    return result, elapsed


def main():
    """Demonstrate caching behavior."""
    print("=" * 60)
    print("B8TeX Build Cache Demo")
    print("=" * 60)

    # Create document
    document = Document.from_string(LATEX_CONTENT, name="cache_demo")
    options = BuildOptions()

    # Initialize compiler with caching enabled (default)
    cache = BuildCache()
    compiler = TectonicCompiler(cache=cache, use_cache=True)

    print("\nCache Statistics (Initial):")
    stats = cache.stats()
    print(f"  Entries: {stats['total_entries']}")
    print(f"  Size: {stats['db_size_bytes']:,} bytes")

    # First compilation - should be slow (no cache)
    result1, time1 = compile_with_timing(
        compiler, document, "First Compilation (Building cache)"
    )

    # Second compilation - should be FAST (cache hit!)
    result2, time2 = compile_with_timing(
        compiler, document, "Second Compilation (Cache hit expected)"
    )

    # Third compilation - still fast
    result3, time3 = compile_with_timing(
        compiler, document, "Third Compilation (Cache hit expected)"
    )

    # Print summary
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    print(f"First compile:  {time1:.3f}s (no cache)")
    print(f"Second compile: {time2:.3f}s (cached)")
    print(f"Third compile:  {time3:.3f}s (cached)")

    if time2 < time1:
        speedup = time1 / time2
        print(f"\nCache speedup: {speedup:.1f}x faster!")
    else:
        print("\nNote: Cache speedup may vary on first run.")
        print("Try running this example multiple times.")

    # Cache statistics
    print("\n" + "=" * 60)
    print("Cache Statistics (Final)")
    print("=" * 60)
    stats = cache.stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Database size: {stats['db_size_bytes']:,} bytes")
    print(f"Total size: {stats['total_size_bytes']:,} bytes")
    print(f"Artifacts dir: {cache.artifacts_dir}")

    # Show cache fingerprint
    fingerprint = cache.get_fingerprint(
        document,
        options,
        tectonic_version=compiler.binary.capabilities.version
        if compiler.binary.capabilities
        else "unknown",
    )
    print(f"\nCache fingerprint: {fingerprint[:16]}...")

    # Demonstrate cache invalidation
    print("\n" + "=" * 60)
    print("Cache Management")
    print("=" * 60)
    print("Cache operations available:")
    print("  - cache.clear()      # Clear all entries")
    print("  - cache.cleanup()    # Remove old entries")
    print("  - cache.invalidate() # Invalidate specific entry")
    print("  - cache.stats()      # Get statistics")

    print("\n" + "=" * 60)
    print("Key Takeaways")
    print("=" * 60)
    print("1. First compilation caches the result")
    print("2. Subsequent compilations reuse cached artifacts")
    print("3. Cache is content-addressed for efficiency")
    print("4. Changing document content invalidates cache")
    print("5. Cache persists across Python sessions")

    # Copy PDF to outputs directory
    print("\n" + "=" * 60)
    print("Copying output to repository...")
    print("=" * 60)

    # Get repo root (examples are in examples/ subdirectory)
    repo_root = Path(__file__).parent.parent
    outputs_dir = repo_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    output_name = "05_cache_demo.pdf"
    output_path = outputs_dir / output_name

    shutil.copy2(result3.pdf_path, output_path)

    print(f"Source: {result3.pdf_path}")
    print(f"Saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print()
    print("You can now view the output PDF in the outputs/ directory!")
    print("=" * 60)


if __name__ == "__main__":
    main()
