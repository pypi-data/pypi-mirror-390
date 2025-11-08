"""Tests for Workspace."""

import platform
from pathlib import Path

import pytest

from b8tex.core.document import Document, InMemorySource, Resource
from b8tex.core.options import BuildOptions
from b8tex.core.project import InputPath
from b8tex.core.workspace import LayoutStrategy, Workspace


@pytest.fixture
def temp_workdir(tmp_path: Path) -> Path:
    """Create a temporary workspace directory."""
    return tmp_path / "workspace"


@pytest.fixture
def workspace(temp_workdir: Path) -> Workspace:
    """Create a Workspace instance."""
    return Workspace.create_persistent(temp_workdir)


def test_workspace_create_temp():
    """Test creating a temporary workspace."""
    ws = Workspace.create_temp()

    assert ws.workdir.exists()
    assert ws.cleanup_on_exit is True
    assert ws.layout == LayoutStrategy.MIRROR

    # Cleanup
    ws.cleanup()
    assert not ws.workdir.exists()


def test_workspace_create_persistent(temp_workdir: Path):
    """Test creating a persistent workspace."""
    ws = Workspace.create_persistent(temp_workdir)

    assert ws.workdir == temp_workdir
    assert ws.workdir.exists()
    assert ws.cleanup_on_exit is False


def test_stage_in_memory_source(workspace: Workspace):
    """Test staging an in-memory source."""
    source = InMemorySource("test.tex", "content")
    path = workspace._materialize_in_memory(source)

    assert path.exists()
    assert path.name == "test.tex"
    assert path.read_text() == "content"


def test_stage_document_in_memory(workspace: Workspace):
    """Test staging a document with in-memory entrypoint."""
    doc = Document.from_string("content", name="test")
    path = workspace.stage_document(doc)

    assert path.exists()
    assert path.read_text() == "content"


def test_stage_document_from_file(workspace: Workspace, tmp_path: Path):
    """Test staging a document from a file."""
    # Create a source file
    source_file = tmp_path / "source.tex"
    source_file.write_text("test content")

    doc = Document.from_path(source_file)
    path = workspace.stage_document(doc)

    assert path.exists()
    assert path.read_text() == "test content"


def test_stage_resources(workspace: Workspace, tmp_path: Path):
    """Test staging resource files."""
    # Create source files
    style_file = tmp_path / "style.sty"
    style_file.write_text("style content")

    image_file = tmp_path / "image.png"
    image_file.write_bytes(b"fake image")

    # Create in-memory resource
    in_mem = InMemorySource("custom.cls", "class content")

    resources = [
        Resource(style_file),
        Resource(image_file),
        Resource(in_mem),
    ]

    staged = workspace.stage_resources(resources)

    assert len(staged) == 3
    assert all(p.exists() for p in staged)


def test_layout_flat(tmp_path: Path):
    """Test FLAT layout strategy."""
    ws = Workspace.create_persistent(tmp_path / "flat", layout=LayoutStrategy.FLAT)

    # Create nested source file
    source_dir = tmp_path / "source" / "subdir"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "file.tex"
    source_file.write_text("content")

    staged = ws._stage_file(source_file)

    # Should be flattened to workspace root
    assert staged.parent == ws.workdir
    assert staged.name == "file.tex"


def test_layout_mirror(tmp_path: Path):
    """Test MIRROR layout strategy."""
    ws = Workspace.create_persistent(tmp_path / "mirror", layout=LayoutStrategy.MIRROR)

    # Create source file relative to cwd
    source_file = Path("test.tex")
    source_file.write_text("content")

    try:
        staged = ws._stage_file(source_file)

        # Should preserve relative structure
        assert staged.exists()
        assert staged.read_text() == "content"
    finally:
        # Cleanup
        if source_file.exists():
            source_file.unlink()


def test_layout_tmp_only(tmp_path: Path):
    """Test TMP_ONLY layout strategy."""
    ws = Workspace.create_persistent(tmp_path / "tmponly", layout=LayoutStrategy.TMP_ONLY)

    # Create source file
    source_file = tmp_path / "source.tex"
    source_file.write_text("content")

    staged = ws._stage_file(source_file)

    # Should return original path, not copy
    assert staged == source_file
    assert not (ws.workdir / "source.tex").exists()


