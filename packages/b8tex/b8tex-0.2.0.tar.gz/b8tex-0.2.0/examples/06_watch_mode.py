"""Example demonstrating watch mode for auto-rebuild on file changes.

This example shows how to use B8TeX's watch mode to automatically recompile
your LaTeX documents whenever source files change, perfect for live editing.

Note: Requires the 'watch' extra: pip install b8tex[watch]
"""

import asyncio
import shutil
from pathlib import Path
from b8tex import Document, TectonicCompiler, BuildOptions

# Check if watch mode is available
try:
    from b8tex import Watcher
except ImportError:
    print("Watch mode is not available.")
    print("Install with: pip install b8tex[watch]")
    exit(1)


async def watch_demo():
    """Demonstrate watch mode functionality."""
    print("=" * 60)
    print("B8TeX Watch Mode Demo")
    print("=" * 60)
    print()

    # Create a sample document
    sample_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\title{Watch Mode Demo}
\author{B8TeX}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}

This document is being watched for changes.

Try editing this file and saving it - B8TeX will automatically
rebuild the document!

\section{Features}

Watch mode provides:
\begin{itemize}
    \item Automatic rebuilds on file changes
    \item Debouncing to avoid excessive builds
    \item Custom file patterns
    \item Success/error callbacks
\end{itemize}

\end{document}
"""

    # Create a temporary file
    temp_file = Path("watched_document.tex")
    temp_file.write_text(sample_content)

    try:
        # Create document and compiler
        document = Document.from_path(temp_file)
        compiler = TectonicCompiler()
        watcher = Watcher(compiler, debounce_seconds=1.0)

        # Define callbacks
        def on_success(result):
            print(f"✓ Build successful in {result.elapsed:.2f}s")
            print(f"  PDF: {result.pdf_path}")
            if result.warnings:
                print(f"  Warnings: {len(result.warnings)}")

            # Copy PDF to outputs directory on each rebuild
            try:
                repo_root = Path(__file__).parent.parent
                outputs_dir = repo_root / "outputs"
                outputs_dir.mkdir(exist_ok=True)
                output_path = outputs_dir / "06_watch_demo.pdf"
                shutil.copy2(result.pdf_path, output_path)
                print(f"  Copied to: {output_path}")
            except Exception as e:
                print(f"  Warning: Could not copy to outputs/: {e}")

        def on_error(error):
            print(f"✗ Build failed: {error}")

        print("Starting watch mode...")
        print(f"Watching: {temp_file}")
        print()
        print("Instructions:")
        print("1. Edit watched_document.tex in another window")
        print("2. Save the file")
        print("3. Watch B8TeX automatically rebuild!")
        print()
        print("Press Ctrl+C to stop watching...")
        print()

        # Start watching
        handle = await watcher.watch_document(
            document,
            options=BuildOptions(),
            on_success=on_success,
            on_error=on_error,
            watch_patterns=["*.tex", "*.sty", "*.bib"],
        )

        # Keep running until interrupted
        try:
            while handle.is_running():
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping watch mode...")
            handle.stop()
            await handle.wait()

        print(f"\nTotal compilations: {handle.compile_count}")

    finally:
        # Clean up
        print("\nCleaning up...")
        if temp_file.exists():
            temp_file.unlink()
        pdf_file = Path("watched_document.pdf")
        if pdf_file.exists():
            pdf_file.unlink()

    print("Done!")


async def watch_project_demo():
    """Example of watching an entire project directory."""
    print("=" * 60)
    print("B8TeX Watch Mode - Project Example")
    print("=" * 60)
    print()
    print("This example shows watching a project directory.")
    print()

    # In a real scenario, you would:
    # 1. Create a project with Tectonic.toml
    # 2. Watch the project directory
    # 3. Auto-rebuild on any .tex, .sty, or resource changes

    print("Setup for project watching:")
    print()
    print("```python")
    print("from b8tex import Document, Watcher, TectonicCompiler")
    print("from pathlib import Path")
    print()
    print("# Your project structure:")
    print("# my_project/")
    print("#   Tectonic.toml")
    print("#   main.tex")
    print("#   chapters/")
    print("#     chapter1.tex")
    print("#     chapter2.tex")
    print("#   styles/")
    print("#     mystyle.sty")
    print()
    print("document = Document.from_path(Path('my_project/main.tex'))")
    print("compiler = TectonicCompiler()")
    print("watcher = Watcher(compiler)")
    print()
    print("handle = await watcher.watch_document(")
    print("    document,")
    print("    on_success=lambda r: print(f'Built: {r.pdf_path}'),")
    print("    watch_patterns=['*.tex', '*.sty', '*.bib', '*.cls'],")
    print(")")
    print()
    print("# Let it run...")
    print("await handle.wait()")
    print("```")
    print()


def show_advanced_usage():
    """Show advanced watch mode patterns."""
    print("=" * 60)
    print("Advanced Watch Mode Patterns")
    print("=" * 60)
    print()

    print("1. Custom Debouncing:")
    print("   watcher = Watcher(compiler, debounce_seconds=2.0)")
    print()

    print("2. Watching Specific Patterns:")
    print("   handle = await watcher.watch_document(")
    print("       document,")
    print("       watch_patterns=['*.tex', '*.bib']  # Only .tex and .bib")
    print("   )")
    print()

    print("3. Conditional Rebuilds:")
    print("   def smart_rebuild(result):")
    print("       if result.warnings:")
    print("           print('⚠️  Build has warnings, check output')")
    print("       else:")
    print("           print('✓ Clean build!')")
    print()
    print("   handle = await watcher.watch_document(")
    print("       document,")
    print("       on_success=smart_rebuild")
    print("   )")
    print()

    print("4. Error Handling:")
    print("   def handle_error(error):")
    print("       # Log error to file, send notification, etc.")
    print("       with open('build_errors.log', 'a') as f:")
    print("           f.write(f'{datetime.now()}: {error}\\n')")
    print()
    print("   handle = await watcher.watch_document(")
    print("       document,")
    print("       on_error=handle_error")
    print("   )")
    print()

    print("5. Stopping Programmatically:")
    print("   # Stop after N builds")
    print("   async def stop_after_n_builds(handle, n):")
    print("       while handle.compile_count < n:")
    print("           await asyncio.sleep(1)")
    print("       handle.stop()")
    print()


async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run the interactive demo
        await watch_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--project":
        # Show project example
        await watch_project_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--advanced":
        # Show advanced patterns
        show_advanced_usage()
    else:
        print("B8TeX Watch Mode Examples")
        print()
        print("Usage:")
        print("  python 06_watch_mode.py --demo      # Run interactive demo")
        print("  python 06_watch_mode.py --project   # Show project example")
        print("  python 06_watch_mode.py --advanced  # Show advanced patterns")
        print()
        print("Note: Requires watchfiles package")
        print("      Install with: pip install b8tex[watch]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
