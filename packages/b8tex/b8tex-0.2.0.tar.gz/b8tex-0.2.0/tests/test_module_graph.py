"""Tests for ModuleGraph and LogParser."""

from pathlib import Path

from b8tex.core.diagnostics import LogParser, ModuleGraph, ModuleNode


def test_module_node_creation():
    """Test ModuleNode creation."""
    node = ModuleNode(
        path="/path/to/file.tex",
        mtime=1234567.0,
        size=1024,
        content_hash="abc123",
    )

    assert node.path == "/path/to/file.tex"
    assert node.mtime == 1234567.0
    assert node.size == 1024
    assert node.content_hash == "abc123"


def test_module_graph_init():
    """Test ModuleGraph initialization."""
    graph = ModuleGraph()

    assert graph.nodes == {}
    assert graph.edges == []


def test_module_graph_add_node():
    """Test adding nodes to the graph."""
    graph = ModuleGraph()

    # Add a node manually
    graph.add_node("file1.tex", mtime=100.0, size=200)

    # Path is normalized, so check with resolved path
    normalized_path = str(Path("file1.tex").resolve())
    assert normalized_path in graph.nodes
    assert graph.nodes[normalized_path].mtime == 100.0
    assert graph.nodes[normalized_path].size == 200


def test_module_graph_add_node_with_real_file(tmp_path: Path):
    """Test adding a node from a real file."""
    # Create a temp file
    test_file = tmp_path / "test.tex"
    test_file.write_text("test content")

    graph = ModuleGraph()
    graph.add_node(test_file)

    # Path should be normalized (absolute)
    assert str(test_file.resolve()) in graph.nodes
    node = graph.nodes[str(test_file.resolve())]
    assert node.mtime > 0
    assert node.size > 0


def test_module_graph_record_include():
    """Test recording include relationships."""
    graph = ModuleGraph()

    graph.record_include("main.tex", "style.sty")
    graph.record_include("main.tex", "chapter1.tex")

    assert len(graph.edges) == 2
    assert ("main.tex", "style.sty") in graph.edges or (
        str(Path("main.tex").resolve()),
        str(Path("style.sty").resolve()),
    ) in graph.edges


def test_module_graph_roots():
    """Test finding root nodes."""
    graph = ModuleGraph()

    graph.record_include("main.tex", "style.sty")
    graph.record_include("main.tex", "chapter1.tex")
    graph.record_include("chapter1.tex", "section1.tex")

    roots = graph.roots()

    # main.tex should be the only root (no parents)
    assert len(roots) == 1


def test_module_graph_transitive_dependencies():
    """Test computing transitive dependencies."""
    graph = ModuleGraph()

    # Create a chain: main -> ch1 -> sec1
    graph.record_include("main.tex", "ch1.tex")
    graph.record_include("ch1.tex", "sec1.tex")

    # Get all dependencies of main
    main_path = str(Path("main.tex").resolve())
    deps = graph.transitive_of(main_path)

    # Should include both ch1 and sec1
    assert len(deps) == 2


def test_module_graph_fingerprint():
    """Test fingerprint generation."""
    graph1 = ModuleGraph()
    graph1.record_include("main.tex", "style.sty")

    graph2 = ModuleGraph()
    graph2.record_include("main.tex", "style.sty")

    # Same graph should have same fingerprint
    fp1 = graph1.fingerprint()
    fp2 = graph2.fingerprint()

    assert fp1 == fp2
    assert len(fp1) == 64  # SHA256 hex digest


def test_module_graph_fingerprint_changes_with_content():
    """Test that fingerprint changes when content changes."""
    graph1 = ModuleGraph()
    graph1.add_node("file.tex", mtime=100.0, size=200)

    graph2 = ModuleGraph()
    graph2.add_node("file.tex", mtime=200.0, size=200)  # Different mtime

    assert graph1.fingerprint() != graph2.fingerprint()


def test_module_graph_to_dict():
    """Test converting graph to dictionary."""
    graph = ModuleGraph()
    graph.record_include("main.tex", "ch1.tex")
    graph.record_include("main.tex", "ch2.tex")

    result = graph.to_dict()

    # Should have main.tex with two children
    assert len(result) >= 1


def test_log_parser_init():
    """Test LogParser initialization."""
    parser = LogParser()

    assert parser.messages == []
    assert isinstance(parser.module_graph, ModuleGraph)


def test_log_parser_parse_error():
    """Test parsing LaTeX errors."""
    parser = LogParser()

    line = "! Undefined control sequence."
    msg = parser.parse_line(line)

    assert msg is not None
    assert msg.severity == "error"
    assert "Undefined control sequence" in msg.text


def test_log_parser_parse_warning():
    """Test parsing LaTeX warnings."""
    parser = LogParser()

    line = "LaTeX Font Warning: Font shape warning here"
    msg = parser.parse_line(line)

    assert msg is not None
    assert msg.severity == "warning"
    assert "Font shape warning here" in msg.text


def test_log_parser_extract_includes():
    """Test extracting included files."""
    parser = LogParser()

    # Simulate LaTeX log with file includes
    parser.parse_line("(./main.tex")
    parser.parse_line("(./style.sty)")

    # Should have recorded includes in module graph
    assert len(parser.module_graph.nodes) > 0


def test_log_parser_build_module_graph():
    """Test building module graph from logs."""
    parser = LogParser()

    # Simulate some log lines
    parser.parse_line("(./main.tex")
    parser.parse_line("(./style.sty)")

    graph = parser.build_module_graph()

    assert isinstance(graph, ModuleGraph)
    assert len(graph.nodes) > 0


def test_log_parser_get_errors():
    """Test getting error messages."""
    parser = LogParser()

    parser.parse_line("! Error 1")
    parser.parse_line("LaTeX Font Warning: Warning 1")
    parser.parse_line("! Error 2")

    errors = parser.get_errors()
    assert len(errors) == 2


def test_log_parser_get_warnings():
    """Test getting warning messages."""
    parser = LogParser()

    parser.parse_line("! Error 1")
    parser.parse_line("LaTeX Font Warning: Warning 1")
    parser.parse_line("Package hyperref Warning: Warning 2")

    warnings = parser.get_warnings()
    assert len(warnings) == 2


def test_log_parser_parse_output():
    """Test parsing complete output."""
    parser = LogParser()

    output = """(./main.tex
LaTeX Font Warning: Font shape warning
! Undefined control sequence
(./style.sty)
)"""

    messages = parser.parse_output(output)

    # Should have found both warning and error
    assert len(messages) >= 2
    assert any(msg.severity == "error" for msg in messages)
    assert any(msg.severity == "warning" for msg in messages)
