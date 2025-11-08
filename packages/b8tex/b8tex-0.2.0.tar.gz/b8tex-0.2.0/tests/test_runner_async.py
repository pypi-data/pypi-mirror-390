"""Tests for async ProcessRunner functionality."""

from pathlib import Path

import pytest

from b8tex.core.runner import CompletedProcess, LogLine, ProcessRunner
from b8tex.exceptions import TimeoutExpired


@pytest.mark.asyncio
async def test_run_async_basic():
    """Test basic async process execution."""
    runner = ProcessRunner()

    # Run a simple command
    result = await runner.run_async(
        cmd=["echo", "hello world"],
        cwd=Path.cwd(),
    )

    assert isinstance(result, CompletedProcess)
    assert result.returncode == 0
    assert "hello world" in result.stdout
    assert result.elapsed >= 0


@pytest.mark.asyncio
async def test_run_async_with_env(tmp_path: Path):
    """Test async execution with custom environment."""
    runner = ProcessRunner()

    # Run command that echoes environment variable
    result = await runner.run_async(
        cmd=["sh", "-c", "echo $TEST_VAR"],
        cwd=tmp_path,
        env={"TEST_VAR": "test_value"},
    )

    assert result.returncode == 0
    assert "test_value" in result.stdout


@pytest.mark.asyncio
async def test_run_async_timeout(tmp_path: Path):
    """Test async execution with timeout."""
    runner = ProcessRunner()

    # Run a command that sleeps longer than timeout
    with pytest.raises(TimeoutExpired):
        await runner.run_async(
            cmd=["sleep", "10"],
            cwd=tmp_path,
            timeout=0.1,
        )


@pytest.mark.asyncio
async def test_run_async_failed_command(tmp_path: Path):
    """Test async execution of failing command."""
    runner = ProcessRunner()

    result = await runner.run_async(
        cmd=["sh", "-c", "exit 1"],
        cwd=tmp_path,
    )

    assert result.returncode == 1


@pytest.mark.asyncio
async def test_run_async_captures_stderr(tmp_path: Path):
    """Test that async execution captures stderr."""
    runner = ProcessRunner()

    result = await runner.run_async(
        cmd=["sh", "-c", "echo error >&2"],
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "error" in result.stderr


@pytest.mark.asyncio
async def test_run_streaming_async_basic(tmp_path: Path):
    """Test basic async streaming."""
    runner = ProcessRunner()

    lines = []
    async for log_line in runner.run_streaming_async(
        cmd=["echo", "line1\nline2\nline3"],
        cwd=tmp_path,
    ):
        lines.append(log_line)

    assert len(lines) > 0
    assert all(isinstance(line, LogLine) for line in lines)


@pytest.mark.asyncio
async def test_run_streaming_async_timeout(tmp_path: Path):
    """Test async streaming with timeout."""
    runner = ProcessRunner()

    with pytest.raises(TimeoutExpired):
        async for _ in runner.run_streaming_async(
            cmd=["sleep", "10"],
            cwd=tmp_path,
            timeout=0.1,
        ):
            pass


@pytest.mark.asyncio
async def test_multiple_async_compilations_concurrent(tmp_path: Path):
    """Test running multiple async compilations concurrently."""
    import asyncio

    runner = ProcessRunner()

    # Run multiple echo commands concurrently
    tasks = [
        runner.run_async(
            cmd=["echo", f"test{i}"],
            cwd=tmp_path,
        )
        for i in range(5)
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 5
    assert all(r.returncode == 0 for r in results)
    assert all(isinstance(r, CompletedProcess) for r in results)


@pytest.mark.asyncio
async def test_async_with_working_directory(tmp_path: Path):
    """Test that async execution respects working directory."""
    runner = ProcessRunner()

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    # List files in the directory
    result = await runner.run_async(
        cmd=["ls"],
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "test.txt" in result.stdout


@pytest.mark.asyncio
async def test_async_elapsed_time(tmp_path: Path):
    """Test that elapsed time is tracked correctly."""
    runner = ProcessRunner()

    result = await runner.run_async(
        cmd=["sleep", "0.1"],
        cwd=tmp_path,
    )

    # Should have taken at least 0.1 seconds
    assert result.elapsed >= 0.1
    # But not more than 1 second (with margin)
    assert result.elapsed < 1.0
