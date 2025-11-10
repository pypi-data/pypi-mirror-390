"""Build utilities for creating and managing project builds.

This module provides functions for building and managing project artifacts,
including creating build scripts, configuring build environments, and
handling build dependencies. These utilities help with the packaging and
distribution of project code.
"""

from pathlib import Path

from winipedia_utils.dev.artifacts.build import Build


class WinipediaUtilsBuild(Build):
    """Build script for winipedia_utils."""

    @classmethod
    def get_artifacts(cls) -> list[Path]:
        """Build the project."""
        paths = [cls.ARTIFACTS_PATH / "build.txt"]
        for path in paths:
            path.write_text("Hello World!")
        return paths


if __name__ == "__main__":
    WinipediaUtilsBuild()
