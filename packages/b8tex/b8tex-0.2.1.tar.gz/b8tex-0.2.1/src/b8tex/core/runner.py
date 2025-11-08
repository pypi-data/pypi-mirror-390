"""Process execution for Tectonic compilation."""

import asyncio
import contextlib
import logging
import subprocess
import sys
from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from b8tex.exceptions import TimeoutExpired as B8TexTimeoutExpired

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """Resource limits for process execution.

    Attributes:
        memory_mb: Maximum memory in megabytes (None = unlimited)
        timeout_seconds: Maximum execution time in seconds
        max_output_size_mb: Maximum stdout/stderr size in MB
        cpu_time_seconds: Maximum CPU time (Unix only, None = unlimited)
    """

    memory_mb: int | None = 1024  # 1GB default
    timeout_seconds: float | None = 300.0  # 5 minutes default
    max_output_size_mb: int = 100  # 100MB default
    cpu_time_seconds: int | None = None


def _set_memory_limit_unix(memory_mb: int) -> None:
    """Set memory limit for Unix systems (Linux, macOS).

    Args:
        memory_mb: Memory limit in megabytes
    """
    import resource

    memory_bytes = memory_mb * 1024 * 1024
    # RLIMIT_AS = address space (virtual memory)
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))


def _set_cpu_limit_unix(cpu_seconds: int) -> None:
    """Set CPU time limit for Unix systems.

    Args:
        cpu_seconds: CPU time limit in seconds
    """
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))


@dataclass
class LogLine:
    """A line of output from Tectonic.

    Attributes:
        text: Line content
        is_stderr: Whether from stderr (vs stdout)
    """

    text: str
    is_stderr: bool


@dataclass
class CompletedProcess:
    """Result of a completed process execution.

    Attributes:
        returncode: Process exit code
        stdout: Standard output
        stderr: Standard error
        elapsed: Execution time in seconds
    """

    returncode: int
    stdout: str
    stderr: str
    elapsed: float


