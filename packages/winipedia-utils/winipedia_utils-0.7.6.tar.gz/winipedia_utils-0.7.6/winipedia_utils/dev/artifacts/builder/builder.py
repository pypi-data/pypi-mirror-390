"""Build script.

All subclasses of Builder in the builds package are automatically called.
"""

from winipedia_utils.dev.artifacts.builder.base.base import Builder


class WinipediaUtilsBuilder(Builder):
    """Build script for winipedia_utils."""

    @classmethod
    def create_artifacts(cls) -> None:
        """Build the project."""
        paths = [cls.ARTIFACTS_PATH / "build.txt"]
        for path in paths:
            path.write_text("Hello World!")
