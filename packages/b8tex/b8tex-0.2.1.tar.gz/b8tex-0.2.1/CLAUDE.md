# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

B8TeX is a modern, type-safe Python wrapper for the Tectonic LaTeX compiler. It provides a high-level, Pythonic interface for compiling LaTeX documents with features like in-memory compilation, custom packages, project-aware builds, security policies, resource management, and build caching.

- **Language**: Python 3.13+ with strict type hints
- **Package Manager**: `uv` (modern Python package manager)
- **Build Backend**: hatchling
- **Testing**: pytest with coverage
- **Type Checking**: mypy (strict mode)
- **Linting/Formatting**: ruff
- **Status**: Alpha (0.1.0)

## Common Development Commands

### Essential Commands
```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=b8tex --cov-report=html

# Run single test file
uv run pytest tests/test_api.py

# Run tests matching pattern
uv run pytest -k "test_compile"

# Type checking
uv run mypy src/b8tex

# Linting
uv run ruff check src tests

# Auto-fix lint issues
uv run ruff check --fix src tests

# Format code
uv run ruff format src tests

# Check formatting without changes
uv run ruff format --check src tests

# Run all quality checks
uv run pytest && uv run mypy src/b8tex && uv run ruff check src tests

# Build package
uv build

# Clean artifacts
make clean
```

### CLI Commands
```bash
# Install Tectonic binary
b8tex install-binary

# Show current config
b8tex config

# Initialize config file
b8tex init-config

# Clean cache
b8tex clean-cache
```

## Architecture & Design

### Layered Architecture
```
┌─────────────────────────────────────┐
│   Public API (compile_document)     │  High-level convenience functions
├─────────────────────────────────────┤
│   TectonicCompiler (api.py)         │  Main compiler interface
├─────────────────────────────────────┤
│   Core Modules (src/b8tex/core/)    │  Low-level functionality
│   - binary.py: Binary discovery     │
│   - workspace.py: File staging      │
│   - runner.py: Process execution    │
│   - cache.py: Build caching         │
│   - validation.py: Security checks  │
├─────────────────────────────────────┤
│   External: Tectonic Binary         │  LaTeX compilation engine
└─────────────────────────────────────┘
```

### Key Design Patterns

1. **Dataclass-driven Configuration**: `Document`, `BuildOptions`, `Project`, `SecurityPolicy`, `ResourceLimits` are all dataclasses providing type-safe, immutable configurations.

2. **Factory Pattern**:
   - `TectonicBinary.discover()` - Auto-discovery and download
   - `Workspace.create_temp()`, `Workspace.create_persistent()`
   - `Document.from_path()`, `Document.from_string()`

3. **Strategy Pattern**:
   - `LayoutStrategy` - Workspace layout (MIRROR, FLAT, TMP_ONLY)
   - `ValidationMode` - Validation strictness (strict, permissive, disabled)

4. **Composition over Inheritance**: `TectonicCompiler` composes Binary, Cache, Validator, and Runner components.

5. **Context Managers**: Temporary workspaces use context managers for automatic cleanup.

### Core Modules (src/b8tex/core/)

| Module | Lines | Responsibility |
|--------|-------|---------------|
| `binary.py` | ~400 | Tectonic binary discovery, version detection, auto-download |
| `workspace.py` | ~400 | Build workspace management, file staging, layout strategies |
| `diagnostics.py` | ~400 | Log parsing, error extraction, module dependency graphs |
| `validation.py` | ~400 | LaTeX content validation, security policy enforcement |
| `runner.py` | ~300 | Process execution with resource limits (memory, CPU, timeout) |
| `watcher.py` | ~300 | File watching for auto re-compilation |
| `cache.py` | ~250 | Fingerprint-based build caching with version tracking |
| `config.py` | ~200 | Configuration loading from TOML files and environment variables |
| `timeouts.py` | ~150 | Timeout configuration with document size-based scaling |
| `document.py` | ~150 | Document and Resource dataclasses with auto-type detection |
| `retry.py` | ~100 | Retry policies with exponential backoff |
| `results.py` | ~100 | CompileResult and OutputArtifact dataclasses |
| `project.py` | ~100 | Multi-target projects with V1/V2 interface support |
| `options.py` | ~90 | BuildOptions, OutputFormat, SecurityPolicy enums |

