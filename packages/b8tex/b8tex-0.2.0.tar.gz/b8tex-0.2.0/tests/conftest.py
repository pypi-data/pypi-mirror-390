"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_tex_content() -> str:
    """Sample LaTeX document content."""
    return r"""
\documentclass{article}
\usepackage[utf8]{inputenc}

\title{Test Document}
\author{B8TeX}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}

This is a test document for B8TeX.

\end{document}
"""


@pytest.fixture
def sample_style_content() -> str:
    """Sample LaTeX style file content."""
    return r"""
\ProvidesPackage{teststyle}

\newcommand{\testcmd}{This is a test command}
"""


@pytest.fixture
def temp_tex_file(tmp_path: Path, sample_tex_content: str) -> Path:
    """Create a temporary .tex file."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(sample_tex_content)
    return tex_file
