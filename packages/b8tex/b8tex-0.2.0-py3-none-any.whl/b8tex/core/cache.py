"""Build cache for B8TeX compilation."""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import types
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from b8tex.core.diagnostics import ModuleGraph
    from b8tex.core.document import Document
    from b8tex.core.options import BuildOptions
    from b8tex.core.results import CompileResult, OutputArtifact

CacheStrategy = Literal["mtime", "content"]

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """An entry in the build cache.

    Attributes:
        fingerprint: Unique hash identifying this build
        result_data: Serialized CompileResult
        timestamp: When this entry was created
        tectonic_version: Version of Tectonic used
    """

    fingerprint: str
    result_data: dict[str, object]
    timestamp: datetime
    tectonic_version: str


class BuildCache:
    """Manages caching of compilation results.

    The cache uses a SQLite database to store compilation results indexed by
    a fingerprint that includes:
    - All source file contents/mtimes
    - Build options
    - Tectonic version
    - Module dependency graph

    This allows skipping re-compilation when nothing has changed.

    Attributes:
        db_path: Path to the SQLite database
    """

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize the build cache.

        Args:
            db_path: Path to cache database (auto-detected if None)
        """
        self.db_path = db_path or self._get_default_cache_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create artifacts storage directory
        self.artifacts_dir = self.db_path.parent / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def __enter__(self) -> BuildCache:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit context manager and close connections."""
        self.close()

    def close(self) -> None:
        """Close any open database connections.

        This method is a no-op since BuildCache doesn't maintain persistent connections.
        All database operations use context managers that automatically close connections.
        This method exists for API consistency and future-proofing.
        """
        # All database operations use 'with sqlite3.connect()' which automatically
        # closes connections. This method exists for explicit cleanup semantics
        # and to support context manager protocol.
        pass

    def _get_default_cache_path(self) -> Path:
        """Get the default cache directory for the current platform.

        Returns:
            Path to cache directory
        """
        import os
        import platform

        system = platform.system()

        if system == "Darwin":  # macOS
            cache_dir = Path.home() / "Library" / "Caches" / "b8tex"
        elif system == "Windows":
            cache_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "b8tex" / "cache"
        else:  # Linux and others
            cache_dir = Path.home() / ".cache" / "b8tex"

        return cache_dir / "build_cache.db"

    def _init_db(self) -> None:
        """Initialize the cache database schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    fingerprint TEXT PRIMARY KEY,
                    result_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tectonic_version TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON cache(timestamp)
            """)
            conn.commit()
        finally:
            conn.close()

    def get_fingerprint(
        self,
        document: Document,
        options: BuildOptions,
        module_graph: ModuleGraph | None = None,
        tectonic_version: str = "unknown",
    ) -> str:
        """Generate a fingerprint for cache lookup.

        The fingerprint is a hash of:
        - Document entrypoint content/digest
        - All resource contents/digests
        - Module graph fingerprint
        - Build options (serialized)
        - Tectonic version

        Args:
            document: Document being compiled
            options: Build options
            module_graph: Dependency graph (if available)
            tectonic_version: Version of Tectonic

        Returns:
            Hexadecimal fingerprint string
        """
        hasher = hashlib.sha256()

        # Hash document entrypoint
        from b8tex.core.document import InMemorySource

        if isinstance(document.entrypoint, InMemorySource):
            hasher.update(document.entrypoint.content.encode())
        else:
            # File-based entrypoint
            if document.entrypoint.exists():
                hasher.update(document.entrypoint.read_bytes())
                stat = document.entrypoint.stat()
                hasher.update(str(stat.st_mtime).encode())
                hasher.update(str(stat.st_size).encode())

        # Hash all resources
        for resource in document.resources:
            if isinstance(resource.path_or_mem, InMemorySource):
                hasher.update(resource.path_or_mem.filename.encode())
                hasher.update(resource.path_or_mem.content.encode())
            else:
                # File-based resource
                if resource.path_or_mem.exists():
                    hasher.update(str(resource.path_or_mem).encode())
                    stat = resource.path_or_mem.stat()
                    hasher.update(str(stat.st_mtime).encode())
                    hasher.update(str(stat.st_size).encode())

        # Hash module graph if available
        if module_graph:
            hasher.update(module_graph.fingerprint().encode())

        # Hash build options (exclude mutable fields like outdir)
        options_dict = {
            "outfmt": options.outfmt.value,
            "reruns": options.reruns,
            "synctex": options.synctex,
            "keep_logs": options.keep_logs,
            "keep_intermediates": options.keep_intermediates,
            "only_cached": options.only_cached,
            "extra_args": tuple(options.extra_args),  # Make hashable
            "security_untrusted": options.security.untrusted,
            "security_shell_escape": options.security.allow_shell_escape,
        }
        hasher.update(json.dumps(options_dict, sort_keys=True).encode())

        # Hash Tectonic version
        hasher.update(tectonic_version.encode())

        return hasher.hexdigest()

    def read(self, fingerprint: str) -> CacheEntry | None:
        """Read a cache entry.

        Args:
            fingerprint: Cache key

        Returns:
            CacheEntry if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT result_data, timestamp, tectonic_version FROM cache WHERE fingerprint = ?",
                (fingerprint,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            result_data_json, timestamp_str, tectonic_version = row

            return CacheEntry(
                fingerprint=fingerprint,
                result_data=json.loads(result_data_json),
                timestamp=datetime.fromisoformat(timestamp_str),
                tectonic_version=tectonic_version,
            )
        finally:
            conn.close()

    def restore_artifacts(self, cache_entry: CacheEntry, target_dir: Path) -> list[OutputArtifact]:
        """Restore cached artifacts to a target directory.

        Args:
            cache_entry: Cache entry containing artifact metadata
            target_dir: Directory where artifacts should be restored

        Returns:
            List of OutputArtifact objects pointing to restored files
        """
        from b8tex.core.results import OutputArtifact

        target_dir.mkdir(parents=True, exist_ok=True)
        restored_artifacts: list[OutputArtifact] = []

        artifacts_list = cache_entry.result_data.get("artifacts", [])
        if not isinstance(artifacts_list, list):
            return restored_artifacts

        for artifact_data in artifacts_list:
            cached_filename = artifact_data.get("cached_filename")
            if not cached_filename:
                # Old cache format without cached artifacts
                continue

            cached_path = self.artifacts_dir / cached_filename

            if not cached_path.exists():
                # Artifact was deleted or cache is corrupted
                logger.warning(f"Cached artifact {cached_filename} not found")
                continue

            # Restore with original name
            original_name = artifact_data.get("original_name", cached_path.name)
            target_path = target_dir / original_name

            try:
                # Copy cached artifact to target location
                import shutil
                shutil.copy2(cached_path, target_path)

                # Create OutputArtifact
                from b8tex.core.options import OutputFormat
                restored_artifacts.append(
                    OutputArtifact(
                        kind=OutputFormat(artifact_data["kind"]),
                        path=target_path,
                        size=artifact_data["size"],
                    )
                )
            except OSError as e:
                logger.warning(f"Failed to restore artifact {cached_filename}: {e}")
                continue

        return restored_artifacts

    def _store_artifact(self, artifact_path: Path) -> str:
        """Store an artifact file in cache storage.

        Uses content-addressed storage: hash the file content and store it
        with the hash as filename for deduplication.

        Args:
            artifact_path: Path to artifact file to store

        Returns:
            Hash-based filename where artifact is stored
        """
        # Read and hash the file content
        content = artifact_path.read_bytes()
        content_hash = hashlib.sha256(content).hexdigest()

        # Determine file extension
        extension = artifact_path.suffix

        # Create cached filename
        cached_filename = f"{content_hash}{extension}"
        cached_path = self.artifacts_dir / cached_filename

        # Only write if not already cached (content-addressed = deduplication)
        if not cached_path.exists():
            cached_path.write_bytes(content)

        return cached_filename

    def write(
        self,
        fingerprint: str,
        result: CompileResult,
        tectonic_version: str = "unknown",
    ) -> None:
        """Write a compilation result to the cache.

        Stores both metadata in SQLite and artifact files in cache storage.

        Args:
            fingerprint: Cache key
            result: Compilation result to cache
            tectonic_version: Version of Tectonic used
        """
        # Store artifacts in cache storage and build serialized metadata
        cached_artifacts = []
        for artifact in result.artifacts:
            try:
                cached_filename = self._store_artifact(artifact.path)
                cached_artifacts.append({
                    "kind": artifact.kind.value,
                    "cached_filename": cached_filename,
                    "size": artifact.size,
                    "original_name": artifact.path.name,
                })
            except OSError as e:
                # If we can't cache an artifact, log but don't fail the entire cache write
                logger.warning(f"Failed to cache artifact {artifact.path}: {e}")
                continue

        # Serialize result
        result_data = {
            "success": result.success,
            "artifacts": cached_artifacts,
            "warnings": result.warnings,
            "errors": result.errors,
            "returncode": result.returncode,
            "elapsed": result.elapsed,
        }

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (fingerprint, result_data, timestamp, tectonic_version)
                VALUES (?, ?, ?, ?)
                """,
                (
                    fingerprint,
                    json.dumps(result_data),
                    datetime.now().isoformat(),
                    tectonic_version,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def is_fresh(
        self,
        fingerprint: str,
        max_age_seconds: float | None = None,
    ) -> bool:
        """Check if a cache entry is still fresh.

        Args:
            fingerprint: Cache key
            max_age_seconds: Maximum age in seconds (None = no age limit)

        Returns:
            True if entry exists and is fresh
        """
        entry = self.read(fingerprint)

        if entry is None:
            return False

        if max_age_seconds is not None:
            age = (datetime.now() - entry.timestamp).total_seconds()
            return age <= max_age_seconds

        return True

    def invalidate(self, fingerprint: str) -> None:
        """Invalidate (delete) a cache entry.

        Args:
            fingerprint: Cache key to invalidate
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM cache WHERE fingerprint = ?", (fingerprint,))
            conn.commit()
        finally:
            conn.close()

    def clear(self) -> None:
        """Clear all cache entries and artifacts."""
        import shutil

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM cache")
            conn.commit()
        finally:
            conn.close()

        # Also clear artifact storage
        if self.artifacts_dir.exists():
            shutil.rmtree(self.artifacts_dir)
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def cleanup(self, max_age_days: int = 30) -> int:
        """Remove old cache entries.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of entries removed
        """
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        cutoff_dt = datetime.fromtimestamp(cutoff)

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "DELETE FROM cache WHERE timestamp < ?",
                (cutoff_dt.isoformat(),),
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            total_entries = cursor.fetchone()[0]

            cursor = conn.execute("SELECT SUM(LENGTH(result_data)) FROM cache")
            total_size = cursor.fetchone()[0] or 0

            return {
                "total_entries": total_entries,
                "total_size_bytes": total_size,
                "db_size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
            }
        finally:
            conn.close()
