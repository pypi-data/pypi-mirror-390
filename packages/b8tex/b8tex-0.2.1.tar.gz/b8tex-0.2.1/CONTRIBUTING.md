# Contributing to B8TeX

Thank you for your interest in contributing to B8TeX! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.13 or later
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/samehkamaleldin/pytex.git
   cd b8tex
   ```

2. **Create a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   uv pip install -e ".[dev,watch]"
   ```

4. **Verify your setup**:
   ```bash
   pytest
   mypy src/b8tex
   ruff check src tests
   ```

## Development Workflow

### Branch Strategy

- `main` - Stable branch, reflects the latest release
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Workflow Steps

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our [code standards](#code-standards)

3. **Add tests** for new functionality

4. **Run the test suite**:
   ```bash
   pytest --cov=b8tex --cov-report=html
   ```

5. **Check code quality**:
   ```bash
   mypy src/b8tex
   ruff check src tests
   ruff format src tests
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

7. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Python Style

B8TeX follows modern Python best practices:

- **PEP 8** with modifications enforced by `ruff`
- **Type hints** on all functions and methods (checked with `mypy`)
- **Docstrings** on all public classes, methods, and functions (Google style)
- **Line length**: 100 characters (enforced by ruff)

### Type Hints

All code must have comprehensive type hints:

```python
def compile_document(
    document: Document,
    options: BuildOptions | None = None,
    *,
    timeout: float | None = None,
) -> CompileResult:
    """Compile a LaTeX document.

    Args:
        document: Document to compile
        options: Build options (uses defaults if None)
        timeout: Compilation timeout in seconds

    Returns:
        CompileResult with compilation results

    Raises:
        CompilationFailed: If compilation fails
    """
```

### Docstring Format

Use Google-style docstrings:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """Short description of function.

    Longer description if needed, explaining behavior,
    edge cases, or important details.

    Args:
        arg1: Description of first argument
        arg2: Description of second argument

    Returns:
        Description of return value

    Raises:
        ValueError: When and why this is raised

    Example:
        >>> my_function("test", 42)
        True
    """
```

### Import Organization

Organize imports in this order (enforced by ruff):

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs

from b8tex.core.binary import TectonicBinary
from b8tex.exceptions import TexError

if TYPE_CHECKING:
    from b8tex.core.document import Document
```

### Code Quality Principles

1. **No hacks or workarounds** - Write clean, maintainable code
2. **No TODOs in production code** - Implement features fully or create an issue
3. **Security-conscious** - Validate inputs, handle errors, use timeouts
4. **Performance-aware** - Cache when appropriate, avoid unnecessary work
5. **No over-engineering** - Keep solutions simple and focused

## Testing

### Test Requirements

- **All new features must have tests**
- **Maintain 85%+ code coverage**
- **Test both success and failure cases**
- **Test edge cases and error conditions**

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=b8tex --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run tests matching a pattern
pytest -k "test_compile"

# Run with verbose output
pytest -v

# Run async tests
pytest tests/test_runner_async.py -v
```

### Writing Tests

Use pytest with fixtures:

```python
import pytest
from pathlib import Path

from b8tex import Document, compile_document


@pytest.fixture
def sample_document(tmp_path: Path):
    """Create a sample LaTeX document for testing."""
    doc_file = tmp_path / "test.tex"
    doc_file.write_text(r"""
\documentclass{article}
\begin{document}
Test document
\end{document}
""")
    return Document.from_path(doc_file)


def test_compile_success(sample_document):
    """Test successful compilation."""
    result = compile_document(sample_document)

    assert result.success
    assert result.pdf_path is not None
    assert result.pdf_path.exists()
```

### Test Organization

- `tests/test_*.py` - Unit and integration tests
- `tests/conftest.py` - Shared fixtures
- One test file per module in `src/b8tex/`

## Documentation

### Code Documentation

- **All public APIs must be documented**
- **Include usage examples in docstrings**
- **Document all parameters and return values**
- **Explain non-obvious behavior**

### Documentation Files

When adding new features, update:

- `README.md` - If adding user-facing functionality
- `docs/api.md` - For new public APIs
- `examples/` - Add examples for significant features
- `CHANGELOG.md` - Note changes under "Unreleased"

### Example Files

Examples should:

- Be runnable as-is (with dependencies installed)
- Include clear comments explaining each step
- Demonstrate real-world usage
- Handle errors gracefully

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `pytest`
2. **Check type hints**: `mypy src/b8tex`
3. **Verify code style**: `ruff check src tests`
4. **Update documentation** if adding features
5. **Add entry to CHANGELOG.md** under "Unreleased"

### PR Guidelines

1. **Title**: Clear, concise description of changes
   - Good: "Add Jinja2 preprocessor support"
   - Bad: "Update code"

2. **Description**: Include:
   - What changes were made and why
   - How to test the changes
   - Any breaking changes
   - Related issues (if any)

3. **Keep PRs focused**: One feature/fix per PR

4. **Respond to review feedback** promptly

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Changes
- List of specific changes
- Breaking changes (if any)

## Testing
How to test these changes:
1. Step one
2. Step two

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] CHANGELOG.md updated
- [ ] All tests passing
- [ ] No mypy errors
- [ ] Ruff checks passing
```

## Development Tips

### Running Linters

```bash
# Check code style
ruff check src tests

# Auto-fix issues
ruff check --fix src tests

# Format code
ruff format src tests

# Type checking
mypy src/b8tex

# All checks at once
pytest && mypy src/b8tex && ruff check src tests
```

### Debugging

Enable verbose output:

```python
from b8tex import TectonicCompiler, BuildOptions

options = BuildOptions(print_log=True, keep_logs=True)
compiler = TectonicCompiler()

result = compiler.compile_document(document, options)

# Check logs
if result.log_path:
    print(result.log_path.read_text())
```

### Performance Profiling

```python
import time
from b8tex import compile_string

start = time.time()
result = compile_string(latex_content)
elapsed = time.time() - start

print(f"Compilation took {elapsed:.2f}s")
print(f"Result reported: {result.elapsed:.2f}s")
```

## Project Structure

```
b8tex/
├── src/b8tex/           # Main package
│   ├── __init__.py      # Public API exports
│   ├── api.py           # High-level compiler API
│   ├── cli.py           # Command-line interface
│   ├── exceptions.py    # Exception hierarchy
│   └── core/            # Core functionality
│       ├── binary.py    # Tectonic binary management
│       ├── cache.py     # Build caching
│       ├── config.py    # Configuration system
│       ├── diagnostics.py  # Log parsing
│       ├── document.py  # Document model
│       ├── options.py   # Build options
│       ├── project.py   # Project model
│       ├── results.py   # Compilation results
│       ├── runner.py    # Process execution
│       ├── watcher.py   # File watching
│       └── workspace.py # Workspace management
├── tests/               # Test suite
├── examples/            # Usage examples
├── docs/                # Documentation
└── .github/workflows/   # CI/CD configuration
```

## Getting Help

- **Documentation**: Check `README.md` and `docs/`
- **Examples**: See `examples/` directory
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions

## Release Process

(For maintainers)

1. Update version in `src/b8tex/__init__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with release date
3. Create git tag: `git tag -a v0.X.0 -m "Release v0.X.0"`
4. Push tag: `git push origin v0.X.0`
5. GitHub Actions will automatically publish to PyPI

## License

By contributing to B8TeX, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or discussion if you have any questions about contributing!

---

Thank you for contributing to B8TeX! 🎉
