"""Git utilities for file and directory operations.

This module provides utility functions for working with Git repositories,
including checking if paths are in .gitignore and walking directories
while respecting gitignore patterns. These utilities help with file operations
that need to respect Git's ignore rules.
"""

import os
from collections.abc import Generator
from pathlib import Path

import pathspec

from winipedia_utils.dev.configs.gitignore import GitIgnoreConfigFile
from winipedia_utils.utils.logging.logger import get_logger

logger = get_logger(__name__)


def path_is_in_gitignore(relative_path: str | Path) -> bool:
    """Check if a path matches any pattern in the .gitignore file.

    Args:
        relative_path: The path to check, relative to the repository root

    Returns:
        True if the path matches any pattern in .gitignore, False otherwise

    """
    as_path = Path(relative_path)
    is_dir = (
        bool(as_path.suffix == "") or as_path.is_dir() or str(as_path).endswith(os.sep)
    )
    is_dir = is_dir and not as_path.is_file()

    as_posix = as_path.as_posix()
    if is_dir and not as_posix.endswith("/"):
        as_posix += "/"

    spec = pathspec.PathSpec.from_lines(
        "gitwildmatch",
        GitIgnoreConfigFile.load(),
    )

    return spec.match_file(as_posix)


def walk_os_skipping_gitignore_patterns(
    folder: str | Path = ".",
) -> Generator[tuple[Path, list[str], list[str]], None, None]:
    """Walk a directory tree while skipping paths that match gitignore patterns.

    Similar to os.walk, but skips directories and files that match patterns
    in the .gitignore file.

    Args:
        folder: The root directory to start walking from

    Yields:
        Tuples of (current_path, directories, files) for each directory visited

    """
    folder = Path(folder)
    for root, dirs, files in os.walk(folder):
        rel_root = Path(root).relative_to(".")

        # skip all in patterns in .gitignore
        if path_is_in_gitignore(rel_root):
            logger.info("Skipping %s because it is in .gitignore", rel_root)
            dirs.clear()
            continue

        # remove all files that match patterns in .gitignore
        valid_files = [f for f in files if not path_is_in_gitignore(rel_root / f)]
        valid_dirs = [d for d in dirs if not path_is_in_gitignore(rel_root / d)]

        yield rel_root, valid_dirs, valid_files
