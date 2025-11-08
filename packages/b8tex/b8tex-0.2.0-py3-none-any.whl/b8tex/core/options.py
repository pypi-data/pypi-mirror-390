"""Build options and configuration classes."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class OutputFormat(Enum):
    """Supported output formats for Tectonic compilation."""

    PDF = "pdf"
    HTML = "html"
    XDV = "xdv"
    AUX = "aux"
    FMT = "fmt"


@dataclass(frozen=True)
class SecurityPolicy:
    """Security policy for LaTeX compilation.

    Attributes:
        untrusted: If True, compile in untrusted mode (disables dangerous features)
        allow_shell_escape: Allow shell-escape commands (requires untrusted=False)
        shell_escape_cwd: Working directory for shell-escape commands
    """

    untrusted: bool = False
    allow_shell_escape: bool = False
    shell_escape_cwd: Path | None = None

    def __post_init__(self) -> None:
        """Validate security policy invariants."""
        if self.untrusted and self.allow_shell_escape:
            from b8tex.exceptions import SecurityPolicyError

            raise SecurityPolicyError(
                "Cannot enable shell-escape in untrusted mode"
            )


@dataclass
class BundleConfig:
    """Configuration for Tectonic bundle (TeX package repository).

    Attributes:
        id_or_path: Bundle identifier, URL, or local path
        offline: If True, do not download packages (only use cached)
    """

    id_or_path: str | Path | None = None
    offline: bool = False


@dataclass
class BuildOptions:
    """Options for a Tectonic compilation run.

    Attributes:
        outdir: Output directory for artifacts (None = use workspace default)
        outfmt: Output format
        reruns: Number of compilation reruns (None = Tectonic default)
        synctex: Enable SyncTeX for PDF->source mapping
        print_log: Print compilation log to stderr
        keep_logs: Keep log files after compilation
        keep_intermediates: Keep intermediate files (.aux, .log, etc.)
        only_cached: Only use cached packages (fail if download needed)
        extra_args: Additional command-line arguments to pass to Tectonic
        bundle: Bundle configuration
        security: Security policy
        env: Additional environment variables for the compilation process
    """

    outdir: Path | None = None
    outfmt: OutputFormat = OutputFormat.PDF
    reruns: int | None = None
    synctex: bool = False
    print_log: bool = False
    keep_logs: bool = False
    keep_intermediates: bool = False
    only_cached: bool = False
    extra_args: list[str] = field(default_factory=list)
    bundle: BundleConfig | None = None
    security: SecurityPolicy = field(default_factory=SecurityPolicy)
    env: dict[str, str] = field(default_factory=dict)