class ProcessRunner:
    """Executes Tectonic compilation processes with resource limits."""

    def __init__(self, limits: ResourceLimits | None = None):
        """Initialize process runner.

        Args:
            limits: Resource limits to enforce (uses defaults if None)
        """
        self.limits = limits or ResourceLimits()

    def _get_preexec_fn(self) -> Callable[[], None] | None:
        """Get preexec_fn for subprocess with resource limits.

        Returns:
            Callable to set limits, or None on Windows
        """
        # Windows doesn't support preexec_fn
        if sys.platform == "win32":
            return None

        def set_limits() -> None:
            """Set resource limits in child process."""
            if self.limits.memory_mb:
                try:
                    _set_memory_limit_unix(self.limits.memory_mb)
                except Exception as e:
                    logger.warning(f"Failed to set memory limit: {e}")

            if self.limits.cpu_time_seconds:
                try:
                    _set_cpu_limit_unix(self.limits.cpu_time_seconds)
                except Exception as e:
                    logger.warning(f"Failed to set CPU limit: {e}")

        return set_limits

    def run(
        self,
        cmd: list[str],
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> CompletedProcess:
        """Run a command and capture output.

        Args:
            cmd: Command and arguments
            cwd: Working directory
            env: Environment variables (merged with os.environ)
            timeout: Timeout in seconds

        Returns:
            CompletedProcess with results

        Raises:
            TimeoutExpired: If process times out
        """
        import os
        import time

        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        # Use provided timeout or default from limits
        effective_timeout = timeout or self.limits.timeout_seconds

        logger.debug(f"Running command: {' '.join(cmd)}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")
        if self.limits.memory_mb:
            logger.debug(f"Memory limit: {self.limits.memory_mb}MB")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=full_env,
                capture_output=True,
                text=True,
                check=False,
                timeout=effective_timeout,
                preexec_fn=self._get_preexec_fn(),
            )

            elapsed = time.time() - start_time

            # Check output size and truncate if necessary
            output_size_mb = (len(result.stdout) + len(result.stderr)) / (1024 * 1024)
            if output_size_mb > self.limits.max_output_size_mb:
                logger.warning(
                    f"Output size {output_size_mb:.1f}MB exceeds limit "
                    f"{self.limits.max_output_size_mb}MB, truncating"
                )
                # Truncate output
                max_chars = self.limits.max_output_size_mb * 1024 * 1024
                result.stdout = result.stdout[: max_chars // 2]
                result.stderr = result.stderr[: max_chars // 2]

            return CompletedProcess(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                elapsed=elapsed,
            )

        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            if timeout:
                raise B8TexTimeoutExpired(timeout) from e
            raise

    def run_streaming(
        self,
        cmd: list[str],
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Iterator[LogLine]:
        """Run a command and stream output line by line.

        Args:
            cmd: Command and arguments
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds

        Yields:
            LogLine instances

        Raises:
            TimeoutExpired: If process times out
        """
        import os

        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=full_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Stream stdout and stderr
            # Note: This is a simplified implementation
            # A production version would use threading or async I/O
            # to properly interleave stdout/stderr

            if process.stdout:
                for line in process.stdout:
                    yield LogLine(text=line.rstrip("\n"), is_stderr=False)

            process.wait(timeout=timeout)

            if process.stderr:
                stderr_content = process.stderr.read()
                for line in stderr_content.splitlines():
                    yield LogLine(text=line, is_stderr=True)

        except subprocess.TimeoutExpired as e:
            if process:
                process.kill()
            if timeout:
                raise B8TexTimeoutExpired(timeout) from e
            raise

    async def run_async(
        self,
        cmd: list[str],
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> CompletedProcess:
        """Run a command asynchronously and capture output.

        Args:
            cmd: Command and arguments
            cwd: Working directory
            env: Environment variables (merged with os.environ)
            timeout: Timeout in seconds

        Returns:
            CompletedProcess with results

        Raises:
            TimeoutExpired: If process times out
        """
        import os
        import time

        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        start_time = time.time()

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                env=full_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for completion with timeout
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

            elapsed = time.time() - start_time

            return CompletedProcess(
                returncode=process.returncode or 0,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
                elapsed=elapsed,
            )

        except TimeoutError as e:
            # Kill the process
            if process:
                process.kill()
                await process.wait()

            elapsed = time.time() - start_time
            if timeout:
                raise B8TexTimeoutExpired(timeout) from e
            raise

    async def run_streaming_async(
        self,
        cmd: list[str],
        cwd: Path,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> AsyncIterator[LogLine]:
        """Run a command asynchronously and stream output line by line.

        Args:
            cmd: Command and arguments
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds

        Yields:
            LogLine instances

        Raises:
            TimeoutExpired: If process times out
        """
        import os
        import time

        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        logger.debug(f"Running async command: {' '.join(cmd)}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")

        process = None
        time.time()

        try:
            # Use asyncio.timeout context manager (Python 3.11+)
            from contextlib import nullcontext
            async with asyncio.timeout(timeout) if timeout else nullcontext():
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=cwd,
                    env=full_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Stream stdout
                if process.stdout:
                    async for line_bytes in process.stdout:
                        line = line_bytes.decode("utf-8", errors="replace").rstrip("\n")
                        yield LogLine(text=line, is_stderr=False)

                # Wait for process completion
                await process.wait()

                # Read any remaining stderr
                if process.stderr:
                    stderr_bytes = await process.stderr.read()
                    stderr_content = stderr_bytes.decode("utf-8", errors="replace")
                    for line in stderr_content.splitlines():
                        yield LogLine(text=line, is_stderr=True)

        except TimeoutError as e:
            if process:
                process.kill()
                with contextlib.suppress(Exception):
                    await process.wait()
            if timeout:
                raise B8TexTimeoutExpired(timeout) from e
            raise
