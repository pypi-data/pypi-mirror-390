"""Project-level compilation support."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from b8tex.core.document import Document
from b8tex.core.options import BuildOptions

if TYPE_CHECKING:
    from b8tex.core.diagnostics import ModuleGraph


@dataclass
class InputPath:
    """A search path for LaTeX input files.

    Attributes:
        path: Directory to add to search path
        order: Search order (lower = searched earlier)
    """

    path: Path
    order: int = 100


@dataclass
class Target:
    """A build target within a project.

    Attributes:
        name: Target name (e.g., 'pdf', 'html')
        document: Document to compile
        options: Build options for this target
    """

    name: str
    document: Document
    options: BuildOptions = field(default_factory=BuildOptions)


@dataclass
class Project:
    """A multi-target LaTeX project.

    Attributes:
        root: Project root directory
        targets: Build targets by name
        tectonic_toml_present: Whether Tectonic.toml exists in root
        search_paths: Global search paths for the project
        module_graph: Dependency graph (populated after builds)
    """

    root: Path
    targets: dict[str, Target] = field(default_factory=dict)
    tectonic_toml_present: bool = False
    search_paths: list[InputPath] = field(default_factory=list)
    module_graph: ModuleGraph | None = None

    def __post_init__(self) -> None:
        """Check for Tectonic.toml presence."""
        toml_path = self.root / "Tectonic.toml"
        # Set directly - dataclass allows this in __post_init__
        self.tectonic_toml_present = toml_path.exists()

    def add_target(self, target: Target) -> None:
        """Add a build target to the project.

        Args:
            target: Target to add
        """
        self.targets[target.name] = target

    def detect_v2(self) -> bool:
        """Check if this project should use Tectonic V2 interface.

        Returns:
            True if Tectonic.toml exists
        """
        return self.tectonic_toml_present

    @classmethod
    def from_directory(cls, root: Path) -> Project:
        """Create a Project from a directory.

        Args:
            root: Project root directory

        Returns:
            Project instance
        """
        return cls(root=root)
