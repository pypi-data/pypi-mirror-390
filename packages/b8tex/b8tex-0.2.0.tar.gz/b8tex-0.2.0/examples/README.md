# B8TeX Examples

This directory contains examples demonstrating various B8TeX features.

## Prerequisites

Make sure you have Tectonic installed:

```bash
# macOS
brew install tectonic

# Or install from https://tectonic-typesetting.github.io/
```

## Running Examples

Install B8TeX in development mode:

```bash
# From the project root
uv pip install -e .
```

Then run any example:

```bash
python examples/01_basic_usage.py
```

## Examples

1. **01_basic_usage.py** - Basic document compilation from a string
2. **02_custom_styles.py** - Using custom style files and packages
3. **03_project_build.py** - Multi-target project builds
4. **04_async_compilation.py** - Async/concurrent compilation for batch processing
5. **05_cache_demo.py** - Build caching and performance optimization
6. **06_watch_mode.py** - File watching and auto-rebuild on changes
7. **07_ml_experiment_report.py** - Complex ML experiment report with plots and tables

## Example Details

### 01_basic_usage.py
Demonstrates the simplest way to compile LaTeX with B8TeX. Shows:
- Compiling from a string using `compile_string()`
- Checking compilation results
- Accessing generated PDF files
- Handling warnings and errors

### 02_custom_styles.py
Shows how to bundle custom style files with your documents. Demonstrates:
- Creating in-memory style packages
- Adding resources to documents
- Using custom LaTeX packages defined in Python

### 03_project_build.py
Multi-target project compilation. Demonstrates:
- Creating projects with multiple build targets
- Different output formats (PDF, HTML)
- Target-specific build options

### 04_async_compilation.py
Concurrent document compilation. Demonstrates:
- Async compilation patterns
- Batch processing multiple documents
- Performance benefits of concurrent builds
- Using the async runner API

### 05_cache_demo.py
Build caching and performance. Demonstrates:
- How B8TeX caches compilation results
- Cache speedup measurements
- Cache management operations
- Content-addressed artifact storage

### 06_watch_mode.py
File watching and auto-rebuild. Demonstrates:
- Automatic recompilation on file changes
- Watch mode with custom file patterns
- Success/error callbacks
- Debouncing to avoid excessive builds
- Project directory watching

**Note**: Requires `watchfiles` package. Install with: `pip install b8tex[watch]`

### 07_ml_experiment_report.py
Machine learning experiment report generation. Demonstrates:
- Multi-file LaTeX project structure
- CSV data integration with PGFPlots
- Training curves visualization (loss and accuracy)
- Confusion matrix visualization with TikZ
- Professional tables with tabularx
- Per-class performance metrics
- Comprehensive scientific document formatting
- Bibliography and citations

**Note**: Requires `numpy` package. Install with: `pip install b8tex numpy`

This example generates a complete ML experiment report including:
- Abstract and introduction
- Experimental setup (ResNet-50 on CIFAR-10)
- Training dynamics with convergence plots
- Performance evaluation with metrics tables
- Ablation studies
- Confusion matrix analysis
- Conclusions and references

Perfect for generating reproducible ML experiment reports!

## Notes

- All examples use in-memory compilation for simplicity
- Check the generated PDF files in the workspace directory
- Some features may require specific Tectonic versions
- Examples 01, 02, 03, 05, and 07 can be run directly
- Example 04 demonstrates async patterns (conceptual)
- Example 06 requires the `watch` extra dependency
- Example 07 requires the `numpy` package