def test_resolve_outdir_default(workspace: Workspace):
    """Test default output directory resolution."""
    options = BuildOptions()
    outdir = workspace.resolve_outdir(options)

    assert outdir == workspace.workdir / "output"
    assert outdir.exists()


def test_resolve_outdir_custom(workspace: Workspace, tmp_path: Path):
    """Test custom output directory."""
    custom_dir = tmp_path / "custom_output"
    options = BuildOptions(outdir=custom_dir)

    outdir = workspace.resolve_outdir(options)

    assert outdir == custom_dir


def test_setup_search_paths_basic(workspace: Workspace, tmp_path: Path):
    """Test basic search path setup."""
    path1 = tmp_path / "path1"
    path2 = tmp_path / "path2"
    path1.mkdir()
    path2.mkdir()

    doc_paths = [InputPath(path1, order=10)]
    proj_paths = [InputPath(path2, order=20)]

    env = workspace.setup_search_paths(doc_paths, proj_paths)

    assert "TEXINPUTS" in env
    texinputs = env["TEXINPUTS"]

    # Should contain all paths
    assert str(workspace.workdir) in texinputs
    assert str(path1.resolve()) in texinputs
    assert str(path2.resolve()) in texinputs

    # Should have correct separator
    if platform.system() == "Windows":
        assert ";" in texinputs
    else:
        assert ":" in texinputs


def test_setup_search_paths_ordering(workspace: Workspace, tmp_path: Path):
    """Test search path ordering."""
    path1 = tmp_path / "path1"
    path2 = tmp_path / "path2"
    path3 = tmp_path / "path3"

    for p in [path1, path2, path3]:
        p.mkdir()

    doc_paths = [
        InputPath(path1, order=100),
        InputPath(path2, order=10),  # Should come first
    ]

    env = workspace.setup_search_paths(doc_paths)
    texinputs = env["TEXINPUTS"]

    # Extract paths
    separator = ";" if platform.system() == "Windows" else ":"
    paths = texinputs.split(separator)

    # Remove empty entries (trailing ::)
    paths = [p for p in paths if p]

    # Workspace should be first
    assert paths[0] == str(workspace.workdir.resolve())

    # path2 (order=10) should come before path1 (order=100)
    path1_idx = next(i for i, p in enumerate(paths) if str(path1.resolve()) in p)
    path2_idx = next(i for i, p in enumerate(paths) if str(path2.resolve()) in p)
    assert path2_idx < path1_idx


def test_isolate_environment(workspace: Workspace):
    """Test environment isolation."""
    # Create a test environment with LaTeX vars
    test_env = {
        "TEXINPUTS": "/some/path",
        "TEXMFHOME": "/home/texmf",
        "PATH": "/usr/bin",
        "HOME": "/home/user",
    }

    isolated = workspace.isolate_environment(test_env)

    # LaTeX vars should be removed
    assert "TEXINPUTS" not in isolated
    assert "TEXMFHOME" not in isolated

    # Other vars should remain
    assert isolated["PATH"] == "/usr/bin"
    assert isolated["HOME"] == "/home/user"


def test_staged_files_caching(workspace: Workspace, tmp_path: Path):
    """Test that files are only staged once."""
    source_file = tmp_path / "test.tex"
    source_file.write_text("content")

    # Stage twice
    path1 = workspace._stage_file(source_file)
    path2 = workspace._stage_file(source_file)

    # Should return the same path
    assert path1 == path2

    # Should be recorded in cache
    assert str(source_file.resolve()) in workspace._staged_files


def test_cleanup(temp_workdir: Path):
    """Test workspace cleanup."""
    ws = Workspace.create_persistent(temp_workdir)
    ws.cleanup_on_exit = True  # Set after creation

    # Create some files
    (ws.workdir / "test.txt").write_text("test")

    assert ws.workdir.exists()

    ws.cleanup()

    assert not ws.workdir.exists()


def test_no_cleanup_when_disabled(temp_workdir: Path):
    """Test that cleanup doesn't happen when disabled."""
    ws = Workspace.create_persistent(temp_workdir)
    ws.cleanup_on_exit = False  # Set after creation

    (ws.workdir / "test.txt").write_text("test")

    assert ws.workdir.exists()

    ws.cleanup()

    # Should still exist
    assert ws.workdir.exists()
