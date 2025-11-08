"""Common dict utilities."""

from typing import Any


def reverse_dict(d: dict[Any, Any]) -> dict[Any, Any]:
    """Reverse a dictionary.

    Args:
        d: Dictionary to reverse

    Returns:
        Reversed dictionary

    """
    return {v: k for k, v in d.items()}
