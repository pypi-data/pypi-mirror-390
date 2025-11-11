"""Functions related to logging and terminal output handling."""

import collections.abc as c
import io
import logging
import os
import sys
import typing as t
from types import TracebackType


def only_allow_specific_loggers(
    allowed_loggers: c.Sequence[str],
    logging_level_for_disallowed: int = logging.CRITICAL,
) -> None:
    """Restrict logging to only the specified loggers.

    Logging is blocked by setting the log level of all other loggers to the specified
    level.

    Args:
        allowed_loggers:
            An iterable of logger names to allow. All other loggers will be disabled.
        logging_level_for_disallowed:
            The logging level to set for disallowed loggers. Default is
            logging.CRITICAL.

    Example:
        >>> only_allow_specific_loggers(allowed_loggers=["my_logger", "another_logger"])
        >>> logging.getLogger("my_logger").info("This will be logged.")
        >>> logging.getLogger("other_logger").info("This will NOT be logged.")
    """
    for logging_name in logging.root.manager.loggerDict:
        if logging_name not in allowed_loggers:
            logging.getLogger(name=logging_name).setLevel(
                level=logging_level_for_disallowed
            )


class no_terminal_output:
    """Context manager that suppresses all terminal output.

    This implementation is robust, handling both low-level file descriptor
    redirection (to suppress output from C/C++ libraries) and falling back
    to Python-level stream redirection in environments where file descriptors
    are not available (e.g., in doctests, some IDEs, or Jupyter notebooks).

    Example:
        >>> with no_terminal_output():
        ...     print("This will not be printed to the terminal.")
        >>> with no_terminal_output(disable=True):
        ...     print("This will be printed to the terminal.")
        This will be printed to the terminal.
        >>> print("This will also be printed to the terminal.")
        This will also be printed to the terminal.
    """

    def __init__(self, disable: bool = False) -> None:
        """Initialise the context manager.

        Args:
            disable:
                If True, this context manager does nothing.
        """
        self.disable = disable
        self.devnull_file: io.TextIOWrapper | None = None

        # For FD redirection
        self._original_stdout_fd: int | None = None
        self._original_stderr_fd: int | None = None

        # For stream redirection (fallback)
        self._original_stdout: t.TextIO | None = None
        self._original_stderr: t.TextIO | None = None

        # Flag to indicate which method was used
        self._fd_redirect_successful = False

    def __enter__(self) -> None:
        """Suppress all terminal output, trying FD redirection first."""
        if self.disable:
            return

        # Always save original Python streams for the fallback method
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self.devnull_file = open(os.devnull, "w")

        # Try the primary method, using file descriptor redirection. This is the most
        # robust method for suppressing all output, including from subprocesses and C
        # libraries.
        try:
            # Save original FDs by duplicating them
            self._original_stdout_fd = os.dup(sys.stdout.fileno())
            self._original_stderr_fd = os.dup(sys.stderr.fileno())

            # Redirect stdout/stderr to /dev/null
            os.dup2(self.devnull_file.fileno(), sys.stdout.fileno())
            os.dup2(self.devnull_file.fileno(), sys.stderr.fileno())

            self._fd_redirect_successful = True

        # If this fails, fall back to Python stream redirection. This can happen
        # in environments where sys.stdout/sys.stderr do not have real file
        # descriptors (such as when testing, running in Jupyter, on Windows, etc.)
        except (io.UnsupportedOperation, AttributeError, OSError):
            sys.stdout = self.devnull_file
            sys.stderr = self.devnull_file
            self._fd_redirect_successful = False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Re-enable terminal output.

        Args:
            exc_type:
                The exception type, if an exception occurred.
            exc_val:
                The exception value, if an exception occurred.
            exc_tb:
                The traceback, if an exception occurred.
        """
        if self.disable:
            return

        # If we used FD redirection, restore the original FDs
        if self._fd_redirect_successful:
            try:
                if self._original_stdout_fd is not None:
                    os.dup2(self._original_stdout_fd, sys.stdout.fileno())
                if self._original_stderr_fd is not None:
                    os.dup2(self._original_stderr_fd, sys.stderr.fileno())
            except OSError:
                # This could happen if the original FDs were closed, which is unusual
                # but possible.
                pass
            finally:
                # Close the duplicated FDs we created
                if self._original_stdout_fd is not None:
                    os.close(self._original_stdout_fd)
                if self._original_stderr_fd is not None:
                    os.close(self._original_stderr_fd)

        # If we used stream redirection, restore the original streams
        else:
            if self._original_stdout is not None:
                sys.stdout = self._original_stdout
            if self._original_stderr is not None:
                sys.stderr = self._original_stderr

        # Close the /dev/null file in all cases
        if self.devnull_file is not None:
            self.devnull_file.close()
