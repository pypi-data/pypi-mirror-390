"""High-level API for B8TeX."""

import logging
import time
from pathlib import Path

from b8tex.core.binary import TectonicBinary
from b8tex.core.cache import BuildCache
from b8tex.core.config import load_config
from b8tex.core.diagnostics import LogParser
from b8tex.core.document import Document, InMemorySource
from b8tex.core.options import BuildOptions, OutputFormat
from b8tex.core.project import Project
from b8tex.core.results import CompileResult, OutputArtifact
from b8tex.core.runner import ProcessRunner
from b8tex.core.validation import ContentValidator
from b8tex.core.workspace import Workspace
from b8tex.exceptions import CompilationFailed

# Set up logging
logger = logging.getLogger(__name__)


class TectonicCompiler:
    """Main compiler interface for Tectonic.

    This is the primary entrypoint for compiling LaTeX documents.

    Attributes:
        binary: Tectonic binary instance
        runner: Process runner for executing commands
    """

    def __init__(
        self,
        binary: TectonicBinary | None = None,
        cache: BuildCache | None = None,
        use_cache: bool = True,
        validator: ContentValidator | None = None,
    ) -> None:
        """Initialize the compiler.

        Args:
            binary: Tectonic binary (auto-discovered if None)
            cache: Build cache (creates default if None)
            use_cache: Whether to use caching
            validator: Content validator (creates from config if None)
        """
        self.binary = binary or TectonicBinary.discover()

        # Load config for resource limits and validation settings
        config = load_config()
        self.runner = ProcessRunner(limits=config.resource_limits)
        self.use_cache = use_cache
        self.cache = cache if use_cache else None

        # Create validator from config if not provided
        self.validator = validator or ContentValidator(
            limits=config.validation_limits,
            mode=config.validation_mode,
        )

        # Create default cache if needed
        if self.use_cache and self.cache is None:
            self.cache = BuildCache()

        # Probe binary capabilities
        if not self.binary.capabilities:
            self.binary.probe()

    def compile_document(
        self,
        document: Document,
        options: BuildOptions | None = None,
        *,
        workdir: Path | None = None,
        timeout: float | None = None,
    ) -> CompileResult:
        """Compile a LaTeX document.

        Args:
            document: Document to compile
            options: Build options (uses defaults if None)
            workdir: Custom workspace directory (creates temp if None)
            timeout: Compilation timeout in seconds

        Returns:
            CompileResult with compilation results

        Raises:
            CompilationFailed: If compilation fails
            ValidationError: If document validation fails
        """
        opts = options or BuildOptions()

        logger.info(f"Compiling document: {document.name}")
        start_time = time.time()

        # Validate options against binary capabilities
        self.binary.validate_options(opts)

        # Validate document content for security and resource constraints
        validation_errors = self.validator.validate_document(document)
        if validation_errors:
            # Log all validation errors/warnings
            for error in validation_errors:
                if error.severity == "error":
                    logger.error(f"Validation error: {error}")
                else:
                    logger.warning(f"Validation warning: {error}")

            # If there are any errors (not just warnings), fail
            error_count = sum(1 for e in validation_errors if e.severity == "error")
            if error_count > 0:
                from b8tex.core.validation import ValidationError
                raise ValidationError(
                    f"Document validation failed with {error_count} error(s)",
                    severity="error",
                )

        # Check cache first
        cache_fingerprint = None
        if self.use_cache and self.cache:
            cache_fingerprint = self.cache.get_fingerprint(
                document,
                opts,
                tectonic_version=self.binary.capabilities.version if self.binary.capabilities else "unknown",
            )

            if self.cache.is_fresh(cache_fingerprint):
                cached_entry = self.cache.read(cache_fingerprint)
                if cached_entry:
                    # Cache hit! Restore artifacts to a temp or persistent workspace
                    workspace = (
                        Workspace.create_persistent(workdir) if workdir else Workspace.create_temp()
                    )

                    try:
                        # Resolve output directory
                        outdir = workspace.resolve_outdir(opts)

                        # Restore cached artifacts to output directory
                        artifacts = self.cache.restore_artifacts(cached_entry, outdir)

                        logger.info(f"Using cached result for {document.name}")
                        result_data = cached_entry.result_data
                        # Type assertion: we know the structure from cache.write()
                        # These are guaranteed to be correct types by cache.write()
                        from typing import cast

                        cached_result = CompileResult(
                            success=cast(bool, result_data["success"]),
                            artifacts=artifacts,
                            warnings=cast(list[str], result_data.get("warnings", [])),
                            errors=cast(list[str], result_data.get("errors", [])),
                            returncode=cast(int, result_data.get("returncode", 0)),
                            elapsed=cast(float, result_data.get("elapsed", 0.0)),
                            invocation=[],  # Cached result - no invocation
                            module_graph=None,
                        )

                        # If using temp workspace, copy artifacts to persistent location
                        if not workdir and cached_result.success:
                            import shutil
                            import tempfile

                            persistent_dir = Path(tempfile.mkdtemp(prefix="b8tex_output_"))
                            persistent_artifacts = []

                            for artifact in cached_result.artifacts:
                                # Copy to persistent location
                                persistent_path = persistent_dir / artifact.path.name
                                shutil.copy2(artifact.path, persistent_path)

                                # Create new artifact with persistent path
                                persistent_artifacts.append(
                                    OutputArtifact(
                                        kind=artifact.kind,
                                        path=persistent_path,
                                        size=artifact.size,
                                        created_at=artifact.created_at,
                                    )
                                )

                            # Update result with persistent artifacts
                            cached_result.artifacts = persistent_artifacts
                            logger.debug(f"Copied cached artifacts to persistent location: {persistent_dir}")

                        return cached_result
                    finally:
                        # Only cleanup if temp workspace
                        if not workdir:
                            workspace.cleanup()

        # Create workspace
        workspace = (
            Workspace.create_persistent(workdir) if workdir else Workspace.create_temp()
        )

        try:
            # Stage document and resources
            entrypoint_path = workspace.stage_document(document)
            workspace.stage_resources(document.resources)

            # Resolve output directory
            outdir = workspace.resolve_outdir(opts)

            # Setup search paths environment
            search_path_env = workspace.setup_search_paths(
                document_paths=document.search_paths,
                project_paths=None,
            )

            # Merge with user environment
            env = workspace.isolate_environment(opts.env)
            env.update(search_path_env)

            # Build command
            cmd = self._build_command(entrypoint_path, outdir, opts)

            # Run compilation
            start_time = time.time()
            result = self.runner.run(
                cmd=cmd,
                cwd=workspace.workdir,
                env=env,
                timeout=timeout,
            )
            elapsed = time.time() - start_time

            # Parse output
            parser = LogParser()
            parser.parse_output(result.stdout + result.stderr)

            # Collect artifacts
            # Get the base name from the entrypoint file
            if isinstance(document.entrypoint, InMemorySource):
                base_name = Path(document.entrypoint.filename).stem
            else:
                base_name = document.entrypoint.stem
            artifacts = self._collect_artifacts(outdir, opts.outfmt, base_name)

            # Build result
            compile_result = CompileResult(
                success=result.returncode == 0,
                artifacts=artifacts,
                warnings=[msg.text for msg in parser.get_warnings()],
                errors=[msg.text for msg in parser.get_errors()],
                returncode=result.returncode,
                elapsed=elapsed,
                invocation=cmd,
                module_graph=parser.build_module_graph(),
            )

            # Write to cache if successful
            if compile_result.success and self.use_cache and self.cache and cache_fingerprint:
                self.cache.write(
                    cache_fingerprint,
                    compile_result,
                    tectonic_version=self.binary.capabilities.version if self.binary.capabilities else "unknown",
                )

            # Raise exception if failed
            if not compile_result.success:
                logger.error(f"Compilation failed for {document.name}: {compile_result.errors[:3] if compile_result.errors else 'Unknown error'}")
                raise CompilationFailed(
                    message=f"Compilation failed with return code {result.returncode}",
                    errors=compile_result.errors,
                    log_tail=result.stderr[-1000:] if result.stderr else None,
                    returncode=result.returncode,
                )

            logger.info(f"Compilation completed: {document.name} ({elapsed:.2f}s)")

            # If using temp workspace, copy artifacts to a persistent temp location
            # so they survive workspace cleanup
            if not workdir and compile_result.success:
                import shutil
                import tempfile

                persistent_dir = Path(tempfile.mkdtemp(prefix="b8tex_output_"))
                persistent_artifacts = []

                for artifact in compile_result.artifacts:
                    # Copy to persistent location
                    persistent_path = persistent_dir / artifact.path.name
                    shutil.copy2(artifact.path, persistent_path)

                    # Create new artifact with persistent path
                    persistent_artifacts.append(
                        OutputArtifact(
                            kind=artifact.kind,
                            path=persistent_path,
                            size=artifact.size,
                            created_at=artifact.created_at,
                        )
                    )

                # Update result with persistent artifacts
                compile_result.artifacts = persistent_artifacts
                logger.debug(f"Copied artifacts to persistent location: {persistent_dir}")

            return compile_result

        finally:
            if not workdir:  # Clean up temp workspace
                workspace.cleanup()

    def build_project(
        self,
        project: Project,
        target: str | None = None,
        *,
        workdir: Path | None = None,
        timeout: float | None = None,
    ) -> CompileResult:
        """Build a project target.

        Args:
            project: Project to build
            target: Target name (uses first target if None)
            workdir: Custom workspace directory
            timeout: Compilation timeout

        Returns:
            CompileResult with compilation results

        Raises:
            CompilationFailed: If compilation fails
            ValueError: If target not found
        """
        if not project.targets:
            raise ValueError("Project has no targets")

        target_name = target or next(iter(project.targets))
        target_obj = project.targets.get(target_name)

        if not target_obj:
            raise ValueError(f"Target '{target_name}' not found in project")

        return self.compile_document(
            document=target_obj.document,
            options=target_obj.options,
            workdir=workdir,
            timeout=timeout,
        )

    def _build_command(
        self,
        entrypoint: Path,
        outdir: Path,
        options: BuildOptions,
    ) -> list[str]:
        """Build the tectonic command line.

        Args:
            entrypoint: Path to main .tex file
            outdir: Output directory
            options: Build options

        Returns:
            Command as list of strings
        """
        # Determine if we should use V2 interface
        # V2 is used if binary supports it and we're in a project directory
        # For now, we default to V1 for compile_document (V2 will be used in build_project)
        interface = self.binary.interface_for(project_dir=None)

        if interface == "v2":
            # Use V2 compile command
            return self.binary.build_v2_compile_cmd(entrypoint, outdir, options)

        # V1 command building (legacy)
        cmd = [str(self.binary.path)]

        # Basic compilation
        cmd.append(str(entrypoint))

        # Output options
        cmd.extend(["--outdir", str(outdir)])
        cmd.extend(["--outfmt", options.outfmt.value])

        # Optional flags
        if options.reruns is not None:
            cmd.extend(["--reruns", str(options.reruns)])

        if options.synctex:
            cmd.append("--synctex")

        if options.print_log:
            cmd.append("--print")

        if options.keep_logs:
            cmd.append("--keep-logs")

        if options.keep_intermediates:
            cmd.append("--keep-intermediates")

        if options.only_cached:
            cmd.append("--only-cached")

        # Security options
        if options.security.untrusted:
            cmd.append("--untrusted")

        # Bundle options
        if options.bundle and options.bundle.id_or_path:
            cmd.extend(["--bundle", str(options.bundle.id_or_path)])

        # Extra arguments
        cmd.extend(options.extra_args)

        return cmd

    def _collect_artifacts(
        self,
        outdir: Path,
        fmt: OutputFormat,
        doc_name: str,
    ) -> list[OutputArtifact]:
        """Collect output artifacts from the output directory.

        Args:
            outdir: Output directory
            fmt: Expected output format
            doc_name: Document name

        Returns:
            List of output artifacts
        """
        artifacts = []

        # Look for primary output
        output_file = outdir / f"{doc_name}.{fmt.value}"
        if output_file.exists():
            artifacts.append(
                OutputArtifact(
                    kind=fmt,
                    path=output_file,
                    size=output_file.stat().st_size,
                )
            )

        return artifacts


def compile_document(
    document: Document,
    options: BuildOptions | None = None,
    *,
    timeout: float | None = None,
) -> CompileResult:
    """Compile a LaTeX document (convenience function).

    Args:
        document: Document to compile
        options: Build options
        timeout: Compilation timeout

    Returns:
        CompileResult with compilation results
    """
    compiler = TectonicCompiler()
    return compiler.compile_document(document, options, timeout=timeout)


def compile_string(
    content: str,
    *,
    name: str = "document",
    options: BuildOptions | None = None,
    timeout: float | None = None,
) -> CompileResult:
    """Compile LaTeX source code (convenience function).

    Args:
        content: LaTeX source code
        name: Document name
        options: Build options
        timeout: Compilation timeout

    Returns:
        CompileResult with compilation results
    """
    document = Document.from_string(content, name=name)
    return compile_document(document, options, timeout=timeout)
