"""Log parsing and diagnostics for Tectonic compilation."""

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Severity = Literal["info", "warning", "error"]

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class TectonicMessage:
    """A diagnostic message from Tectonic.

    Attributes:
        severity: Message severity level
        text: Message text
        code: Error/warning code (if identifiable)
        file: Source file (if identifiable)
        line: Line number (if identifiable)
    """

    severity: Severity
    text: str
    code: str | None = None
    file: str | None = None
    line: int | None = None


@dataclass
class ModuleNode:
    """A node in the module dependency graph.

    Attributes:
        path: Normalized path to the file
        mtime: Last modification time (for caching)
        size: File size in bytes
        content_hash: Hash of file content (for in-memory sources)
    """

    path: str
    mtime: float = 0.0
    size: int = 0
    content_hash: str | None = None


class ModuleGraph:
    """Tracks dependencies between LaTeX files.

    This class maintains a graph of included files to support:
    - Cache invalidation when dependencies change
    - Watch mode to monitor all relevant files
    - Dependency visualization

    Attributes:
        nodes: Dictionary mapping normalized paths to ModuleNode instances
        edges: List of (parent, child) tuples representing includes
    """

    def __init__(self) -> None:
        """Initialize an empty module graph."""
        self.nodes: dict[str, ModuleNode] = {}
        self.edges: list[tuple[str, str]] = []
        self._children_cache: dict[str, set[str]] = {}
        self._cache_valid = False

    def record_include(self, parent: str | Path, child: str | Path) -> None:
        """Record an include relationship between files.

        Args:
            parent: Path to the parent file (the one doing the including)
            child: Path to the included file
        """
        parent_path = self._normalize_path(parent)
        child_path = self._normalize_path(child)

        # Add nodes if they don't exist
        if parent_path not in self.nodes:
            self.add_node(parent_path)
        if child_path not in self.nodes:
            self.add_node(child_path)

        # Add edge if it doesn't exist
        edge = (parent_path, child_path)
        if edge not in self.edges:
            self.edges.append(edge)
            self._cache_valid = False

    def add_node(
        self,
        path: str | Path,
        mtime: float | None = None,
        size: int | None = None,
        content_hash: str | None = None,
    ) -> None:
        """Add or update a node in the graph.

        Args:
            path: Path to the file
            mtime: Last modification time (auto-detected if None)
            size: File size (auto-detected if None)
            content_hash: Content hash for in-memory sources
        """
        norm_path = self._normalize_path(path)

        # Auto-detect file metadata if not provided
        if mtime is None or size is None:
            file_path = Path(path)
            if file_path.exists():
                stat = file_path.stat()
                mtime = mtime or stat.st_mtime
                size = size or stat.st_size

        self.nodes[norm_path] = ModuleNode(
            path=norm_path,
            mtime=mtime or 0.0,
            size=size or 0,
            content_hash=content_hash,
        )
        self._cache_valid = False

    def roots(self) -> list[str]:
        """Find root nodes (nodes with no parents).

        Returns:
            List of paths to root nodes
        """
        all_nodes = set(self.nodes.keys())
        children = {child for _, child in self.edges}
        return sorted(all_nodes - children)

    def transitive_of(self, node: str | Path) -> set[str]:
        """Get all transitive dependencies of a node.

        Args:
            node: Path to the node

        Returns:
            Set of paths to all dependencies (direct and transitive)
        """
        norm_path = self._normalize_path(node)
        if norm_path not in self.nodes:
            return set()

        visited: set[str] = set()
        to_visit = [norm_path]

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue

            visited.add(current)

            # Add all children to visit list
            children = self._get_children(current)
            to_visit.extend(children)

        # Remove the node itself from the result
        visited.discard(norm_path)
        return visited

    def fingerprint(self) -> str:
        """Generate a stable hash of the entire graph for cache validation.

        The fingerprint includes:
        - All node paths, mtimes, sizes, and content hashes
        - Graph structure (edges)

        Returns:
            Hexadecimal fingerprint string
        """
        hasher = hashlib.sha256()

        # Hash nodes in sorted order for stability
        for path in sorted(self.nodes.keys()):
            node = self.nodes[path]
            hasher.update(node.path.encode())
            hasher.update(str(node.mtime).encode())
            hasher.update(str(node.size).encode())
            if node.content_hash:
                hasher.update(node.content_hash.encode())

        # Hash edges in sorted order
        for parent, child in sorted(self.edges):
            hasher.update(f"{parent}->{child}".encode())

        return hasher.hexdigest()

    def _normalize_path(self, path: str | Path) -> str:
        """Normalize a path for consistent comparison.

        Args:
            path: Path to normalize

        Returns:
            Normalized path string
        """
        # Convert to Path object and resolve to absolute path
        p = Path(path)
        try:
            # Try to resolve to absolute path
            resolved = p.resolve()
            return str(resolved)
        except (OSError, RuntimeError) as e:
            # If resolution fails (e.g., file doesn't exist), just normalize
            logger.debug(f"Failed to resolve path {path}: {e}")
            return str(p.as_posix())

    def _get_children(self, node: str) -> list[str]:
        """Get direct children of a node.

        Args:
            node: Normalized path to the node

        Returns:
            List of child paths
        """
        if not self._cache_valid:
            self._rebuild_children_cache()

        return list(self._children_cache.get(node, set()))

    def _rebuild_children_cache(self) -> None:
        """Rebuild the children cache from edges."""
        self._children_cache.clear()
        for parent, child in self.edges:
            if parent not in self._children_cache:
                self._children_cache[parent] = set()
            self._children_cache[parent].add(child)
        self._cache_valid = True

    def to_dict(self) -> dict[str, list[str]]:
        """Convert graph to a simple dictionary format.

        Returns:
            Dictionary mapping parent paths to lists of child paths
        """
        result: dict[str, list[str]] = {}
        for parent, child in self.edges:
            if parent not in result:
                result[parent] = []
            result[parent].append(child)

        # Include roots even if they have no children
        for root in self.roots():
            if root not in result:
                result[root] = []

        return result


