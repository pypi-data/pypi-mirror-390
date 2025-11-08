"""Document and resource classes for LaTeX compilation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from b8tex.core.project import InputPath

ResourceKind = Literal["tex", "sty", "cls", "bib", "cfg", "image", "other"]


@dataclass
class InMemorySource:
    """An in-memory LaTeX source file.

    Attributes:
        filename: Name of the file (e.g., 'main.tex', 'mystyle.sty')
        content: File content as string
        encoding: Character encoding (default: utf-8)
    """

    filename: str
    content: str
    encoding: str = "utf-8"


@dataclass
class Resource:
    """A resource file needed for compilation (style file, image, bibliography, etc.).

    Attributes:
        path_or_mem: Either a Path to a file on disk or an InMemorySource
        kind: Type of resource
    """

    path_or_mem: Path | InMemorySource
    kind: ResourceKind = "other"

    def __post_init__(self) -> None:
        """Auto-detect resource kind if not specified."""
        if self.kind == "other":
            if isinstance(self.path_or_mem, InMemorySource):
                filename = self.path_or_mem.filename
            else:
                filename = self.path_or_mem.name

            suffix = Path(filename).suffix.lower()
            kind_map = {
                ".tex": "tex",
                ".sty": "sty",
                ".cls": "cls",
                ".bib": "bib",
                ".cfg": "cfg",
                ".png": "image",
                ".jpg": "image",
                ".jpeg": "image",
                ".pdf": "image",
                ".svg": "image",
                ".eps": "image",
            }
            detected = kind_map.get(suffix, "other")
            # Set kind directly - dataclass allows this in __post_init__
            self.kind = cast(ResourceKind, detected)


@dataclass
class Document:
    """A LaTeX document to be compiled.

    Attributes:
        name: Document name (used for output file naming)
        entrypoint: Main .tex file (Path or in-memory source)
        resources: Additional files needed (style files, images, etc.)
        search_paths: Additional directories to search for included files
    """

    name: str
    entrypoint: Path | InMemorySource
    resources: list[Resource] = field(default_factory=list)
    search_paths: list[InputPath] = field(default_factory=list)

    @classmethod
    def from_path(cls, path: Path, name: str | None = None) -> Document:
        """Create a Document from a .tex file path.

        Args:
            path: Path to the .tex file
            name: Document name (defaults to file stem)

        Returns:
            Document instance
        """
        return cls(
            name=name or path.stem,
            entrypoint=path,
        )

    @classmethod
    def from_string(
        cls,
        content: str,
        name: str = "document",
        filename: str = "main.tex",
    ) -> Document:
        """Create a Document from a LaTeX string.

        Args:
            content: LaTeX source code
            name: Document name
            filename: Filename for the in-memory source

        Returns:
            Document instance
        """
        return cls(
            name=name,
            entrypoint=InMemorySource(filename=filename, content=content),
        )
