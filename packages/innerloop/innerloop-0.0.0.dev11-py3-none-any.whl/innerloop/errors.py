"""Library-specific exceptions to avoid swallowing errors.

Define clear, typed exceptions that callers can handle precisely.
"""


class InnerLoopError(Exception):
    """Base exception for all library-specific errors."""


class CliNotFoundError(InnerLoopError):
    """Raised when the 'opencode' executable is not found on PATH."""


class CliExitError(InnerLoopError):
    """Raised when the 'opencode' CLI exits with a non-zero status code."""

    def __init__(self, message: str, return_code: int, stderr: str) -> None:
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr


class CliTimeoutError(InnerLoopError):
    """Raised when the CLI operation exceeds the specified timeout."""

    def __init__(self, message: str, timeout: float) -> None:
        super().__init__(message)
        self.timeout = timeout