class LogParser:
    """Parses Tectonic compilation logs into structured messages."""

    # Common LaTeX error/warning patterns
    ERROR_PATTERN = re.compile(r"^! (.+)$")
    WARNING_PATTERN = re.compile(r"^(LaTeX|Package) \w+ Warning: (.+)$")
    FILE_LINE_PATTERN = re.compile(r"l\.(\d+)\s")
    INCLUDE_PATTERN = re.compile(r"\(([^)]+\.(?:tex|sty|cls|bib))\)")

    # Additional patterns for better file/line extraction
    FILE_PATTERN = re.compile(r"\./([^\s]+\.(?:tex|sty|cls|bib))")
    TECTONIC_INPUT_PATTERN = re.compile(r"(?:input|openout|openin):\s*(.+\.(?:tex|sty|cls|bib))")
    LINE_NUMBER_PATTERN = re.compile(r"(?:line|l\.)\s*(\d+)")

    def __init__(self) -> None:
        """Initialize the log parser."""
        self.messages: list[TectonicMessage] = []
        self.module_graph = ModuleGraph()
        self._current_file: str | None = None
        self._file_stack: list[str] = []

    def parse_line(self, line: str) -> TectonicMessage | None:
        """Parse a single log line.

        Args:
            line: Log line to parse

        Returns:
            TectonicMessage if line contains a diagnostic, None otherwise
        """
        # Track file context (for error messages)
        self._update_file_context(line)

        # Extract line number from context
        line_num = None
        line_match = self.LINE_NUMBER_PATTERN.search(line)
        if line_match:
            line_num = int(line_match.group(1))

        # Check for errors
        error_match = self.ERROR_PATTERN.match(line)
        if error_match:
            msg = TectonicMessage(
                severity="error",
                text=error_match.group(1),
                file=self._current_file,
                line=line_num,
            )
            self.messages.append(msg)
            return msg

        # Check for warnings
        warning_match = self.WARNING_PATTERN.match(line)
        if warning_match:
            msg = TectonicMessage(
                severity="warning",
                text=warning_match.group(2),
                file=self._current_file,
                line=line_num,
            )
            self.messages.append(msg)
            return msg

        # Extract includes and build dependency graph
        self._extract_includes(line)

        return None

    def _update_file_context(self, line: str) -> None:
        """Update current file context from log line.

        Args:
            line: Log line to analyze
        """
        # Look for file references in parentheses (LaTeX convention)
        for match in self.INCLUDE_PATTERN.finditer(line):
            filepath = match.group(1)
            self._file_stack.append(filepath)
            self._current_file = filepath

        # Look for explicit file patterns
        file_match = self.FILE_PATTERN.search(line)
        if file_match:
            self._current_file = file_match.group(1)

        # Look for Tectonic-specific patterns
        tect_match = self.TECTONIC_INPUT_PATTERN.search(line)
        if tect_match:
            self._current_file = tect_match.group(1)

    def _extract_includes(self, line: str) -> None:
        """Extract include relationships from a log line.

        Args:
            line: Log line to analyze
        """
        # Extract includes from parentheses
        for match in self.INCLUDE_PATTERN.finditer(line):
            included_file = match.group(1)

            # Add to module graph
            if self._current_file and included_file != self._current_file:
                self.module_graph.record_include(self._current_file, included_file)
            else:
                # If no current file, this might be a root
                self.module_graph.add_node(included_file)

        # Extract from Tectonic-specific patterns
        tect_match = self.TECTONIC_INPUT_PATTERN.search(line)
        if tect_match:
            included_file = tect_match.group(1)
            if self._current_file and included_file != self._current_file:
                self.module_graph.record_include(self._current_file, included_file)
            else:
                self.module_graph.add_node(included_file)

    def parse_output(self, output: str) -> list[TectonicMessage]:
        """Parse complete compilation output.

        Args:
            output: Full compilation output

        Returns:
            List of diagnostic messages
        """
        self.messages.clear()
        self.module_graph = ModuleGraph()
        self._current_file = None
        self._file_stack.clear()

        for line in output.splitlines():
            self.parse_line(line)

        return self.messages

    def get_errors(self) -> list[TectonicMessage]:
        """Get all error messages.

        Returns:
            List of error messages
        """
        return [msg for msg in self.messages if msg.severity == "error"]

    def get_warnings(self) -> list[TectonicMessage]:
        """Get all warning messages.

        Returns:
            List of warning messages
        """
        return [msg for msg in self.messages if msg.severity == "warning"]

    def build_module_graph(self) -> ModuleGraph:
        """Build the module dependency graph.

        Returns:
            ModuleGraph instance populated during parsing
        """
        return self.module_graph
