"""Retry strategies and cleanup management for transient failures."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryPolicy:
    """Configuration for retry behavior.

    Implements exponential backoff with configurable parameters for
    handling transient failures like network issues or temporary I/O errors.

    Attributes:
        max_attempts: Maximum number of attempts (1 = no retry, default: 3)
        initial_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries (default: 30.0)
        exponential_backoff: Whether to use exponential backoff (default: True)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        retryable_exceptions: Exception types to retry on

    Example:
        >>> policy = RetryPolicy(max_attempts=5, initial_delay=2.0)
        >>> result = retry_with_policy(policy, lambda: download_file(), "download")
    """

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    exponential_backoff: bool = True
    backoff_factor: float = 2.0
    retryable_exceptions: tuple[type[Exception], ...] = (
        OSError,
        IOError,
        TimeoutError,
    )


def retry_with_policy[T](
    policy: RetryPolicy,
    operation: Callable[[], T],
    operation_name: str = "operation",
) -> T:
    """Execute an operation with retry policy.

    Retries the operation according to the policy, with exponential backoff
    for transient failures. Logs warnings for each retry attempt.

    Args:
        policy: Retry policy to use
        operation: Callable to execute (should be idempotent)
        operation_name: Name for logging purposes

    Returns:
        Result from successful operation execution

    Raises:
        Exception: The last exception if all retries fail

    Example:
        >>> policy = RetryPolicy(max_attempts=3)
        >>> def flaky_operation():
        ...     if random.random() < 0.5:
        ...         raise OSError("Network error")
        ...     return "success"
        >>> result = retry_with_policy(policy, flaky_operation, "network_call")
    """
    last_exception: Exception | None = None
    delay = policy.initial_delay

    for attempt in range(1, policy.max_attempts + 1):
        try:
            logger.debug(f"{operation_name}: attempt {attempt}/{policy.max_attempts}")
            return operation()

        except policy.retryable_exceptions as e:
            last_exception = e

            if attempt == policy.max_attempts:
                logger.error(
                    f"{operation_name} failed after {policy.max_attempts} attempts: {e}"
                )
                raise

            logger.warning(
                f"{operation_name} failed (attempt {attempt}/{policy.max_attempts}), "
                f"retrying in {delay:.1f}s: {e}"
            )

            time.sleep(delay)

            # Update delay for next iteration
            if policy.exponential_backoff:
                delay = min(delay * policy.backoff_factor, policy.max_delay)

    # Should never reach here, but satisfy type checker
    if last_exception:
        raise last_exception
    raise RuntimeError(f"{operation_name} failed with no exception recorded")


class CleanupManager:
    """Manages cleanup of resources on failure.

    Provides a context manager that ensures cleanup callbacks are executed
    even if operations fail. Callbacks are executed in reverse registration
    order (LIFO) to properly handle dependencies.

    Example:
        >>> with CleanupManager() as cleanup:
        ...     temp_file = create_temp_file()
        ...     cleanup.register(lambda: temp_file.unlink(), "temp_file_cleanup")
        ...
        ...     workspace = create_workspace()
        ...     cleanup.register(lambda: workspace.cleanup(), "workspace_cleanup")
        ...
        ...     # If an exception occurs, cleanups run in reverse order:
        ...     # workspace_cleanup, then temp_file_cleanup
        ...     do_work()
    """

    def __init__(self) -> None:
        """Initialize the cleanup manager."""
        self._cleanup_callbacks: list[tuple[Callable[[], None], str]] = []

    def register(self, callback: Callable[[], None], name: str = "cleanup") -> None:
        """Register a cleanup callback.

        Callbacks are executed in reverse registration order (LIFO).

        Args:
            callback: Function to call on cleanup (should not raise)
            name: Name for logging purposes

        Example:
            >>> cleanup = CleanupManager()
            >>> cleanup.register(lambda: print("cleanup 1"), "first")
            >>> cleanup.register(lambda: print("cleanup 2"), "second")
            >>> cleanup.cleanup()  # Prints: cleanup 2, then cleanup 1
        """
        self._cleanup_callbacks.append((callback, name))
        logger.debug(f"Registered cleanup callback: {name}")

    def cleanup(self) -> None:
        """Execute all cleanup callbacks in reverse order.

        Exceptions during cleanup are logged but do not prevent other
        callbacks from executing.
        """
        for callback, name in reversed(self._cleanup_callbacks):
            try:
                logger.debug(f"Running cleanup: {name}")
                callback()
            except Exception as e:
                logger.error(f"Cleanup '{name}' failed: {e}", exc_info=True)

    def __enter__(self) -> CleanupManager:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> Literal[False]:
        """Exit context manager and run cleanup if exception occurred.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            False to propagate the exception
        """
        if exc_type is not None:
            logger.debug(f"Exception occurred, running cleanup: {exc_type.__name__}")
            self.cleanup()
        return False
