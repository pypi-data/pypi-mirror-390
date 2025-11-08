"""Tests for Document and related classes."""

from pathlib import Path

from b8tex.core.document import Document, InMemorySource, Resource


def test_in_memory_source():
    """Test InMemorySource creation."""
    source = InMemorySource(
        filename="test.tex",
        content=r"\documentclass{article}",
    )

    assert source.filename == "test.tex"
    assert source.content == r"\documentclass{article}"
    assert source.encoding == "utf-8"


def test_resource_auto_detection():
    """Test automatic resource kind detection."""
    # Test .sty file
    sty_resource = Resource(InMemorySource("style.sty", ""))
    assert sty_resource.kind == "sty"

    # Test .bib file
    bib_resource = Resource(Path("refs.bib"))
    assert bib_resource.kind == "bib"

    # Test image
    img_resource = Resource(Path("figure.png"))
    assert img_resource.kind == "image"


def test_document_from_string():
    """Test creating Document from string."""
    content = r"\documentclass{article}\begin{document}Hello\end{document}"
    doc = Document.from_string(content, name="test")

    assert doc.name == "test"
    assert isinstance(doc.entrypoint, InMemorySource)
    assert doc.entrypoint.content == content


def test_document_from_path(temp_tex_file: Path):
    """Test creating Document from path."""
    doc = Document.from_path(temp_tex_file)

    assert doc.name == "test"
    assert doc.entrypoint == temp_tex_file
