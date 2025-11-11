import subprocess
import sys


class RuffFormattingError(Exception):
    """Exception raised when ruff formatting fails."""

    pass


def format_code_with_ruff(code: str) -> str:
    """Format Python code using ruff.

    Returns formatted code.

    Raises:
        RuffFormattingError: If ruff formatting fails.
    """
    result = subprocess.run(
        ["ruff", "format", "-"],
        input=code.encode("utf-8"),
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8")
        raise RuffFormattingError(error_msg)

    return result.stdout.decode("utf-8")