### Security & Resource Management

B8TeX emphasizes security and resource control:

- **Content Validation**: Pre-compilation validation with configurable limits
- **Package Blacklist**: Blocks dangerous packages (shellesc, minted, pythontex)
- **Resource Limits**: Memory, CPU time, output size, and timeout controls
- **Workspace Isolation**: Each compilation runs in an isolated workspace
- **Retry Policies**: Automatic retry with exponential backoff for transient failures

### Tectonic Interface Support

- **V1 Interface**: Standard LaTeX compilation
- **V2 Interface**: Project-aware builds with `Tectonic.toml` support
- Auto-detection based on project structure

### Configuration Hierarchy

1. Environment variables (highest priority)
2. Config file (`~/.config/b8tex/config.toml`)
3. Default values (lowest priority)

Key environment variables:
- `B8TEX_NO_AUTO_DOWNLOAD`: Disable binary auto-download
- `B8TEX_TECTONIC_VERSION`: Specify Tectonic version
- `TECTONIC_PATH`: Custom binary path
- `B8TEX_CONFIG_PATH`: Override config file location
- `B8TEX_VALIDATION_MODE`: Set validation mode (strict/permissive/disabled)

## Code Quality Standards

### Type Hints (Enforced by mypy strict mode)
- All functions and methods must have full type hints
- Use modern Python 3.13+ type syntax (`|` for unions, built-in generics)
- Use `from __future__ import annotations` for forward references
- Include `py.typed` marker for PEP 561 compliance

### Docstrings (Google style)
```python
def compile_document(
    document: Document,
    options: BuildOptions | None = None,
    *,
    timeout: float | None = None,
) -> CompileResult:
    """Compile a LaTeX document.

    Args:
        document: Document to compile with entrypoint and resources
        options: Build options (uses defaults if None)
        timeout: Compilation timeout in seconds

    Returns:
        CompileResult with compilation status, artifacts, and diagnostics

    Raises:
        CompilationFailed: If compilation fails
        MissingBinaryError: If Tectonic binary not found
        TimeoutExpired: If compilation exceeds timeout
    """
```

### Import Organization (Enforced by ruff)
```python
from __future__ import annotations

# Standard library
import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

# Third-party
import platformdirs

# Local
from b8tex.core.binary import TectonicBinary
from b8tex.exceptions import TexError

# Type-checking only imports
if TYPE_CHECKING:
    from b8tex.core.document import Document
```

### Code Quality Principles
- **No hacks or workarounds** - Write clean, maintainable code
- **No TODOs in production code** - Implement fully or create an issue
- **Security-conscious** - Always validate inputs, handle errors, use timeouts
- **Performance-aware** - Use caching, avoid unnecessary work
- **No over-engineering** - Keep solutions simple and focused
- **Type-safe first** - Leverage type system to prevent bugs

### Test Requirements
- All new features must have tests
- Maintain 85%+ code coverage
- Test both success and failure cases
- Test edge cases and error conditions
- Use fixtures from `tests/conftest.py`
- Async tests use `pytest-asyncio`

## Development Workflow

### Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature`
2. Add tests first (TDD recommended)
3. Implement feature with full type hints
4. Add docstrings to public APIs
5. Run quality checks: `pytest && mypy src/b8tex && ruff check src tests`
6. Update `CHANGELOG.md` under "Unreleased"
7. Add example to `examples/` if user-facing feature
8. Update `README.md` if adding significant functionality

### Binary Management
- Tectonic binary is auto-downloaded on first use
- Discovery order: config file → `TECTONIC_PATH` → system PATH → cache
- Binary is cached in platform-specific directory (via `platformdirs`)
- Supports Linux, macOS, Windows (x86_64 and aarch64)

### Cache System
- Build cache uses fingerprinting (content + options + binary version)
- Cache stored in platform cache directory
- Automatic invalidation on changes
- Manual cleanup: `cache.cleanup(max_age_days=30)` or `b8tex clean-cache`

## Important File Locations

### Configuration
- Config file: `~/.config/b8tex/config.toml` (platform-specific via `platformdirs`)
- Cache directory: `~/.cache/b8tex/` (macOS: `~/Library/Caches/b8tex/`)

### Source Structure
```
src/b8tex/
├── __init__.py          # Public API exports
├── api.py              # TectonicCompiler class, high-level functions
├── cli.py              # CLI entry point (install-binary, config, clean-cache)
├── exceptions.py       # Exception hierarchy (TexError → specific errors)
└── core/               # Core functionality modules
    ├── binary.py       # Binary discovery and management
    ├── cache.py        # Build caching system
    ├── config.py       # Configuration loading
    ├── diagnostics.py  # Log parsing and error extraction
    ├── document.py     # Document and Resource models
    ├── options.py      # Build options and enums
    ├── project.py      # Multi-target project support
    ├── results.py      # Compilation result models
    ├── retry.py        # Retry policies
    ├── runner.py       # Process execution with limits
    ├── timeouts.py     # Timeout configuration
    ├── validation.py   # Content validation and security
    └── workspace.py    # Workspace management
```

### Test Structure
- 18 test modules in `tests/` (~5000 lines total)
- Shared fixtures in `tests/conftest.py`
- Coverage reports in `htmlcov/index.html` after running `pytest --cov`

## Common Patterns & Examples

### Creating Documents
```python
# From string
doc = Document.from_string("main.tex", latex_content)

# From path
doc = Document.from_path(Path("document.tex"))

# With resources (auto-detects type from extension)
doc = Document(
    entrypoint=InMemorySource("main.tex", content),
    resources=[
        Resource(Path("mystyle.sty")),      # Auto-detected as style
        Resource(Path("image.png")),         # Auto-detected as image
        Resource(Path("refs.bib")),          # Auto-detected as bibliography
    ]
)
```

### Build Options
```python
from b8tex import BuildOptions, OutputFormat

options = BuildOptions(
    outfmt=OutputFormat.PDF,
    reruns=2,
    print_log=False,
    keep_logs=True,
    only_cached=False,  # Set True for offline/fast builds
)
```

### Error Handling
```python
from b8tex import compile_document
from b8tex.exceptions import CompilationFailed, TimeoutExpired

try:
    result = compile_document(doc, timeout=60.0)
    if not result.success:
        print(f"Compilation failed with {len(result.errors)} errors")
        for error in result.errors:
            print(f"  {error}")
except CompilationFailed as e:
    print(f"Compilation failed: {e}")
    print(f"Log tail: {e.log_tail}")
except TimeoutExpired as e:
    print(f"Compilation timed out after {e.timeout}s")
```

### Caching
```python
from b8tex import TectonicCompiler, BuildCache

# Caching enabled by default
compiler = TectonicCompiler(use_cache=True)

# Explicit cache management
cache = BuildCache()
compiler = TectonicCompiler(cache=cache)

# Cache stats and cleanup
stats = cache.stats()
print(f"Cache entries: {stats['total_entries']}")
cache.cleanup(max_age_days=30)  # Remove old entries
cache.clear()  # Clear all entries
```

## Testing Notes

### Running Specific Tests
```bash
# All tests
uv run pytest

# Specific module
uv run pytest tests/test_api.py

# Specific test function
uv run pytest tests/test_api.py::test_compile_success

# Pattern matching
uv run pytest -k "test_compile"

# With verbose output
uv run pytest -v

# Async tests
uv run pytest tests/test_runner_async.py -v
```

### Debugging Tests
```python
# Enable verbose output in tests
options = BuildOptions(print_log=True, keep_logs=True)
result = compiler.compile_document(doc, options)

# Check log files
if result.log_path:
    print(result.log_path.read_text())
```

## Troubleshooting

### Common Issues

**Binary not found**: Set `B8TEX_NO_AUTO_DOWNLOAD=0` to enable auto-download, or install manually with `b8tex install-binary`.

**Type errors**: Ensure all functions have type hints and run `mypy src/b8tex` to verify.

**Import errors**: Check that imports are organized correctly (stdlib → third-party → local).

**Test failures**: Run with verbose output (`pytest -v`) and check test logs. Ensure Tectonic binary is available.

**Cache issues**: Clear cache with `b8tex clean-cache` or programmatically with `cache.clear()`.

## Additional Resources

- Examples: See `examples/` directory for 7 progressive examples
- Documentation: `README.md` for user guide, `CONTRIBUTING.md` for contributor guide
- Issue tracking: GitHub Issues at https://github.com/samehkamaleldin/pytex/issues
